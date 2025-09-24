# Project 5: Regression Problem - Revenue Prediction

This project implements a machine learning model to solve a regression problem: predicting product revenue. It exposes the model via a web API built with FastAPI and includes a frontend for user interaction.

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
    REVENUE_MODEL_PATH=./resources/revenue/model_ridge.joblib
    REVENUE_SCALER_PATH=./resources/revenue/standard_scaler.joblib
    REVENUE_CATEGORY_PATH=./resources/revenue/category_by_price_dict.joblib
    REVENUE_PLATFORM_PATH=./resources/revenue/platform_by_price_dict.joblib
    REVENUE_LOCATION_PATH=./resources/revenue/location_by_price_dict.joblib
    PREDICT_REVENUE_ENDPOINT=/predict/revenue # API endpoint for predictions
    API_URL=http://127.0.0.1:8000 # Backend URL for local/devcontainer runs
    AISLE_IMG=./resources/images/aisle.png
    ```
    *Note: All model, scaler, and encoder files are expected to be in the `resources/` directory as specified above.*

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

After opening the project in the Dev Container, you can run each service in a separate terminal from the project root.

#### Running the Backend

1.  Open a new terminal in VS Code (which will be at the project root).
2.  Start the FastAPI server:
    ```bash
    uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API will be available at `http://localhost:8000`.

#### API Documentation

Once the backend server is running, you can access the interactive API documentation (provided by Swagger UI) at:
http://localhost:8000/docs

#### Running the Frontend

1.  Open a second terminal in VS Code (which will be at the project root).
2.  Start the Streamlit application:
    ```bash
    streamlit run frontend/main.py
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

## Deployment

This section provides a guide for deploying the application to a production environment using Docker Compose. The key difference from the development setup is that we will use the self-contained Docker images without mounting local volumes.

### Prerequisites

-   A server (e.g., a cloud VM from AWS, GCP, DigitalOcean) with a public IP address.
-   Docker and Docker Compose installed on the server.
-   Git installed on the server.
-   Your firewall configured to allow traffic on the port you will use (e.g., 8501 for Streamlit, or 80/443 if using a reverse proxy).

### Steps

1.  **SSH into your server.**

2.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd proyecto5-problema-regresion-grupo1
    ```

3.  **Create the `.env` file:**
    Create a `.env` file in the project root. The values will be the same as in development. The `API_URL` variable is overridden by the `docker-compose.yml` for the container-to-container communication.
    ```env
    REVENUE_MODEL_PATH=./resources/revenue/model_ridge.joblib
    REVENUE_SCALER_PATH=./resources/revenue/standard_scaler.joblib
    REVENUE_CATEGORY_PATH=./resources/revenue/category_by_price_dict.joblib
    REVENUE_PLATFORM_PATH=./resources/revenue/platform_by_price_dict.joblib
    REVENUE_LOCATION_PATH=./resources/revenue/location_by_price_dict.joblib
    PREDICT_REVENUE_ENDPOINT=/predict/revenue # API endpoint for predictions
    API_URL=http://127.0.0.1:8000 # Not used by Docker Compose, but good to have
    AISLE_IMG=./resources/images/aisle.png
    ```
    *Note: Ensure the `resources/` directory and its contents are on the server.*

4.  **Build and Run with Docker Compose:**
    For production, it's crucial to run the application using the code baked into the images, not the local files. To do this, you can comment out or remove the `volumes` sections from your `docker-compose.yml` file.

    Then, build the images and run the containers in detached mode (`-d`):
    ```bash
    docker-compose up --build -d
    ```

5.  **Access the Application:**
    The frontend application should now be accessible in your web browser at `http://<your-server-ip>:8501`.

### Production Considerations

-   **Security**: For a real production environment, you should not expose the Streamlit port (8501) directly. It's highly recommended to use a reverse proxy like Nginx or Traefik to handle incoming traffic on standard ports (80/443), manage SSL/TLS certificates, and route requests to the Streamlit container.
-   **Backend Exposure**: The backend API port (8000) does not need to be exposed publicly if it's only accessed by the frontend container. In your `docker-compose.yml`, you can remove the `ports` section for the `backend` service to make it only accessible within the Docker network.
-   **Separate Production Config**: A best practice is to have a separate `docker-compose.prod.yml` file that omits the `volumes` and development-only `command` overrides. You would run it with `docker-compose -f docker-compose.prod.yml up --build -d`.