import streamlit as st
import requests
import joblib
import os
from pathlib import Path
from dotenv import load_dotenv
import datetime

# Define the project root directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="Análisis de Productos",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Esta es una aplicación para predecir ingresos y calcular descuentos."
    },
)

# Load environment variables
load_dotenv()

# --- API Configuration ---
API_URL = os.getenv("API_URL", "http://localhost:8000")
REVENUE_PREDICT_ENDPOINT = os.getenv("REVENUE_PREDICTION_ENDPOINT", "/predict/revenue")
DISCOUNT_PREDICT_ENDPOINT = os.getenv(
    "DISCOUNT_PREDICTION_ENDPOINT", "/predict/discount"
)
METADATA_ENDPOINT = "/metadata"
PRICE_PREDICT_ENDPOINT = os.getenv("PRICE_PREDICTION_ENDPOINT", "/predict/price")

# Define the path to the images
AISLE_IMG = PROJECT_ROOT / os.getenv("AISLE_IMG")


# --- API Functions ---
@st.cache_data(ttl=3600)  # Cache the response for one hour
def get_metadata():
    try:
        response = requests.get(f"{API_URL}{METADATA_ENDPOINT}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(
            f"Error de conexión: Asegúrate de que la API de FastAPI se esté ejecutando en {API_URL}."
        )
        return None
    except requests.exceptions.HTTPError as e:
        st.error(
            f"Ocurrió un error al obtener metadatos de la API: {e}. Revisa que el endpoint {METADATA_ENDPOINT} esté funcionando."
        )
        return None


@st.cache_data(ttl=3600)
def load_list_from_mapping(mapping_file_path):
    try:
        list_mapping = joblib.load(mapping_file_path)
        list_items = sorted([item for item in list_mapping.keys() if item != "Unknown"])
        list_items.append("Unknown")
        return list_items
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo de mapeo en {mapping_file_path}")
        return []


# Load metadata
metadata = get_metadata()
if metadata is None:
    st.stop()

# Load lists from the API metadata
available_products = metadata.get("products", [])
product_info = metadata.get("product_info", {})
available_categories = sorted(metadata.get("categories", []))
available_locations = sorted(metadata.get("locations", []))
available_platforms = sorted(metadata.get("platforms", []))


# --- Init session status ---
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = 0
if 'prediction_error' not in st.session_state:
    st.session_state.last_prediction = None
if "prediction_error" not in st.session_state:
    st.session_state.prediction_error = None
if "last_discount_prediction" not in st.session_state:
    st.session_state.last_discount_prediction = None
if "discount_prediction_error" not in st.session_state:
    st.session_state.discount_prediction_error = None

# --- Title and description ---
st.title("Análisis de suplementos alimenticios")

# --- Widgets ---
tab1, tab2, tab3 = st.tabs(["Predicción de Ingresos", "Predicción de Descuento", "Predicción de precios de suplementos"])

with st.sidebar:
    st.image(str(AISLE_IMG), caption="Supermercado")
    st.markdown("---")
    st.write("Análisis de suplementos alimenticios")

with tab1:
    st.header("Predicción de Ingresos")

    col1, col2 =st.columns([2, 1])

    with col1:
        # Input for Price (range 1 to 75, as in your Pydantic model)
        price = st.slider("Precio ($)", min_value=1.0, max_value=75.0, value=25.0, step=0.5, format="$%.2f")

        # Input for Day (range 1 to 31, as in your Pydantic model)
        day = st.slider("Día del Mes", min_value=1, max_value=31, value=15)

        # Dropdown for Category
        if available_categories:
            category = st.selectbox("Tipo de suplemento", available_categories)
        else:
            st.warning("No se pudieron cargar las categorías. Verifica el archivo de mapeo.")
            category = "" # Default to empty if no categories are loaded

        # Dropdown for Location 
        if available_locations:
            location = st.selectbox("País", available_locations)
        else:
            st.warning("No se pudieron cargar las localizaciones. Verifica el archivo de mapeo.")
            location = "" # Default to empty if no categories are loaded

        # Dropdown for Platform
        if available_platforms:
            platform = st.selectbox("Tienda", available_platforms)
        else:
            st.warning("No se pudieron cargar las tiendas. Verifica el archivo de mapeo.")
            platform = "" # Default to empty if no categories are loaded


        sub_col1, sub_col2 = st.columns([3, 1])


        with sub_col2:
            # --- Prediction Button ---
            if st.button("Predecir Ingresos", use_container_width=True):
        
                if not category:
                    st.error("Por favor, selecciona una categoría.")
                else:
                    # Prepare data to send to the API
                    payload = {
                        "Price": price,
                        "Day": float(day), # Asegúrate de que Day sea float si tu Pydantic lo espera así
                        "Category": category,
                        "Location": location,
                        "Platform": platform
                    }

                    try:
                        # Send the POST request to your FastAPI API
                        response = requests.post(f"{API_URL}{REVENUE_PREDICT_ENDPOINT}", json=payload)
                        response.raise_for_status() # Lanza un error si la solicitud no fue exitosa (4xx o 5xx)

                        # Get and display the prediction
                        prediction_data = response.json()
                        predicted_revenue = prediction_data.get("predicted_revenue")

                        st.session_state.last_prediction = predicted_revenue
                        st.session_state.prediction_error = None

                    except requests.exceptions.ConnectionError:
                        st.session_state.prediction_error = f"Error de conexión: Asegúrate de que la API de FastAPI se esté ejecutando en {API_URL}."
                        st.session_state.last_prediction = None
                    except requests.exceptions.HTTPError as e:
                        error_details = response.json() if response else "No hay detalles"
                        st.session_state.prediction_error = f"Error en la API: {e}. Detalles: {error_details}"
                        st.session_state.last_prediction = None
                    except Exception as e:
                        st.session_state.prediction_error = f"Ocurrió un error inesperado: {e}"
                        st.session_state.last_prediction = None

    with col2:
        if st.session_state.prediction_error:
            st.error(st.session_state.prediction_error)
        elif st.session_state.last_prediction is not None:
            st.success(f"**Última Predicción de Ingresos:** ${st.session_state.last_prediction:,.2f}", )

    

