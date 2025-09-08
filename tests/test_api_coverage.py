# tests/test_api_coverage.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import main as api_main
from fastapi import HTTPException

client = TestClient(app)


def test_get_brands_success():
    # mock dropdowns
    with patch.object(api_main.fetcher, "fetch_dropdown_options", return_value={"make": ["bmw", "audi"]}):
        r = client.get("/api/brands")
        assert r.status_code == 200
        data = r.json()
        assert "brands" in data
        assert set(data["brands"]) == {"audi", "bmw"}


def test_get_brands_fetch_error():
    with patch.object(api_main.fetcher, "fetch_dropdown_options", side_effect=api_main.FetchError("network")):
        r = client.get("/api/brands")
        assert r.status_code == 503
        assert "detail" in r.json()


def test_get_models_success():
    with patch.object(api_main.fetcher, "fetch_car_models", return_value=["320i", "x3"]):
        r = client.get("/api/models?brand=bmw")
        assert r.status_code == 200
        data = r.json()
        assert data["brand"] == "bmw"
        assert "320i" in data["models"]


def test_get_models_missing_brand():
    r = client.get("/api/models")  # missing brand param -> 400
    assert r.status_code == 400
    assert "detail" in r.json()


def test_get_models_fetcherror():
    with patch.object(api_main.fetcher, "fetch_car_models", side_effect=api_main.FetchError("nope")):
        r = client.get("/api/models?brand=unknown")
        assert r.status_code == 503
        assert "detail" in r.json()


def fake_fetch_car_costs(selected_values):
    # deterministic price as function of registration year
    year = int(selected_values.get("firstRegistration") or 2025)
    age = 2025 - year
    # ensure positive price
    return max(1000, 30000 - age * 2000)


