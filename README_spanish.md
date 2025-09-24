# Proyecto de Predicción de Descuentos e Ingresos

Este proyecto consta de dos partes principales: un **backend** construido con **FastAPI** y un **frontend** desarrollado con **Streamlit**.  
Juntos, permiten predecir ingresos futuros y calcular un descuento predicho para diferentes productos, basándose en un modelo de regresión.

---

## 1. Configuración del Proyecto

### Requisitos

Asegúrate de tener **Python 3.8** o superior instalado.

### Entorno Virtual

Es muy recomendable crear y activar un entorno virtual para gestionar las dependencias del proyecto de forma aislada.

```bash
# Crea un entorno virtual
python -m venv .venv

# Activa el entorno virtual (Linux/macOS)
source .venv/bin/activate

# Activa el entorno virtual (Windows)
.\.venv\Scripts\activate
```

### Instalación de Dependencias

Una vez activado el entorno, instala todas las bibliotecas necesarias:

```
pip install -r requirements.txt
```

### Variables de Entorno

El proyecto utiliza un archivo .env para las rutas y URLs.
Asegúrate de tener este archivo en la raíz del proyecto con la siguiente configuración:

```
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
```

## 2. Cómo Levantar la Aplicación

### Paso 1: Levantar el Backend

El backend de FastAPI debe estar en funcionamiento para que el frontend pueda comunicarse con él.
Abre una terminal en la raíz del proyecto y ejecuta:

```
uvicorn backend.api:app --reload
```

### Paso 2: Levantar el Frontend

Con el backend en ejecución, abre una segunda terminal, navega a la raíz del proyecto y ejecuta:

```
streamlit run frontend/main.py
```

## 3. Funcionamiento de la Predicción de Descuentos

La aplicación utiliza un modelo de machine learning de regresión para predecir el descuento.
El modelo fue entrenado usando un RandomForestRegressor, y su función es analizar datos históricos de ventas para encontrar correlaciones entre variables.

### Variables de Entrada

El modelo toma en cuenta los siguientes factores para hacer la predicción:

- Producto: El tipo de suplemento.

- Categoría: La categoría a la que pertenece el producto.

- Precio: El costo por unidad.

- Unidades Vendidas: El volumen de ventas.

- Ubicación: El país de venta.

- Plataforma: La tienda online.

## ¿Qué hace el modelo?

Basándose en estas variables, el modelo te da un descuento predicho.
Este valor refleja la correlación que el modelo encontró en los datos históricos.

Si los descuentos predichos son bajos, significa que las correlaciones eran débiles o los descuentos históricos eran pequeños.

La predicción es un reflejo directo de los patrones que el modelo aprendió de esos datos.
