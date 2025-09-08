import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import statistics
import yaml
from difflib import SequenceMatcher

CURRENT_YEAR = 2024
DEFAULT_MONTHLY_MAINTENANCE = 100
DEFAULT_NUMBER_OF_YEARS = 10
DEFAULT_PURCHASE_YEAR = 3


# AutoScout24 scraping functions
def fetch_dropdown_options(url: str, selected_values: Dict[str, str] = None) -> Dict[str, List[str]]:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    dropdowns = {}
    for dropdown in soup.find_all('select'):
        dropdown_name = dropdown.get('name', 'Unnamed Dropdown')
        options = [option.text.strip() for option in dropdown.find_all('option') if option.text.strip()]
        dropdowns[dropdown_name] = options

    if selected_values:
        make = selected_values.get("make", "").lower()
        if make:
            dropdowns['model'] = fetch_car_models(brand_name=make, url=url)

    return dropdowns


def fetch_car_models(brand_name: str, url: str) -> List[str]:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    lookup = {}
    for select in soup.find_all('select'):
        dropdown_name = select.get('name', 'Unnamed Dropdown')
        if dropdown_name == 'make':
            lookup = {option.text.strip().lower(): option.get('value') for option in select.find_all('option') if
                      option.text.strip()}

    car_id = lookup.get(brand_name)
    if car_id:
        response_yaml = yaml.safe_load(
            requests.get(f"https://www.autoscout24.it/as24-home/api/taxonomy/cars/makes/{car_id}/models").content)
        car_names = [car['label']['it_IT'].lower().replace(" ", "-") for car in
                     response_yaml['models']['modelLine']['values'] if car['label']['it_IT']]
        car_names = car_names + [car['name'].lower().replace(" ", "-") for car in
                                 response_yaml['models']['model']['values']]
        return car_names
    return []


def construct_base_url(base_url: str, selected_values: Dict[str, str]) -> str:
    """Constructs the base URL path based on make, model, and details."""
    make = selected_values.get("make", "").lower()
    model = selected_values.get("model", "").lower()
    details = selected_values.get("details", "").lower().replace(" ", "-")

    url_parts = [make, model, f"ve_{details}"]
    return f"{base_url}lst/" + "/".join(filter(None, url_parts))


def construct_year_filter(selected_values: Dict[str, str]) -> str:
    """Adds the year filter to the URL if available."""
    year = selected_values.get("firstRegistration", "")
    return f"&fregfrom={year}&fregto={year}&" if year else ""


def construct_zip_filter(selected_values: Dict[str, str]) -> str:
    """Adds the zip filter to the URL."""
    zip_code = selected_values.get("zip", "").lower()
    return f"&zip={zip_code}&zipr=200" if zip_code else ""


def construct_shift_filter(selected_values: Dict[str, str]) -> str:
    """Adds the zip filter to the URL."""
    shift_types = selected_values.get("shift_type", [])
    return f"&gear={'%2C'.join(shift_types)}" if shift_types else ""


def define_car_cost(costs: List[str], kms: List[str] = [], target_yarly_km: int = 0, years: int = 0) -> int:
    # Calculate the cost per km
    if costs:
        if kms and any(int(j) > target_yarly_km for j in kms):
            costs = [int(i) for i in costs]
            kms = [int(i) for i in kms]
            km_costs = [i / j for i, j in zip(costs, kms) if j > target_yarly_km]
            mean_cost = statistics.mean([int(i) for i in costs])
            mean_cost_per_km = statistics.mean(km_costs)
            print(
                f"Car costs: {costs}, resulting mean: {mean_cost}. km costs: {km_costs}, resulting mean: {mean_cost_per_km}, estimaded cost per km: {mean_cost_per_km * target_yarly_km * years}.")
            return mean_cost_per_km * target_yarly_km * years
        else:
            print("No kms found!")
            mean_cost = statistics.mean([int(i) for i in costs])
            print(f"Car costs: {costs}, resulting mean: {mean_cost}.")
            return mean_cost
    else:
        print("No costs found")
        return 0


