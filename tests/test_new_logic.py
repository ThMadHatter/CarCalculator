import pytest
from src.calculator import LoanCalculator, CarValueCalculator

def test_zero_value_test():
    """
    The "Zero-Value" Test: Set Final Value to 0.
    Does Monthly Depreciation * Ot exactly equal Purchase Price?
    """
    P = 30000
    Vf = 0
    Ot_years = 5
    Ot_months = Ot_years * 12
    # year_values index matches (purchase_year_index + year_offset)
    # We set purchase_year_index = 0 for simplicity in this test
    year_values = [P, 25000, 20000, 15000, 10000, Vf]

    calc = CarValueCalculator(
        year_values=year_values,
        number_of_years=Ot_years,
        monthly_maintenance=100.0,
        purchase_year_index=0,
        loan_value=0.0
    )

    D = calc.monthly_depreciation()
    assert pytest.approx(D * Ot_months) == P

def test_cash_buyer_test():
    """
    The "Cash Buyer" Test: Set Loan Amount to 0.
    Does the 'During Loan' cost correctly match 'After Loan' cost?
    """
    P = 30000
    Vf = 15000
    Ot_years = 5
    M = 200.0
    year_values = [P, 27000, 24000, 21000, 18000, Vf]

    calc = CarValueCalculator(
        year_values=year_values,
        number_of_years=Ot_years,
        monthly_maintenance=M,
        purchase_year_index=0,
        loan_value=0.0
    )

    # Even if we pass some loan parameters, if loan_value is 0, PMT is 0
    loan_calc = LoanCalculator(loan_value=0.0, bank_rate_percent=5.0, number_of_years=3)
    loan_monthly, _ = loan_calc.calculate_loan_costs()

    cost_during, cost_after, _ = calc.calculate_period_costs(loan_monthly, loan_years=3)

    assert cost_during == M
    assert cost_after == M

def test_duration_match_test():
    """
    The "Duration Match" Test: Set Loan Term equal to Ownership Term.
    Does the Average Monthly Cost correctly reflect all expenses minus resale?
    """
    P = 20000.0
    L = 15000.0
    I = 5.0
    Lt_years = 3
    Ot_years = 3
    Vf = 10000.0
    M = 100.0

    year_values = [P, 16000, 13000, Vf]

    loan_calc = LoanCalculator(loan_value=L, bank_rate_percent=I, number_of_years=Lt_years)
    loan_monthly, _ = loan_calc.calculate_loan_costs()

    calc = CarValueCalculator(
        year_values=year_values,
        number_of_years=Ot_years,
        monthly_maintenance=M,
        purchase_year_index=0,
        loan_value=L
    )

    # We will need to update monthly_total_cost to take loan_years or ensure it's handled
    # For now, let's assume we update the signature as planned
    try:
        tco_monthly = calc.monthly_total_cost(loan_monthly=loan_monthly, loan_years=Lt_years)
    except TypeError:
        # Fallback for current signature to see it failing or check current behavior
        tco_monthly = calc.monthly_total_cost(loan_monthly=loan_monthly)

    Lt_months = Lt_years * 12
    Ot_months = Ot_years * 12
    # Expected TCO per Month: ((PMT * Lt) + (P - L) + (M * Ot) - Vf) / Ot
    expected_tco = ((loan_monthly * Lt_months) + (P - L) + (M * Ot_months) - Vf) / Ot_months

    assert pytest.approx(tco_monthly) == expected_tco

def test_maintenance_floor_test():
    """
    The "Maintenance Floor" Test: Ensure that if M = 500,
    the 'After Loan' result cannot be lower than 500.
    """
    M = 500.0
    P = 30000.0
    Vf = 10000.0
    Ot_years = 5
    year_values = [P, 26000, 22000, 18000, 14000, Vf]

    calc = CarValueCalculator(
        year_values=year_values,
        number_of_years=Ot_years,
        monthly_maintenance=M,
        purchase_year_index=0,
        loan_value=10000.0
    )

    _, cost_after, _ = calc.calculate_period_costs(loan_monthly=300.0, loan_years=3)

    assert cost_after is not None
    assert cost_after >= M
