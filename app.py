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
#                      PESTAÑA 1: ANÁLISIS DIARIO
# ==============================================================================
def render_analisis_diario(df):
    st.header(f"Análisis de Operaciones Diarias")
    
    st.sidebar.header("Filtro para Análisis Diario")
    fechas_op = sorted(df[FECHA_COLUMN].dt.date.unique())
    if not fechas_op:
        st.warning("No hay fechas válidas en los datos.")
        return

    fecha_sel_op = st.sidebar.date_input(
        f"Selecciona una Fecha:", value=fechas_op[-1], min_value=fechas_op[0], max_value=fechas_op[-1], key="date_op_tab1"
    )
    
    st.subheader(f"Resultados para el {fecha_sel_op.strftime('%d-%m-%Y')}")
    df_filtrado_op = df[df[FECHA_COLUMN].dt.date == fecha_sel_op].copy()

    if df_filtrado_op.empty:
        st.warning(f"No se encontraron datos para la fecha seleccionada.")
        return

    # KPIs
    tonelaje_total = df_filtrado_op[VOLUME_COLUMN].sum()
    guias_totales = len(df_filtrado_op)
    
    col1, col2 = st.columns(2)
    col1.metric("Tonelaje Total del Día", f"{tonelaje_total:,.2f} Ton")
    col2.metric("Nro. de Guías Emitidas", f"{guias_totales:,}")
    
    st.markdown("---")
    st.subheader("📈 Visualizaciones Analíticas del Día")
    
    # --- GRÁFICO Y ANÁLISIS POR EMPRESA ---
    empresa_data = pd.DataFrame()
    tonelaje_por_empresa = df_filtrado_op.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    guias_por_empresa = df_filtrado_op.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
    if not tonelaje_por_empresa.empty:
        empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left').fillna(0)

    if not empresa_data.empty:
        fig_emp = go.Figure(data=[go.Bar(x=empresa_data[EMPRESA_COLUMN], y=empresa_data[VOLUME_COLUMN], name='Tonelaje')])
        fig_emp.add_trace(go.Scatter(x=empresa_data[EMPRESA_COLUMN], y=empresa_data['CANTIDAD_GUIAS'], name='Guías', yaxis='y2', mode='lines+markers', line=dict(color='firebrick', width=2, dash='dash')))
        fig_emp.update_layout(title_text='Análisis de Rendimiento por Transportista', yaxis=dict(title='Tonelaje (toneladas)'), yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right', showgrid=False), legend=dict(y=1.1, x=1))
        st.plotly_chart(fig_emp, use_container_width=True)

        with st.expander("Ver Análisis Ejecutivo por Transportista (Detallado)"):
            empresa_top1 = empresa_data.iloc[0]
            porcentaje_top1 = (empresa_top1[VOLUME_COLUMN] / tonelaje_total) * 100 if tonelaje_total > 0 else 0
            eficiencia_top1 = empresa_top1[VOLUME_COLUMN] / empresa_top1['CANTIDAD_GUIAS'] if empresa_top1['CANTIDAD_GUIAS'] > 0 else 0

            st.markdown(f"""
            #### Resumen Ejecutivo del Rendimiento de Transportistas:
            *   **Dominio Estratégico:** **{empresa_top1[EMPRESA_COLUMN]}** lidera la operación con **{empresa_top1[VOLUME_COLUMN]:,.2f} Toneladas**, concentrando un impresionante **{porcentaje_top1:.1f}%** del volumen total del día. Esto resalta nuestra dependencia operativa en este socio clave.
            *   **Eficiencia Operativa:** El líder promedia **{eficiencia_top1:.2f} toneladas por guía**. Un ratio alto sugiere cargas consolidadas y una logística eficiente. Este es un KPI crucial para negociaciones y evaluaciones de rendimiento.
            """
            )
            if len(empresa_data) > 1:
                empresa_last = empresa_data.iloc[-1]
                st.markdown(f"*   **Área de Oportunidad:** La empresa con menor participación es **{empresa_last[EMPRESA_COLUMN]}** ({empresa_last[VOLUME_COLUMN]:,.2f} Ton). Es fundamental analizar si su bajo rendimiento se debe a asignación, capacidad o eficiencia, presentando una oportunidad de optimización o reevaluación de contratos.")
            
    # --- GRÁFICO Y ANÁLISIS POR PRODUCTO ---
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

        with st.expander("Ver Análisis Ejecutivo por Producto (Detallado)"):
            producto_top1 = producto_data.iloc[0]
            porcentaje_top1_prod = (producto_top1[VOLUME_COLUMN] / tonelaje_total) * 100 if tonelaje_total > 0 else 0
            st.markdown(f"""
            #### Resumen Ejecutivo del Portafolio de Productos:
            *   **Producto Estrella (Volumen):** El producto **{producto_top1[PRODUCTO_COLUMN]}** es el motor de la operación, aportando **{porcentaje_top1_prod:.1f}%** del tonelaje total. La estrategia de inventario y producción debe asegurar su disponibilidad constante.
            *   **Frecuencia vs. Volumen:** Con **{producto_top1['CANTIDAD_GUIAS']} guías** para el producto líder, se observa una alta rotación. El análisis debe centrarse en si la relación volumen/guía es óptima para minimizar costos de transporte o si se podrían consolidar más envíos.
            """)
    
    # --- GRÁFICO Y ANÁLISIS POR DESTINO ---
    tonelaje_por_destino = df_filtrado_op.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
    if not tonelaje_por_destino.empty:
        fig_dest = px.bar(tonelaje_por_destino, x=DESTINO_COLUMN, y=VOLUME_COLUMN, title='Distribución de Tonelaje por Destino')
        st.plotly_chart(fig_dest, use_container_width=True)

        with st.expander("Ver Análisis Ejecutivo por Destino (Detallado)"):
            destino_top1 = tonelaje_por_destino.iloc[0]
            porcentaje_top1_dest = (destino_top1[VOLUME_COLUMN] / tonelaje_total) * 100 if tonelaje_total > 0 else 0
            st.markdown(f"""
            #### Resumen Ejecutivo de la Distribución Geográfica:
            *   **Mercado Clave:** **{destino_top1[DESTINO_COLUMN]}** absorbe el **{porcentaje_top1_dest:.1f}%** de nuestro volumen. Los esfuerzos de servicio y logística deben priorizar este destino para mantener la satisfacción del cliente.
            *   **Oportunidades de Crecimiento:** Los destinos con menor tonelaje representan mercados con potencial de desarrollo. Se debe investigar si la baja demanda es por penetración de mercado o por deficiencias logísticas, abriendo la puerta a nuevas estrategias comerciales.
            """)
            
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
    delta_total_percent = ((delta_total / kpi2_total) * 100) if kpi2_total > 0 else float('inf')
    
    st.metric("Variación de Tonelaje (Período 1 vs 2)", f"{kpi1_total:,.2f} Ton", f"{delta_total:,.2f} ({delta_total_percent:.1f}%)")
    
    st.markdown("---")
    st.subheader("📊 Comparación Visual Detallada")
    
    def plot_comparison(group_by_col, df1, df2):
        st.markdown(f"#### Por {group_by_col}")
        col1, col2 = st.columns(2)
        with col1:
            if not df1.empty:
                data1 = df1.groupby(group_by_col)[VOLUME_COLUMN].sum().sort_values(ascending=False)
                st.bar_chart(data1)
        with col2:
            if not df2.empty:
                data2 = df2.groupby(group_by_col)[VOLUME_COLUMN].sum().sort_values(ascending=False)
                st.bar_chart(data2)

    plot_comparison(EMPRESA_COLUMN, periodo1_df, periodo2_df)
    plot_comparison(PRODUCTO_COLUMN, periodo1_df, periodo2_df)
    plot_comparison(DESTINO_COLUMN, periodo1_df, periodo2_df)

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
        df_maestro[EMPRESA_COLUMN] = df_maestro[EMPRESA_COLUMN].apply(lambda x: empresa_mapping.get(str(x).strip().upper(), x))

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