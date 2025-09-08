import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk
from urllib.parse import quote
import statistics
import yaml


class AutoScoutScraper:
    def __init__(self):
        self.make_selection = None

    def fetch_dropdown_options(self, url: str, selected_values: Optional[Dict[str, str]] = None) -> Dict[
        str, List[str]]:
        """
        Fetches dropdown options from the specified AutoScout24 URL based on selected values.

        Args:
            url (str): The URL of the AutoScout24 page to scrape.
            selected_values (Optional[Dict[str, str]]): The currently selected values from the dropdowns.

        Returns:
            Dict[str, List[str]]: A dictionary containing dropdown names and their options.
        """
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        dropdowns = self._extract_dropdowns(soup)

        if selected_values:
            make = selected_values.get("make", "").lower()
            if make != self.make_selection:
                dropdowns['model'] = self.fetch_car_models(brand_name=make, url=url)
                self.make_selection = make

        return dropdowns

    @staticmethod
    def _extract_dropdowns(soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extracts dropdown options from the HTML soup."""
        dropdowns = {}
        for dropdown in soup.find_all('select'):
            dropdown_name = dropdown.get('name', 'Unnamed Dropdown')
            options = [option.text.strip() for option in dropdown.find_all('option') if option.text.strip()]
            dropdowns[dropdown_name] = options
        return dropdowns

    def fetch_car_models(self, brand_name: str, url: str) -> List[str]:
        """
        Fetches the car models for a given brand from AutoScout24.

        Args:
            brand_name (str): The name of the car brand.
            url (str): The base URL to use for the request.

        Returns:
            List[str]: A list of car models for the specified brand.
        """
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        car_id = self._get_car_id(soup, brand_name)
        response_yaml = yaml.safe_load(
            requests.get(f"https://www.autoscout24.it/as24-home/api/taxonomy/cars/makes/{car_id}/models").content
        )

        return [car['name'].lower().replace(" ", "-") for car in response_yaml['models']['model']['values']]

    @staticmethod
    def _get_car_id(soup: BeautifulSoup, brand_name: str) -> str:
        """Extracts the car ID for a given brand from the dropdown options."""
        lookup = {}
        for select in soup.find_all('select'):
            dropdown_name = select.get('name', 'Unnamed Dropdown')
            if dropdown_name == 'make':
                lookup = dict(zip(
                    [option.text.strip().lower() for option in select.find_all('option') if option.text.strip()],
                    [option.get('value') for option in select.find_all('option') if option.text.strip()]
                ))

        return lookup.get(brand_name)

    def fetch_car_costs(self, url: str, selected_values: Optional[Dict[str, str]] = None) -> int:
        """
        Fetches and calculates the average car costs based on selected values.

        Args:
            url (str): The base URL for fetching car costs.
            selected_values (Optional[Dict[str, str]]): Selected values from the dropdowns.

        Returns:
            int: The average car cost.
        """
        url = self._build_url(url, selected_values)

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        costs = ["".join([ele for ele in a.text if ele.isdigit()]) for a in
                 soup.find_all("div", "PriceAndSeals_wrapper__BMNaJ")]
        avg_cost = statistics.mean([int(i) for i in costs]) if costs else 0

        if avg_cost:
            print(f"Average cost: {avg_cost}")
        else:
            print("No costs found")

        return avg_cost

    @staticmethod
    def _build_url(base_url: str, selected_values: Optional[Dict[str, str]]) -> str:
        """Constructs the URL based on the selected dropdown values."""
        if selected_values:
            make = selected_values.get("make", "").lower()
            model = selected_values.get("model", "").lower()
            zip_code = selected_values.get("zip", "").lower()
            year = selected_values.get("firstRegistration", "").lower()

            url_parts = [f"lst", make, model, zip_code]
            url_path = "/".join(filter(None, url_parts))

            year_filter = f"&fregfrom={year}&fregto={year}" if year else ""
            return f"{base_url}{url_path}?sort=standard&amp{year_filter}"
        return base_url


class AutoScoutGUI:
    def __init__(self, scraper: AutoScoutScraper, url: str):
        self.scraper = scraper
        self.url = url
        self.selected_values = {}
        self.dropdown_widgets = {}

    def create_gui(self, dropdown_options: Dict[str, List[str]]) -> None:
        """Creates the main GUI for displaying dropdowns and a submit button."""
        root = tk.Tk()
        root.title("AutoScout24 Dropdowns")

        for dropdown_name, options in dropdown_options.items():
            label = tk.Label(root, text=dropdown_name)
            label.pack(pady=5)

            dropdown = ttk.Combobox(root, values=options)
            dropdown.pack(pady=5)
            self.dropdown_widgets[dropdown_name] = dropdown
            self.selected_values[dropdown_name] = dropdown

            dropdown.bind("<<ComboboxSelected>>", lambda e, name=dropdown_name: self.update_dropdowns(name))

        submit_button = tk.Button(root, text="Submit", command=self.submit_form)
        submit_button.pack(pady=20)

        root.mainloop()

    def update_dropdowns(self, dropdown_name: str) -> None:
        """Updates the dropdown options based on user selection."""
        self.selected_values[dropdown_name] = self.dropdown_widgets[dropdown_name].get()

        new_options = self.scraper.fetch_dropdown_options(self.url, self.selected_values)
        for name, widget in self.dropdown_widgets.items():
            if name in new_options:
                widget['values'] = new_options[name]

    def submit_form(self) -> None:
        """Handles form submission and fetches car costs based on selected values."""
        costs = self.scraper.fetch_car_costs(self.url,
                                             {name: widget.get() for name, widget in self.dropdown_widgets.items()})
        print(f"Calculated costs: {costs}")


if __name__ == '__main__':
    url = "https://www.autoscout24.it/"
    scraper = AutoScoutScraper()

    # Fetch initial dropdown options
    dropdown_options = scraper.fetch_dropdown_options(url, {})

    # Create and run the GUI
    gui = AutoScoutGUI(scraper, url)
    gui.create_gui(dropdown_options)
