# Project 5: Regression Problem - Revenue Prediction

This project implements a machine learning model to solve a regression problem: predicting product revenue. It exposes the model via a web API built with FastAPI and includes a frontend for user interaction.

## Project Structure

-   `.devcontainer/`: Contains configuration for the development container, ensuring a consistent development environment.
-   `backend/`: The FastAPI application that serves the machine learning model.
-   `frontend/`: The user interface for interacting with the prediction API.

## Getting Started

This project is configured to run inside a VS Code Development Container, which simplifies setup and ensures a consistent environment.

### Prerequisites

-   Docker
-   Visual Studio Code
-   Dev Containers extension for VS Code.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd proyecto5-problema-regresion-grupo1
    ```

2.  **Create Environment File:**
    The application requires environment variables to locate the model files. Create a `.env` file in the project root (`/workspaces/proyecto5-problema-regresion-grupo1`) and add the following, adjusting the paths if necessary:

    ```env
    REVENUE_MODEL_PATH=./models/revenue_model.joblib
    REVENUE_SCALER_PATH=./models/revenue_scaler.joblib
    REVENUE_CATEGORY_PATH=./models/revenue_category_encoder.joblib
    REVENUE_PLATFORM_PATH=./models/revenue_platform_encoder.joblib
    REVENUE_LOCATION_PATH=./models/revenue_location_encoder.joblib
    PREDICT_REVENUE_ENDPOINT=/predict/revenue
    FASTAPI_URL=http://localhost:8000
    ```
    *Note: The model, scaler, and encoder files should be placed in a `models/` directory in the project root.*

3.  **Open in Dev Container:**
    Open the project folder in VS Code. You should see a prompt in the bottom-right corner asking to "Reopen in Container". Click it. This will build the Docker container and install all dependencies from `backend/requirements.txt` and `frontend/requirements.txt`.

### Alternative: Local Setup with Virtual Environment

If you prefer not to use Docker or Dev Containers, you can set up the project locally using a Python virtual environment.

#### Prerequisites

-   Python 3.12 or later.
-   `pip` (Python's package installer).

#### Installation & Setup

1.  **Follow steps 1 and 2 from the main `Installation & Setup` section** to clone the repository and create the `.env` file.

2.  **Create and activate a virtual environment:**
    From the project's root directory, run:

    ```bash
    # Create the virtual environment
    python3 -m venv .venv

    # Activate it (Linux/macOS)
    source .venv/bin/activate

    # Or on Windows (Command Prompt)
    # .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    With the virtual environment activated, install the required packages for both the backend and frontend:
    ```bash
    pip install -r backend/requirements.txt && pip install -r frontend/requirements.txt
    ```

Once set up, you can run the services as described in `Usage > Method 1: Running in Dev Container`.

## Usage

This project can be run in two ways: inside the VS Code Dev Container (recommended for development) or using Docker Compose.

### Method 1: Running in Dev Container

After opening the project in the Dev Container, you can run each service in a separate terminal.

#### Running the Backend

1.  Open a new terminal in VS Code (which will be inside the dev container).
2.  Navigate to the backend directory and start the server:
    ```bash
    cd backend
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API will be available at `http://localhost:8000`.

#### API Documentation

Once the backend server is running, you can access the interactive API documentation (provided by Swagger UI) at:
http://localhost:8000/docs

#### Running the Frontend

1.  Open a second terminal in VS Code.
2.  Navigate to the frontend directory and start the application:
    ```bash
    cd frontend
    streamlit run main.py
    ```
    The frontend will be available at `http://localhost:8501`.

### Method 2: Running with Docker Compose

This method uses `docker-compose.yml` to build the Docker images from the `Dockerfile`s and run the entire application stack.

1.  **Build Images and Run Containers:**
    From the project's root directory, run:
    ```bash
    docker-compose up --build
    ```
    This command builds the `backend` and `frontend` images using their respective `Dockerfile`s and starts the containers. If you only want to build the images without running them, use `docker-compose build`.

2.  **Access the Services:**
    -   **Backend API:** http://localhost:8000
    -   **Frontend App:** http://localhost:8501

3.  **Stop the Application:**
    Press `Ctrl+C` in the terminal, then run `docker-compose down` to stop and remove the containers.