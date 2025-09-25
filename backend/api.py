import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI

from .models.revenue_model import RevenueModel
from backend.utils import prepare_data, create_features, train_models

#from .utils import prepare_data, create_features, train_models   # 👈 tienes que tener esto en utils.py

# --- Path and Environment Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

def get_absolute_path(path: str) -> Path:
    if os.path.isabs(path):
        return Path(path)
    return PROJECT_ROOT / path

REVENUE_MODEL_PATH = get_absolute_path(os.getenv("REVENUE_MODEL_PATH"))
REVENUE_SCALER_PATH = get_absolute_path(os.getenv("REVENUE_SCALER_PATH"))
REVENUE_LOCATION_PATH = get_absolute_path(os.getenv("REVENUE_LOCATION_PATH"))
REVENUE_CATEGORY_PATH = get_absolute_path(os.getenv("REVENUE_CATEGORY_PATH"))
REVENUE_PLATFORM_PATH = get_absolute_path(os.getenv("REVENUE_PLATFORM_PATH"))

PREDICT_REVENUE_ENDPOINT = os.getenv("PREDICT_REVENUE_ENDPOINT")

# --- Load trained models ---
try:
    revenue_model = joblib.load(REVENUE_MODEL_PATH)
    revenue_scaler = joblib.load(REVENUE_SCALER_PATH)
    revenue_category_dict = joblib.load(REVENUE_CATEGORY_PATH)
    revenue_platform_dict = joblib.load(REVENUE_PLATFORM_PATH)
    revenue_location_dict = joblib.load(REVENUE_LOCATION_PATH)
except FileNotFoundError as e:
    raise RuntimeError(f"Model or scaler not found. Details: {e}")

# --- FastAPI ---
app = FastAPI()

@app.post(PREDICT_REVENUE_ENDPOINT)
def predict_revenue(data: RevenueModel):
    unknown_category_val = revenue_category_dict.get('Unknown')
    unknown_platform_val = revenue_platform_dict.get('Unknown')
    unknown_location_val = revenue_location_dict.get('Unknown')

    category_by_price = revenue_category_dict.get(data.Category, unknown_category_val)
    platform_by_price = revenue_platform_dict.get(data.Platform, unknown_platform_val)
    location_by_price = revenue_location_dict.get(data.Location, unknown_location_val)

    input_df = pd.DataFrame(
        [[data.Price, category_by_price, location_by_price, platform_by_price, data.Day]],
        columns=["Price", "Category_By_Price", "Location_By_Price", "Platform_By_Price", "Day"]
    )

    scaled_input = revenue_scaler.transform(input_df)
    prediction = revenue_model.predict(scaled_input)
    return {"predicted_revenue": prediction[0]}

# --- Modelo Bunty ---
# Cargar dataset de suplementos
DATA_PATH = PROJECT_ROOT / "resources" / "data" / "Supplement_Sales_Weekly_Expanded.csv"
df = pd.read_csv(DATA_PATH)

# Preparar datos y entrenar modelos
df_prepared = prepare_data(df)
df_features = create_features(df_prepared)
models = train_models(df_features)

@app.get("/products")
def get_products():
    products = df_prepared["Product_Name"].unique().tolist()
    return {"products": products}


@app.get("/predict")
def predict(product: str, year: int, month: int):
    if product not in models:
        return {"error": "Producto no encontrado"}
    
    model = models[product]

    features = {
        "Year": year,
        "Month": month,
        "Month_sin": np.sin(2 * np.pi * month / 12),
        "Month_cos": np.cos(2 * np.pi * month / 12),
        "Years_From_Start": year - df_prepared['Year'].min(),
        "Time_Index": (year - df_prepared['Year'].min()) * 12 + month,
        "Time_Index_Squared": ((year - df_prepared['Year'].min()) * 12 + month) ** 2,
        "Price_Lag_1": df_features[df_features['Product_Name'] == product]['Price_Avg'].iloc[-1],
        "Price_Lag_3": df_features[df_features['Product_Name'] == product]['Price_Avg'].iloc[-3],
        "Price_Lag_12": df_features[df_features['Product_Name'] == product]['Price_Avg'].iloc[-12],
        "Price_MA_6": df_features[df_features['Product_Name'] == product]['Price_Avg'].rolling(6).mean().iloc[-1],
        "Price_MA_12": df_features[df_features['Product_Name'] == product]['Price_Avg'].rolling(12).mean().iloc[-1],
    }

    X_new = pd.DataFrame([features])
    pred = model.predict(X_new)[0]

    return {
        "product": product,
        "year": year,
        "month": month,
        "predicted_price": round(float(pred), 2)
    }
