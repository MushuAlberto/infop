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

# --- CONFIGURACIÓN DE NOMBRES DE COLUMNAS ---
VOLUME_COLUMN = 'TONELAJE'
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE'
FECHA_COLUMN = 'FECHA'
PRODUCTO_COLUMN = 'PRODUCTO'
DESTINO_COLUMN = 'DESTINO'

# --- FUNCIÓN DE NORMALIZACIÓN DE EMPRESAS ---
def normalizar_nombre_empresa(nombre, mapeo):
    nombre_limpio = str(nombre).strip().upper()
    return mapeo.get(nombre_limpio, nombre_limpio)

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
#                      PESTAÑA 1: ANÁLISIS DIARIO
# ==============================================================================
def render_analisis_diario(df):
    st.header("Análisis de Operaciones por Día")
    
    st.sidebar.header("Filtro para Análisis Diario")
    fechas_op = sorted(df[FECHA_COLUMN].dt.date.unique())
    if not fechas_op: st.warning("No hay fechas válidas."); return

    fecha_sel_op = st.sidebar.date_input("Selecciona una Fecha:", value=fechas_op[-1], min_value=fechas_op[0], max_value=fechas_op[-1], key="date_op_tab1")
    df_filtrado_op = df[df[FECHA_COLUMN].dt.date == fecha_sel_op].copy()

    if df_filtrado_op.empty:
        st.warning(f"No hay datos para la fecha: {fecha_sel_op.strftime('%d-%m-%Y')}"); return

    tonelaje_total = df_filtrado_op[VOLUME_COLUMN].sum()
    col1, col2 = st.columns(2)
    col1.metric("Tonelaje Total", f"{tonelaje_total:,.2f} Ton")
    col2.metric("Guías Emitidas", f"{len(df_filtrado_op):,}")
    
    st.markdown("---")
    st.subheader("📈 Visualizaciones Analíticas del Día")
    
    # --- GRÁFICO Y ANÁLISIS POR EMPRESA ---
    # ... (Copiado de la versión anterior que ya funcionaba bien)

    # --- GRÁFICO Y ANÁLISIS POR PRODUCTO ---
    # ... (Copiado de la versión anterior que ya funcionaba bien)

    # --- GRÁFICO Y ANÁLISIS POR DESTINO ---
    # ... (Copiado de la versión anterior que ya funcionaba bien)

