# Frontend - Revenue Prediction

This directory contains the Streamlit frontend application for the revenue prediction project.

## Features

-   **User-friendly Interface**: Allows users to input product features through sliders and dropdowns.
-   **Dynamic Dropdowns**: The lists for `Category`, `Location`, and `Platform` are dynamically loaded from the model's encoder files.
-   **API Integration**: Communicates with the backend FastAPI to get revenue predictions.
-   **Persistent State**: Displays the last successful prediction or error message using Streamlit's session state.

## Setup and Installation

This project is designed to be run within the provided Dev Container, which handles dependency installation automatically.

If you are running the frontend outside of the Dev Container, you must install the dependencies manually:

```bash
# Navigate to the frontend directory
cd frontend

# Install Python packages
pip install -r requirements.txt
```

## Environment Variables

The frontend requires environment variables to connect to the backend API and load the necessary data for the UI. These are typically defined in a `.env` file in the project root.

-   `FASTAPI_URL`: The base URL for the backend API (e.g., `http://backend:8000` inside Docker, or `http://localhost:8000` if running locally).
-   `PREDICT_REVENUE_ENDPOINT`: The specific endpoint for predictions (e.g., `/predict/revenue`).
-   `REVENUE_CATEGORY_PATH`: Path to the category encoder file (`.joblib`).
-   `REVENUE_LOCATION_PATH`: Path to the location encoder file (`.joblib`).
-   `REVENUE_PLATFORM_PATH`: Path to the platform encoder file (`.joblib`).

Refer to the main `README.md` for an example of the `.env` file structure.

## How to Run

1.  **Start the Backend**: Ensure the backend API server is running.
    ```bash
    # From the project root
    cd backend
    uvicorn api:app --host 0.0.0.0 --port 8000
    ```

2.  **Start the Frontend**: Open a new terminal.
    ```bash
    # From the project root
    cd frontend
    streamlit run main.py
    ```

The application will be available in your browser, typically at `http://localhost:8501`.