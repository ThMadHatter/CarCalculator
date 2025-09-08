import pytest
from src.calculator import LoanCalculator, CarValueCalculator

def test_loan_zero_rate():
    loan = LoanCalculator(12000, 0.0, 2)
    monthly, total_interest = loan.calculate_loan_costs()
    assert pytest.approx(monthly, rel=1e-6) == 12000 / 24
    assert total_interest == 0.0

def test_loan_with_rate():
    loan = LoanCalculator(10000, 6.0, 3)
    monthly, total_interest = loan.calculate_loan_costs()
    assert monthly > 0
    assert total_interest >= 0

def test_car_value_calculator_depreciation():
    # newest->older: [2025_value, 2024, 2023, ...]
    series = [30000.0, 28000.0, 25000.0, 22000.0, 20000.0, 18000.0]
    calc = CarValueCalculator(series, number_of_years=3, monthly_maintenance=100.0, purchase_year_index=1)
    # start value = series[1] = 28000; end index = 1+3 = 4 => end value 20000 => total depr = 8000 => monthly = 8000/(36) = 222.22...
    assert pytest.approx(calc.monthly_depreciation(), rel=1e-3) == 8000 / 36.0
    assert pytest.approx(calc.monthly_total_cost(loan_monthly=200.0), rel=1e-3) == (8000 / 36.0) + 100.0 + 200.0
