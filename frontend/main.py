import streamlit as st
import requests
import joblib  # Para cargar el mapeo y obtener las categorías reales
import os  # Para acceder a la ruta del mapeo desde .env
from pathlib import Path
from dotenv import load_dotenv

# Define the project root directory. This makes path handling robust regardless of where the script is run from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Cargar variables de entorno
load_dotenv()

# --- Configuración de la API ---
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
PREDICT_REVENUE_ENDPOINT = os.getenv("PREDICT_REVENUE_ENDPOINT", "/predict/revenue")
PREDICT_DISCOUNT_ENDPOINT = os.getenv(
    "DISCOUNT_PREDICTION_ENDPOINT", "/predict/discount"
)
DATA_METADATA_ENDPOINT = os.getenv("DATA_METADATA_ENDPOINT", "/metadata")

AISLE_IMG = PROJECT_ROOT / os.getenv("AISLE_IMG")


# --- Funciones para cargar datos ---
@st.cache_data
def load_list_from_mapping(mapping_file_path):
    try:
        list_mapping = joblib.load(mapping_file_path)
        list_data = sorted([cat for cat in list_mapping.keys() if cat != "Unknown"])
        list_data.append("Unknown")
        return list_data
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo de mapeo en {mapping_file_path}")
        return []
    except Exception as e:
        st.error(f"Error al cargar el archivo de mapeo: {e}")
        return []


@st.cache_data
def get_product_data():
    try:
        response = requests.get(f"{API_URL}{DATA_METADATA_ENDPOINT}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(
            f"Error de conexión: Asegúrate de que la API de FastAPI se esté ejecutando en {API_URL}."
        )
        return None
    except Exception as e:
        st.error(f"Ocurrió un error al obtener metadatos de la API: {e}")
        return None


# Cargar las categorías y otros datos al inicio
CATEGORY_MAP = PROJECT_ROOT / os.getenv("REVENUE_CATEGORY_PATH", "")
LOCATION_MAP = PROJECT_ROOT / os.getenv("REVENUE_LOCATION_PATH", "")
PLATFORM_MAP = PROJECT_ROOT / os.getenv("REVENUE_PLATFORM_PATH", "")

available_categories = load_list_from_mapping(CATEGORY_MAP)
available_locations = load_list_from_mapping(LOCATION_MAP)
available_platforms = load_list_from_mapping(PLATFORM_MAP)
product_metadata = get_product_data()

# --- Configuración de la interfaz ---
st.set_page_config(
    page_title="Análisis de Productos",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Esta es una aplicación para predecir ingresos y calcular descuentos."
    },
)

st.title("Análisis de suplementos alimenticios")

# --- Inicialización del estado de sesión ---
if "last_revenue_prediction" not in st.session_state:
    st.session_state.last_revenue_prediction = None
if "revenue_prediction_error" not in st.session_state:
    st.session_state.revenue_prediction_error = None
if "last_discount_prediction" not in st.session_state:
    st.session_state.last_discount_prediction = None
if "discount_prediction_error" not in st.session_state:
    st.session_state.discount_prediction_error = None

# --- Widgets ---
tab1, tab2 = st.tabs(["Predicción de Ingresos", "Predicción de Descuento"])

with st.sidebar:
    st.image(str(AISLE_IMG), caption="Supermercado")
    st.markdown("---")
    st.write("Análisis de suplementos alimenticios")

