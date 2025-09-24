import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import joblib
import os
from pathlib import Path

# --- Configuración de rutas (debe coincidir con tu .env) ---
# Se define la ruta del proyecto como el directorio padre del directorio donde se encuentra este script
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Se define el directorio del modelo, saliendo del directorio 'backend' y yendo a la ruta especificada
DISCOUNT_MODEL_DIR = PROJECT_ROOT / "resources/discount"
DISCOUNT_MODEL_PATH = DISCOUNT_MODEL_DIR / "discount_model.joblib"


# --- Lógica del modelo (la misma que ya tenías) ---
def train_discount_model():
    """
    Entrena un modelo de regresión para predecir el descuento.
    """
    try:
        df = pd.read_csv("../data/sales_data.csv")
    except FileNotFoundError:
        print(
            "Error: El archivo 'sales_data.csv' no se encontró. Asegúrate de que esté en la carpeta 'data'."
        )
        return None

    df.columns = df.columns.str.lower().str.replace(" ", "_")
    for col in ["product_name", "category", "location", "platform"]:
        if col in df.columns:
            df[col] = df[col].str.strip()

    features = [
        "product_name",
        "category",
        "price",
        "units_sold",
        "location",
        "platform",
    ]
    X = df[features]
    y = df["discount"]

    categorical_features = ["product_name", "category", "location", "platform"]
    numerical_features = ["price", "units_sold"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
            ("num", "passthrough", numerical_features),
        ]
    )

    model_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
        ]
    )

    model_pipeline.fit(X, y)

    return model_pipeline


def save_model(model, path):
    """
    Guarda el modelo entrenado en un archivo .joblib.
    """
    # Aseguramos que el directorio exista
    if not os.path.exists(DISCOUNT_MODEL_DIR):
        os.makedirs(DISCOUNT_MODEL_DIR)

    joblib.dump(model, path)
    print(f"Modelo guardado exitosamente en: {path}")


# --- Proceso principal ---
if __name__ == "__main__":
    print("Iniciando el entrenamiento del modelo de descuento...")

    # Entrenar el modelo
    model = train_discount_model()

    if model:
        # Guardar el modelo en la ruta especificada
        save_model(model, DISCOUNT_MODEL_PATH)
    else:
        print("El modelo no pudo ser entrenado. Por favor, revisa el error anterior.")
