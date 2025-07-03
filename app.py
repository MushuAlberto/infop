import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import timedelta

# --- CONFIGURACIÓN GLOBAL DE LA APLICACIÓN ---
st.set_page_config(
    page_title="Dashboard Integral de Operaciones",
    page_icon="📊",
    layout="wide"
)

pio.templates.default = "plotly"

# --- CONFIGURACIÓN DE NOMBRES DE COLUMNAS (Centralizado) ---
VOLUME_COLUMN = 'TONELAJE'
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE'
FECHA_COLUMN = 'FECHA'
PRODUCTO_COLUMN = 'PRODUCTO'
DESTINO_COLUMN = 'DESTINO'

# --- MAPEO DE EMPRESAS ---
empresa_mapping = {
    "JORQUERA TRANSPORTE S A": "JORQUERA TRANSPORTE S. A.", "JORQUERA TRANSPORTE S. A.": "JORQUERA TRANSPORTE S. A.",
    "MINING SERVICES AND DERIVATES": "M S & D SPA", "MINING SERVICES AND DERIVATES SPA": "M S & D SPA",
    "M S AND D": "M S & D SPA", "M S AND D SPA": "M S & D SPA", "MSANDD SPA": "M S & D SPA",
    "M S D": "M S & D SPA", "M S D SPA": "M S & D SPA", "M S & D": "M S & D SPA", "MS&D SPA": "M S & D SPA",
    "M AND Q SPA": "M&Q SPA", "M AND Q": "M&Q SPA", "M Q SPA": "M&Q SPA", "MQ SPA": "M&Q SPA",
    "MANDQ SPA": "M&Q SPA", "MINING AND QUARRYING SPA": "M&Q SPA", "MINING AND QUARRYNG SPA": "M&Q SPA",
    "AG SERVICE SPA": "AG SERVICES SPA", "AG SERVICES SPA": "AG SERVICES SPA",
    "COSEDUCAM S A": "COSEDUCAM S A", "COSEDUCAM": "COSEDUCAM S A"
}

# ==============================================================================
#                      FUNCIÓN PARA PESTAÑA 1: ANÁLISIS DIARIO
# ==============================================================================
def render_analisis_diario(df):
    st.header("Análisis de Operaciones por Día")
    
    st.sidebar.header("Filtro para Análisis Diario")
    fechas_op = sorted(df[FECHA_COLUMN].dt.date.unique())
    if not fechas_op: st.warning("No hay fechas válidas."); return

    fecha_sel_op = st.sidebar.date_input("Selecciona una Fecha:", value=fechas_op[0], min_value=fechas_op[0], max_value=fechas_op[-1], key="date_op_tab1")

    df_filtrado_op = df[df[FECHA_COLUMN].dt.date == fecha_sel_op].copy()

    if df_filtrado_op.empty:
        st.warning(f"No hay datos disponibles para la fecha: {fecha_sel_op.strftime('%d-%m-%Y')}"); return

    # ... (el código de KPIs y gráficos del análisis diario que ya teníamos va aquí)
    st.info("Pestaña de Análisis Diario: El contenido que ya creamos se muestra aquí.")