@patch.object(api_main.fetcher, "fetch_car_costs", side_effect=fake_fetch_car_costs)
def test_estimate_success(mock_fetch):
    payload = {
        "brand": "testbrand",
        "model": "testmodel",
        "details": "",
        "zip_code": "10139-torino",
        "registration_year": 2025,
        "number_of_years": 3,
        "purchase_year_index": 1,
        "monthly_maintenance": 100.0,
        "loan_value": 0.0,
        "bank_rate_percent": 0.0,
        "loan_years": 0,
        "shift_types": []
    }
    r = client.post("/api/estimate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "purchase_price" in data
    assert data["loan_monthly_payment"] == 0.0
    # year_values length should be number_of_years + purchase_year_index + 1
    assert len(data["year_values"]) == payload["number_of_years"] + payload["purchase_year_index"] + 1


def test_estimate_fetcherror():
    # simulate fetcher failing -> returns 503
    with patch.object(api_main.fetcher, "fetch_car_costs", side_effect=api_main.FetchError("fail")):
        payload = {
            "brand": "testbrand",
            "model": "testmodel",
            "registration_year": 2025,
            "number_of_years": 2,
            "purchase_year_index": 1,
            "monthly_maintenance": 100.0,
            "loan_value": 0.0,
            "bank_rate_percent": 0.0,
            "loan_years": 0,
            "shift_types": []
        }
        r = client.post("/api/estimate", json=payload)
        assert r.status_code == 503
        assert "detail" in r.json()


def test_estimate_internal_exception():
    # patch fetch_car_costs OK then force LoanCalculator.calculate_loan_costs to raise -> 500
    with patch.object(api_main.fetcher, "fetch_car_costs", side_effect=fake_fetch_car_costs):
        with patch.object(api_main.LoanCalculator, "calculate_loan_costs", side_effect=RuntimeError("boom")):
            payload = {
                "brand": "testbrand",
                "model": "testmodel",
                "registration_year": 2025,
                "number_of_years": 2,
                "purchase_year_index": 1,
                "monthly_maintenance": 100.0,
                "loan_value": 1000.0,
                "bank_rate_percent": 5.0,
                "loan_years": 1,
                "shift_types": []
            }
            r = client.post("/api/estimate", json=payload)
            assert r.status_code == 500
            assert "detail" in r.json()


def test_break_even_breakeven_found():
    # patch estimate_monthly_costs to return an object with low total_monthly_cost
    est = api_main.EstimateResponse(
        purchase_price=20000.0,
        estimated_final_value=12000.0,
        monthly_depreciation=200.0,
        monthly_maintenance=100.0,
        loan_monthly_payment=50.0,
        loan_total_interest=500.0,
        total_monthly_cost=350.0,
        year_values=[20000, 18000, 15000, 12000, 9000]
    )
    with patch.object(api_main, "estimate_monthly_costs", return_value=est):
        payload = {
            "estimate": {
                "brand": "testbrand",
                "model": "testmodel",
                "registration_year": 2025,
                "number_of_years": 3,
                "purchase_year_index": 1,
                "monthly_maintenance": 100.0,
                "loan_value": 0.0,
                "bank_rate_percent": 0.0,
                "loan_years": 0,
                "shift_types": []
            },
            "rent_monthly_cost": 400.0,
            "years": 2
        }
        r = client.post("/api/break_even", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["months_to_break_even"] == 1
        assert len(data["buy_monthly_series"]) == 24
        assert len(data["rent_monthly_series"]) == 24


def test_break_even_no_breakeven():
    # estimate total monthly cost larger than rent -> no break-even
    est = api_main.EstimateResponse(
        purchase_price=20000.0,
        estimated_final_value=12000.0,
        monthly_depreciation=500.0,
        monthly_maintenance=200.0,
        loan_monthly_payment=300.0,
        loan_total_interest=1000.0,
        total_monthly_cost=1000.0,
        year_values=[20000, 18000, 15000, 12000, 9000]
    )
    with patch.object(api_main, "estimate_monthly_costs", return_value=est):
        payload = {
            "estimate": {
                "brand": "testbrand",
                "model": "testmodel",
                "registration_year": 2025,
                "number_of_years": 3,
                "purchase_year_index": 1,
                "monthly_maintenance": 100.0,
                "loan_value": 0.0,
                "bank_rate_percent": 0.0,
                "loan_years": 0,
                "shift_types": []
            },
            "rent_monthly_cost": 300.0,
            "years": 1
        }
        r = client.post("/api/break_even", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["months_to_break_even"] is None
        assert data["message"] is not None


def test_break_even_unexpected_error():
    # make estimate_monthly_costs raise a generic exception -> 500
    with patch.object(api_main, "estimate_monthly_costs", side_effect=RuntimeError("unexpected")):
        payload = {
            "estimate": {
                "brand": "testbrand",
                "model": "testmodel",
                "registration_year": 2025,
                "number_of_years": 1,
                "purchase_year_index": 0,
                "monthly_maintenance": 100.0,
                "loan_value": 0.0,
                "bank_rate_percent": 0.0,
                "loan_years": 0,
                "shift_types": []
            },
            "rent_monthly_cost": 300.0,
            "years": 1
        }
        r = client.post("/api/break_even", json=payload)
        assert r.status_code == 500
        assert "detail" in r.json()


def test_brands_empty_results():
    """If fetcher returns no 'make' key or empty list, API should return empty brands list."""
    with patch.object(api_main.fetcher, "fetch_dropdown_options", return_value={}):
        r = client.get("/api/brands")
        assert r.status_code == 200
        data = r.json()
        assert "brands" in data
        assert data["brands"] == []


def test_models_returns_empty_list():
    """If fetcher returns an empty list for models, API returns 200 with empty 'models' array."""
    with patch.object(api_main.fetcher, "fetch_car_models", return_value=[]):
        r = client.get("/api/models?brand=testbrand")
        assert r.status_code == 200
        data = r.json()
        assert data["brand"] == "testbrand"
        assert isinstance(data["models"], list)
        assert len(data["models"]) == 0


def test_estimate_backfill_zero_price():
    """
    Ensure that when fetch_car_costs returns a sequence with a zero after a non-zero
    the code backfills the zero with the last known non-zero value.
    This hits the 'if price == 0 and len(year_values) > 1: year_values[-1] = year_values[-2]' branch.
    """
    # side effect sequence: newest->older prices (3 calls required for number_of_years=2, purchase_year_index=0)
    seq = [30000, 0, 25000]

    def side_effect(selected):
        return seq.pop(0)

    with patch.object(api_main.fetcher, "fetch_car_costs", side_effect=side_effect):
        payload = {
            "brand": "tb",
            "model": "tm",
            "details": "",
            "zip_code": "10139-torino",
            "registration_year": 2025,
            "number_of_years": 2,
            "purchase_year_index": 0,
            "monthly_maintenance": 100.0,
            "loan_value": 0.0,
            "bank_rate_percent": 0.0,
            "loan_years": 0,
            "shift_types": []
        }
        r = client.post("/api/estimate", json=payload)
        assert r.status_code == 200
        data = r.json()
        # second entry should have been backfilled to first non-zero (30000)
        assert data["year_values"][1] == 30000.0


def test_estimate_validation_error():
    """Missing required fields for /api/estimate should return 422 from FastAPI validation."""
    # send an empty body which doesn't satisfy EstimateRequest schema
    r = client.post("/api/estimate", json={})
    assert r.status_code == 422


def test_break_even_propagates_http_exception():
    """
    If estimate_monthly_costs raises an HTTPException (e.g. 503), break_even should re-raise it.
    This exercises the 'except HTTPException: raise' path inside break_even.
    """
    http_exc = HTTPException(status_code=503, detail="upstream")
    with patch.object(api_main, "estimate_monthly_costs", side_effect=http_exc):
        payload = {
            "estimate": {
                "brand": "testbrand",
                "model": "testmodel",
                "registration_year": 2025,
                "number_of_years": 1,
                "purchase_year_index": 0,
                "monthly_maintenance": 100.0,
                "loan_value": 0.0,
                "bank_rate_percent": 0.0,
                "loan_years": 0,
                "shift_types": []
            },
            "rent_monthly_cost": 300.0,
            "years": 1
        }
        r = client.post("/api/break_even", json=payload)
        assert r.status_code == 503
        assert r.json().get("detail") == "upstream"
