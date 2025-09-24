import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Define la ruta raíz del proyecto. El archivo api.py está en backend/, así que la raíz es un nivel arriba.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Se han corregido las importaciones para que sean absolutas desde la raíz del proyecto.
# Esto previene el error 'ModuleNotFoundError' al ejecutar el comando desde la raíz.
from backend.models.revenue_model import RevenueModel
from backend.models.discount_model import DiscountModel

# Define las rutas absolutas para los archivos del modelo y datos
REVENUE_MODEL_PATH = PROJECT_ROOT / os.getenv("REVENUE_MODEL_PATH")
REVENUE_SCALER_PATH = PROJECT_ROOT / os.getenv("REVENUE_SCALER_PATH")
REVENUE_CATEGORY_PATH = PROJECT_ROOT / os.getenv("REVENUE_CATEGORY_PATH")
REVENUE_LOCATION_PATH = PROJECT_ROOT / os.getenv("REVENUE_LOCATION_PATH")
REVENUE_PLATFORM_PATH = PROJECT_ROOT / os.getenv("REVENUE_PLATFORM_PATH")

DISCOUNT_MODEL_PATH = PROJECT_ROOT / os.getenv("DISCOUNT_MODEL_PATH")
DATA_PATH = PROJECT_ROOT / os.getenv("DATA_PATH")


# Cargar los modelos y mapeos
try:
    revenue_model = joblib.load(REVENUE_MODEL_PATH)
    revenue_scaler = joblib.load(REVENUE_SCALER_PATH)
    revenue_category_map = joblib.load(REVENUE_CATEGORY_PATH)
    revenue_location_map = joblib.load(REVENUE_LOCATION_PATH)
    revenue_platform_map = joblib.load(REVENUE_PLATFORM_PATH)

    # Ahora solo cargamos el modelo de descuento, que incluye el mapeo interno
    discount_model = joblib.load(DISCOUNT_MODEL_PATH)

    products_df = pd.read_csv(DATA_PATH)

except FileNotFoundError as e:
    raise RuntimeError(
        f"Error al cargar archivos del modelo/mapeo. Asegúrate de que las rutas en .env sean correctas. {e}"
    )
except Exception as e:
    raise RuntimeError(f"Ocurrió un error inesperado al cargar los archivos: {e}")


# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Predicción de Precios y Descuentos",
    description="Una API simple para predecir ingresos y descuentos óptimos para suplementos alimenticios.",
    version="1.0.0",
)


# Definir los esquemas de entrada y salida
class RevenuePayload(BaseModel):
    Price: float
    Day: float
    Category: str
    Location: str
    Platform: str


class DiscountPayload(BaseModel):
    product_name: str
    category: str
    price: float
    units_sold: int
    location: str
    platform: str


class PredictionResult(BaseModel):
    predicted_revenue: float


class DiscountPredictionResult(BaseModel):
    predicted_discount: float


# Endpoint para metadatos de productos
@app.get("/metadata")
def get_metadata():
    if products_df.empty:
        raise HTTPException(
            status_code=500, detail="No se pudo cargar el DataFrame de productos."
        )

    product_list = products_df["Product Name"].unique().tolist()
    product_info = {
        name: {
            "category": products_df[products_df["Product Name"] == name]["Category"]
            .mode()
            .iloc[0],
            "avg_price": products_df[products_df["Product Name"] == name][
                "Price"
            ].mean(),
            "avg_units_sold": products_df[products_df["Product Name"] == name][
                "Units Sold"
            ].mean(),
        }
        for name in product_list
    }

    return {
        "products": product_list,
        "product_info": product_info,
        "categories": sorted(products_df["Category"].unique().tolist()),
        "locations": sorted(products_df["Location"].unique().tolist()),
        "platforms": sorted(products_df["Platform"].unique().tolist()),
    }


# Endpoint para la predicción de ingresos
@app.post("/predict/revenue", response_model=PredictionResult)
def predict_revenue(payload: RevenuePayload):
    try:
        # Convertir a DataFrame
        data = pd.DataFrame([payload.dict()])

        # Mapear categorías, ubicaciones y plataformas a sus representaciones numéricas
        data["Category_mapped"] = (
            data["Category"]
            .map(revenue_category_map)
            .fillna(revenue_category_map.get("Unknown", -1))
            .astype(int)
        )
        data["Location_mapped"] = (
            data["Location"]
            .map(revenue_location_map)
            .fillna(revenue_location_map.get("Unknown", -1))
            .astype(int)
        )
        data["Platform_mapped"] = (
            data["Platform"]
            .map(revenue_platform_map)
            .fillna(revenue_platform_map.get("Unknown", -1))
            .astype(int)
        )

        # Asegurarse de que las columnas estén en el orden correcto
        features = data[
            ["Price", "Day", "Category_mapped", "Location_mapped", "Platform_mapped"]
        ]

        # Realizar la predicción
        prediction = revenue_model.predict(features)[0]

        return {"predicted_revenue": prediction}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para la predicción de descuento
@app.post("/predict/discount", response_model=DiscountPredictionResult)
def predict_discount(payload: DiscountPayload):
    try:
        data = pd.DataFrame([payload.dict()])

        # El pipeline del modelo de descuento maneja las variables categóricas internamente
        prediction = discount_model.predict(data)[0]

        return {"predicted_discount": prediction}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
