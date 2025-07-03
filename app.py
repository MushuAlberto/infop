import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import timedelta

# --- CONFIGURACIÓN GLOBAL DE LA APLICACIÓN ---
st.set_page_config(
    page_title="Dashboard Integral de Operaciones",
    layout="wide",
    page_icon="📊"
)

pio.templates.default = "plotly"

# --- CONFIGURACIÓN DE NOMBRES DE COLUMNAS (Centralizado) ---
VOLUME_COLUMN = 'TONELAJE'
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE'
FECHA_COLUMN = 'FECHA'
PRODUCTO_COLUMN = 'PRODUCTO'
DESTINO_COLUMN = 'DESTINO'

# --- FUNCIÓN DE NORMALIZACIÓN DE EMPRESAS (DEFINIDA GLOBALMENTE) ---
def normalizar_nombre_empresa(nombre):
    """Normaliza nombres de empresa para estandarizar variantes."""
    nombre = str(nombre).strip().upper()
    nombre = nombre.replace('.', '').replace('&', 'AND')
    nombre = ' '.join(nombre.split())
    equivalencias = {
        "JORQUERA TRANSPORTE S A": "JORQUERA TRANSPORTE S. A.",
        "MINING SERVICES AND DERIVATES": "M S & D SPA", "MINING SERVICES AND DERIVATES SPA": "M S & D SPA",
        "M S AND D": "M S & D SPA", "M S AND D SPA": "M S & D SPA", "MSANDD SPA": "M S & D SPA",
        "M S D": "M S & D SPA", "M S D SPA": "M S & D SPA", "M S & D": "M S & D SPA", "MS&D SPA": "M S & D SPA",
        "M AND Q SPA": "M&Q SPA", "M AND Q": "M&Q SPA", "M Q SPA": "M&Q SPA", "MQ SPA": "M&Q SPA",
        "MANDQ SPA": "M&Q SPA", "MINING AND QUARRYING SPA": "M&Q SPA", "MINING AND QUARRYNG SPA": "M&Q SPA",
        "AG SERVICE SPA": "AG SERVICES SPA", "AG SERVICES SPA": "AG SERVICES SPA",
        "COSEDUCAM S A": "COSEDUCAM S A", "COSEDUCAM": "COSEDUCAM S A"
    }
    return equivalencias.get(nombre, nombre)


