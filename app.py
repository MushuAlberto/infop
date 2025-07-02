import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image
from fpdf import FPDF
import tempfile
import os
from pathlib import Path

# --- CONFIGURACIÓN GLOBAL DE LA APLICACIÓN ---
st.set_page_config(
    page_title="Dashboard Ejecutivo de Operaciones",
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
GUIA_COLUMN_IDENTIFIER = None       
REGULACION_COLUMNS_TO_COUNT = ['REGULACION 1', 'REGULACION 2', 'REGULACION 3'] 

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

# --- TÍTULO PRINCIPAL ---
st.title("📊 Dashboard Ejecutivo de Operaciones")
st.markdown("### Análisis Detallado de Operaciones")

# --- CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("📂 Carga tu archivo Excel", type=["xlsx", "xlsm"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("Archivo cargado correctamente!")

        # --- PREPROCESAMIENTO DE DATOS ---
        
        required_cols = [FECHA_COLUMN, VOLUME_COLUMN, PRODUCTO_COLUMN, EMPRESA_COLUMN, DESTINO_COLUMN]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Error: Faltan las siguientes columnas esenciales en el archivo cargado: {', '.join(missing_cols)}. Por favor, verifica el archivo.")
            st.stop()
            
        df[FECHA_COLUMN] = pd.to_datetime(df[FECHA_COLUMN], errors='coerce')
        df.dropna(subset=[FECHA_COLUMN], inplace=True)
        df[VOLUME_COLUMN] = pd.to_numeric(df[VOLUME_COLUMN], errors='coerce').fillna(0)
        df[EMPRESA_COLUMN] = df[EMPRESA_COLUMN].map(empresa_mapping).fillna(df[EMPRESA_COLUMN])
        
        # --- FILTRO POR FECHA ---
        st.sidebar.header("Filtros de Datos")
        
        fechas_disponibles_ordenadas = sorted(df[FECHA_COLUMN].dt.date.unique())
        if not fechas_disponibles_ordenadas:
            st.warning("No se encontraron fechas válidas en el archivo.")
            st.stop()
        
        fecha_seleccionada = st.sidebar.date_input(
            f"Selecciona una {FECHA_COLUMN}:",
            value=fechas_disponibles_ordenadas[0],
            min_value=fechas_disponibles_ordenadas[0],
            max_value=fechas_disponibles_ordenadas[-1]
        )
        
        # Corrección del filtro de fecha para ser más robusto
        df_filtrado_fecha = df[df[FECHA_COLUMN].dt.date == fecha_seleccionada].copy()
        
        # --- RENDERIZADO DEL DASHBOARD ---
        st.header(f"Análisis para el {fecha_seleccionada.strftime('%d-%m-%Y')}")
        
        if not df_filtrado_fecha.empty:
            # --- KPIs ---
            tonelaje_total = df_filtrado_fecha[VOLUME_COLUMN].sum()
            productos_distintos = df_filtrado_fecha[PRODUCTO_COLUMN].nunique()
            col1, col2 = st.columns(2)
            col1.metric("Tonelaje Total", f"{tonelaje_total:,.2f} Ton")
            col2.metric("Productos Distintos", f"{productos_distintos}")
            
            st.subheader("📈 Visualizaciones Analíticas")
            
            # --- Gráfico y Análisis por Empresa ---
            empresa_data = pd.DataFrame()
            if EMPRESA_COLUMN in df_filtrado_fecha.columns:
                tonelaje_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
                guias_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
                if not tonelaje_por_empresa.empty:
                    empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left').fillna(0)
            
            if not empresa_data.empty:
                # Creación del gráfico
                fig_emp = go.Figure(data=[go.Bar(x=empresa_data[EMPRESA_COLUMN], y=empresa_data[VOLUME_COLUMN], name='Tonelaje')])
                fig_emp.add_trace(go.Scatter(x=empresa_data[EMPRESA_COLUMN], y=empresa_data['CANTIDAD_GUIAS'], name='Guías', yaxis='y2', mode='lines+markers', line=dict(color='firebrick', width=2, dash='dash')))
                fig_emp.update_layout(
                    title_text='Análisis de Rendimiento por Transportista',
                    yaxis=dict(title='Tonelaje'),
                    yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right', showgrid=False),
                    legend=dict(y=1.1, x=1)
                )
                st.plotly_chart(fig_emp, use_container_width=True)

                # Análisis ejecutivo
                with st.expander("Ver Análisis Ejecutivo por Empresa"):
                    empresa_top1 = empresa_data.iloc[0]
                    eficiencia = empresa_top1[VOLUME_COLUMN] / empresa_top1['CANTIDAD_GUIAS'] if empresa_top1['CANTIDAD_GUIAS'] > 0 else 0
                    st.markdown(f"**Líder en Volumen:** **{empresa_top1[EMPRESA_COLUMN]}** dominó la operación con **{empresa_top1[VOLUME_COLUMN]:,.2f} Toneladas**. **Eficiencia Operativa:** Promedió **{eficiencia:.2f} toneladas por guía**.")
            
            # --- Gráfico y Análisis por Producto ---
            producto_data = pd.DataFrame()
            tonelaje_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
            guias_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
            if not tonelaje_por_producto.empty:
                producto_data = pd.merge(tonelaje_por_producto, guias_por_producto, on=PRODUCTO_COLUMN, how='left').fillna(0)
            
            if not producto_data.empty:
                # Creación del gráfico
                fig_prod = go.Figure(data=[go.Bar(x=producto_data[PRODUCTO_COLUMN], y=producto_data[VOLUME_COLUMN], name='Tonelaje', marker_color='lightseagreen')])
                fig_prod.add_trace(go.Scatter(x=producto_data[PRODUCTO_COLUMN], y=producto_data['CANTIDAD_GUIAS'], name='Guías', yaxis='y2', mode='lines+markers', line=dict(color='mediumvioletred', width=2, dash='dot')))
                fig_prod.update_layout(title_text='Análisis de Rendimiento por Producto', yaxis=dict(title='Tonelaje'), yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right', showgrid=False), legend=dict(y=1.1, x=1))
                st.plotly_chart(fig_prod, use_container_width=True)

                # Análisis ejecutivo
                with st.expander("Ver Análisis Ejecutivo por Producto"):
                    producto_top1 = producto_data.iloc[0]
                    porcentaje_top1_prod = (producto_top1[VOLUME_COLUMN] / tonelaje_total) * 100 if tonelaje_total > 0 else 0
                    st.markdown(f"**Producto Estrella:** **{producto_top1[PRODUCTO_COLUMN]}** fue el producto con mayor movimiento, representando el **{porcentaje_top1_prod:.1f}%** del tonelaje total del día.")
            
            # --- Gráfico y Análisis por Destino ---
            tonelaje_por_destino = df_filtrado_fecha.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
            if not tonelaje_por_destino.empty:
                fig_dest = px.bar(tonelaje_por_destino, x=DESTINO_COLUMN, y=VOLUME_COLUMN, title='Distribución de Tonelaje por Destino')
                st.plotly_chart(fig_dest, use_container_width=True)

                # Análisis ejecutivo
                with st.expander("Ver Análisis Ejecutivo por Destino"):
                    destino_top1 = tonelaje_por_destino.iloc[0]
                    porcentaje_top1_dest = (destino_top1[VOLUME_COLUMN] / tonelaje_total) * 100 if tonelaje_total > 0 else 0
                    st.markdown(f"**Principal Mercado:** El destino **{destino_top1[DESTINO_COLUMN]}** recibió el **{porcentaje_top1_dest:.1f}%** del volumen total, consolidándose como el mercado clave del día.")
                    
            # --- Tabla de Datos Detallados ---
            st.subheader("📋 Tabla de Datos Detallados")
            columnas_tabla = [FECHA_COLUMN, PRODUCTO_COLUMN, DESTINO_COLUMN, EMPRESA_COLUMN, VOLUME_COLUMN]
            columnas_existentes = [col for col in columnas_tabla if col in df_filtrado_fecha.columns]
            st.dataframe(df_filtrado_fecha[columnas_existentes])
            
        else:
            st.warning("No se encontraron datos para la fecha seleccionada.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
        st.exception(e)
else:
    st.info("📌 Por favor, carga un archivo Excel para comenzar el análisis.")