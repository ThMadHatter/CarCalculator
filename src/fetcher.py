"""
Fetcher: stable wrappers around the AutoScout24 scraping logic
- uses a retry session
- handles parsing errors
- returns normalized Python types
"""

from typing import Dict, List, Optional
import time
import re
from bs4 import BeautifulSoup
import yaml
import requests
from .utils import create_retry_session

DEFAULT_BASE_URL = "https://www.autoscout24.it/"

# instantiate a session for reuse
_SESSION = create_retry_session()


class FetchError(RuntimeError):
    """Raised when fetching/parsing fails in a recoverable manner."""


def _safe_get(url: str, timeout: float = 10.0) -> requests.Response:
    """Perform HTTP GET with configured session, raise FetchError on failure."""
    try:
        resp = _SESSION.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.RequestException as ex:
        raise FetchError(f"HTTP error for {url}: {ex}") from ex


class Fetcher:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip("/") + "/"

    def fetch_dropdown_options(self, url: Optional[str] = None, selected_values: Optional[Dict[str, str]] = None) -> Dict[str, List[str]]:
        """
        Fetch HTML and parse all <select> dropdowns found on the page.
        If selected_values contains 'make', attempt to fetch models for that brand (via API endpoint).
        """
        url = url or self.base_url
        resp = _safe_get(url)
        soup = BeautifulSoup(resp.content, "html.parser")
        dropdowns: Dict[str, List[str]] = {}
        for select in soup.find_all("select"):
            name = select.get("name") or "unnamed"
            opts = [opt.text.strip() for opt in select.find_all("option") if opt.text and opt.text.strip()]
            dropdowns[name] = opts

        if selected_values:
            make = (selected_values.get("make") or "").strip().lower()
            if make:
                try:
                    dropdowns["model"] = self.fetch_car_models(make)
                except FetchError:
                    # return whatever parsed so far
                    dropdowns["model"] = []

        # Remove 'Marca' from dropdowns
        if "Marca" in dropdowns.get("make"):
            dropdowns.get("make", []).remove("Marca")

        return dropdowns

    def fetch_car_models(self, brand_name: str) -> List[str]:
        """
        Query AutoScout taxonomy endpoint for models given a brand name string (case-insensitive).
        Returns a list of model slugs (lowercase, hyphenated).
        """
        # step 1: fetch home page to map brand names -> id values
        resp = _safe_get(self.base_url)
        soup = BeautifulSoup(resp.content, "html.parser")
        lookup: Dict[str, str] = {}
        for select in soup.find_all("select"):
            if select.get("name") == "make":
                for opt in select.find_all("option"):
                    text = (opt.text or "").strip().lower()
                    value = opt.get("value") or ""
                    if text:
                        lookup[text] = value

        brand_id = lookup.get(brand_name.lower())
        if not brand_id:
            # tolerant match: try contains
            for k in lookup.keys():
                if brand_name.lower() in k:
                    brand_id = lookup[k]
                    break
        if not brand_id:
            raise FetchError(f"brand '{brand_name}' not found on {self.base_url}")

        api_url = f"https://www.autoscout24.it/as24-home/api/taxonomy/cars/makes/{brand_id}/models"
        try:
            resp = _safe_get(api_url)
        except FetchError:
            raise
        # try json first, fallback to yaml parsing if needed
        data = {}
        try:
            data = resp.json()
        except ValueError:
            data = yaml.safe_load(resp.content)

        models: List[str] = []
        # traverse expected structure defensively
        try:
            modelline_vals = data.get("models", {}).get("modelLine", {}).get("values") or []
            models += [m["label"]["it_IT"].strip().lower().replace(" ", "-") for m in modelline_vals if m.get("label", {}).get("it_IT")]
            model_vals = data.get("models", {}).get("model", {}).get("values") or []
            models += [m.get("name", "").strip().lower().replace(" ", "-") for m in model_vals if m.get("name")]
        except Exception:
            # If structure differs, try to pull any 'label' names anywhere
            def _collect_labels(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        yield from _collect_labels(v)
                elif isinstance(obj, list):
                    for it in obj:
                        yield from _collect_labels(it)
                else:
                    return
            # ignore heavy fallback: keep models empty
            pass

        # deduplicate preserving order
        seen = set()
        out = []
        for m in models:
            if m and m not in seen:
                seen.add(m)
                out.append(m)
        return out

    def construct_search_url(self, selected_values: Dict[str, object]) -> str:
        """Construct a listing URL with filters encoded (non-authoritative, used for scraping)."""
        make = (selected_values.get("make") or "").strip().lower().replace(" ", "-")
        model = (selected_values.get("model") or "").strip().lower().replace(" ", "-")
        details = (selected_values.get("details") or "").strip().lower().replace(" ", "-")
        base = f"{self.base_url}lst"
        parts = [make, model]
        if details:
            parts.append(f"ve_{details}")
        url_path = "/".join([p for p in parts if p])
        url = f"{base}/{url_path}" if url_path else f"{self.base_url}lst/"
        # query parameters
        year = selected_values.get("firstRegistration")
        q = []
        if year:
            q.append(f"fregfrom={int(year)}")
            q.append(f"fregto={int(year)}")
        zip_code = (selected_values.get("zip") or "").strip()
        if zip_code:
            q.append(f"zip={zip_code}")
            q.append("zipr=200")
        shift = selected_values.get("shift_type", [])
        if isinstance(shift, (list, tuple)) and shift:
            q.append(f"gear={'%2C'.join([s for s in shift])}")
        # fixed filters
        q.append("custtype=D")
        q.append("cy=I")
        q.append("damaged_listing=exclude")
        q.append("desc=0")
        q.append("lat=45.07086")
        q.append("lon=7.643")
        q.append("powertype=kw")
        q.append("sort=standard")
        return url + "?" + "&".join(q)

    @staticmethod
    def _extract_price_from_node(node_text: str) -> Optional[int]:
        """Given a text snippet like '€ 12.500,-' or '€12.500', extract integer EUR value or return None."""
        if not node_text:
            return None
        # remove currency symbols and non-digit except thousand separators
        # keep digits only
        digits = "".join(ch for ch in node_text if ch.isdigit())
        if not digits:
            return None
        try:
            return int(digits)
        except ValueError:
            return None

    def fetch_car_costs(self, selected_values: Dict[str, object]) -> (int, float):
        """
        Fetch the listing page(s) and extract the representative price for a given selection.
        Returns an integer EUR estimate (e.g. median of found listing prices) or 0 when none found.
        This function is defensive: it will try to parse multiple listing price nodes and take the median.
        """
        url = self.construct_search_url(selected_values)
        resp = _safe_get(url)
        soup = BeautifulSoup(resp.content, "html.parser")

        # heuristics: find price nodes by class or by euro symbol presence
        price_texts = []
        # primary: look for known class
        for div in soup.find_all("div", class_=re.compile(r"Price|price", re.I)):
            txt = (div.get_text(separator=" ", strip=True) or "")
            if "€" in txt:
                price_texts.append(txt)

        # fallback: search for literal € in any element
        if not price_texts:
            for el in soup.find_all(text=re.compile(r"€\s*\d")):
                price_texts.append(str(el))

        # parse ints
        prices = [self._extract_price_from_node(t) for t in price_texts]
        prices = [p for p in prices if p is not None and p > 0]

        if not prices:
            return 0, 0

        # choose robust central tendency: median
        import statistics
        try:
            median_price = int(statistics.median(prices))
            price_stddev = statistics.stdev(prices)
        except Exception:
            median_price = int(prices[0])
            price_stddev = 0

        return median_price, price_stddev

