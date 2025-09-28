# Discount and Revenue Prediction Project

This project consists of two main parts: a **backend** built with
**FastAPI** and a **frontend** developed with **Streamlit**.\
Together, they allow predicting future revenues, calculating a
predicted discount, and forecasting future prices for different products.

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

### Using Dev Containers (Recommended)

This project is configured to run inside a VS Code Dev Container. This is the easiest way to get started as it automatically sets up the environment and installs all dependencies.

**Prerequisites:**
-   [Visual Studio Code](https://code.visualstudio.com/)
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
-   [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code.

**Steps:**

1.  Clone the repository and open the project folder in VS Code.
2.  A notification will appear in the bottom-right corner asking if you want to **"Reopen in Container"**. Click it.
3.  VS Code will build the container and install all Python dependencies automatically. This might take a few minutes on the first run.
4.  Once the container is running, you can proceed to the "How to Run the Application" section below. All commands should be run inside the VS Code integrated terminal.


### Virtual Environment

It is highly recommended to create and activate a virtual environment to
manage the project dependencies in an isolated way.

``` bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (Linux/macOS)
source .venv/bin/activate

# Activate the virtual environment (Windows)
.\.venv\Scripts\activate
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

    # Price Model
    PRICE_PREDICTION_ENDPOINT=/predict/price

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

## 3. How Prediction Works
The application uses three different machine learning models to provide predictions.

### Model 1: Revenue Prediction
This model predicts future revenue based on a set of input features.

*   **Model Type**: Ridge Regression (`model_ridge.joblib`)
*   **Inputs**:
    *   Price: The cost per unit.
    *   Day: The day of the month.
    *   Category: The product category.
    *   Location: The country of sale.
    *   Platform: The online store.
*   **Output**: A predicted revenue amount.

### Model 2: Discount Prediction
This model analyzes historical sales data to suggest a discount for a product.

*   **Model Type**: Random Forest Regressor (`discount_model.joblib`)
*   **Inputs**:
    *   Product: The type of supplement.
    *   Category: The category the product belongs to.
    *   Price: The cost per unit.
    *   Units Sold: The historical sales volume.
    *   Location: The country of sale.
    *   Platform: The online store.
*   **Output**: A predicted discount percentage. This value reflects the correlations the model found in the historical data. If the predicted discounts are low, it suggests that historical discounts were small or correlations were weak.

### Model 3: Price Prediction
This model uses time-series analysis to forecast the future price of a specific product. A separate model is trained for each product when the API starts.

*   **Model Type**: Gradient Boosting Regressor (one per product)
*   **Inputs**:
    *   Product: The name of the supplement.
    *   Year: The target year for the forecast.
    *   Month: The target month for the forecast.
*   **Output**: The predicted average price for the product in the given month and year.
