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
VOLUME_COLUMN = 'TONELAJE'
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE'
FECHA_COLUMN = 'FECHA'
PRODUCTO_COLUMN = 'PRODUCTO'
DESTINO_COLUMN = 'DESTINO'
GUIA_COLUMN_IDENTIFIER = None       
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
        
        df[FECHA_COLUMN] = df[FECHA_COLUMN].astype(str)
        df[FECHA_COLUMN] = pd.to_datetime(df[FECHA_COLUMN], errors='coerce') 

        if not pd.api.types.is_datetime64_any_dtype(df[FECHA_COLUMN]):
            st.error(f"Error: La columna '{FECHA_COLUMN}' no pudo ser convertida a un tipo de fecha y hora. Verifica el formato de tus fechas en el archivo Excel. Un formato esperado es DD-MM-YYYY o YYYY-MM-DD.")
            st.stop()
            
        df.dropna(subset=[FECHA_COLUMN], inplace=True)

        # 2. Validar VOLUME_COLUMN y otras columnas
        if VOLUME_COLUMN not in df.columns:
            st.error(...)
            st.stop()
        df[VOLUME_COLUMN] = pd.to_numeric(df[VOLUME_COLUMN], errors='coerce').fillna(0) # Reemplazar errores con 0

        if PRODUCTO_COLUMN not in df.columns:
            st.error(...)
            st.stop()

        if EMPRESA_COLUMN not in df.columns:
            st.error(...)
            st.stop()
        
        # --- Mapeo y otros preprocesamientos ---
        df[EMPRESA_COLUMN] = df[EMPRESA_COLUMN].map(empresa_mapping).fillna(df[EMPRESA_COLUMN])
        
        # --- Filtro por Fecha (aquí se soluciona el problema de la pantalla en blanco) ---
        fechas_disponibles_ordenadas = sorted(df[FECHA_COLUMN].dt.date.unique())
        
        if not fechas_disponibles_ordenadas:
            st.warning("No se encontraron fechas válidas en el archivo cargado después del preprocesamiento. El archivo podría estar vacío o tener problemas de formato.")
            st.stop()

        # Renderizado del Dashboard (el resto del código sigue igual)
        # ...
        
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        st.exception(e) # Muestra el traceback completo
else:
    st.info("Carga tu archivo Excel para comenzar.")