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
uploaded_file = st.sidebar.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("Archivo cargado correctamente!")

        # --- Preprocesamiento de Datos ---
        # (Se omite por brevedad, el código completo es el que ya tienes para esta parte)

        # Filtro por Fecha y Renderizado del Dashboard (aquí está la parte relevante)
        
        fecha_por_defecto = sorted(df[FECHA_COLUMN].dt.date.unique())[0]
        fecha_seleccionada = st.sidebar.date_input(
            f"Selecciona una {FECHA_COLUMN}:", value=fecha_por_defecto
        )
        fecha_dt_seleccionada = pd.to_datetime(fecha_seleccionada)
        df_filtrado_fecha = df[df[FECHA_COLUMN].dt.date == fecha_dt_seleccionada.date()]

        st.header(f"Análisis para el {fecha_dt_seleccionada.strftime('%d-%m-%Y')}")

        if not df_filtrado_fecha.empty:
            # --- KPIs ---
            # ... (código de KPIs se mantiene)

            # --- Cálculos para Gráficos ---
            # Gráfico Combinado por Empresa
            if EMPRESA_COLUMN in df_filtrado_fecha.columns:
                tonelaje_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
                guias_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
                empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left').fillna(0)
            
            # Gráfico de Tonelaje por Destino
            if DESTINO_COLUMN in df_filtrado_fecha.columns:
                tonelaje_por_destino = df_filtrado_fecha.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
            
            # Gráfico de Regulaciones por Producto
            # ... (código para regulaciones se mantiene)
            
            # Gráfico Combinado por Producto
            if PRODUCTO_COLUMN in df_filtrado_fecha.columns:
                tonelaje_por_producto_detail = df_filtrado_fecha.groupby(PRODUCTO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
                guias_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
                producto_data_combinado = pd.merge(tonelaje_por_producto_detail, guias_por_producto, on=PRODUCTO_COLUMN, how='left').fillna(0)
                

            # --- RENDERIZADO DE GRÁFICOS ---
            st.subheader("📈 Visualizaciones")
            
            # --- GRÁFICO 1: TONELAJE Y GUÍAS POR EMPRESA ---
            if not empresa_data.empty:
                # ... (código para el gráfico de empresa se mantiene)
                # Ejemplo de la creación del gráfico de empresa
                fig_empresa_combinado = px.bar(empresa_data, x=EMPRESA_COLUMN, y=VOLUME_COLUMN, title='Tonelaje y Guías por Empresa')
                fig_empresa_combinado.add_scatter(x=empresa_data[EMPRESA_COLUMN], y=empresa_data['CANTIDAD_GUIAS'], mode='lines', name='Guías', yaxis='y2')
                # ... (resto de la configuración del gráfico)
                st.plotly_chart(fig_empresa_combinado, use_container_width=True)

            # --- GRÁFICO 2: TONELAJE POR DESTINO ---
            if not tonelaje_por_destino.empty:
                # ... (código para el gráfico de destino se mantiene)
                fig_destino = px.bar(tonelaje_por_destino, x=DESTINO_COLUMN, y=VOLUME_COLUMN, title='Tonelaje por Destino')
                st.plotly_chart(fig_destino, use_container_width=True)
            
            # --- GRÁFICO 3: REGULACIONES POR PRODUCTO ---
            # ... (código para el gráfico de regulaciones se mantiene)

            # --- GRÁFICO 4: TONELAJE Y GUÍAS POR PRODUCTO (COMBINADO) ---
            if not producto_data_combinado.empty:
                # ... (código para el gráfico combinado de producto se mantiene)
                fig_producto_combinado = px.bar(producto_data_combinado, x=PRODUCTO_COLUMN, y=VOLUME_COLUMN, title='Tonelaje y Guías por Producto')
                fig_producto_combinado.add_scatter(x=producto_data_combinado[PRODUCTO_COLUMN], y=producto_data_combinado['CANTIDAD_GUIAS'], mode='lines', name='Guías', yaxis='y2')
                # ... (resto de la configuración del gráfico)
                st.plotly_chart(fig_producto_combinado, use_container_width=True)
            
            # --- Tabla de Datos Detallados ---
            # ... (código para la tabla se mantiene)
            
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        st.exception(e)
else:
    st.info("Carga tu archivo Excel para comenzar.")