def fetch_car_costs(base_url: str, selected_values: Dict[str, str]) -> int:
    """Fetches car cost data from the constructed URL."""
    url = construct_base_url(base_url, selected_values)
    url += "?&custtype=D&cy=I&damaged_listing=exclude&desc=0&"
    url += construct_year_filter(selected_values)
    url += construct_shift_filter(selected_values)
    url += "&lat=45.07086&lon=7.643&powertype=kw&sort=standard"
    url += construct_zip_filter(selected_values)

    print(f"Fetching car costs from: {url} ...")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract car costs
    costs = [
        "".join(
            [ele for ele in list(filter(lambda x: x.startswith("€"), [b.strip("-") for b in a.text.split(",")]))[-1] if
             ele.isdigit()])
        for a in soup.find_all("div", "PriceAndSeals_wrapper__BMNaJ")
    ]

    kms = []
    for car_details_div in soup.find_all("div", "VehicleDetailTable_container__XhfV1"):
        km_value = car_details_div.find_all(class_="VehicleDetailTable_item__4n35N")[0]
        km_value = "".join(char if char.isdigit() else "" for char in km_value.text)
        kms.append(km_value)

    return define_car_cost(costs)


# Car depreciation and loan calculators
class CarValueCalculator:
    def __init__(self, car_value_per_year: list[int], number_of_years: int, monthly_maintenance_cost: float,
                 purchase_year: int):
        self.car_value_per_year = car_value_per_year
        self.number_of_years = number_of_years
        self.monthly_maintenance_cost = monthly_maintenance_cost
        self.purchase_year = purchase_year - 1
        self.final_value = car_value_per_year[purchase_year + number_of_years]

    def calculate_monthly_expenses(self, loan_monthly_costs: float = 0) -> float:
        total_car_depreciation = self.car_value_per_year[self.purchase_year] - self.car_value_per_year[
            self.number_of_years + self.purchase_year]

        print(
            f"Total car depreciation: {total_car_depreciation} --- Monthly depreciation: {total_car_depreciation / (self.number_of_years * 12)}")
        return total_car_depreciation / (self.number_of_years * 12) + self.monthly_maintenance_cost + loan_monthly_costs


from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk


class ChartPlotter:
    def __init__(self, parent, car_value_data: List[float]):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.car_value_data = car_value_data

        # Create a canvas to hold the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=7, column=0, columnspan=2)

        # Create a frame for the toolbar
        self.toolbar_frame = ttk.Frame(parent)
        self.toolbar_frame.grid(row=8, column=0, columnspan=2)

        # Create an interactive toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def plot_car_value(self, purchase_year=3) -> None:
        """Plot the car value data on the graph."""
        self.ax.clear()  # Clear any existing plot
        self.ax.plot(CURRENT_YEAR - np.array(range(len(self.car_value_data))), self.car_value_data, '.-b')
        # plot a dot in the year of purchase
        self.ax.plot(CURRENT_YEAR - purchase_year + 1, self.car_value_data[purchase_year - 1], 'ro')

        # add callout with price value for each year
        for year, value in enumerate(self.car_value_data):
            self.ax.text(CURRENT_YEAR - year, value, f"{value:.2f}")

        self.ax.set_xlabel("Years")
        self.ax.set_ylabel("Car Value")
        self.ax.set_title("Car Value Over Time")
        self.ax.invert_xaxis()
        self.canvas.draw()  # Redraw the canvas with the updated plot


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


