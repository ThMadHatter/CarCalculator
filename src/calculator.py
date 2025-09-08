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
    def __init__(self, year_values: List[float], number_of_years: int, monthly_maintenance: float, purchase_year_index: int):
        if not year_values:
            raise ValueError("year_values must be non-empty")
        self.year_values = [float(x) for x in year_values]
        self.number_of_years = int(number_of_years)
        self.monthly_maintenance = float(monthly_maintenance)
        self.purchase_year_index = int(purchase_year_index)  # 1-based in your GUI previously, but here we accept 0-based
        # ensure indices within range
        if self.purchase_year_index < 0:
            raise ValueError("purchase_year_index must be >= 0")
        if self.purchase_year_index + self.number_of_years >= len(self.year_values):
            # if not enough years provided, clamp
            raise ValueError("not enough historical values to compute requested depreciation window")

    def monthly_depreciation(self) -> float:
        """Return monthly depreciation over the planned ownership horizon."""
        start_value = self.year_values[self.purchase_year_index]
        end_index = self.purchase_year_index + self.number_of_years
        end_value = self.year_values[end_index]
        total_depr = start_value - end_value
        return total_depr / (self.number_of_years * 12.0)

    def monthly_total_cost(self, loan_monthly: float = 0.0) -> float:
        """Depreciation + maintenance + loan monthly payment"""
        return self.monthly_depreciation() + self.monthly_maintenance + loan_monthly
