import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Import for error messages
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

DEFAULT_DECREASE_RATES = [25, 19, 16, 12, 8, 4]
DEFAULT_MONTHLY_MAINTENANCE = 100
DEFAULT_NUMBER_OF_YEARS = 10


class CarValueCalculator:
    def __init__(self, initial_value: float, decrease_rates: list[float], number_of_years: int,
                 monthly_maintenance_cost: float, purchase_year: int):
        self.initial_value = initial_value
        self.decrease_rates = decrease_rates
        self.number_of_years = number_of_years
        self.monthly_maintenance_cost = monthly_maintenance_cost
        self.purchase_year = purchase_year
        self.car_value_over_time = []

    def calculate_depreciation(self) -> None:
        interpolated_rates = np.interp(
            np.arange(self.number_of_years),
            np.arange(len(self.decrease_rates)),
            self.decrease_rates,
            left=self.decrease_rates[0],
            right=self.decrease_rates[-1]
        )

        car_value = [self.initial_value]
        for i in range(self.number_of_years):
            monthly_decrease_rate = ((1 + interpolated_rates[i] / 100) ** (1 / 12) - 1) * 100
            for _ in range(12):
                monthly_depreciation = car_value[-1] * (monthly_decrease_rate / 100)
                new_value = car_value[-1] - monthly_depreciation - self.monthly_maintenance_cost
                car_value.append(max(new_value, 0))

        self.car_value_over_time = car_value

    def get_final_value(self) -> float:
        return self.car_value_over_time[-1]

    def get_purchase_price(self) -> float:
        return self.car_value_over_time[self.purchase_year * 12]


class LoanCalculator:
    def __init__(self, loan_value: float, bank_rate: float, number_of_years: int):
        self.loan_value = loan_value
        self.bank_rate = bank_rate
        self.number_of_years = number_of_years

    def calculate_loan_costs(self) -> tuple[float, float]:
        if self.loan_value == 0:
            return 0, 0

        taeg_decimal = self.bank_rate / 100
        monthly_taeg = taeg_decimal / 12
        payments_num = self.number_of_years * 12

        loan_monthly_cost = (self.loan_value * (1 + monthly_taeg) ** payments_num * monthly_taeg) / \
                            ((1 + monthly_taeg) ** payments_num - 1)
        total_interest = loan_monthly_cost * payments_num - self.loan_value
        return loan_monthly_cost, total_interest


class ChartPlotter:
    def __init__(self, parent, car_value_data: list[float]):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.car_value_data = car_value_data
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()

    def plot_car_value(self) -> None:
        self.ax.clear()
        self.ax.plot(range(len(self.car_value_data)), self.car_value_data)
        self.ax.set_xlabel("Months")
        self.ax.set_ylabel("Car Value")
        self.ax.set_title("Car Value Over Time")
        self.canvas.draw()


class CarValueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Value Calculator")
        self.initialize_gui()

    def initialize_gui(self) -> None:
        self.frame = ttk.Frame(self, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Added section for Initial Value and other fields
        ttk.Label(self.frame, text="Initial Value:").grid(row=0, column=0, sticky=tk.W)
        self.initial_value_entry = ttk.Entry(self.frame)
        self.initial_value_entry.grid(row=0, column=1)

        ttk.Label(self.frame, text="Decrease Rates (comma-separated):").grid(row=1, column=0, sticky=tk.W)
        self.decrease_rates_entry = ttk.Entry(self.frame)
        self.decrease_rates_entry.grid(row=1, column=1)
        self.decrease_rates_entry.insert(0, ', '.join(map(str, DEFAULT_DECREASE_RATES)))

        ttk.Label(self.frame, text="Number of Years:").grid(row=2, column=0, sticky=tk.W)
        self.years_entry = ttk.Entry(self.frame)
        self.years_entry.grid(row=2, column=1)
        self.years_entry.insert(0, str(DEFAULT_NUMBER_OF_YEARS))

        ttk.Label(self.frame, text="Year of Purchase:").grid(row=3, column=0, sticky=tk.W)
        self.purchase_year_combobox = ttk.Combobox(self.frame, values=list(range(0, 11)))
        self.purchase_year_combobox.grid(row=3, column=1)
        self.purchase_year_combobox.set(0)

        ttk.Label(self.frame, text="Monthly Maintenance Cost:").grid(row=4, column=0, sticky=tk.W)
        self.maintenance_cost_entry = ttk.Entry(self.frame)
        self.maintenance_cost_entry.grid(row=4, column=1)
        self.maintenance_cost_entry.insert(0, str(DEFAULT_MONTHLY_MAINTENANCE))

        self.create_loan_section()

        self.calculate_button = ttk.Button(self.frame, text="Calculate", command=self.calculate)
        self.calculate_button.grid(row=5, column=0, columnspan=2)

        self.chart = None
        self.final_value_label = ttk.Label(self, text="")
        self.final_value_label.grid(row=2, column=0, sticky=tk.W)

        self.monthly_cost_label = ttk.Label(self, text="")
        self.monthly_cost_label.grid(row=3, column=0, sticky=tk.W)

        self.interpolated_rates_label = ttk.Label(self, text="")
        self.interpolated_rates_label.grid(row=4, column=0, sticky=tk.W)

    def create_loan_section(self) -> None:
        self.loan_frame = ttk.LabelFrame(self, text="Loan Details", padding="10")
        self.loan_frame.grid(row=6, column=0, sticky=(tk.W, tk.E))

        ttk.Label(self.loan_frame, text="Loan Value:").grid(row=0, column=0, sticky=tk.W)
        self.loan_value_entry = ttk.Entry(self.loan_frame)
        self.loan_value_entry.grid(row=0, column=1)

        ttk.Label(self.loan_frame, text="Bank Rate (%):").grid(row=1, column=0, sticky=tk.W)
        self.bank_rate_entry = ttk.Entry(self.loan_frame)
        self.bank_rate_entry.grid(row=1, column=1)

    def validate_input(self, entry: ttk.Entry, default_value: float = 0.0) -> float:
        """Validates and retrieves float value from entry or returns a default value."""
        try:
            return float(entry.get())
        except ValueError:
            return default_value

    def calculate(self) -> None:
        initial_value = self.validate_input(self.initial_value_entry, default_value=0)
        provided_rates = [float(rate) for rate in self.decrease_rates_entry.get().split(",")]
        number_of_years = int(self.years_entry.get() or DEFAULT_NUMBER_OF_YEARS)
        purchase_year = int(self.purchase_year_combobox.get())
        maintenance_cost = self.validate_input(self.maintenance_cost_entry, default_value=DEFAULT_MONTHLY_MAINTENANCE)

        if initial_value <= 0:
            messagebox.showerror("Input Error", "Please enter a valid initial value for the car.")
            return

        car_calculator = CarValueCalculator(initial_value, provided_rates, number_of_years, maintenance_cost,
                                            purchase_year)
        car_calculator.calculate_depreciation()

        final_value = car_calculator.get_final_value()
        purchase_price = car_calculator.get_purchase_price()

        loan_value = self.validate_input(self.loan_value_entry, default_value=0)
        bank_rate = self.validate_input(self.bank_rate_entry, default_value=0)

        loan_calculator = LoanCalculator(loan_value, bank_rate, number_of_years)
        loan_monthly_cost, total_interest = loan_calculator.calculate_loan_costs()

        monthly_cost = (purchase_price - final_value) / (number_of_years * 12) + maintenance_cost
        total_monthly_cost_with_loan = monthly_cost + loan_monthly_cost

        self.final_value_label.config(
            text=f"Estimated Final Value: € {final_value:.2f}\nPurchase Price: € {purchase_price:.2f}\nTotal loan costs: € {total_interest:.2f}")
        self.monthly_cost_label.config(
            text=f"Monthly Cost: € {monthly_cost:.2f} + € {loan_monthly_cost:.2f} (loan)")
        self.interpolated_rates_label.config(
            text=f"Total Monthly Cost: € {total_monthly_cost_with_loan:.2f}")

        if self.chart:
            self.chart.canvas_widget.destroy()
        self.chart = ChartPlotter(self, car_calculator.car_value_over_time)
        self.chart.plot_car_value()
