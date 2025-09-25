from pathlib import Path
import streamlit as st
import requests
import joblib # Para cargar el mapeo y obtener las categorías reales
import os # Para acceder a la ruta del mapeo desde .env
from dotenv import load_dotenv # Para cargar las variables de entorno
import datetime # para el Tab3 

# Define the project root directory. api.py is in backend/, so root is one level up.
# This makes path handling robust regardless of where the script is run from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(
    page_title="Análisis de Productos",
    layout="wide", # Opcional: Esto hace que el contenido principal ocupe todo el ancho disponible
    initial_sidebar_state="expanded", # Opcional: Hace que la barra lateral esté expandida por defecto
    menu_items={
        'About': "Esta es una aplicación para predecir ingresos y calcular descuentos."
    }
)

# Cargar variables de entorno (igual que en FastAPI, para saber la URL del backend)
load_dotenv()

# --- Configuración de la API ---
# URL base de tu API de FastAPI (asegúrate de que coincida con donde se ejecuta tu FastAPI)
# Si FastAPI se ejecuta localmente en el puerto 8000, será:
API_URL = os.getenv("API_URL", "http://backend:8000")
PREDICT_ENDPOINT = os.getenv("PREDICT_REVENUE_ENDPOINT", "/predict/revenue") # Usa el mismo endpoint que en FastAPI
AISLE_IMG = PROJECT_ROOT / os.getenv("AISLE_IMG")

# Ruta al archivo de mapeo para obtener la lista de categorías (sin '__UNKNOWN__')
# Asegúrate de que esta ruta sea accesible desde donde ejecutas Streamlit
CATEGORY_MAP = PROJECT_ROOT / os.getenv("REVENUE_CATEGORY_PATH")
LOCATION_MAP = PROJECT_ROOT / os.getenv("REVENUE_LOCATION_PATH")
PLATFORM_MAP = PROJECT_ROOT / os.getenv("REVENUE_PLATFORM_PATH")

# --- Función para cargar las categorías disponibles ---
@st.cache_data # Cachea la función para que no se ejecute cada vez que Streamlit se actualiza
def load_list_from_mapping(mapping_file_path):
    try:
        list_mapping = joblib.load(mapping_file_path)
        # Filtra la clave 'Unknown' si existe y devuelve las categorías como una lista
        list = sorted([cat for cat in list_mapping.keys() if cat != 'Unknown'])
        list.append('Unknown')
        return list
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo de mapeo de categorías en {mapping_file_path}")
        return []
    except Exception as e:
        st.error(f"Error al cargar las categorías: {e}")
        return []

# Cargar las categorías al inicio
available_categories = load_list_from_mapping(CATEGORY_MAP)
if not available_categories:
    st.stop() # Stop app

available_locations = load_list_from_mapping(LOCATION_MAP)
if not available_locations:
    st.stop() # Stop app

available_platforms = load_list_from_mapping(PLATFORM_MAP)
if not available_platforms:
    st.stop() # Stop app

# --- Title and description ---
st.title("Análisis de suplementos alimenticios")

# --- Init session status ---
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None
if 'prediction_error' not in st.session_state:
    st.session_state.prediction_error = None

# --- Widgets  ---
tab1, tab2, tab3 = st.tabs(["Predicción de Ingresos", "Otros", "Predicción de precios de suplementos"])

with st.sidebar:
    st.image(AISLE_IMG, caption="Supermercado")
    st.markdown("---") # Separador
    st.write("Análisis de suplementos alimenticios")
    # Aquí puedes añadir más widgets o texto que quieras en la barra lateral
    # Por ejemplo: st.help(st.selectbox)


with tab1:
    st.header("Predicción de Ingresos")

    # Input para Price (rango de 1 a 75, como en tu modelo Pydantic)
    price = st.slider("Precio ($)", min_value=1.0, max_value=75.0, value=25.0, step=0.5, format="$%.2f")

    # Input para Day (rango de 1 a 31, como en tu modelo Pydantic)
    day = st.slider("Día del Mes", min_value=1, max_value=31, value=15)

    # Dropdown para Category
    if available_categories:
        category = st.selectbox("Tipo de suplemento", available_categories)
    else:
        st.warning("No se pudieron cargar las categorías. Verifica el archivo de mapeo.")
        category = "" # Default to empty if no categories are loaded

    # Dropdown para Location 
    if available_locations:
        location = st.selectbox("País", available_locations)
    else:
        st.warning("No se pudieron cargar las localizaciones. Verifica el archivo de mapeo.")
        location = "" # Default to empty if no categories are loaded

    # Dropdown para Platform
    if available_platforms:
        platform = st.selectbox("Tienda", available_platforms)
    else:
        st.warning("No se pudieron cargar las tiendas. Verifica el archivo de mapeo.")
        platform = "" # Default to empty if no categories are loaded


    # --- Botón de Predicción ---
    if st.button("Predecir Ingresos"):
        if not category:
            st.error("Por favor, selecciona una categoría.")
        else:
            # Preparar los datos para enviar a la API
            payload = {
                "Price": price,
                "Day": float(day), # Asegúrate de que Day sea float si tu Pydantic lo espera así
                "Category": category,
                "Location": location,
                "Platform": platform
            }

            try:
                # Enviar la solicitud POST a tu API de FastAPI
                response = requests.post(f"{API_URL}{PREDICT_ENDPOINT}", json=payload)
                response.raise_for_status() # Lanza un error si la solicitud no fue exitosa (4xx o 5xx)

                # Obtener y mostrar la predicción
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
            
    # --- Mostrar el último resultado (persistente) ---
    st.markdown("---") # Separador visual

    if st.session_state.prediction_error:
        st.error(st.session_state.prediction_error)
    elif st.session_state.last_prediction is not None:
        st.success(f"**Última Predicción de Ingresos:** ${st.session_state.last_prediction:,.2f}")

with tab2:
    st.header("Otros")
    st.write("Esta sección se utilizará para otros calculos Se pueden hacer tantas pestañas como sea necesario.")

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
                f"{API_URL}/predict",
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
