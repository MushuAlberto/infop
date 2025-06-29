import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard Ejecutivo de Operaciones",
    page_icon="📊",
    layout="wide"
)

# --- Título Principal ---
st.title("📊 Dashboard Ejecutivo de Operaciones")
st.markdown("### Análisis Detallado de Operaciones")

# --- Configuración de Nombres de Columnas (¡AJUSTA ESTAS SI TUS NOMBRES SON DIFERENTES!) ---
VOLUME_COLUMN = 'TONELAJE'           # Columna que contiene el volumen/tonelaje.
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE' # Columna que contiene los nombres de las empresas de transporte.
FECHA_COLUMN = 'FECHA'              # Columna que contiene las fechas.
PRODUCTO_COLUMN = 'PRODUCTO'        # Columna que contiene los nombres de los productos.
DESTINO_COLUMN = 'DESTINO'          # Columna que contiene los destinos.
# Columna para identificar guías únicas. Si no hay una columna específica,
# se contarán las filas por producto. Si es así, déjala como None.
GUIA_COLUMN_IDENTIFIER = None       
# Lista de columnas que indican la presencia de una regulación para un producto.
REGULACION_COLUMNS_TO_COUNT = ['REGULACION 1', 'REGULACION 2', 'REGULACION 3'] 

# --- Mapeo de Nombres de Empresas ---
empresa_mapping = {
    "JORQUERA TRANSPORTE S. A.": "JORQUERA TRANSPORTE S. A.", "JORQUERA TRANSPORTE S A": "JORQUERA TRANSPORTE S. A.",
    "MINING SERVICES AND DERIVATES": "M S & D SPA", "MINING SERVICES AND DERIVATES SPA": "M S & D SPA",
    "M S AND D": "M S & D SPA", "M S AND D SPA": "M S & D SPA", "MSANDD SPA": "M S & D SPA",
    "M S D": "M S & D SPA", "M S D SPA": "M S & D SPA", "M S & D": "M S & D SPA", "MS&D SPA": "M S & D SPA",
    "M AND Q SPA": "M&Q SPA", "M AND Q": "M&Q SPA", "M Q SPA": "M&Q SPA", "MQ SPA": "M&Q SPA",
    "MANDQ SPA": "M&Q SPA", "MINING AND QUARRYING SPA": "M&Q SPA", "MINING AND QUARRYNG SPA": "M&Q SPA",
    "AG SERVICE SPA": "AG SERVICES SPA", "AG SERVICES SPA": "AG SERVICES SPA",
    "COSEDUCAM S A": "COSEDUCAM S A", "COSEDUCAM": "COSEDUCAM S A"
}

# --- Carga de Datos ---
df = None
uploaded_file = st.sidebar.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("Archivo cargado correctamente!")

        # --- Preprocesamiento de Datos ---
        # 1. Convertir FECHA de forma robusta
        if FECHA_COLUMN not in df.columns:
            st.error(f"Error: No se encontró la columna '{FECHA_COLUMN}'. Por favor, asegúrate de que exista y se llame exactamente '{FECHA_COLUMN}'.")
            st.stop()
        
        # Primero, convierte la columna 'FECHA' a string para asegurar consistencia
        df[FECHA_COLUMN] = df[FECHA_COLUMN].astype(str)
        # Luego, intenta convertir a datetime
        df[FECHA_COLUMN] = pd.to_datetime(df[FECHA_COLUMN], errors='coerce') # Usamos parseo automático más robusto de pandas

        # Validamos que después de la conversión, la columna tenga el tipo correcto
        if not pd.api.types.is_datetime64_any_dtype(df[FECHA_COLUMN]):
            st.error(f"Error: La columna '{FECHA_COLUMN}' no pudo ser convertida a un tipo de fecha y hora. Verifica el formato de tus fechas en el archivo Excel. Un formato esperado es DD-MM-YYYY o YYYY-MM-DD.")
            st.stop()
            
        # Eliminar filas donde la conversión de fecha falló y dejó NaN
        df.dropna(subset=[FECHA_COLUMN], inplace=True)

        # --- Filtro por Fecha (aquí se soluciona el error) ---
        fechas_disponibles_ordenadas = sorted(df[FECHA_COLUMN].dt.date.unique())
        
        if not fechas_disponibles_ordenadas:
            st.warning("No se encontraron fechas válidas en el archivo cargado después del preprocesamiento.")
            st.stop()

        # Validar VOLUME_COLUMN y otras columnas aquí (la parte del código que ya estaba)
        if VOLUME_COLUMN not in df.columns:
            st.error(...)
            st.stop()
        # ... (código de validación de otras columnas)

        # Continuar con el resto del preprocesamiento (mapeo de empresas, etc.)
        # ...

        # El resto del código continúa desde aquí...
        # ...
        
    except Exception as e:
        st.error(f"Ocurrió un error durante la carga o preprocesamiento de los datos: {e}")
        st.exception(e) # Muestra el traceback completo
else:
    st.info("Carga tu archivo Excel para comenzar.")