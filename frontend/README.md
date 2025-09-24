# Frontend - Revenue Prediction

This directory contains the Streamlit frontend application for the revenue prediction project.

## Features

-   **User-friendly Interface**: Allows users to input product features through sliders and dropdowns.
-   **Dynamic Dropdowns**: The lists for `Category`, `Location`, and `Platform` are dynamically loaded from the model's encoder files.
-   **API Integration**: Communicates with the backend FastAPI to get revenue predictions.
-   **Persistent State**: Displays the last successful prediction or error message using Streamlit's session state.

## Setup and Installation

This project is designed to be run from the project root, either within the Dev Container or a local virtual environment. The dependencies for both frontend and backend are installed from the root.

If you are setting up a local environment, follow these steps from the **project root**:
```bash
# Create and activate a virtual environment (e.g., .venv)
# Then install all dependencies
pip install -r backend/requirements.txt && pip install -r frontend/requirements.txt
```

## Environment Variables

The frontend requires environment variables to connect to the backend API and load the necessary data for the UI. These are typically defined in a `.env` file in the project root.

-   `FASTAPI_URL`: The base URL for the backend API (e.g., `http://backend:8000` inside Docker, or `http://localhost:8000` if running locally).
-   `PREDICT_REVENUE_ENDPOINT`: The specific endpoint for predictions (e.g., `/predict/revenue`).
-   `REVENUE_CATEGORY_PATH`: Path to the category encoder file (`.joblib`).
-   `REVENUE_LOCATION_PATH`: Path to the location encoder file (`.joblib`).
-   `REVENUE_PLATFORM_PATH`: Path to the platform encoder file (`.joblib`).
-   `AISLE_IMG`: Path to the aisle image (`.png`).


Refer to the main `README.md` for an example of the `.env` file structure.

## How to Run

1.  **Start the Backend**: Ensure the backend API server is running.

2.  **Start the Frontend**: Open a new terminal and, from the project root, run:
    ```bash
    streamlit run frontend/main.py
    ```

The application will be available in your browser, typically at `http://localhost:8501`.