# ==============================================================================
#                      FUNCIÓN PARA PESTAÑA 2: ANÁLISIS COMPARATIVO
# ==============================================================================
def render_analisis_comparativo(df):
    st.header("Análisis Comparativo por Rango de Fechas")
    st.sidebar.header("Filtros para Comparación")
    
    fechas_comp = sorted(df[FECHA_COLUMN].dt.date.unique())
    
    # Selectores para Período 1
    st.sidebar.markdown("#### Período 1 (Actual)")
    fecha_inicio_1 = st.sidebar.date_input("Fecha Inicio 1:", value=fechas_comp[-7] if len(fechas_comp) > 7 else fechas_comp[0], key="start1")
    fecha_fin_1 = st.sidebar.date_input("Fecha Fin 1:", value=fechas_comp[-1], key="end1")
    
    # Selectores para Período 2
    st.sidebar.markdown("#### Período 2 (Anterior)")
    fecha_inicio_2 = st.sidebar.date_input("Fecha Inicio 2:", value=fechas_comp[-14] if len(fechas_comp) > 14 else fechas_comp[0], key="start2")
    fecha_fin_2 = st.sidebar.date_input("Fecha Fin 2:", value=fechas_comp[-8] if len(fechas_comp) > 8 else fechas_comp[0], key="end2")

    # Filtrar datos para cada período
    periodo1_df = df[(df[FECHA_COLUMN].dt.date >= fecha_inicio_1) & (df[FECHA_COLUMN].dt.date <= fecha_fin_1)]
    periodo2_df = df[(df[FECHA_COLUMN].dt.date >= fecha_inicio_2) & (df[FECHA_COLUMN].dt.date <= fecha_fin_2)]

    st.subheader("📊 Comparación de KPIs Generales")
    
    kpi1_total, kpi1_avg, kpi1_guides = 0, 0, 0
    kpi2_total, kpi2_avg, kpi2_guides = 0, 0, 0

    if not periodo1_df.empty:
        kpi1_total = periodo1_df[VOLUME_COLUMN].sum()
        kpi1_guides = len(periodo1_df)
        kpi1_avg = kpi1_total / kpi1_guides if kpi1_guides > 0 else 0
        
    if not periodo2_df.empty:
        kpi2_total = periodo2_df[VOLUME_COLUMN].sum()
        kpi2_guides = len(periodo2_df)
        kpi2_avg = kpi2_total / kpi2_guides if kpi2_guides > 0 else 0

    delta_total = kpi1_total - kpi2_total
    delta_avg = kpi1_avg - kpi2_avg
    delta_guides = kpi1_guides - kpi2_guides
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tonelaje Total", f"{kpi1_total:,.2f}", f"{delta_total:,.2f}")
    col2.metric("Guías Emitidas", f"{kpi1_guides:,}", f"{delta_guides:,}")
    col3.metric("Tonelaje Prom./Guía", f"{kpi1_avg:,.2f}", f"{delta_avg:,.2f}")
    
    st.subheader("📊 Comparación de Rendimiento por Empresa")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"**Período 1: {fecha_inicio_1.strftime('%d/%m')} al {fecha_fin_1.strftime('%d/%m')}**")
        if not periodo1_df.empty:
            data_empresa1 = periodo1_df.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False)
            st.bar_chart(data_empresa1)
    
    with col_p2:
        st.markdown(f"**Período 2: {fecha_inicio_2.strftime('%d/%m')} al {fecha_fin_2.strftime('%d/%m')}**")
        if not periodo2_df.empty:
            data_empresa2 = periodo2_df.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False)
            st.bar_chart(data_empresa2)


# ==============================================================================
#                      CUERPO PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
st.title("📊 Dashboard Integral de Operaciones")

uploaded_file = st.sidebar.file_uploader("📂 Carga tu archivo Excel", type=["xlsx", "xlsm"])

if uploaded_file:
    try:
        df_maestro = pd.read_excel(uploaded_file, engine='openpyxl')
        
        required_cols = [FECHA_COLUMN, VOLUME_COLUMN, PRODUCTO_COLUMN, EMPRESA_COLUMN, DESTINO_COLUMN]
        if not all(col in df_maestro.columns for col in required_cols):
            st.error(f"Faltan columnas esenciales. Asegúrate de que existan: {required_cols}")
            st.stop()
        
        df_maestro[FECHA_COLUMN] = pd.to_datetime(df_maestro[FECHA_COLUMN], dayfirst=True, errors='coerce')
        df_maestro.dropna(subset=[FECHA_COLUMN], inplace=True)
        df_maestro[VOLUME_COLUMN] = pd.to_numeric(df_maestro[VOLUME_COLUMN], errors='coerce').fillna(0)
        df_maestro[EMPRESA_COLUMN] = df_maestro[EMPRESA_COLUMN].apply(normalizar_nombre_empresa)
        
        # --- CREACIÓN DE PESTAÑAS ---
        tab1, tab2 = st.tabs(["📊 Análisis Diario", "📈 Análisis Comparativo"])

        with tab1:
            render_analisis_diario(df_maestro.copy())
        with tab2:
            render_analisis_comparativo(df_maestro.copy())
            
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.exception(e)
else:
    st.info("📌 Por favor, carga un archivo Excel para comenzar el análisis.")