import os
from pathlib import Path
from dotenv import load_dotenv
import joblib
import pandas as pd
from fastapi import FastAPI

from .models.revenue_model import RevenueModel

# --- Path and Environment Configuration ---

# Define the project root directory. api.py is in backend/, so root is one level up.
# This makes path handling robust regardless of where the script is run from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load env variables from the .env file in the project root
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

def get_absolute_path(path: str) -> Path:
    """
    Converts a relative path from the project root to an absolute path.
    If the path is already absolute, it returns it as a Path object.
    """
    if os.path.isabs(path):
        return Path(path)
    return PROJECT_ROOT / path

REVENUE_MODEL_PATH = get_absolute_path(os.getenv("REVENUE_MODEL_PATH"))
REVENUE_SCALER_PATH = get_absolute_path(os.getenv("REVENUE_SCALER_PATH"))
REVENUE_LOCATION_PATH = get_absolute_path(os.getenv("REVENUE_LOCATION_PATH"))
REVENUE_CATEGORY_PATH = get_absolute_path(os.getenv("REVENUE_CATEGORY_PATH"))
REVENUE_PLATFORM_PATH = get_absolute_path(os.getenv("REVENUE_PLATFORM_PATH"))

# The endpoint is a string, not a file path
PREDICT_REVENUE_ENDPOINT = os.getenv("PREDICT_REVENUE_ENDPOINT")

# 1. Load the pre-trained model and scaler
try:
    revenue_model = joblib.load(REVENUE_MODEL_PATH)
    revenue_scaler = joblib.load(REVENUE_SCALER_PATH)
    revenue_category_dict = joblib.load(REVENUE_CATEGORY_PATH)
    revenue_platform_dict = joblib.load(REVENUE_PLATFORM_PATH)
    revenue_location_dict = joblib.load(REVENUE_LOCATION_PATH)  
except FileNotFoundError as e:
    raise RuntimeError(f"Model or scaler not found. Please ensure they exist. Details: {e}")

# 2. Initialize the FastAPI app
app = FastAPI()

# 3. Create the prediction endpoint for Revenue
@app.post(PREDICT_REVENUE_ENDPOINT)
def predict_revenue(data: RevenueModel):
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

    # Create a DataFrame from the input data
    # The column names MUST match the names used during training.
    input_df = pd.DataFrame([[data.Price, category_by_price, location_by_price, platform_by_price, data.Day]],
                            columns=["Price", "Category_By_Price", "Location_By_Price", "Platform_By_Price", "Day"])

    # Scale the input data using the pre-trained scaler
    scaled_input = revenue_scaler.transform(input_df)

    # Make the prediction using the loaded model
    prediction = revenue_model.predict(scaled_input)

    # Return the prediction as a JSON object
    return {"predicted_revenue": prediction[0]}