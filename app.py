import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import timedelta, datetime

# --- CONFIGURACIÓN GLOBAL DE LA APLICACIÓN ---
st.set_page_config(
    page_title="Dashboard Integral de Operaciones",
    layout="wide",
    page_icon="📊"
)
pio.templates.default = "plotly"

# --- CONFIGURACIÓN DE NOMBRES DE COLUMNAS ---
VOLUME_COLUMN = 'TONELAJE'
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE'
FECHA_COLUMN = 'FECHA'
PRODUCTO_COLUMN = 'PRODUCTO'
DESTINO_COLUMN = 'DESTINO'

# --- FUNCIÓN DE NORMALIZACIÓN DE EMPRESAS Y MAPEO (DEFINIDO GLOBALMENTE) ---
def normalizar_nombre_empresa(nombre, mapeo):
    nombre_limpio = str(nombre).strip().upper()
    nombre_limpio = ' '.join(nombre_limpio.split())
    return mapeo.get(nombre_limpio, nombre_limpio)

empresa_mapping = {
    "JORQUERA TRANSPORTE S A": "JORQUERA TRANSPORTE S. A.", "JORQUERA TRANSPORTE S. A.": "JORQUERA TRANSPORTE S. A.",
    "MINING SERVICES AND DERIVATES": "M S & D SPA", "MINING SERVICES AND DERIVATES SPA": "M S & D SPA",
    # (El resto de tus equivalencias de empresa aquí)
}

# ==============================================================================
#                      PESTAÑA 1: ANÁLISIS DIARIO
# ==============================================================================
def render_analisis_diario(df):
    st.header("Análisis de Operaciones por Día")
    
    st.sidebar.header("Filtro para Análisis Diario")
    fechas_op = sorted(df[FECHA_COLUMN].dt.date.unique())
    if not fechas_op: st.warning("No hay fechas válidas."); return

    fecha_sel_op = st.sidebar.date_input("Selecciona una Fecha:", value=fechas_op[-1], key="date_op_tab1")
    df_filtrado_op = df[df[FECHA_COLUMN].dt.date == fecha_sel_op].copy()

    if df_filtrado_op.empty:
        st.warning(f"No hay datos para la fecha: {fecha_sel_op.strftime('%d-%m-%Y')}"); return

    # KPIs
    tonelaje_total = df_filtrado_op[VOLUME_COLUMN].sum()
    col1, col2 = st.columns(2)
    col1.metric("Tonelaje Total", f"{tonelaje_total:,.2f} Ton")
    col2.metric("Guías Emitidas", f"{len(df_filtrado_op):,}")
    
    st.subheader("📈 Visualizaciones Analíticas del Día")
    
    # --- GRÁFICO Y ANÁLISIS POR EMPRESA ---
    empresa_data = pd.DataFrame()
    tonelaje_por_empresa = df_filtrado_op.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    guias_por_empresa = df_filtrado_op.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
    if not tonelaje_por_empresa.empty:
        empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left').fillna(0)

    if not empresa_data.empty:
        # (Aquí va la lógica completa del gráfico de empresa que ya teníamos)
        st.info("Gráfico por Empresa aquí.")

    # --- GRÁFICO Y ANÁLISIS POR PRODUCTO ---
    # ... (y así sucesivamente)

# ==============================================================================
#                      PESTAÑA 2: ANÁLISIS COMPARATIVO
# ==============================================================================
def render_analisis_comparativo(df_original):
    st.header("Análisis Comparativo por Rango de Fechas")
    # ... (código de esta pestaña se mantiene)

# ==============================================================================
#                      CUERPO PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
st.title("📊 Dashboard Integral de Operaciones")

uploaded_file = st.sidebar.file_uploader("📂 Carga tu archivo Excel", type=["xlsx", "xlsm"])

if uploaded_file:
    try:
        df_maestro = pd.read_excel(uploaded_file, engine='openpyxl')
        
        required_cols = [FECHA_COLUMN, VOLUME_COLUMN, PRODUCTO_COLUMN, EMPRESA_COLUMN, DESTINO_COLUMN]
        # (código de validación de columnas aquí)
        
        df_maestro[FECHA_COLUMN] = pd.to_datetime(df_maestro[FECHA_COLUMN], dayfirst=True, errors='coerce')
        df_maestro = df_maestro.dropna(subset=[FECHA_COLUMN])
        df_maestro[VOLUME_COLUMN] = pd.to_numeric(df_maestro[VOLUME_COLUMN], errors='coerce').fillna(0)
        df_maestro[EMPRESA_COLUMN] = df_maestro[EMPRESA_COLUMN].apply(lambda x: normalizar_nombre_empresa(x, empresa_mapping))
        
        tab1, tab2 = st.tabs(["📊 Análisis Diario", "📈 Análisis Comparativo"])

        with tab1:
            render_analisis_diario(df_maestro.copy())
        with tab2:
            render_analisis_comparativo(df_maestro.copy())
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.exception(e)
else:
    st.info("📌 Carga tu archivo Excel para comenzar.")