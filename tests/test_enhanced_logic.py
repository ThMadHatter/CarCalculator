import pytest
from src.calculator import CarValueCalculator, LoanCalculator
from main import fill_missing_prices

def test_fill_missing_prices_interpolation():
    prices = [10000.0, 0.0, 8000.0]
    # Linear interpolation: (8000 - 10000) / 2 = -1000 per step
    # 10000 -> 9000 -> 8000
    filled = fill_missing_prices(prices, extend=True)
    assert filled == [10000.0, 9000.0, 8000.0]

def test_fill_missing_prices_extrapolation_start():
    prices = [0.0, 9000.0, 8000.0]
    # Slope: (8000 - 9000) / 1 = -1000
    # Before 9000: 9000 - (-1000) = 10000
    filled = fill_missing_prices(prices, extend=True)
    assert filled == [10000.0, 9000.0, 8000.0]

def test_fill_missing_prices_extrapolation_end():
    prices = [10000.0, 9000.0, 0.0]
    # Slope: (9000 - 10000) / 1 = -1000
    # After 9000: 9000 + (-1000) = 8000
    filled = fill_missing_prices(prices, extend=True)
    assert filled == [10000.0, 9000.0, 8000.0]

def test_fill_missing_prices_constant_extrapolation():
    prices = [0.0, 5000.0, 0.0]
    # Only one valid point -> constant extrapolation
    filled = fill_missing_prices(prices, extend=True)
    assert filled == [5000.0, 5000.0, 5000.0]

def test_car_value_calculator_inflation():
    year_values = [10000.0, 9000.0, 8000.0] # 2 years
    maint = 100.0
    inflation = 10.0 # 10%
    calc = CarValueCalculator(year_values, number_of_years=2, monthly_maintenance=maint, purchase_year_index=0, inflation_rate=inflation)

    # Year 0: 100 * 12 = 1200
    # Year 1: 1200 * 1.1 = 1320
    # Total: 1200 + 1320 = 2520
    assert calc.total_maintenance_cost(2) == 2520.0

    # Depreciation: (10000 - 8000) / 24 = 2000 / 24 = 83.333...
    # Avg monthly maint: 2520 / 24 = 105
    # Total: 83.333 + 105 = 188.333...
    assert calc.monthly_total_cost(years=2) == pytest.approx(188.333333333)

def test_car_value_calculator_with_loan():
    # Purchase Price: 20000, Resell Price: 12000, Loan: 10000, Years: 2
    # Depreciation should be (20000 - 10000 - 12000) / 24 = -2000 / 24 = -83.333
    # Maint: 100 * 12 * 2 = 2400 (inflation 0)
    # Avg Monthly cost = (-2000 + 2400) / 24 = 400 / 24 = 16.666
    # If loan monthly is 500, total should be 516.666
    year_values = [25000, 20000, 15000, 12000] # Purchase at index 1 (20000), sell after 2 years at index 3 (12000)
    calc = CarValueCalculator(year_values, number_of_years=2, monthly_maintenance=100.0, purchase_year_index=1, loan_value=10000.0)
    assert calc.monthly_depreciation(years=2) == pytest.approx(-83.333333333)
    assert calc.monthly_total_cost(loan_monthly=500.0, years=2) == pytest.approx(516.666666667)

def test_loan_calculator_zero_interest():
    loan_calc = LoanCalculator(loan_value=12000, bank_rate_percent=0, number_of_years=1)
    monthly, total_interest = loan_calc.calculate_loan_costs()
    assert monthly == 1000.0
    assert total_interest == 0.0

def test_loan_calculator_standard():
    loan_calc = LoanCalculator(loan_value=10000, bank_rate_percent=12, number_of_years=1)
    monthly, total_interest = loan_calc.calculate_loan_costs()
    # Monthly rate = 1%
    # PMT = 10000 * 0.01 / (1 - (1.01^-12)) = 888.48
    assert monthly == pytest.approx(888.48788678)
    assert total_interest == pytest.approx(888.48788678 * 12 - 10000)
