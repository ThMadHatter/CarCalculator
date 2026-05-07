import pytest
from unittest.mock import patch
from types import SimpleNamespace
from src.fetcher import Fetcher, FetchError, _SESSION
import yaml

# helper mock response object used to simulate requests.Response
class MockResp:
    def __init__(self, content: bytes | str, json_data=None):
        if isinstance(content, str):
            self.content = content.encode("utf-8")
        else:
            self.content = content
        self._json = json_data

    def json(self):
        if self._json is None:
            raise ValueError("No JSON")
        return self._json


def test_fetch_dropdown_options_parses_selects_and_uses_fetch_models(monkeypatch):
    html = """
    <html>
      <body>
        <select name="make">
          <option value="">--</option>
          <option value="123">BrandName</option>
        </select>
        <select name="other">
          <option value="a">A</option>
          <option value="b">B</option>
        </select>
      </body>
    </html>
    """
    # patch Fetcher.fetch_car_models to be called when selected_values contains make
    f = Fetcher()
    monkeypatch.setattr(f, "fetch_car_models", lambda brand: ["m1", "m2"])
    # patch _safe_get to return home page
    with patch("src.fetcher._safe_get", return_value=MockResp(html)):
        res = f.fetch_dropdown_options(selected_values={"make": "BrandName"})
        assert "make" in res
        assert "other" in res
        # model was added from fetch_car_models
        assert res["model"] == ["m1", "m2"]


def test_fetch_car_models_success_json(monkeypatch):
    # home page with make select
    home_html = """
    <html><body>
      <select name="make">
        <option value="">--</option>
        <option value="123">BrandName</option>
      </select>
    </body></html>
    """
    # api response JSON structure expected by parser
    api_json = {
        "models": {
            "modelLine": {
                "values": [
                    {"label": {"it_IT": "Model A"}}
                ]
            },
            "model": {
                "values": [
                    {"name": "Model B"}
                ]
            }
        }
    }
    # two sequential _safe_get calls: home page then api
    calls = [MockResp(home_html), MockResp("", json_data=api_json)]
    with patch("src.fetcher._safe_get", side_effect=calls):
        f = Fetcher()
        res = f.fetch_car_models("brandname")
        # hyphenated lowercase expected
        assert "model-a" in res
        assert "model-b" in res


def test_fetch_car_models_with_yaml_fallback(monkeypatch):
    home_html = """
    <html><body>
      <select name="make"><option value="123">BrandName</option></select>
    </body></html>
    """
    # YAML string matching expected structure; note using 'label' and 'name'
    yaml_text = yaml.safe_dump({
        "models": {
            "modelLine": {"values": [{"label": {"it_IT": "YModelA"}}]},
            "model": {"values": [{"name": "YModelB"}]}
        }
    })
    calls = [MockResp(home_html), MockResp(yaml_text)]
    with patch("src.fetcher._safe_get", side_effect=calls):
        f = Fetcher()
        res = f.fetch_car_models("brandname")
        assert "ymodela" in res or "y-modela" in res  # accept small variation
        assert any("ymodelb" in x for x in res)


def test_fetch_car_models_not_found_raises():
    # home page that lacks the make mapping
    html = "<html><body><select name='make'></select></body></html>"
    with patch("src.fetcher._safe_get", return_value=MockResp(html)):
        f = Fetcher()
        with pytest.raises(FetchError):
            f.fetch_car_models("nonexistent")


def test_construct_search_url_contains_filters():
    f = Fetcher()
    selected = {
        "make": "bmw",
        "model": "320i",
        "details": "sport",
        "zip": "10139-torino",
        "firstRegistration": 2020,
        "shift_type": ["M", "A"],
    }
    url = f.construct_search_url(selected)
    assert "fregfrom=2020" in url and "fregto=2020" in url
    assert "zip=10139-torino" in url
    assert "gear=M%2CA" in url or "gear=M,A" in url
    assert "ve_sport" in url or "ve-sport" in url


def test__extract_price_from_node_various_inputs():
    f = Fetcher()
    assert f._extract_price_from_node("€ 12.500,-") == 12500
    assert f._extract_price_from_node("€12.000") == 12000
    assert f._extract_price_from_node("no digits") is None
    assert f._extract_price_from_node("") is None
    assert f._extract_price_from_node(None) is None


def test_fetch_car_costs_parses_price_nodes_and_median():
    # HTML contains several divs with a Price-like class and euro amounts
    html = """
    <div class="PriceAndSeals_wrapper__BMNaJ">€ 30.000</div>
    <div class="PriceAndSeals_wrapper__BMNaJ">€ 28.000</div>
    <div class="PriceAndSeals_wrapper__BMNaJ">€ 26.000</div>
    """
    with patch("src.fetcher._safe_get", return_value=MockResp(html)):
        f = Fetcher()
        price = f.fetch_car_costs({"make":"bmw","model":"m","firstRegistration":2022})
        # median of [30000,28000,26000] is 28000
        assert price == 28000


def test_fetch_car_costs_fallback_to_text_search_and_zero_when_none():
    # first case: fallback to text nodes that include €... numbers
    html_with_text = "<p>Special price € 9.999 today</p>"
    with patch("src.fetcher._safe_get", return_value=MockResp(html_with_text)):
        f = Fetcher()
        price = f.fetch_car_costs({"make":"x","model":"y","firstRegistration":2021})
        assert price == 9999

    # second case: no euro strings at all -> returns 0
    html_no_euro = "<div>No price here</div>"
    with patch("src.fetcher._safe_get", return_value=MockResp(html_no_euro)):
        f = Fetcher()
        price = f.fetch_car_costs({"make":"x","model":"y","firstRegistration":2021})
        assert price == 0
