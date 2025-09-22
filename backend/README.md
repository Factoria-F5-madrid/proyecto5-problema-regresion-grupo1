 # Backend - API de Predicción de Ingresos
 
 Este directorio contiene el servicio de backend para el proyecto de predicción de ingresos. Es una aplicación FastAPI que expone un endpoint para predecir los ingresos basándose en el precio y el día.
 
 ## Requisitos Previos
 
 *   Python 3.10+
 *   `pip`
 
 ## Configuración
 
 La aplicación carga su configuración desde variables de entorno. La forma más sencilla de configurarlas es creando un archivo `.env` en este directorio (`backend/`).
 
 Copia y pega el siguiente contenido en tu archivo `backend/.env`:
 
 ```env
 REVENUE_MODEL_PATH=resources/revenue-model_ridge.joblib
 REVENUE_SCALER_PATH=resources/revenue-standard_scaler.joblib
 PREDICT_REVENUE_ENDPOINT=/predict/revenue
 ```
 
 ## Instalación
 
 1.  Navega al directorio `backend`.
 
 2.  Instala los paquetes de Python necesarios:
     ```bash
     pip install -r requirements.txt
     ```
 
 3.  Asegúrate de que los archivos del modelo y del escalador (referenciados en tu archivo `.env`) estén presentes en el directorio `resources`.
 
 ## Ejecución de la Aplicación
 
 Desde el directorio `backend`, ejecuta el siguiente comando para iniciar el servidor de la API:
 
 ```bash
 uvicorn api:app --reload
 ```
 
 La API estará disponible en `http://127.0.0.1:8000`.
 
 ## Documentación de la API
 
 Una vez que el servidor esté en funcionamiento, puedes acceder a la documentación interactiva de la API (Swagger UI) en `http://127.0.0.1:8000/docs`.
 
 ## Endpoint: `/predict/revenue`
 
 *   **Método:** `POST`
 *   **Descripción:** Predice los ingresos basándose en el precio de un producto y el día del mes.
 *   **Cuerpo de la Solicitud:** Un objeto JSON con las siguientes claves:
     *   `Price` (float): El precio del producto. Debe estar entre 1 y 75.
     *   `Day` (float): El día del mes. Debe estar entre 1 y 31.
 
 *   **Ejemplo de Solicitud con `curl`:**
 
     ```bash
     curl -X 'POST' \
       'http://127.0.0.1:8000/predict/revenue' \
       -H 'accept: application/json' \
       -H 'Content-Type: application/json' \
       -d '{
       "Price": 50,
       "Day": 15
     }'
     ```
 
 *   **Ejemplo de Respuesta:**
 
     ```json
     {
       "predicted_revenue": 543.21
     }
     ```
     *(Nota: El valor real dependerá de la predicción del modelo.)*
 
 ## Estructura del Proyecto
 
 ```
 backend/
 ├── resources/
 │   ├── revenue-model_ridge.joblib
 │   └── revenue-standard_scaler.joblib
 ├── models/
 │   └── revenue_model.py
 ├── api.py
 ├── README.md
 └── requirements.txt
 ```