# Main application class
class CarValueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Value Calculator with AutoScout24")
        self.initialize_gui()

    def initialize_gui(self) -> None:
        self.frame = ttk.Frame(self, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Dropdowns for make and model
        ttk.Label(self.frame, text="Car Brand:").grid(row=0, column=0, sticky=tk.W)
        self.car_brand_combobox = ttk.Combobox(self.frame, values=[])
        self.car_brand_combobox.grid(row=0, column=1)
        self.car_brand_combobox.bind("<KeyRelease>", self.search_brands)

        ttk.Label(self.frame, text="Car Model:").grid(row=1, column=0, sticky=tk.W)
        self.car_model_combobox = ttk.Combobox(self.frame, values=[])
        self.car_model_combobox.grid(row=1, column=1)
        self.car_model_combobox.bind("<KeyRelease>", self.search_models)

        self.car_brand_combobox.bind("<<ComboboxSelected>>", self.update_models)

        self.fetch_initial_data()

        # Number of years
        ttk.Label(self.frame, text="Number of Years:").grid(row=2, column=0, sticky=tk.W)
        self.years_entry = ttk.Entry(self.frame)
        self.years_entry.grid(row=2, column=1)
        self.years_entry.insert(0, str(DEFAULT_NUMBER_OF_YEARS))

        # New input for car details
        ttk.Label(self.frame, text="Details:").grid(row=3, column=0, sticky=tk.W)
        self.details_entry = ttk.Entry(self.frame)
        self.details_entry.grid(row=3, column=1)

        # Input for monthly maintenance cost
        ttk.Label(self.frame, text="Monthly Maintenance Cost:").grid(row=4, column=0, sticky=tk.W)
        self.maintenance_entry = ttk.Entry(self.frame)
        self.maintenance_entry.grid(row=4, column=1)
        self.maintenance_entry.insert(0, str(DEFAULT_MONTHLY_MAINTENANCE))

        # Input for purchase year
        ttk.Label(self.frame, text="Purchase Year:").grid(row=5, column=0, sticky=tk.W)
        self.purchase_year_entry = ttk.Entry(self.frame)
        self.purchase_year_entry.grid(row=5, column=1)
        self.purchase_year_entry.insert(0, str(DEFAULT_PURCHASE_YEAR))

        # Checkboxes for shift types (multiple selections allowed)
        ttk.Label(self.frame, text="Shift Types:").grid(row=6, column=0, sticky=tk.W)

        # Boolean variables to store checkbox states
        self.manual_var = tk.BooleanVar()
        self.automatic_var = tk.BooleanVar()
        self.semiautomatic_var = tk.BooleanVar()

        self.manual_checkbox = ttk.Checkbutton(self.frame, text="Manual", variable=self.manual_var)
        self.manual_checkbox.grid(row=6, column=1, sticky=tk.W)

        self.automatic_checkbox = ttk.Checkbutton(self.frame, text="Automatic", variable=self.automatic_var)
        self.automatic_checkbox.grid(row=7, column=1, sticky=tk.W)

        self.semiautomatic_checkbox = ttk.Checkbutton(self.frame, text="Semiautomatic", variable=self.semiautomatic_var)
        self.semiautomatic_checkbox.grid(row=8, column=1, sticky=tk.W)

        self.create_loan_section()

        # Calculate button
        self.calculate_button = ttk.Button(self.frame, text="Calculate", command=self.calculate)
        self.calculate_button.grid(row=9, column=0, columnspan=2)

        self.chart = None

        # Labels for displaying final output
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

        ttk.Label(self.loan_frame, text="Loan years:").grid(row=2, column=0, sticky=tk.W)
        self.loan_years = ttk.Entry(self.loan_frame)
        self.loan_years.grid(row=2, column=1)

    def fetch_initial_data(self) -> None:
        url = "https://www.autoscout24.it/"
        dropdown_options = fetch_dropdown_options(url)
        self.car_brand_combobox['values'] = dropdown_options.get("make", [])

    def update_models(self, event) -> None:
        selected_brand = self.car_brand_combobox.get().lower()
        url = "https://www.autoscout24.it/"
        models = fetch_car_models(selected_brand, url)
        self.car_model_combobox['values'] = models

    def sort_brands(self) -> None:
        """Sort the car brand options alphabetically."""
        self.car_brand_combobox['values'] = sorted(self.car_brand_combobox['values'])

    def sort_models(self) -> None:
        """Sort the car model options alphabetically."""
        self.car_model_combobox['values'] = sorted(self.car_model_combobox['values'])

    def search_brands(self, event) -> None:
        """Search and filter the car brands based on user input."""
        typed_text = self.car_brand_combobox.get().lower()
        if typed_text == '':
            data = sorted(self.car_brand_combobox['values'])
        else:
            data = sorted(self.car_brand_combobox['values'], key=lambda x: SequenceMatcher(None, typed_text, x).ratio(),
                          reverse=True)
        self.car_brand_combobox['values'] = data
        if data:
            self.car_model_combobox.event_generate('<Down>')

    def search_models(self, event) -> None:
        """Search and filter the car models based on user input."""
        typed_text = self.car_model_combobox.get().lower()
        if typed_text == '':
            data = sorted(self.car_model_combobox['values'])
        else:
            # sort data by best match
            data = sorted(self.car_model_combobox['values'], key=lambda x: SequenceMatcher(None, typed_text, x).ratio(),
                          reverse=True)
        self.car_model_combobox['values'] = data
        if data:
            self.car_model_combobox.event_generate('<Down>')
            self.car_model_combobox.focus_set()

    def validate_input(self, entry: ttk.Entry, default_value: float = 0.0) -> float:
        """Validates and retrieves float value from entry or returns a default value."""
        try:
            return float(entry.get())
        except ValueError:
            return default_value

    def calculate(self) -> None:

        shift_types_selected = []
        if self.manual_var.get():
            shift_types_selected.append("M")
        if self.automatic_var.get():
            shift_types_selected.append("A")
        if self.semiautomatic_var.get():
            shift_types_selected.append("S")

        selected_values = {
            "make": self.car_brand_combobox.get(),
            "model": self.car_model_combobox.get(),
            "zip": "10139-torino",
            "firstRegistration": CURRENT_YEAR,
            "details": self.details_entry.get(),
            "shift_type": shift_types_selected
        }
        url = "https://www.autoscout24.it/"
        car_price_per_year = []

        number_of_parsed_years = int(self.years_entry.get()) + int(self.purchase_year_entry.get())
        for i, year in enumerate(reversed(range(CURRENT_YEAR - number_of_parsed_years, CURRENT_YEAR + 1))):
            selected_values["firstRegistration"] = year
            car_price_per_year.append(fetch_car_costs(url, selected_values))

        # ensure that all elements of car_price_per_year are >0 if not the 0 will be replaced with i-1 element
        for i, price in enumerate(car_price_per_year):
            if price == 0:
                car_price_per_year[i] = car_price_per_year[i - 1]

        monthly_maintenance = float(self.maintenance_entry.get())
        purchase_year = int(self.purchase_year_entry.get())

        calculator = CarValueCalculator(car_price_per_year, int(self.years_entry.get()), monthly_maintenance,
                                        purchase_year)

        loan_calculator = LoanCalculator(self.validate_input(self.loan_value_entry),
                                         self.validate_input(self.bank_rate_entry),
                                         self.validate_input(self.loan_years))
        loan_monthly_cost, total_interest = loan_calculator.calculate_loan_costs()

        purchase_price = calculator.car_value_per_year[purchase_year - 1]
        final_value = calculator.final_value
        monthly_cost = calculator.calculate_monthly_expenses()
        loan_monthly_cost_avg = total_interest / (12 * int(self.years_entry.get()))
        total_monthly_cost_with_loan = monthly_cost + loan_monthly_cost_avg

        self.final_value_label.config(
            text=f"Estimated Final Value: € {final_value:.2f}\nPurchase Price: € {purchase_price:.2f}\nTotal loan costs: € {total_interest:.2f}\nLoan monthly cost: € {loan_monthly_cost:.2f}")
        self.monthly_cost_label.config(
            text=f"Monthly Cost: € {monthly_cost:.2f} + € {loan_monthly_cost_avg:.2f} (loan averaged expenses over {int(self.years_entry.get())} years)")
        self.interpolated_rates_label.config(
            text=f"Total Monthly Cost: € {total_monthly_cost_with_loan:.2f}")

        self.show_results(car_price_per_year)

    def show_results(self, car_value_over_time: list[int]) -> None:
        if self.chart:
            self.chart.canvas_widget.destroy()
        self.chart = ChartPlotter(self, car_value_over_time)
        self.chart.plot_car_value()


# Running the application
if __name__ == '__main__':
    app = CarValueApp()
    app.focus_set()
    app.mainloop()
