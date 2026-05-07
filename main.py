# api/main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from src.fetcher import Fetcher, FetchError
from src.models import (
    BrandListResponse,
    ModelListResponse,
    EstimateRequest,
    EstimateResponse,
    BreakEvenRequest,
    BreakEvenResponse,
    BreakEvenAnalysisRequest,
    BreakEvenAnalysisResponse,
    PurchaseYearSeries,
    DataPoint
)
from src.calculator import CarValueCalculator, LoanCalculator
import logging
import datetime

app = FastAPI(title="Car Cost Estimator API", version="1.0")

# CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

fetcher = Fetcher()

logger = logging.getLogger("uvicorn.error")


def fill_missing_prices(prices: List[float], extend: bool = False) -> tuple[List[float], List[bool]]:
    """
    Interpolate and extrapolate missing values (0.0) in the price list.
    If extend is False, returns prices as is and all False for simulated.
    Returns (filled_prices, is_simulated_mask)
    """
    n = len(prices)
    is_simulated = [p <= 0 for p in prices]

    if not extend or not prices:
        return prices, is_simulated

    filled = list(prices)

    # 1. Find indices of non-zero values
    valid_indices = [i for i, p in enumerate(prices) if p > 0]

    if not valid_indices:
        return filled, is_simulated

    # 2. Linear interpolation for internal gaps
    for i in range(len(valid_indices) - 1):
        idx1 = valid_indices[i]
        idx2 = valid_indices[i+1]
        if idx2 - idx1 > 1:
            val1 = filled[idx1]
            val2 = filled[idx2]
            step = (val2 - val1) / (idx2 - idx1)
            for j in range(idx1 + 1, idx2):
                filled[j] = val1 + step * (j - idx1)

    # 3. Extrapolation for start/end gaps
    # Start (before first valid)
    first_valid = valid_indices[0]
    if first_valid > 0:
        if len(valid_indices) > 1:
            # use slope between first two valid points
            idx1, idx2 = valid_indices[0], valid_indices[1]
            slope = (filled[idx2] - filled[idx1]) / (idx2 - idx1)
            for j in range(first_valid - 1, -1, -1):
                filled[j] = filled[j+1] - slope
        else:
            # constant
            for j in range(first_valid - 1, -1, -1):
                filled[j] = filled[first_valid]

    # End (after last valid)
    last_valid = valid_indices[-1]
    if last_valid < n - 1:
        if len(valid_indices) > 1:
            # use slope between last two valid points
            idx1, idx2 = valid_indices[-2], valid_indices[-1]
            slope = (filled[idx2] - filled[idx1]) / (idx2 - idx1)
            for j in range(last_valid + 1, n):
                filled[j] = filled[j-1] + slope
        else:
            # constant
            for j in range(last_valid + 1, n):
                filled[j] = filled[last_valid]

    # Ensure no negative prices
    return [max(0.0, p) for p in filled], is_simulated


@app.get("/api/brands", response_model=BrandListResponse)
def list_brands():
    """Return brand list discovered on the listing home page."""
    try:
        dropdowns = fetcher.fetch_dropdown_options()
        return BrandListResponse(brands=sorted(set(dropdowns.get("make", []))))
    except FetchError as ex:
        logger.exception("Failed to fetch brands")
        raise HTTPException(status_code=503, detail=str(ex))


@app.get("/api/models", response_model=ModelListResponse)
def list_models(brand: Optional[str] = None):
    """Return models for a brand name (case-insensitive)."""
    # Explicit check so missing brand -> 400 (matches test expectation)
    if not brand:
        raise HTTPException(status_code=400, detail="brand parameter is required")
    try:
        models = fetcher.fetch_car_models(brand.strip().lower())
        return ModelListResponse(brand=brand, models=sorted(models))
    except FetchError as ex:
        logger.exception("Failed to fetch models")
        raise HTTPException(status_code=503, detail=str(ex))


@app.post("/api/estimate", response_model=EstimateResponse)
def estimate_monthly_costs(req: EstimateRequest):
    """
    Accepts a request describing selection and financial parameters,
    returns monthly cost breakdown and the year-by-year values series used.
    """
    # Build series of year values by querying different registration years
    try:
        years_to_query = req.number_of_years + req.purchase_year_index + 1
        year_values = []
        missing_years = []
        std_devs = []
        
        current_year = req.registration_year or datetime.datetime.now().year
        
        for offset in range(years_to_query):
            selected = {
                "make": req.brand,
                "model": req.model,
                "details": req.details or "",
                "zip": req.zip_code,
                "firstRegistration": current_year - offset,
                "shift_type": req.shift_types or []
            }
            price, std_dev = fetcher.fetch_car_costs(selected)
            year_values.append(float(price))
            std_devs.append(float(std_dev))
        
        year_values, is_simulated = fill_missing_prices(year_values, req.extend_missing_values)

        warning = None
        adjusted_years = None

        if all(sim for sim in is_simulated):
             raise HTTPException(status_code=400, detail="No historical data found to perform an estimate.")

        loan_calc = LoanCalculator(req.loan_value, req.bank_rate_percent, req.loan_years)
        loan_monthly, loan_total_interest = loan_calc.calculate_loan_costs()

        calc = CarValueCalculator(year_values, req.number_of_years, req.monthly_maintenance, req.purchase_year_index, req.inflation_rate, req.loan_value)
        monthly_depr = calc.monthly_depreciation()
        monthly_tot = calc.monthly_total_cost(loan_monthly, req.loan_years)

        cost_during, cost_after, inflation_impact_total = calc.calculate_period_costs(loan_monthly, req.loan_years)

        purchase_price = year_values[req.purchase_year_index]
        final_value = year_values[req.purchase_year_index + req.number_of_years]

        return EstimateResponse(
            purchase_price=purchase_price,
            estimated_final_value=final_value,
            monthly_depreciation=monthly_depr,
            monthly_maintenance=req.monthly_maintenance,
            loan_monthly_payment=loan_monthly,
            loan_total_interest=loan_total_interest,
            total_monthly_cost=monthly_tot,
            year_values=year_values,
            is_simulated=is_simulated,
            monthly_cost_during_loan=cost_during,
            monthly_cost_after_loan=cost_after,
            inflation_impact_total=inflation_impact_total,
            warning=warning,
            price_stddev=std_devs,
            adjusted_number_of_years=adjusted_years
        )
    except FetchError as ex:
        logger.exception("Fetch error during estimate")
        raise HTTPException(status_code=503, detail=str(ex))
    except Exception as ex:
        logger.exception("Unexpected error during estimate")
        raise HTTPException(status_code=500, detail=str(ex))


