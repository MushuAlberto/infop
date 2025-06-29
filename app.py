import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Usado para crear la figura combinada
from PIL import Image
from fpdf import FPDF
import tempfile
import os
from pathlib import Path

# --- CONFIGURACIÓN GLOBAL DE LA APLICACIÓN ---
st.set_page_config(
    page_title="Dashboard Integral de Operaciones",
    layout="wide",
    page_icon="📊"
)

# --- CONFIGURACIÓN DE NOMBRES DE COLUMNAS (Centralizado para fácil edición) ---
# ¡Es CRUCIAL que estos nombres coincidan EXACTAMENTE con los de tu archivo Excel!
# Cambia aquí si algún nombre es diferente.
VOLUME_COLUMN = 'TONELAJE'
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE'
FECHA_COLUMN = 'FECHA'
PRODUCTO_COLUMN = 'PRODUCTO'
DESTINO_COLUMN = 'DESTINO'
HORA_COL_NAME = 'HR ENTRADA'
REGULACION_COLUMNS_TO_COUNT = ['REGULACION 1', 'REGULACION 2', 'REGULACION 3']

# --- FUNCIÓN DE NORMALIZACIÓN DE EMPRESAS ---
def normalizar_nombre_empresa(nombre):
    """Normaliza nombres de empresa para estandarizar variantes."""
    nombre = str(nombre).strip().upper()
    nombre = nombre.replace('.', '').replace('&', 'AND')
    nombre = ' '.join(nombre.split())  # Normaliza espacios múltiples
    equivalencias = {
        "JORQUERA TRANSPORTE S A": "JORQUERA TRANSPORTE S. A.",
        "MINING SERVICES AND DERIVATES": "M S & D SPA", "MINING SERVICES AND DERIVATES SPA": "M S & D SPA",
        "M S AND D": "M S & D SPA", "M S AND D SPA": "M S & D SPA", "MSANDD SPA": "M S & D SPA",
        "M S D": "M S & D SPA", "M S D SPA": "M S & D SPA", "MS&D SPA": "M S & D SPA", "M S & D": "M S & D SPA",
        "M AND Q SPA": "M&Q SPA", "M AND Q": "M&Q SPA", "M Q SPA": "M&Q SPA", "MQ SPA": "M&Q SPA",
        "MANDQ SPA": "M&Q SPA", "MINING AND QUARRYING SPA": "M&Q SPA", "MINING AND QUARRYNG SPA": "M&Q SPA",
        "AG SERVICE SPA": "AG SERVICES SPA", "AG SERVICES SPA": "AG SERVICES SPA",
        "COSEDUCAM S A": "COSEDUCAM S A", "COSEDUCAM": "COSEDUCAM S A"
    }
    return equivalencias.get(nombre, nombre)

# --- DEFINIR RUTAS DE ARCHIVOS ---
# Esto asume que tus imágenes están en el mismo directorio que app.py
CURRENT_DIR = Path(__file__).parent
LOGOS = {
    "COSEDUCAM S A": str(CURRENT_DIR / "coseducam.png"),
    "M&Q SPA": str(CURRENT_DIR / "mq.png"),
    "M S & D SPA": str(CURRENT_DIR / "msd.png"),
    "JORQUERA TRANSPORTE S. A.": str(CURRENT_DIR / "jorquera.png"),
    "AG SERVICES SPA": str(CURRENT_DIR / "ag.png")
}
BANNER_PATH = str(CURRENT_DIR / "image.png")