with tab1:
    st.header("Predicción de Ingresos")
    price = st.slider(
        "Precio ($)",
        min_value=1.0,
        max_value=75.0,
        value=25.0,
        step=0.5,
        format="$%.2f",
    )
    day = st.slider("Día del Mes", min_value=1, max_value=31, value=15)
    category = (
        st.selectbox("Tipo de suplemento", available_categories)
        if available_categories
        else ""
    )
    location = st.selectbox("País", available_locations) if available_locations else ""
    platform = (
        st.selectbox("Tienda", available_platforms) if available_platforms else ""
    )

    if st.button("Predecir Ingresos"):
        payload = {
            "Price": price,
            "Day": float(day),
            "Category": category,
            "Location": location,
            "Platform": platform,
        }
        try:
            response = requests.post(
                f"{API_URL}{PREDICT_REVENUE_ENDPOINT}", json=payload
            )
            response.raise_for_status()
            prediction_data = response.json()
            st.session_state.last_revenue_prediction = prediction_data.get(
                "predicted_revenue"
            )
            st.session_state.revenue_prediction_error = None
        except requests.exceptions.ConnectionError:
            st.session_state.revenue_prediction_error = "Error de conexión: Asegúrate de que la API de FastAPI se esté ejecutando."
            st.session_state.last_revenue_prediction = None
        except Exception as e:
            st.session_state.revenue_prediction_error = f"Ocurrió un error: {e}"
            st.session_state.last_revenue_prediction = None

    st.markdown("---")
    if st.session_state.revenue_prediction_error:
        st.error(st.session_state.revenue_prediction_error)
    elif st.session_state.last_revenue_prediction is not None:
        st.success(
            f"**Última Predicción de Ingresos:** ${st.session_state.last_revenue_prediction:,.2f}"
        )

with tab2:
    st.header("Predicción de Descuento")
    if product_metadata and "products" in product_metadata:
        product_list = product_metadata.get("products", [])

        selected_product = st.selectbox(
            "Producto", product_list, key="discount_product"
        )

        product_info = product_metadata.get("product_info", {}).get(
            selected_product, {}
        )
        default_category = product_info.get("category", "")
        default_price = product_info.get("avg_price", 0.0)
        default_units = product_info.get("avg_units_sold", 0)

        selected_category = st.selectbox(
            "Categoría",
            product_metadata.get("categories", []),
            index=(
                product_metadata.get("categories", []).index(default_category)
                if default_category in product_metadata.get("categories", [])
                else 0
            ),
            key="discount_category",
        )
        selected_price = st.number_input(
            "Precio por unidad",
            min_value=1.0,
            value=float(default_price),
            step=0.1,
            key="discount_price",
        )
        selected_units_sold = st.number_input(
            "Unidades Vendidas (históricas)",
            min_value=1,
            value=int(default_units),
            key="discount_units",
        )
        selected_location = st.selectbox(
            "Ubicación", product_metadata.get("locations", []), key="discount_location"
        )
        selected_platform = st.selectbox(
            "Plataforma", product_metadata.get("platforms", []), key="discount_platform"
        )

        if st.button("Predecir Descuento"):
            payload = {
                "product_name": selected_product,
                "category": selected_category,
                "price": selected_price,
                "units_sold": selected_units_sold,
                "location": selected_location,
                "platform": selected_platform,
            }
            try:
                response = requests.post(
                    f"{API_URL}{PREDICT_DISCOUNT_ENDPOINT}", json=payload
                )
                response.raise_for_status()
                predicted_discount = response.json().get("predicted_discount")
                st.session_state.last_discount_prediction = predicted_discount
                st.session_state.discount_prediction_error = None
            except requests.exceptions.ConnectionError:
                st.session_state.discount_prediction_error = "Error de conexión: Asegúrate de que la API de FastAPI se esté ejecutando."
                st.session_state.last_discount_prediction = None
            except Exception as e:
                st.session_state.discount_prediction_error = f"Ocurrió un error: {e}"
                st.session_state.last_discount_prediction = None

        st.markdown("---")
        if st.session_state.discount_prediction_error:
            st.error(st.session_state.discount_prediction_error)
        elif st.session_state.last_discount_prediction is not None:
            st.success(
                f"**Última Predicción de Descuento:** {st.session_state.last_discount_prediction*100:.2f}%"
            )
    else:
        st.warning(
            "No se pudo obtener la lista de productos de la API. Revisa que el endpoint `/metadata` esté funcionando."
        )