@app.post("/api/break_even", response_model=BreakEvenResponse)
def break_even(study: BreakEvenRequest):
    """
    Given an EstimateRequest and a monthly rent cost, compute months to break-even
    comparing owning (including depreciation, maintenance, loan) vs renting (fixed cost).
    Returns monthly series for both and month index of break-even (if any).
    """
    try:
        # call estimate logic (we reuse code)
        study.estimate.number_of_years = study.years
        estimate_resp = estimate_monthly_costs(study.estimate)
        months = study.years * 12
        buy_series = []
        rent_series = [float(study.rent_monthly_cost)] * months

        # Calculate corrected cumulative buy cost
        purchase_price = estimate_resp.purchase_price
        resell_price = estimate_resp.estimated_final_value
        monthly_cost = estimate_resp.total_monthly_cost

        # Monthly series remains the same
        buy_series = [monthly_cost] * months

        # Total buy cost over time = purchase - resell + monthly cost × months
        # We'll use this in the cumulative calculation below

        months_to_breakeven = None
        cumulative_buy = 0.0
        cumulative_rent = 0.0
        for m in range(1, months + 1):
            cumulative_buy = purchase_price - resell_price + monthly_cost * m

            cumulative_rent += rent_series[m - 1]
            if cumulative_buy <= cumulative_rent:
                months_to_breakeven = m
                break

        msg = None
        if months_to_breakeven is None:
            msg = "No break-even within provided horizon; renting is cheaper within the requested timeframe."

        return BreakEvenResponse(
            months_to_break_even=months_to_breakeven,
            buy_monthly_series=buy_series,
            rent_monthly_series=rent_series,
            message=msg,
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.exception("break_even unexpected")
        raise HTTPException(status_code=500, detail=str(ex))

@app.post("/api/break_even_analysis", response_model=BreakEvenAnalysisResponse)
def break_even_analysis(req: BreakEvenAnalysisRequest):
    try:
        current_year = datetime.datetime.now().year
        year_values = []
        for offset in range(int(req.max_years) + 1):
            selected = {
                "make": req.brand,
                "model": req.model,
                "details": req.details or "",
                "zip": req.zip_code,
                "firstRegistration": current_year - offset,
                "shift_type": req.shift_types or []
            }
            price, _ = fetcher.fetch_car_costs(selected)
            year_values.append(float(price) if price > 0 else 0.0)

        year_values, _ = fill_missing_prices(year_values, req.extend_missing_values)

        purchase_series = []
        for purchase_offset in range(len(year_values)):
            purchase_price = year_values[purchase_offset]
            if purchase_price == 0:
                continue

            data_points = []
            for sell_offset in range(purchase_offset + 1, len(year_values)):
                sell_price = year_values[sell_offset]
                if sell_price == 0:
                    continue

                years_owned = sell_offset - purchase_offset

                loan_calc = LoanCalculator(req.loan_value, req.bank_rate_percent, req.loan_years)
                loan_monthly, _ = loan_calc.calculate_loan_costs()

                # We need a CarValueCalculator to compute total maintenance and depreciation
                # But we have year_values for all points.
                calc = CarValueCalculator(
                    year_values=year_values,
                    number_of_years=years_owned,
                    monthly_maintenance=req.monthly_maintenance,
                    purchase_year_index=purchase_offset,
                    inflation_rate=req.inflation_rate,
                    loan_value=req.loan_value
                )

                monthly_cost = calc.monthly_total_cost(loan_monthly=loan_monthly, loan_years=req.loan_years)
                overall_cost = monthly_cost * (years_owned * 12)
                _, _, inflation_impact = calc.calculate_period_costs(loan_monthly, req.loan_years)

                data_points.append(DataPoint(
                    years_owned=years_owned,
                    overall_cost=overall_cost,
                    monthly_cost=monthly_cost,
                    inflation_impact=inflation_impact
                ))
            
            if purchase_offset == 0:
                description = "Buy brand new"
            elif purchase_offset == 1:
                description = "Buy 1 year old"
            else:
                description = f"Buy {purchase_offset} years old"

            purchase_series.append(PurchaseYearSeries(
                purchase_description=description,
                data_points=data_points
            ))

        rental_series = []
        for y in range(1, req.max_years + 1):
            rental_series.append(DataPoint(
                years_owned=y,
                overall_cost=req.rent_monthly_cost * 12 * y,
                monthly_cost=req.rent_monthly_cost
            ))
            
        return BreakEvenAnalysisResponse(
            rental_series=rental_series,
            purchase_series=purchase_series
        )
    except FetchError as ex:
        logger.exception("Fetch error during break-even analysis")
        raise HTTPException(status_code=503, detail=str(ex))
    except Exception as ex:
        logger.exception("Unexpected error during break-even analysis")
        raise HTTPException(status_code=500, detail=str(ex))

if __name__ == "__main__":
    uvicorn.run(app, port=8000)