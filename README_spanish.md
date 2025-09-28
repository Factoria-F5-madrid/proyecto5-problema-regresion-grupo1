# Proyecto de Predicción de Ingresos y Descuentos

Este proyecto consta de dos partes principales: un **backend** construido con
**FastAPI** y un **frontend** desarrollado con **Streamlit**.\
Juntos, permiten predecir ingresos futuros, calcular un
descuento predicho y pronosticar precios futuros para diferentes productos.

## Autores

-   Jimena Sonaly Flores Ticona
-   Bunty Nanwani Nanwani
-   Noé Moisés Guamán Álvarez
-   Óscar Rodríguez González

## Estructura del Proyecto
-   `.devcontainer/`: Contiene la configuración para el contenedor de desarrollo, asegurando un entorno de desarrollo consistente.
-   `backend/`: La aplicación FastAPI que sirve el modelo de machine learning. Consulta `backend/README.md` para más detalles.
-   `frontend/`: La interfaz de usuario para interactuar con la API de predicción. Consulta `frontend/README.md` para más detalles.
-   `resources/`: Recursos compartidos utilizados tanto por el backend como por el frontend. Esto incluye modelos de machine learning, codificadores e imágenes.
-   `docker-compose.yml`: Define los servicios para el desarrollo, incluyendo la recarga en vivo.
-   `.env`: Variables de entorno para la configuración (necesitarás crear este archivo).
------------------------------------------------------------------------

## 1. Configuración del Proyecto

### Requisitos

Asegúrate de tener **Python 3.8** o superior instalado.

### Uso de Dev Containers (Recomendado)

Este proyecto está configurado para ejecutarse dentro de un Dev Container de VS Code. Esta es la forma más sencilla de comenzar, ya que configura automáticamente el entorno e instala todas las dependencias.

**Requisitos previos:**
-   [Visual Studio Code](https://code.visualstudio.com/)
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
-   La extensión [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) para VS Code.

**Pasos:**

1.  Clona el repositorio y abre la carpeta del proyecto en VS Code.
2.  Aparecerá una notificación en la esquina inferior derecha preguntando si deseas **"Reabrir en Contenedor"** ("Reopen in Container"). Haz clic en ella.
3.  VS Code construirá el contenedor e instalará todas las dependencias de Python automáticamente. Esto puede tardar unos minutos la primera vez.
4.  Una vez que el contenedor esté en funcionamiento, puedes continuar con la sección "Cómo Ejecutar la Aplicación". Todos los comandos deben ejecutarse dentro de la terminal integrada de VS Code.


### Entorno Virtual

Se recomienda encarecidamente crear y activar un entorno virtual para
gestionar las dependencias del proyecto de forma aislada.

```bash
# Crear un entorno virtual
python -m venv .venv

# Activar el entorno virtual (Linux/macOS)
source .venv/bin/activate

# Activar el entorno virtual (Windows)
.\.venv\Scripts\activate
```

### Instalación de Dependencias

Una vez que el entorno esté activado, instala todas las librerías necesarias:

    pip install -r requirements.txt

### Variables de Entorno

El proyecto utiliza un archivo `.env` para rutas y URLs.\
Asegúrate de tener este archivo en la raíz del proyecto con la
siguiente configuración:

    # URL raíz de la API
    API_URL=http://127.0.0.1:8000

    # Ruta de los datos
    DATA_PATH=./resources/data/Supplement_Sales_Weekly_Expanded.csv

    # Modelo de ingresos
    REVENUE_MODEL_PATH=./resources/revenue/model_ridge.joblib
    REVENUE_SCALER_PATH=./resources/revenue/standard_scaler.joblib
    REVENUE_CATEGORY_PATH=./resources/revenue/category_by_price_dict.joblib
    REVENUE_PLATFORM_PATH=./resources/revenue/platform_by_price_dict.joblib
    REVENUE_LOCATION_PATH=./resources/revenue/location_by_price_dict.joblib
    REVENUE_PREDICTION_ENDPOINT=/predict/revenue

    # Modelo de descuento
    DISCOUNT_MODEL_PATH=./resources/discount/discount_model.joblib
    DISCOUNT_PREDICTION_ENDPOINT=/predict/discount

    # Modelo de precios
    PRICE_PREDICTION_ENDPOINT=/predict/price

    # Streamlit
    AISLE_IMG=./resources/images/aisle.png

## 2. Cómo Ejecutar la Aplicación

### Paso 1: Iniciar el Backend

El backend de FastAPI debe estar en ejecución para que el frontend pueda comunicarse
con él.\
Abre una terminal en la raíz del proyecto y ejecuta:

    uvicorn backend.api:app --reload

### Paso 2: Iniciar el Frontend

Con el backend en ejecución, abre una segunda terminal, navega a la
raíz del proyecto y ejecuta:

    streamlit run frontend/main.py

## 3. Cómo Funciona la Predicción
La aplicación utiliza tres modelos de machine learning diferentes para proporcionar predicciones.

### Modelo 1: Predicción de Ingresos
Este modelo predice los ingresos futuros basándose en un conjunto de características de entrada.

*   **Tipo de Modelo**: Regresión Ridge (`model_ridge.joblib`)
*   **Entradas**:
    *   Precio: El costo por unidad.
    *   Día: El día del mes.
    *   Categoría: La categoría del producto.
    *   Ubicación: El país de venta.
    *   Plataforma: La tienda en línea.
*   **Salida**: Una cantidad de ingresos predicha.

### Modelo 2: Predicción de Descuento
Este modelo analiza datos históricos de ventas para sugerir un descuento para un producto.

*   **Tipo de Modelo**: Random Forest Regressor (`discount_model.joblib`)
*   **Entradas**:
    *   Producto: El tipo de suplemento.
    *   Categoría: La categoría a la que pertenece el producto.
    *   Precio: El costo por unidad.
    *   Unidades Vendidas: El volumen histórico de ventas.
    *   Ubicación: El país de venta.
    *   Plataforma: La tienda en línea.
*   **Salida**: Un porcentaje de descuento predicho. Este valor refleja las correlaciones que el modelo encontró en los datos históricos. Si los descuentos predichos son bajos, sugiere que los descuentos históricos fueron pequeños o las correlaciones débiles.

### Modelo 3: Predicción de Precios
Este modelo utiliza análisis de series temporales para pronosticar el precio futuro de un producto específico. Se entrena un modelo separado para cada producto cuando se inicia la API.

*   **Tipo de Modelo**: Gradient Boosting Regressor (uno por producto)
*   **Entradas**:
    *   Producto: El nombre del suplemento.
    *   Año: El año objetivo para el pronóstico.
    *   Mes: El mes objetivo para el pronóstico.
*   **Salida**: El precio promedio predicho para el producto en el mes y año dados.