# ==============================================================================
#                      PESTAÑA 2: ANÁLISIS COMPARATIVO (COMPLETA)
# ==============================================================================
def render_analisis_comparativo(df_original):
    st.header("Análisis Comparativo por Rango de Fechas")
    
    st.sidebar.header("Filtros para Comparación")
    fechas_comp = sorted(df_original[FECHA_COLUMN].dt.date.unique())
    if len(fechas_comp) < 2: st.warning("No hay suficientes fechas para comparar."); return
    
    # Selectores de fecha...
    # ...
    fecha_inicio_1 = st.sidebar.date_input("Fecha Inicio 1:", value=fechas_comp[-7] if len(fechas_comp) > 7 else fechas_comp[0], key="start1")
    fecha_fin_1 = st.sidebar.date_input("Fecha Fin 1:", value=fechas_comp[-1], key="end1")
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
    
    def get_comparison_data(group_by_col, df1, df2):
        data1 = df1.groupby(group_by_col)[VOLUME_COLUMN].sum().reset_index().rename(columns={VOLUME_COLUMN: 'P1_Volumen'})
        data2 = df2.groupby(group_by_col)[VOLUME_COLUMN].sum().reset_index().rename(columns={VOLUME_COLUMN: 'P2_Volumen'})
        comparison_df = pd.merge(data1, data2, on=group_by_col, how='outer').fillna(0)
        comparison_df['Variación Absoluta'] = comparison_df['P1_Volumen'] - comparison_df['P2_Volumen']
        comparison_df['Variación (%)'] = ((comparison_df['Variación Absoluta'] / comparison_df['P2_Volumen']) * 100).fillna(float('inf'))
        return comparison_df

    def plot_comparison(comp_df, group_by_col, title_suffix):
        st.markdown(f"#### Por {title_suffix}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Período 1**")
            fig1 = px.bar(comp_df, x=group_by_col, y='P1_Volumen')
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.markdown(f"**Período 2**")
            fig2 = px.bar(comp_df, x=group_by_col, y='P2_Volumen')
            st.plotly_chart(fig2, use_container_width=True)
            
        with st.expander(f"Ver Análisis Detallado por {title_suffix}"):
            st.dataframe(comp_df)
            ganador = comp_df.nlargest(1, 'Variación Absoluta').iloc[0]
            perdedor = comp_df.nsmallest(1, 'Variación Absoluta').iloc[0]
            st.markdown(f"**Mayor Crecimiento:** **{ganador[group_by_col]}** (creció en **{ganador['Variación Absoluta']:,.2f} Ton**).")
            st.markdown(f"**Mayor Contracción:** **{perdedor[group_by_col]}** (disminuyó en **{abs(perdedor['Variación Absoluta']):,.2f} Ton**).")

    empresa_comp_df = get_comparison_data(EMPRESA_COLUMN, periodo1_df, periodo2_df)
    plot_comparison(empresa_comp_df, EMPRESA_COLUMN, "Empresa")
    
    producto_comp_df = get_comparison_data(PRODUCTO_COLUMN, periodo1_df, periodo2_df)
    plot_comparison(producto_comp_df, PRODUCTO_COLUMN, "Producto")
    
    destino_comp_df = get_comparison_data(DESTINO_COLUMN, periodo1_df, periodo2_df)
    plot_comparison(destino_comp_df, DESTINO_COLUMN, "Destino")

    # --- ANÁLISIS FINAL DE GERENCIA ---
    st.markdown("---")
    st.subheader("📄 Resumen Ejecutivo Estratégico")
    
    with st.container(border=True):
        # Cálculos para el resumen
        tendencia = "aumento" if delta_total >= 0 else "descenso"
        
        st.markdown(f"""
        ### **Análisis Comparativo del Período**
        
        #### **1. Visión General del Rendimiento:**
        El desempeño del período actual muestra un **{tendencia} del {abs(delta_total_percent):.1f}%** en el tonelaje total, alcanzando **{kpi1_total:,.2f} toneladas**.
        """)
        
        # Análisis de Productos
        if not producto_comp_df.empty:
            prod_crecimiento = producto_comp_df.nlargest(1, 'Variación Absoluta').iloc[0]
            prod_declive = producto_comp_df.nsmallest(1, 'Variación Absoluta').iloc[0]
            st.markdown(f"""
            #### **2. Dinámica del Portafolio de Productos:**
            - **Motor de Crecimiento:** El producto **{prod_crecimiento[PRODUCTO_COLUMN]}** fue el principal impulsor de este resultado, aportando un crecimiento de **{prod_crecimiento['Variación Absoluta']:,.2f} Toneladas**.
            - **Área de Atención:** Es crucial investigar la caída en **{prod_declive[PRODUCTO_COLUMN]}**, que experimentó una contracción de **{abs(prod_declive['Variación Absoluta']):,.2f} Toneladas**. Esto podría indicar un cambio en la demanda o un desafío en la cadena de suministro.
            """)
        
        # Análisis de Transportistas
        if not empresa_comp_df.empty:
            empresa_crecimiento = empresa_comp_df.nlargest(1, 'Variación Absoluta').iloc[0]
            empresa_declive = empresa_comp_df.nsmallest(1, 'Variación Absoluta').iloc[0]
            st.markdown(f"""
            #### **3. Desempeño de Socios Logísticos:**
            - **Socio Clave en Crecimiento:** **{empresa_crecimiento[EMPRESA_COLUMN]}** se destacó como un socio estratégico, incrementando su volumen transportado en **{empresa_crecimiento['Variación Absoluta']:,.2f} Toneladas**.
            - **Riesgo Operativo:** Se identifica un riesgo en el desempeño de **{empresa_declive[EMPRESA_COLUMN]}**, cuyo volumen disminuyó en **{abs(empresa_declive['Variación Absoluta']):,.2f} Toneladas**. Se recomienda una revisión inmediata de su rendimiento y capacidad.
            """)
        
        # Conclusión y Recomendaciones
        st.markdown(f"""
        #### **4. Recomendaciones Estratégicas:**
        - **Acción Inmediata:** Focalizar los esfuerzos en entender las causas de la contracción del producto **{prod_declive[PRODUCTO_COLUMN]}**.
        - **Capitalizar Oportunidades:** Reforzar la relación y la planificación logística con **{empresa_crecimiento[EMPRESA_COLUMN]}** para maximizar el potencial de crecimiento.
        """)

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
        df_maestro[EMPRESA_COLUMN] = df_maestro[EMPRESA_COLUMN].apply(lambda x: normalizar_nombre_empresa(x, empresa_mapping))

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