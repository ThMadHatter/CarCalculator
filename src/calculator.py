from typing import List
from math import isclose
from .models import EstimateRequest
import statistics


class LoanCalculator:
    """
    Amortizing loan monthly payment calculator (standard formula).
    bank_rate is percentage (e.g. 6.5 means 6.5% annual nominal rate).
    """
    def __init__(self, loan_value: float, bank_rate_percent: float, number_of_years: int):
        self.loan_value = float(loan_value)
        self.bank_rate_percent = float(bank_rate_percent)
        self.number_of_years = int(number_of_years)

    def calculate_loan_costs(self) -> tuple[float, float]:
        """
        :return: (monthly_payment, total_interest)
        For zero interest special case: monthly_payment = loan_value / months
        """
        if self.loan_value <= 0 or self.number_of_years <= 0:
            return 0.0, 0.0

        months = self.number_of_years * 12
        if isclose(self.bank_rate_percent, 0.0):
            monthly_payment = self.loan_value / months
            total_interest = 0.0
            return monthly_payment, total_interest

        annual_rate = self.bank_rate_percent / 100.0
        monthly_rate = annual_rate / 12.0
        # monthly payment formula (annuity)
        denom = (1 - (1 + monthly_rate) ** (-months))
        if denom == 0:
            monthly_payment = self.loan_value / months
        else:
            monthly_payment = (self.loan_value * monthly_rate) / denom
        total_interest = monthly_payment * months - self.loan_value
        return monthly_payment, total_interest


class CarValueCalculator:
    """
    Compute monthly depreciation and monthly total costs given a list of car prices over a set of years.

    The expected input is a list `year_values` where index 0 corresponds to the newest year (CURRENT_YEAR),
    index 1 to previous year, ... i.e. a descending timeline. This matches the behavior of your original GUI.
    """
    def __init__(self, year_values: List[float], number_of_years: int, monthly_maintenance: float, purchase_year_index: int, inflation_rate: float = 0.0, loan_value: float = 0.0):
        if not year_values:
            raise ValueError("year_values must be non-empty")
        self.year_values = [float(x) for x in year_values]
        self.number_of_years = int(number_of_years)
        self.monthly_maintenance = float(monthly_maintenance)
        self.purchase_year_index = int(purchase_year_index)
        self.inflation_rate = float(inflation_rate)
        self.loan_value = float(loan_value)

    def total_maintenance_cost(self, years: int) -> float:
        """Calculate cumulative maintenance cost with annual inflation."""
        total = 0.0
        annual_maintenance = self.monthly_maintenance * 12
        for i in range(years):
            total += annual_maintenance * ((1 + self.inflation_rate / 100.0) ** i)
        return total

    def monthly_depreciation(self, years: int = None) -> float:
        """
        Return monthly depreciation over the planned ownership horizon.
        If loan_value > 0, it is subtracted from the initial purchase price to avoid double counting
        capital repayment (as it is included in the loan monthly payment).
        """
        years = years or self.number_of_years
        start_value = self.year_values[self.purchase_year_index]
        end_index = self.purchase_year_index + years
        end_value = self.year_values[end_index]
        
        # Adjusted depreciation: (Purchase Price - loan_amount - Estimated Final Value)
        total_depr = start_value - self.loan_value - end_value

        if years <= 0:
            return 0.0

        return total_depr / (years * 12.0)

    def monthly_total_cost(self, loan_monthly: float = 0.0, years: int = None) -> float:
        """Average monthly cost over years: (Adjusted Depreciation + maintenance) / months + loan monthly payment"""
        years = years or self.number_of_years
        if years <= 0:
            return self.monthly_maintenance + loan_monthly

        total_depr = self.monthly_depreciation(years=years) * (years * 12.0)
        total_maint = self.total_maintenance_cost(years)
        return (total_depr + total_maint) / (years * 12.0) + loan_monthly
