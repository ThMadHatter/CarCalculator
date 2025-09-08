from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)


def fake_fetch_car_costs(selected_values):
    # return deterministic price based on registration year
    year = int(selected_values.get("firstRegistration") or 2025)
    # price decays with age:
    age = 2025 - year
    return max(1000, 30000 - age * 2000)


@patch("src.fetcher.Fetcher.fetch_car_costs", side_effect=fake_fetch_car_costs)
def test_estimate_endpoint(mock_fetch):
    payload = {
        "brand": "testbrand",
        "model": "testmodel",
        "details": "",
        "zip_code": "10139-torino",
        "registration_year": 2025,
        "number_of_years": 3,
        "purchase_year_index": 1,
        "monthly_maintenance": 100.0,
        "loan_value": 0.0,
        "bank_rate_percent": 0.0,
        "loan_years": 0,
        "shift_types": []
    }
    r = client.post("/api/estimate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "purchase_price" in data
    assert data["loan_monthly_payment"] == 0.0
