from main import fill_missing_prices
from src.calculator import CarValueCalculator

def test_fill_missing_prices_interpolation():
    prices = [10000.0, 0.0, 8000.0]
    filled, simulated = fill_missing_prices(prices, extend=True)
    assert filled == [10000.0, 9000.0, 8000.0]
    assert simulated == [False, True, False]

def test_calculate_period_costs():
    year_values = [30000.0, 25000.0, 20000.0]
    calc = CarValueCalculator(year_values, number_of_years=2, monthly_maintenance=100.0, purchase_year_index=0, loan_value=10000.0)
    cost_during, cost_after, inflation_total = calc.calculate_period_costs(loan_monthly=200.0, loan_years=1)
    assert cost_during == 300.0
    assert cost_after == 100.0
