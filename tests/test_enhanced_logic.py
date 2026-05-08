from main import fill_missing_prices
from src.calculator import CarValueCalculator

def test_fill_missing_prices_interpolation():
    prices = [10000.0, 0.0, 8000.0]
    filled, simulated = fill_missing_prices(prices, extend=True)
    assert filled == [10000.0, 9000.0, 8000.0]
    assert simulated == [False, True, False]

def test_fill_missing_prices_extrapolation_start():
    prices = [0.0, 9000.0, 8000.0]
    filled, simulated = fill_missing_prices(prices, extend=True)
    assert filled == [10000.0, 9000.0, 8000.0]
    assert simulated == [True, False, False]

def test_fill_missing_prices_extrapolation_end():
    prices = [10000.0, 9000.0, 0.0]
    filled, simulated = fill_missing_prices(prices, extend=True)
    assert filled == [10000.0, 9000.0, 8000.0]
    assert simulated == [False, False, True]

def test_calculate_period_costs():
    year_values = [30000.0, 25000.0, 20000.0]
    calc = CarValueCalculator(year_values, number_of_years=2, monthly_maintenance=100.0, purchase_year_index=0, loan_value=10000.0)
    # months = 24
    # avg maint = 100 (inflation=0)
    # During: PMT + M = 200 + 100 = 300
    # After: M = 100
    cost_during, cost_after, inflation_total = calc.calculate_period_costs(loan_monthly=200.0, loan_years=1)
    assert cost_during == 300.0
    assert cost_after == 100.0
    assert inflation_total == 0

def test_monthly_depreciation_adjusted():
    # Purchase 30k, Loan 20k, Final Value 5k, 5 years
    year_values = [30000.0, 25000.0, 20000.0, 15000.0, 10000.0, 5000.0]
    calc = CarValueCalculator(year_values, number_of_years=5, monthly_maintenance=0, purchase_year_index=0, loan_value=20000.0)

    # Depr = (30000 - 5000) / (5 * 12) = 25000 / 60 = 416.67
    depr = calc.monthly_depreciation()
    assert round(depr, 2) == 416.67

    # Without loan - same depr
    calc_no_loan = CarValueCalculator(year_values, number_of_years=5, monthly_maintenance=0, purchase_year_index=0, loan_value=0.0)
    # Depr = (30000 - 5000) / 60 = 25000 / 60 = 416.67
    depr_no_loan = calc_no_loan.monthly_depreciation()
    assert round(depr_no_loan, 2) == 416.67

def test_car_value_calculator_inflation():
    year_values = [20000.0, 20000.0, 20000.0]
    calc = CarValueCalculator(year_values, number_of_years=2, monthly_maintenance=100.0, purchase_year_index=0, inflation_rate=10.0)
    # year 1: 1200
    # year 2: 1200 * 1.1 = 1320
    # total = 2520
    # impact = 2520 - 2400 = 120

    _, _, impact = calc.calculate_period_costs(0, 0)
    assert impact == 120.0
