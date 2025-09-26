import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ===============================
# 1. Preparar datos
# ===============================
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y transforma el dataset original.
    Asegura que Date sea datetime y crea columnas de Año y Mes.
    """
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    return df


# ===============================
# 2. Crear features
# ===============================
def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea variables adicionales (seno/coseno estacionales, índice de tiempo,
    rezagos, medias móviles, etc.).
    """
    df = df.copy()

    # Índices de tiempo
    df["Years_From_Start"] = df["Year"] - df["Year"].min()
    df["Time_Index"] = (df["Years_From_Start"] * 12) + df["Month"]
    df["Time_Index_Squared"] = df["Time_Index"] ** 2

    # Codificación estacional
    df["Month_sin"] = np.sin(2 * np.pi * df["Month"] / 12)
    df["Month_cos"] = np.cos(2 * np.pi * df["Month"] / 12)

    # Media mensual por producto
    df_features = (
        df.groupby(["Product_Name", "Year", "Month"])["Price"]
        .mean()
        .reset_index()
        .rename(columns={"Price": "Price_Avg"})
    )

    # Añadir de nuevo las features temporales
    df_features["Years_From_Start"] = df_features["Year"] - df_features["Year"].min()
    df_features["Time_Index"] = (df_features["Years_From_Start"] * 12) + df_features["Month"]
    df_features["Time_Index_Squared"] = df_features["Time_Index"] ** 2
    df_features["Month_sin"] = np.sin(2 * np.pi * df_features["Month"] / 12)
    df_features["Month_cos"] = np.cos(2 * np.pi * df_features["Month"] / 12)

    # Rezagos y medias móviles por producto
    df_features = df_features.sort_values(["Product_Name", "Year", "Month"])
    df_features["Price_Lag_1"] = df_features.groupby("Product_Name")["Price_Avg"].shift(1)
    df_features["Price_Lag_3"] = df_features.groupby("Product_Name")["Price_Avg"].shift(3)
    df_features["Price_Lag_12"] = df_features.groupby("Product_Name")["Price_Avg"].shift(12)

    df_features["Price_MA_6"] = (
        df_features.groupby("Product_Name")["Price_Avg"].transform(lambda x: x.rolling(6).mean())
    )
    df_features["Price_MA_12"] = (
        df_features.groupby("Product_Name")["Price_Avg"].transform(lambda x: x.rolling(12).mean())
    )

    df_features = df_features.dropna().reset_index(drop=True)
    return df_features


# ===============================
# 3. Entrenar modelos
# ===============================
def train_models(df_features: pd.DataFrame) -> dict:
    """
    Entrena un modelo de regresión lineal para cada producto.
    Devuelve un diccionario {producto: modelo}.
    """
    models = {}
    feature_cols = [
        "Year", "Month", "Month_sin", "Month_cos",
        "Years_From_Start", "Time_Index", "Time_Index_Squared",
        "Price_Lag_1", "Price_Lag_3", "Price_Lag_12",
        "Price_MA_6", "Price_MA_12"
    ]

    for product in df_features["Product_Name"].unique():
        subset = df_features[df_features["Product_Name"] == product]

        X = subset[feature_cols]
        y = subset["Price_Avg"]

        model = LinearRegression()
        model.fit(X, y)
        models[product] = model

    return models
