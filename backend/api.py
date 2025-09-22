from json import load
import os
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


# 1. Load the pre-trained model and scaler
try:
    revenue_model = joblib.load(REVENUE_MODEL_PATH)
    revenue_scaler = joblib.load(REVENUE_SCALER_PATH)
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
    # Create a DataFrame from the input data
    # The column names MUST match the names used during training.
    input_df = pd.DataFrame([[data.Price, data.Day]],
                            columns=["Price", "Day"])

    # Scale the input data using the pre-trained scaler
    scaled_input = revenue_scaler.transform(input_df)

    # Make the prediction using the loaded model
    prediction = revenue_model.predict(scaled_input)

    # Return the prediction as a JSON object
    return {"predicted_revenue": prediction[0]}