with tab2:
    st.header("Predicción de Descuento")

    # Handle product selection to disable the category
    if "selected_product" not in st.session_state:
        st.session_state.selected_product = None

    selected_product = st.selectbox(
        "Producto", available_products, key="product_name_select"
    )

    # Get the category of the selected product
    if selected_product in product_info:
        product_category = product_info[selected_product].get("category")
        is_category_disabled = True
    else:
        product_category = ""
        is_category_disabled = False

    category_discount = st.selectbox(
        "Categoría",
        available_categories,
        disabled=is_category_disabled,
        index=(
            available_categories.index(product_category)
            if product_category in available_categories
            else 0
        ),
        key="category_discount_select",
    )

    product_info = product_info.get(selected_product, {})
    default_price = product_info.get("avg_price", 0.0)
    default_units = product_info.get("avg_units_sold", 0)

    price_discount = st.number_input(
        "Precio por unidad",
        min_value=1.0,
        value=float(default_price),
        step=0.1,
        key="discount_price",
    )
    units_sold_discount = st.number_input(
        "Unidades Vendidas (históricas)",
        min_value=1,
        value=int(default_units),
        key="discount_units",
    )
    location_discount = st.selectbox(
        "País", available_locations, key="location_discount_select"
    )
    platform_discount = st.selectbox(
        "Tienda", available_platforms, key="platform_discount_select"
    )

    if st.button("Predecir Descuento"):
        payload = {
            "product_name": selected_product,
            "category": category_discount,
            "price": price_discount,
            "units_sold": units_sold_discount,
            "location": location_discount,
            "platform": platform_discount,
        }

        try:
            response = requests.post(
                f"{API_URL}{DISCOUNT_PREDICT_ENDPOINT}", json=payload
            )
            response.raise_for_status()
            prediction_data = response.json()
            st.session_state.last_discount_prediction = prediction_data.get(
                "predicted_discount"
            )
            st.session_state.discount_prediction_error = None
        except requests.exceptions.ConnectionError:
            st.session_state.discount_prediction_error = f"Error de conexión: Asegúrate de que la API de FastAPI se esté ejecutando en {API_URL}."
            st.session_state.last_discount_prediction = None
        except requests.exceptions.HTTPError as e:
            error_details = response.json() if response else "No hay detalles"
            st.session_state.discount_prediction_error = (
                f"Error en la API: {e}. Detalles: {error_details}"
            )
            st.session_state.last_discount_prediction = None
        except Exception as e:
            st.session_state.discount_prediction_error = (
                f"Ocurrió un error inesperado: {e}"
            )
            st.session_state.last_discount_prediction = None

    st.markdown("---")
    if st.session_state.discount_prediction_error:
        st.error(st.session_state.discount_prediction_error)
    elif st.session_state.last_discount_prediction is not None:
        st.success(
            f"**Última Predicción de Descuento:** {st.session_state.last_discount_prediction*100:,.2f}%"
        )

with tab3:
    st.title("📊 Predicción de precios de suplementos")

    # --- Obtener lista de productos desde la API ---
    try:
        response = requests.get(f"{API_URL}/products")
        if response.status_code == 200:
            products = response.json().get("products", [])
        else:
            products = []
    except Exception as e:
        st.error(f"⚠️ No se pudieron cargar los productos: {e}")
        products = []

    # --- Selección de producto ---
    if products:
        product = st.selectbox("Producto:", products)
    else:
        product = st.selectbox("Producto:", ["Ninguno disponible"])

    # --- Selección de fecha ---
    st.subheader("Selecciona la fecha")
    today = datetime.date.today()
    year = st.number_input("Año", min_value=2023, max_value=2100, value=today.year, step=1)
    month = st.selectbox("Mes", list(range(1, 13)), index=today.month - 1)

    # --- Botón para predecir ---
    if st.button("🔮 Predecir precio"):
        try:
            response = requests.get(
                f"{API_URL}{PRICE_PREDICT_ENDPOINT}",
                params={
                    "product": product,
                    "year": int(year),
                    "month": int(month)
            
            }
            )

            if response.status_code == 200:
                result = response.json()
                st.success(
                    f"💰 Precio estimado para **{product}** en {month}/{year}: **${result['predicted_price']}**"
                )
            else:
                st.error(f"❌ Error en la API: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"⚠️ No se pudo conectar con la API: {e}")