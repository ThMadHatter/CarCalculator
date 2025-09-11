from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class BrandListResponse(BaseModel):
    brands: List[str] = Field(default_factory=list)


class ModelListResponse(BaseModel):
    brand: str
    models: List[str] = Field(default_factory=list)


class EstimateRequest(BaseModel):
    brand: str
    model: str
    details: Optional[str] = ""
    zip_code: Optional[str] = "10139-torino"
    registration_year: Optional[int] = None
    number_of_years: int = 10
    purchase_year_index: int = 3  # index into returned series: how many years after newest
    monthly_maintenance: float = 100.0
    loan_value: float = 0.0
    bank_rate_percent: float = 0.0
    loan_years: int = 0
    shift_types: Optional[List[str]] = []


class EstimateResponse(BaseModel):
    purchase_price: float
    estimated_final_value: float
    monthly_depreciation: float
    monthly_maintenance: float
    loan_monthly_payment: float
    loan_total_interest: float
    total_monthly_cost: float
    year_values: List[float]
    warning: Optional[str] = None
    price_stddev: Optional[List[float]] = None
    adjusted_number_of_years: Optional[int] = None


class BreakEvenRequest(BaseModel):
    estimate: EstimateRequest
    rent_monthly_cost: float
    years: int = 5


class BreakEvenResponse(BaseModel):
    months_to_break_even: Optional[int]
    buy_monthly_series: List[float]
    rent_monthly_series: List[float]
    message: Optional[str]

# New models for break even analysis
class BreakEvenAnalysisRequest(BaseModel):
    brand: str
    model: str
    details: Optional[str] = ""
    zip_code: Optional[str] = "10139-torino"
    monthly_maintenance: float = 100.0
    rent_monthly_cost: float = 500.0
    max_years: int = 10
    shift_types: Optional[List[str]] = []

class DataPoint(BaseModel):
    years_owned: int
    overall_cost: float
    monthly_cost: float

class PurchaseYearSeries(BaseModel):
    purchase_year: int
    data_points: List[DataPoint]

class BreakEvenAnalysisResponse(BaseModel):
    rental_series: List[DataPoint]
    purchase_series: List[PurchaseYearSeries]
