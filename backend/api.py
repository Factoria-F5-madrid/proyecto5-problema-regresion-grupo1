import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException


from .models.revenue import RevenuePayload, RevenuePredictionResult
from .models.discount import DiscountPayload, DiscountPredictionResult

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
DISCOUNT_MODEL_PATH = get_absolute_path(os.getenv("DISCOUNT_MODEL_PATH"))
DATA_PATH = PROJECT_ROOT / os.getenv("DATA_PATH")

# The endpoint is a string, not a file path
REVENUE_PREDICTION_ENDPOINT = os.getenv("REVENUE_PREDICTION_ENDPOINT")
DISCOUNT_PREDICTION_ENDPOINT = os.getenv("DISCOUNT_PREDICTION_ENDPOINT")

# Load the pre-trained model and scaler
try:
    revenue_model = joblib.load(REVENUE_MODEL_PATH)
    revenue_scaler = joblib.load(REVENUE_SCALER_PATH)
    revenue_category_dict = joblib.load(REVENUE_CATEGORY_PATH)
    revenue_platform_dict = joblib.load(REVENUE_PLATFORM_PATH)
    revenue_location_dict = joblib.load(REVENUE_LOCATION_PATH)

    # Now we only load the discount model, which includes the internal mapping
    discount_model = joblib.load(DISCOUNT_MODEL_PATH)
    products_df = pd.read_csv(DATA_PATH)
except FileNotFoundError as e:
    raise RuntimeError(f"Model or scaler not found. Details: {e}")

# --- FastAPI ---
app = FastAPI()

# Endpoint for product metadata
@app.get("/metadata")
def get_metadata():
    if products_df.empty:
        raise HTTPException(
            status_code=500, detail="Could not load the products DataFrame."
        )

    product_list = products_df["Product_Name"].unique().tolist()
    product_info = {
        name: {
            "category": products_df[products_df["Product_Name"] == name]["Category"]
            .mode()
            .iloc[0],
            "avg_price": products_df[products_df["Product_Name"] == name][
                "Price"
            ].mean(),
            "avg_units_sold": products_df[products_df["Product_Name"] == name][
                "Units_Sold"
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


# Create the prediction endpoint for Revenue
@app.post(REVENUE_PREDICTION_ENDPOINT, response_model=RevenuePredictionResult)
def predict_revenue(data: RevenuePayload):
    """
    Predicts revenue based on Price and Day.
    """
    # Get the encoded value for each categorical feature.
    # If the key is not found, default to the value for 'Unknown'.
    # This prevents NaN values if an unseen category is provided.
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

# Endpoint for discount prediction
@app.post(DISCOUNT_PREDICTION_ENDPOINT, response_model=DiscountPredictionResult)
def predict_discount(payload: DiscountPayload):
    try:
        data = pd.DataFrame([payload.model_dump()])

        # The discount model pipeline handles categorical variables internally
        prediction = discount_model.predict(data)[0]

        return {"predicted_discount": prediction}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))