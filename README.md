# Discount and Revenue Prediction Project

This project consists of two main parts: a **backend** built with
**FastAPI** and a **frontend** developed with **Streamlit**.\
Together, they allow predicting future revenues and calculating a
predicted discount for different products, based on a regression model.

## Authors

-   Jimena Sonaly Flores Ticona
-   Bunty Nanwani Nanwani
-   Noé Moisés Guamán Álvarez
-   Óscar Rodríguez González

## Project Structure
-   `.devcontainer/`: Contains configuration for the development container, ensuring a consistent development environment.
-   `backend/`: The FastAPI application that serves the machine learning model. See `backend/README.md` for more details.
-   `frontend/`: The user interface for interacting with the prediction API. See `frontend/README.md` for more details.
-   `resources/`: Shared assets used by both the backend and frontend. This includes machine learning models, encoders, and images.
-   `docker-compose.yml`: Defines the services for development, including live-reloading.
-   `.env`: Environment variables for configuration (you will need to create this).
------------------------------------------------------------------------

## 1. Project Setup

### Requirements

Make sure you have **Python 3.8** or higher installed.

### Virtual Environment

It is highly recommended to create and activate a virtual environment to
manage the project dependencies in an isolated way.

``` bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (Linux/macOS)
source .venv/bin/activate

# Activate the virtual environment (Windows)
.\.venv\Scriptsctivate
```

### Installing Dependencies

Once the environment is activated, install all the necessary libraries:

    pip install -r requirements.txt

### Environment Variables

The project uses a `.env` file for paths and URLs.\
Make sure to have this file at the root of the project with the
following configuration:

    # API root URL
    API_URL=http://127.0.0.1:8000

    # Data path
    DATA_PATH=./resources/data/Supplement_Sales_Weekly_Expanded.csv

    # Revenue model
    REVENUE_MODEL_PATH=./resources/revenue/model_ridge.joblib
    REVENUE_SCALER_PATH=./resources/revenue/standard_scaler.joblib
    REVENUE_CATEGORY_PATH=./resources/revenue/category_by_price_dict.joblib
    REVENUE_PLATFORM_PATH=./resources/revenue/platform_by_price_dict.joblib
    REVENUE_LOCATION_PATH=./resources/revenue/location_by_price_dict.joblib
    REVENUE_PREDICTION_ENDPOINT=/predict/revenue

    # Discount Model
    DISCOUNT_MODEL_PATH=./resources/discount/discount_model.joblib
    DISCOUNT_PREDICTION_ENDPOINT=/predict/discount

    # Streamlit
    AISLE_IMG=./resources/images/aisle.png

## 2. How to Run the Application

### Step 1: Start the Backend

The FastAPI backend must be running so that the frontend can communicate
with it.\
Open a terminal in the project root and run:

    uvicorn backend.api:app --reload

### Step 2: Start the Frontend

With the backend running, open a second terminal, navigate to the
project root, and run:

    streamlit run frontend/main.py

## 3. How Discount Prediction Works

The application uses a regression-based machine learning model to
predict discounts.\
The model was trained using a **RandomForestRegressor**, and its role is
to analyze historical sales data to find correlations between variables.

### Input Variables

The model considers the following factors to make predictions:

-   Product: The type of supplement.\
-   Category: The category the product belongs to.\
-   Price: The cost per unit.\
-   Units Sold: The sales volume.\
-   Location: The country of sale.\
-   Platform: The online store.

## What does the model do?

Based on these variables, the model provides a predicted discount.\
This value reflects the correlation the model found in the historical
data.

If the predicted discounts are low, it means the correlations were weak
or the historical discounts were small.

The prediction is a direct reflection of the patterns the model learned
from that data.
