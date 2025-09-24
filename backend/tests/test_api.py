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

# Es importante establecer las variables de entorno ANTES de importar la app,
# ya que la app las usa en el momento de la carga para encontrar los modelos.
os.environ['REVENUE_MODEL_PATH'] = str(get_absolute_path(os.getenv("REVENUE_MODEL_PATH")))
os.environ['REVENUE_SCALER_PATH'] = str(get_absolute_path(os.getenv("REVENUE_SCALER_PATH")))
os.environ['REVENUE_CATEGORY_PATH'] = str(get_absolute_path(os.getenv("REVENUE_LOCATION_PATH")))
os.environ['REVENUE_PLATFORM_PATH'] = str(get_absolute_path(os.getenv("REVENUE_CATEGORY_PATH")))
os.environ['REVENUE_LOCATION_PATH'] = str(get_absolute_path(os.getenv("REVENUE_PLATFORM_PATH")))
os.environ['PREDICT_REVENUE_ENDPOINT'] = os.getenv("PREDICT_REVENUE_ENDPOINT")

# Crear un cliente de prueba para la aplicación FastAPI
client = TestClient(app)

# Obtener el endpoint de la variable de entorno para asegurar consistencia
PREDICT_ENDPOINT = os.getenv("PREDICT_REVENUE_ENDPOINT")


def test_predict_revenue_success():
    """
    Prueba una predicción exitosa (código 200).
    """
    payload = {
        "Price": 50.5,
        "Day": 15,
        "Category": "Vitamin",
        "Location": "USA",
        "Platform": "Amazon"
    }
    response = client.post(PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_revenue" in data
    assert isinstance(data["predicted_revenue"], float)


def test_predict_revenue_validation_error_price():
    """
    Prueba un error de validación (código 422) por un precio fuera de rango.
    """
    payload = {
        "Price": 100.0,  # Precio > 75, debería fallar
        "Day": 15,
        "Category": "Vitamin",
        "Location": "USA",
        "Platform": "Amazon"
    }
    response = client.post(PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 422


def test_predict_revenue_validation_error_missing_field():
    """
    Prueba un error de validación (código 422) por un campo faltante.
    """
    payload = {
        "Day": 15,
        "Category": "Vitamin",
        "Location": "USA",
        "Platform": "Amazon"
    }
    response = client.post(PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 422


def test_predict_revenue_unknown_category():
    """
    Prueba el manejo de una categoría desconocida.
    El endpoint debería manejarlo sin fallar y devolver una predicción.
    """
    payload = {"Price": 25, "Day": 10, "Category": "NonExistentCategory", "Location": "USA", "Platform": "Amazon"}
    response = client.post(PREDICT_ENDPOINT, json=payload)
    assert response.status_code == 200
    assert "predicted_revenue" in response.json()