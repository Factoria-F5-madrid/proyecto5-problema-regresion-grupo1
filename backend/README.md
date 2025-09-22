# Backend API - Revenue Prediction

This directory contains the FastAPI application that serves the revenue prediction model.

## How it Works

The API receives product data (`Price`, `Day`, `Category`, `Location`, `Platform`), preprocesses it using a saved scaler and encoders, and then uses a pre-trained regression model to predict the revenue.

## Running the Server

From the `backend` directory, run the following command to start the Uvicorn server:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reloading when you make changes to the code. The server will be accessible at `http://localhost:8000`.

## API Endpoint

### Predict Revenue

-   **URL:** `/predict/revenue` (or as defined in `PREDICT_REVENUE_ENDPOINT` env var)
-   **Method:** `POST`
-   **Description:** Predicts revenue based on product features.

#### Request Body

The request body should be a JSON object with the following structure:

```json
{
  "Price": 50.5,
  "Day": 15,
  "Category": "Vitamin",
  "Location": "USA",
  "Platform": "Amazon"
}
```

-   `Price`: `float` (must be between 1 and 75)
-   `Day`: `float` (must be between 1 and 31)
-   `Category`: `string` (e.g., "Vitamin", "Herbs")
-   `Location`: `string` (e.g., "USA", "UK")
-   `Platform`: `string` (e.g., "Amazon", "Walmart")

#### Example `curl` Request

```bash
curl -X 'POST' \
  'http://localhost:8000/predict/revenue' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "Price": 50.5,
  "Day": 15,
  "Category": "Vitamin",
  "Location": "USA",
  "Platform": "Amazon"
}'
```

#### Success Response

-   **Code:** `200 OK`
-   **Content:**

```json
{
  "predicted_revenue": 12345.67
}
```

## Environment Variables

The application relies on a `.env` file in the project root to load necessary configurations. See the main `README.md` for details on setting up this file.