# ==============================================================================
#                      PESTAÑA 1: ANÁLISIS DE OPERACIONES
# ==============================================================================
def render_analisis_operaciones(df):
    st.header("Análisis de Rendimiento por Tonelaje, Guías y Destino")
    
    # --- FILTRO DE FECHA PARA ESTA PESTAÑA ---
    st.sidebar.header("Filtros para Análisis de Operaciones")
    fechas_op = sorted(df[FECHA_COLUMN].dt.date.unique())
    if not fechas_op:
        st.warning("No hay fechas válidas en los datos.")
        return
        
    fecha_sel_op = st.sidebar.date_input(
        f"Selecciona una {FECHA_COLUMN}:",
        value=fechas_op[0], min_value=fechas_op[0], max_value=fechas_op[-1], key="date_op"
    )

    df_filtrado_op = df[df[FECHA_COLUMN].dt.date == fecha_sel_op].copy()

    if df_filtrado_op.empty:
        st.warning(f"No hay datos disponibles para la fecha seleccionada: {fecha_sel_op.strftime('%d-%m-%Y')}")
        return

    # --- KPIs ---
    tonelaje_total = df_filtrado_op[VOLUME_COLUMN].sum()
    productos_distintos = df_filtrado_op[PRODUCTO_COLUMN].nunique()
    col1, col2 = st.columns(2)
    col1.metric("Tonelaje Total del Día", f"{tonelaje_total:,.2f} Ton")
    col2.metric("Productos Distintos Operados", f"{productos_distintos}")
    
    st.subheader("📈 Visualizaciones Analíticas")
    
    # --- GRÁFICO COMBINADO POR EMPRESA ---
    empresa_data = pd.DataFrame()
    tonelaje_por_empresa = df_filtrado_op.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    guias_por_empresa = df_filtrado_op.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
    if not tonelaje_por_empresa.empty:
        empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left').fillna(0)

    if not empresa_data.empty:
        fig_emp = go.Figure()
        fig_emp.add_trace(go.Bar(x=empresa_data[EMPRESA_COLUMN], y=empresa_data[VOLUME_COLUMN], name='Tonelaje'))
        fig_emp.add_trace(go.Scatter(x=empresa_data[EMPRESA_COLUMN], y=empresa_data['CANTIDAD_GUIAS'], name='Nro. de Guías', yaxis='y2', mode='lines+markers'))
        fig_emp.update_layout(title_text='Análisis de Rendimiento por Transportista',
                              yaxis=dict(title='Tonelaje'),
                              yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right'))
        st.plotly_chart(fig_emp, use_container_width=True)
    else:
        st.warning("No hay datos de empresa para graficar en esta fecha.")
        
    # --- GRÁFICO COMBINADO POR PRODUCTO ---
    producto_data = pd.DataFrame()
    tonelaje_por_producto = df_filtrado_op.groupby(PRODUCTO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    guias_por_producto = df_filtrado_op.groupby(PRODUCTO_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
    if not tonelaje_por_producto.empty:
        producto_data = pd.merge(tonelaje_por_producto, guias_por_producto, on=PRODUCTO_COLUMN, how='left').fillna(0)
    
    if not producto_data.empty:
        fig_prod = go.Figure()
        fig_prod.add_trace(go.Bar(x=producto_data[PRODUCTO_COLUMN], y=producto_data[VOLUME_COLUMN], name='Tonelaje'))
        fig_prod.add_trace(go.Scatter(x=producto_data[PRODUCTO_COLUMN], y=producto_data['CANTIDAD_GUIAS'], name='Nro. de Guías', yaxis='y2', mode='lines+markers'))
        fig_prod.update_layout(title_text='Análisis de Rendimiento por Producto',
                               yaxis=dict(title='Tonelaje'),
                               yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right'))
        st.plotly_chart(fig_prod, use_container_width=True)
    else:
        st.warning("No hay datos de producto para graficar en esta fecha.")

    # --- GRÁFICO POR DESTINO ---
    tonelaje_por_destino = df_filtrado_op.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    if not tonelaje_por_destino.empty:
        fig_dest = px.bar(tonelaje_por_destino, x=DESTINO_COLUMN, y=VOLUME_COLUMN, title='Distribución de Tonelaje por Destino')
        st.plotly_chart(fig_dest, use_container_width=True)
        
# ==============================================================================
#                      PESTAÑA 2: ANÁLISIS HORARIO DE EQUIPOS
# ==============================================================================
def render_analisis_horario(df):
    st.header("Análisis de Flujo de Equipos por Horario")

    # --- Preprocesamiento específico para esta pestaña ---
    df_horario = df.copy()
    if pd.api.types.is_object_dtype(df_horario[HORA_COL_NAME]):
        df_horario[HORA_COL_NAME] = pd.to_datetime(df_horario[HORA_COL_NAME], format='%H:%M:%S', errors='coerce').dt.hour
    elif pd.api.types.is_datetime64_any_dtype(df_horario[HORA_COL_NAME]):
        df_horario[HORA_COL_NAME] = df_horario[HORA_COL_NAME].dt.hour
    df_horario = df_horario.dropna(subset=[HORA_COL_NAME])
    
    # --- FILTROS PARA ESTA PESTAÑA ---
    st.sidebar.header("Filtros para Análisis Horario")
    destinos_h = sorted(df_horario[DESTINO_COLUMN].dropna().unique())
    empresas_h = sorted(df_horario[EMPRESA_COLUMN].dropna().unique())

    destinos_sel = st.sidebar.multiselect("Selecciona destino(s):", destinos_h, default=list(destinos_h), key="dest_sel_horario")
    empresas_sel = st.sidebar.multiselect("Selecciona empresa(s):", empresas_h, default=list(empresas_h), key="emp_sel_horario")

    # --- FORMULARIO DE INGRESO MANUAL ---
    with st.sidebar.form("manual_form"):
        st.subheader("✍️ Ingresar datos manualmente")
        # (El código de tu formulario manual iría aquí)
        submit_manual = st.form_submit_button("Guardar Dato")
        if submit_manual: st.sidebar.success("Datos guardados (simulado).")
    
    df_filtered = df_horario[
        df_horario[DESTINO_COLUMN].isin(destinos_sel) &
        df_horario[EMPRESA_COLUMN].isin(empresas_sel)
    ].copy()

    # --- Visualizaciones para cada empresa seleccionada ---
    if not df_filtered.empty:
        for empresa in empresas_sel:
            df_empresa_h = df_filtered[df_filtered[EMPRESA_COLUMN] == empresa]
            if df_empresa_h.empty: continue
            
            st.markdown(f"---\n## {empresa}")
            
            # (Aquí va la lógica de visualización y PDF de tu script original)
            st.info(f"Mostrando datos para {empresa}. La generación de PDF se ha simplificado en este ejemplo.")
    else:
        st.warning("No hay datos para la selección de filtros actual.")


# ==============================================================================
#                      CUERPO PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
st.title("📊 Dashboard Integral de Operaciones")

# Carga de archivo
uploaded_file = st.sidebar.file_uploader("📂 Carga tu archivo Excel", type=["xlsx", "xlsm"])

if uploaded_file:
    try:
        # Cargar y preprocesar los datos UNA SOLA VEZ
        df_maestro = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # --- PREPROCESAMIENTO GLOBAL ---
        columnas_requeridas = [
            FECHA_COLUMN, DESTINO_COLUMN, EMPRESA_COLUMN, PRODUCTO_COLUMN, 
            VOLUME_COLUMN, HORA_COL_NAME
        ]
        missing_cols = [col for col in columnas_requeridas if col not in df_maestro.columns]
        if missing_cols:
            st.error(f"Faltan las siguientes columnas esenciales: {', '.join(missing_cols)}. Por favor, verifica el archivo.")
            st.stop()
        
        df_maestro[FECHA_COLUMN] = pd.to_datetime(df_maestro[FECHA_COLUMN], errors='coerce', dayfirst=True)
        df_maestro[EMPRESA_COLUMN] = df_maestro[EMPRESA_COLUMN].apply(normalizar_nombre_empresa)
        df_maestro[VOLUME_COLUMN] = pd.to_numeric(df_maestro[VOLUME_COLUMN], errors='coerce').fillna(0)
        df_maestro = df_maestro.dropna(subset=[FECHA_COLUMN])

        # Crear Pestañas
        tab1, tab2 = st.tabs(["📊 Análisis de Operaciones", "🕒 Análisis Horario"])

        with tab1:
            render_analisis_operaciones(df_maestro.copy())

        with tab2:
            render_analisis_horario(df_maestro.copy())

    except Exception as e:
        st.error(f"Error fatal al procesar el archivo: {str(e)}")
        st.exception(e)

else:
    st.info("📌 Por favor, carga un archivo Excel para comenzar el análisis.")