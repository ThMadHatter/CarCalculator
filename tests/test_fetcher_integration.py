# tests/test_fetcher_integration.py
import os
import pytest
from src.fetcher import Fetcher, FetchError
import datetime

# RUN_LIVE = os.getenv("RUN_LIVE_SCRAPES", "0") == "1"

# pytestmark = pytest.mark.skipif(not RUN_LIVE, reason="live scraping tests disabled (set RUN_LIVE_SCRAPES=1)")

def test_fetch_brands_live():
    """Fetch dropdowns from the live site to assert we get a 'make' list (basic smoke)."""
    f = Fetcher()
    dropdowns = f.fetch_dropdown_options()
    assert isinstance(dropdowns, dict)
    assert "make" in dropdowns
    assert isinstance(dropdowns["make"], list)
    assert len(dropdowns["make"]) > 0

def test_fetch_models_live_for_known_brand():
    """Try to fetch models for a known brand — this is a smoke check; may need a real brand name."""
    f = Fetcher()
    brands = f.fetch_dropdown_options().get("make", [])
    # pick a brand we hope to exist; this may need tuning per region
    if not brands:
        pytest.skip("No brands found on live site (site may block scraper).")
    brand = brands[0]
    models = f.fetch_car_models(brand)  # may raise FetchError if brand not resolvable
    assert isinstance(models, list)

def test_construct_search_url_basic_format():
    """Construct a URL and assert query parameters and path formatting are present."""
    f = Fetcher()
    sel = {
        "make": "BMW",
        "model": "320i",
        "details": "Sport Line",
        "zip": "10139",
        "firstRegistration": 2020,
        "shift_type": ["M", "A"],
    }
    url = f.construct_search_url(sel)
    # Basic sanity checks on the URL string
    assert url.startswith(f.base_url) or url.startswith("http")
    assert "fregfrom=2020" in url and "fregto=2020" in url
    assert ("ve_sport" in url) or ("ve-sport" in url)
    assert "zip=10139" in url
    assert ("gear=M%2CA" in url) or ("gear=M,A" in url)
    # fixed params must be present
    assert "custtype=D" in url and "sort=standard" in url

def test__extract_price_from_node_examples():
    """Pure function assertions using typical real-world formats."""
    f = Fetcher()
    assert f._extract_price_from_node("€ 12.500,-") == 12500
    assert f._extract_price_from_node("€12.000") == 12000
    assert f._extract_price_from_node("$ 9,999") == 9999
    assert f._extract_price_from_node("no price here") is None
    assert f._extract_price_from_node("") is None
    assert f._extract_price_from_node(None) is None

def test_live_end_to_end_fetch_and_parse():
    """
    Live end-to-end:
      1) fetch dropdown options and pick a brand
      2) fetch models for that brand
      3) call fetch_car_costs for a selected model
    Assertions are permissive: we require valid types and non-negative integer price.
    """
    f = Fetcher()
    # Step 1: dropdowns (brands)
    try:
        dropdowns = f.fetch_dropdown_options()
    except FetchError as e:
        pytest.skip(f"Live site unreachable or blocked (fetch_dropdown_options): {e}")

    brands = dropdowns.get("make") or []
    if not brands:
        pytest.skip("No brands returned by live site - cannot proceed with live test.")

    # pick first brand (hopefully common)
    brand = brands[0]
    # Step 2: models for brand
    try:
        models = f.fetch_car_models(brand)
    except FetchError:
        pytest.skip(f"fetch_car_models failed for brand '{brand}' - site may block taxonomy API or mapping changed.")
    if not models:
        pytest.skip(f"No models returned for brand '{brand}' - cannot proceed.")

    model = models[0]

    # Step 3: fetch car costs for a recent registration year (use current year)
    current_year = datetime.datetime.now().year
    selected_values = {
        "make": brand,
        "model": model,
        "details": "",
        "zip": "10139-torino",
        "firstRegistration": current_year,
        "shift_type": []
    }
    try:
        price = f.fetch_car_costs(selected_values)
    except FetchError as e:
        pytest.skip(f"fetch_car_costs failed (network/parsing): {e}")

    # Accept either 0 (no prices found) or positive int (price found)
    assert isinstance(price, int)
    assert price >= 0