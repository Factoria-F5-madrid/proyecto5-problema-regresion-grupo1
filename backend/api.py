from json import load
import os
from unicodedata import category
from dotenv import load_dotenv
import joblib
import pandas as pd
from fastapi import FastAPI

from models.revenue_model import RevenueModel

# Load env variables
load_dotenv()

# Get env variables for revenue model
REVENUE_MODEL_PATH = os.getenv("REVENUE_MODEL_PATH")
REVENUE_SCALER_PATH = os.getenv("REVENUE_SCALER_PATH")
PREDICT_REVENUE_ENDPOINT = os.getenv("PREDICT_REVENUE_ENDPOINT")
REVENUE_LOCATION_PATH = os.getenv("REVENUE_LOCATION_PATH")
REVENUE_CATEGORY_PATH = os.getenv("REVENUE_CATEGORY_PATH") 
REVENUE_PLATFORM_PATH = os.getenv("REVENUE_PLATFORM_PATH")

# 1. Load the pre-trained model and scaler
try:
    revenue_model = joblib.load(REVENUE_MODEL_PATH)
    revenue_scaler = joblib.load(REVENUE_SCALER_PATH)
    revenue_category_dict = joblib.load(REVENUE_CATEGORY_PATH)
    revenue_platform_dict = joblib.load(REVENUE_PLATFORM_PATH)
    revenue_location_dict = joblib.load(REVENUE_LOCATION_PATH)  
except FileNotFoundError:
    raise RuntimeError("Model or scaler not found. Please ensure they exist.")

# 2. Initialize the FastAPI app
app = FastAPI()

# 3. Create the prediction endpoint for Revenue
@app.post(PREDICT_REVENUE_ENDPOINT)
def predict_revenue(data: RevenueModel):
    """
    Predicts revenue based on Price and Day.
    """
    # Load dictionaries    
    category_by_price = revenue_category_dict.get(data.Category)
    platform_by_price = revenue_platform_dict.get(data.Platform)
    location_by_price = revenue_location_dict.get(data.Location)

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