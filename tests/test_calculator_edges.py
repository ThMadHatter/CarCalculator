import pytest
from src.calculator import LoanCalculator, CarValueCalculator
import math

def test_loan_calculator_zero_loan_or_years():
    # no loan value => zero monthly
    ln = LoanCalculator(0.0, 5.0, 5)
    monthly, total_interest = ln.calculate_loan_costs()
    assert monthly == 0.0 and total_interest == 0.0

    # zero years -> should return zeros
    ln2 = LoanCalculator(10000.0, 5.0, 0)
    monthly2, total_interest2 = ln2.calculate_loan_costs()
    assert monthly2 == 0.0 and total_interest2 == 0.0

def test_loan_calculator_zero_rate():
    ln = LoanCalculator(12000.0, 0.0, 2)
    monthly, total_interest = ln.calculate_loan_costs()
    assert pytest.approx(monthly, rel=1e-9) == 12000.0 / 24.0
    assert total_interest == 0.0

def test_loan_calculator_typical_case():
    ln = LoanCalculator(10000.0, 6.0, 3)
    monthly, interest = ln.calculate_loan_costs()
    assert monthly > 0 and interest >= 0

def test_car_value_calculator_invalid_inputs():
    # empty list -> ValueError
    with pytest.raises(ValueError):
        CarValueCalculator([], 3, 100.0, 0)

    # negative purchase_year_index -> ValueError
    with pytest.raises(ValueError):
        CarValueCalculator([30000.0, 25000.0, 20000.0], 2, 100.0, -1)

    # insufficient years to compute depr -> should raise ValueError
    # here purchase_year_index + number_of_years >= len(year_values)
    with pytest.raises(ValueError):
        CarValueCalculator([30000.0, 28000.0], 2, 100.0, 0)

def test_car_value_calculator_monthly_depr_and_total_cost():
    series = [30000.0, 28000.0, 26000.0, 24000.0, 22000.0]
    # purchase_index 1 (start=28000), number_of_years 2 -> end index 3 => end value 24000 -> total depr 4000 -> monthly 4000/(24)=166.66...
    calc = CarValueCalculator(series, number_of_years=2, monthly_maintenance=50.0, purchase_year_index=1)
    monthly_depr = calc.monthly_depreciation()
    assert pytest.approx(monthly_depr, rel=1e-6) == (28000 - 24000) / (2 * 12.0)
    total = calc.monthly_total_cost(loan_monthly=100.0)
    assert pytest.approx(total, rel=1e-6) == monthly_depr + 50.0 + 100.0
