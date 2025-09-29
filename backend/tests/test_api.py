import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from backend.api import app, get_absolute_path

# Define the project root directory. api.py is in backend/, so root is one level up.
# This makes path handling robust regardless of where the script is run from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load env variables from the .env file in the project root
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# It's important to set the environment variables BEFORE importing the app,
# as the app uses them at load time to find the models.
os.environ['REVENUE_MODEL_PATH'] = str(get_absolute_path(os.getenv("REVENUE_MODEL_PATH")))
os.environ['REVENUE_SCALER_PATH'] = str(get_absolute_path(os.getenv("REVENUE_SCALER_PATH")))
os.environ['REVENUE_CATEGORY_PATH'] = str(get_absolute_path(os.getenv("REVENUE_CATEGORY_PATH")))
os.environ['REVENUE_PLATFORM_PATH'] = str(get_absolute_path(os.getenv("REVENUE_PLATFORM_PATH")))
os.environ['REVENUE_LOCATION_PATH'] = str(get_absolute_path(os.getenv("REVENUE_LOCATION_PATH")))
os.environ['REVENUE_PREDICTION_ENDPOINT'] = os.getenv("REVENUE_PREDICTION_ENDPOINT")
os.environ['DISCOUNT_MODEL_PATH'] = str(get_absolute_path(os.getenv("DISCOUNT_MODEL_PATH")))
os.environ['DATA_PATH'] = str(PROJECT_ROOT / os.getenv("DATA_PATH"))

# Create a test client for the FastAPI application
client = TestClient(app)

# Get endpoints from environment variables to ensure consistency
REVENUE_PREDICT_ENDPOINT = os.getenv("REVENUE_PREDICTION_ENDPOINT")
DISCOUNT_PREDICT_ENDPOINT = os.getenv("DISCOUNT_PREDICTION_ENDPOINT")
PRICE_PREDICT_ENDPOINT = os.getenv("PRICE_PREDICTION_ENDPOINT")


def test_predict_revenue_success():
    """
    Test a successful revenue prediction (200 OK).
    """
    payload = {
        "Price": 50.5,
        "Day": 15,
        "Category": "Vitamin",
        "Location": "USA",
        "Platform": "Amazon"
    }
    response = client.post(REVENUE_PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_revenue" in data
    assert isinstance(data["predicted_revenue"], float)


def test_predict_revenue_validation_error_on_price():
    """
    Test a validation error (422) for an out-of-range price.
    """
    payload = {
        "Price": 100.0,  # Price > 75, should fail
        "Day": 15,
        "Category": "Vitamin",
        "Location": "USA",
        "Platform": "Amazon"
    }
    response = client.post(REVENUE_PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 422


def test_predict_revenue_validation_error_missing_field():
    """
    Test a validation error (422) for a missing field.
    """
    payload = {
        "Day": 15,
        "Category": "Vitamin",
        "Location": "USA",
        "Platform": "Amazon"
    }
    response = client.post(REVENUE_PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 422


def test_predict_revenue_unknown_category():
    """
    Test handling of an unknown category.
    The endpoint should handle it without failing and return a prediction.
    """
    payload = {"Price": 25, "Day": 10, "Category": "NonExistentCategory", "Location": "USA", "Platform": "Amazon"}
    response = client.post(REVENUE_PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 200
    assert "predicted_revenue" in response.json()


def test_get_metadata_success():
    """
    Test a successful call to the /metadata endpoint (200 OK).
    """
    response = client.get("/metadata")
    assert response.status_code == 200
    data = response.json()

    # Check for the presence of all expected top-level keys
    expected_keys = ["products", "product_info", "categories", "locations", "platforms"]
    for key in expected_keys:
        assert key in data

    # Check that the returned values are of the correct type and not empty
    assert isinstance(data["products"], list) and data["products"]
    assert isinstance(data["product_info"], dict) and data["product_info"]
    assert isinstance(data["categories"], list) and data["categories"]


def test_predict_discount_success():
    """
    Test a successful discount prediction (200 OK).
    """
    payload = {
        "product_name": "B-Complex",
        "category": "Vitamin",
        "price": 25.99,
        "units_sold": 150,
        "location": "USA",
        "platform": "Amazon"
    }
    response = client.post(DISCOUNT_PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_discount" in data
    assert isinstance(data["predicted_discount"], float)


def test_predict_discount_validation_error_missing_field():
    """
    Test a validation error (422) for a missing field in discount prediction.
    """
    payload = {
        "product_name": "B-Complex",
        "category": "Vitamin",
        "price": 25.99,
        # "units_sold" is missing
        "location": "USA",
        "platform": "Amazon"
    }
    response = client.post(DISCOUNT_PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 422


def test_predict_price_success():
    """
    Test a successful price prediction (200 OK).
    Note: This test requires a product with enough historical data
    to survive the feature engineering process (e.g., > 12 months).
    "Omega-3" is used here for that reason.
    """
    params = {
        "product": "Vitamin C",
        "year": 2024,
        "month": 12
    }
    response = client.get(PRICE_PREDICT_ENDPOINT, params=params)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_price" in data
    assert isinstance(data["predicted_price"], float)
    assert data["product"] == "Vitamin C"


def test_predict_price_product_not_found():
    """
    Test price prediction for a product that does not exist.
    The API should return a 200 OK status with an error message in the JSON payload.
    """
    params = {
        "product": "NonExistentProduct",
        "year": 2024,
        "month": 12
    }
    response = client.get(PRICE_PREDICT_ENDPOINT, params=params)
    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"] == "Producto no encontrado"


def test_predict_price_validation_error_missing_param():
    """
    Test a validation error (422) for a missing query parameter.
    """
    params = {"product": "Omega-3", "year": 2024}  # Missing 'month'
    response = client.get(PRICE_PREDICT_ENDPOINT, params=params)
    assert response.status_code == 422