# ==============================================================================
#                      FUNCIÓN PARA PESTAÑA 1: ANÁLISIS DIARIO
# ==============================================================================
def render_analisis_diario(df):
    st.header("Análisis de Operaciones por Día")
    
    fechas_op = sorted(df[FECHA_COLUMN].dt.date.unique())
    if not fechas_op:
        st.warning("No hay fechas válidas en los datos.")
        return

    fecha_sel_op = st.date_input(
        f"Selecciona una Fecha:", value=fechas_op[-1], min_value=fechas_op[0], max_value=fechas_op[-1], key="date_op_tab1"
    )
    st.header(f"Resultados para el {fecha_sel_op.strftime('%d-%m-%Y')}")
    df_filtrado_op = df[df[FECHA_COLUMN].dt.date == fecha_sel_op].copy()

    if df_filtrado_op.empty:
        st.warning(f"No se encontraron datos para la fecha seleccionada.")
        return

    # KPIs
    tonelaje_total = df_filtrado_op[VOLUME_COLUMN].sum()
    col1, col2 = st.columns(2)
    col1.metric("Tonelaje Total", f"{tonelaje_total:,.2f} Ton")
    col2.metric("Guías Emitidas", f"{len(df_filtrado_op):,}")
    
    st.markdown("---")
    st.subheader("📈 Visualizaciones Analíticas del Día")
    
    # Gráfico y Análisis por Empresa
    empresa_data = pd.DataFrame()
    tonelaje_por_empresa = df_filtrado_op.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    guias_por_empresa = df_filtrado_op.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
    if not tonelaje_por_empresa.empty:
        empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left').fillna(0)
    
    if not empresa_data.empty:
        fig_emp = go.Figure(data=[go.Bar(x=empresa_data[EMPRESA_COLUMN], y=empresa_data[VOLUME_COLUMN], name='Tonelaje')])
        fig_emp.add_trace(go.Scatter(x=empresa_data[EMPRESA_COLUMN], y=empresa_data['CANTIDAD_GUIAS'], name='Guías', yaxis='y2', mode='lines+markers', line=dict(color='firebrick', width=2, dash='dash')))
        fig_emp.update_layout(title_text='Análisis de Rendimiento por Transportista', yaxis=dict(title='Tonelaje'), yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right', showgrid=False), legend=dict(y=1.1, x=1))
        st.plotly_chart(fig_emp, use_container_width=True)

        with st.expander("Ver Análisis Ejecutivo por Transportista"):
            empresa_top1 = empresa_data.iloc[0]
            eficiencia = empresa_top1[VOLUME_COLUMN] / empresa_top1['CANTIDAD_GUIAS'] if empresa_top1['CANTIDAD_GUIAS'] > 0 else 0
            st.markdown(f"**- Líder en Volumen:** **{empresa_top1[EMPRESA_COLUMN]}** dominó la operación con **{empresa_top1[VOLUME_COLUMN]:,.2f} Toneladas**. **Eficiencia Operativa:** Promedió **{eficiencia:.2f} toneladas por guía**, un benchmark clave.")

    # Gráfico y Análisis por Producto
    producto_data = pd.DataFrame()
    tonelaje_por_producto = df_filtrado_op.groupby(PRODUCTO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    guias_por_producto = df_filtrado_op.groupby(PRODUCTO_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
    if not tonelaje_por_producto.empty:
        producto_data = pd.merge(tonelaje_por_producto, guias_por_producto, on=PRODUCTO_COLUMN, how='left').fillna(0)

    if not producto_data.empty:
        fig_prod = go.Figure(data=[go.Bar(x=producto_data[PRODUCTO_COLUMN], y=producto_data[VOLUME_COLUMN], name='Tonelaje', marker_color='lightseagreen')])
        fig_prod.add_trace(go.Scatter(x=producto_data[PRODUCTO_COLUMN], y=producto_data['CANTIDAD_GUIAS'], name='Guías', yaxis='y2', mode='lines+markers', line=dict(color='mediumvioletred', width=2, dash='dot')))
        fig_prod.update_layout(title_text='Análisis de Rendimiento por Producto', yaxis=dict(title='Tonelaje'), yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right', showgrid=False), legend=dict(y=1.1, x=1))
        st.plotly_chart(fig_prod, use_container_width=True)

        with st.expander("Ver Análisis Ejecutivo por Producto"):
            producto_top1 = producto_data.iloc[0]
            porcentaje_top1_prod = (producto_top1[VOLUME_COLUMN] / tonelaje_total) * 100 if tonelaje_total > 0 else 0
            st.markdown(f"**- Producto Estrella:** **{producto_top1[PRODUCTO_COLUMN]}** fue el motor de la operación, representando el **{porcentaje_top1_prod:.1f}%** del tonelaje total del día. Su disponibilidad es crítica.")

    # Gráfico y Análisis por Destino
    tonelaje_por_destino = df_filtrado_op.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    if not tonelaje_por_destino.empty:
        fig_dest = px.bar(tonelaje_por_destino, x=DESTINO_COLUMN, y=VOLUME_COLUMN, title='Distribución de Tonelaje por Destino')
        st.plotly_chart(fig_dest, use_container_width=True)

        with st.expander("Ver Análisis Ejecutivo por Destino"):
            destino_top1 = tonelaje_por_destino.iloc[0]
            porcentaje_top1_dest = (destino_top1[VOLUME_COLUMN] / tonelaje_total) * 100 if tonelaje_total > 0 else 0
            st.markdown(f"**- Principal Mercado:** El destino **{destino_top1[DESTINO_COLUMN]}** recibió el **{porcentaje_top1_dest:.1f}%** del volumen total, consolidándose como el mercado clave.")
            
# ==============================================================================
#                      PESTAÑA 2: ANÁLISIS COMPARATIVO
# ==============================================================================
def render_analisis_comparativo(df_original):
    st.header("Análisis Comparativo por Rango de Fechas")
    
    st.sidebar.header("Filtros para Comparación")
    fechas_comp = sorted(df_original[FECHA_COLUMN].dt.date.unique())
    if len(fechas_comp) < 2:
        st.warning("No hay suficientes datos de fechas para realizar una comparación.")
        return
    
    # Selectores para Período 1
    st.sidebar.markdown("#### Período 1 (Actual)")
    fecha_inicio_1 = st.sidebar.date_input("Fecha Inicio 1:", value=fechas_comp[-7] if len(fechas_comp) > 7 else fechas_comp[0], key="start1")
    fecha_fin_1 = st.sidebar.date_input("Fecha Fin 1:", value=fechas_comp[-1], key="end1")
    
    # Selectores para Período 2
    st.sidebar.markdown("#### Período 2 (Anterior)")
    fecha_inicio_2 = st.sidebar.date_input("Fecha Inicio 2:", value=fechas_comp[-14] if len(fechas_comp) > 14 else fechas_comp[0], key="start2")
    fecha_fin_2 = st.sidebar.date_input("Fecha Fin 2:", value=fechas_comp[-8] if len(fechas_comp) > 8 else fechas_comp[0], key="end2")

    periodo1_df = df_original[(df_original[FECHA_COLUMN].dt.date >= fecha_inicio_1) & (df_original[FECHA_COLUMN].dt.date <= fecha_fin_1)]
    periodo2_df = df_original[(df_original[FECHA_COLUMN].dt.date >= fecha_inicio_2) & (df_original[FECHA_COLUMN].dt.date <= fecha_fin_2)]

    st.subheader("📊 Comparación de KPIs Generales")
    
    kpi1_total = periodo1_df[VOLUME_COLUMN].sum() if not periodo1_df.empty else 0
    kpi2_total = periodo2_df[VOLUME_COLUMN].sum() if not periodo2_df.empty else 0
    delta_total = kpi1_total - kpi2_total
    delta_total_percent = ((delta_total / kpi2_total) * 100) if kpi2_total > 0 else float('inf') if kpi1_total > 0 else 0
    
    st.metric("Variación de Tonelaje (Período 1 vs 2)", f"{kpi1_total:,.2f} Ton", f"{delta_total:,.2f} Ton ({delta_total_percent:.1f}%)")
    
    st.markdown("---")
    st.subheader("📊 Comparación Visual Detallada")
    
    def plot_comparison(group_by_col, df1, df2, title_suffix):
        st.markdown(f"#### Por {title_suffix}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Período 1:**")
            if not df1.empty:
                data1 = df1.groupby(group_by_col)[VOLUME_COLUMN].sum().sort_values(ascending=False)
                if not data1.empty: st.bar_chart(data1)
    
        with col2:
            st.markdown(f"**Período 2:**")
            if not df2.empty:
                data2 = df2.groupby(group_by_col)[VOLUME_COLUMN].sum().sort_values(ascending=False)
                if not data2.empty: st.bar_chart(data2)

    plot_comparison(EMPRESA_COLUMN, periodo1_df, periodo2_df, "Empresa")
    plot_comparison(PRODUCTO_COLUMN, periodo1_df, periodo2_df, "Producto")
    plot_comparison(DESTINO_COLUMN, periodo1_df, periodo2_df, "Destino")

# ==============================================================================
#                      CUERPO PRINCIPAL DE LA APLICACIÓN
# ==============================================================================
st.title("📊 Dashboard Integral de Operaciones")

uploaded_file = st.sidebar.file_uploader("📂 Carga tu archivo Excel", type=["xlsx", "xlsm"])

if uploaded_file:
    try:
        df_maestro = pd.read_excel(uploaded_file, engine='openpyxl')
        
        required_cols = [FECHA_COLUMN, VOLUME_COLUMN, PRODUCTO_COLUMN, EMPRESA_COLUMN, DESTINO_COLUMN]
        missing_cols = [col for col in required_cols if col not in df_maestro.columns]
        if missing_cols:
            st.error(f"Faltan columnas esenciales: {', '.join(missing_cols)}. Verifica el archivo.")
            st.stop()
            
        df_maestro[FECHA_COLUMN] = pd.to_datetime(df_maestro[FECHA_COLUMN], dayfirst=True, errors='coerce')
        df_maestro = df_maestro.dropna(subset=[FECHA_COLUMN])
        df_maestro[VOLUME_COLUMN] = pd.to_numeric(df_maestro[VOLUME_COLUMN], errors='coerce').fillna(0)
        df_maestro[EMPRESA_COLUMN] = df_maestro[EMPRESA_COLUMN].apply(lambda x: empresa_mapping.get(str(x).strip().upper(), str(x)))

        st.sidebar.success("Archivo cargado y procesado!")
        
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