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
        
        # Diccionario para verificar la existencia de columnas esenciales
        column_checks = {
            FECHA_COLUMN: "fecha", VOLUME_COLUMN: "tonelaje/volumen",
            PRODUCTO_COLUMN: "producto", EMPRESA_COLUMN: "empresa de transporte",
            DESTINO_COLUMN: "destino"
        }
        
        missing_cols = [name for name, desc in column_checks.items() if name not in df.columns]
        if missing_cols:
            st.error(f"Error: Faltan las siguientes columnas esenciales en el archivo cargado: {', '.join(missing_cols)}. Por favor, verifica el archivo o ajusta los nombres en el script.")
            st.stop()
        
        # 1. Convertir FECHA de forma robusta
        df[FECHA_COLUMN] = pd.to_datetime(df[FECHA_COLUMN], errors='coerce')
        if not pd.api.types.is_datetime64_any_dtype(df[FECHA_COLUMN]):
            st.error(f"La columna '{FECHA_COLUMN}' no pudo ser convertida a formato de fecha. Por favor, asegúrate de que el formato sea DD-MM-YYYY o similar.")
            st.stop()
        df.dropna(subset=[FECHA_COLUMN], inplace=True)
        
        # 2. Convertir TONELAJE a numérico
        df[VOLUME_COLUMN] = pd.to_numeric(df[VOLUME_COLUMN], errors='coerce').fillna(0)

        # 3. Mapear Empresas
        df[EMPRESA_COLUMN] = df[EMPRESA_COLUMN].map(empresa_mapping).fillna(df[EMPRESA_COLUMN])
        
        # --- Filtro por Fecha ---
        st.sidebar.header("Filtros de Datos")
        
        fechas_disponibles_ordenadas = sorted(df[FECHA_COLUMN].dt.date.unique())
        if not fechas_disponibles_ordenadas:
            st.warning("No se encontraron fechas válidas en el archivo. Verifica el contenido de tu columna de fecha.")
            st.stop()
        
        fecha_seleccionada = st.sidebar.date_input(
            f"Selecciona una {FECHA_COLUMN}:",
            value=fechas_disponibles_ordenadas[0],
            min_value=fechas_disponibles_ordenadas[0],
            max_value=fechas_disponibles_ordenadas[-1]
        )
        
        df_filtrado_fecha = df[df[FECHA_COLUMN].dt.date == fecha_seleccionada]
        
        # --- Renderizado del Dashboard ---
        st.header(f"Análisis para el {fecha_seleccionada.strftime('%d-%m-%Y')}")
        
        if not df_filtrado_fecha.empty:
            # --- KPIs ---
            tonelaje_total_dia = df_filtrado_fecha[VOLUME_COLUMN].sum()
            productos_distintos_dia = df_filtrado_fecha[PRODUCTO_COLUMN].nunique()
            col1, col2 = st.columns(2)
            col1.metric(label=f"Tonelaje Total del Día", value=f"{tonelaje_total_dia:,.2f} Ton")
            col2.metric(label=f"Productos Distintos", value=f"{productos_distintos_dia}")

            # --- Cálculos para Gráficos ---
            
            # --- GRÁFICO 1: TONELAJE Y GUÍAS POR EMPRESA (COMBINADO) ---
            tonelaje_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
            guias_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
            if not tonelaje_por_empresa.empty:
                empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left').fillna(0)
                
                fig_empresa_combinado = px.bar(empresa_data,
                                               x=EMPRESA_COLUMN, y=VOLUME_COLUMN,
                                               title=f'Tonelaje y Guías por Empresa',
                                               labels={EMPRESA_COLUMN: 'Empresa', VOLUME_COLUMN: 'Tonelaje'})
                fig_empresa_combinado.add_scatter(x=empresa_data[EMPRESA_COLUMN], 
                                                  y=empresa_data['CANTIDAD_GUIAS'], 
                                                  mode='lines+markers', name='Guías', 
                                                  yaxis='y2', 
                                                  line=dict(color='firebrick', width=2, dash='dash'))
                fig_empresa_combinado.update_layout(yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right'))
                st.plotly_chart(fig_empresa_combinado, use_container_width=True)
            else:
                st.warning("No hay datos de empresa para mostrar en el gráfico.")

            # --- GRÁFICO 2: TONELAJE Y GUÍAS POR PRODUCTO (COMBINADO) ---
            tonelaje_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
            guias_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
            if not tonelaje_por_producto.empty:
                producto_data_combinado = pd.merge(tonelaje_por_producto, guias_por_producto, on=PRODUCTO_COLUMN, how='left').fillna(0)
                
                fig_producto_combinado = px.bar(producto_data_combinado,
                                                  x=PRODUCTO_COLUMN, y=VOLUME_COLUMN,
                                                  title=f'Tonelaje y Guías por Producto',
                                                  labels={PRODUCTO_COLUMN: 'Producto', VOLUME_COLUMN: 'Tonelaje'})
                fig_producto_combinado.add_scatter(x=producto_data_combinado[PRODUCTO_COLUMN], 
                                                     y=producto_data_combinado['CANTIDAD_GUIAS'], 
                                                     mode='lines+markers', name='Guías', 
                                                     yaxis='y2', 
                                                     line=dict(color='green', width=2, dash='dot'))
                fig_producto_combinado.update_layout(yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right'))
                st.plotly_chart(fig_producto_combinado, use_container_width=True)
            else:
                st.warning("No hay datos de producto para mostrar en el gráfico.")
            
            # --- GRÁFICO 3: TONELAJE POR DESTINO ---
            tonelaje_por_destino = df_filtrado_fecha.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
            if not tonelaje_por_destino.empty:
                fig_destino = px.bar(tonelaje_por_destino,
                                     x=DESTINO_COLUMN,
                                     y=VOLUME_COLUMN,
                                     title=f'Tonelaje por Destino',
                                     labels={DESTINO_COLUMN: 'Destino', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                     color_discrete_sequence=px.colors.qualitative.Prism)
                st.plotly_chart(fig_destino, use_container_width=True)
            else:
                st.warning("No hay datos de destino para mostrar en el gráfico.")
            

            # --- Tabla de Datos Detallados ---
            st.subheader("📋 Tabla de Datos Detallados")
            columnas_tabla = [FECHA_COLUMN, PRODUCTO_COLUMN, DESTINO_COLUMN, EMPRESA_COLUMN, VOLUME_COLUMN]
            columnas_existentes_tabla = [col for col in columnas_tabla if col in df]
            st.dataframe(df_filtrado_fecha[columnas_existentes_tabla])

        else:
            st.warning("No se encontraron datos para la fecha seleccionada.")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        st.exception(e) # Muestra el traceback completo
else:
    st.info("Carga tu archivo Excel para comenzar.")