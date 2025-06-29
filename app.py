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

        # 2. Validar y Preprocesar Columnas Numéricas y de Categoría
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
        df[EMPRESA_COLUMN] = df[EMPRESA_COLUMN].map(empresa_mapping).fillna(df[EMPRESA_COLUMN])
        
        for col in REGULACION_COLUMNS_TO_COUNT:
            if col not in df.columns:
                st.warning(f"Advertencia: No se encontró la columna de regulación '{col}'. El análisis de regulaciones podría verse afectado.")


        # --- Filtro por Fecha (aquí se soluciona el problema de la pantalla en blanco) ---
        fechas_disponibles_ordenadas = sorted(df[FECHA_COLUMN].dt.date.unique())
        
        if not fechas_disponibles_ordenadas:
            st.warning("No se encontraron fechas válidas en el archivo cargado después del preprocesamiento. El archivo podría estar vacío o tener problemas de formato.")
            st.stop()
        
        fecha_por_defecto = fechas_disponibles_ordenadas[0]
        fecha_seleccionada = st.sidebar.date_input(
            f"Selecciona una {FECHA_COLUMN}:", value=fecha_por_defecto
        )
        fecha_dt_seleccionada = pd.to_datetime(fecha_seleccionada)
        df_filtrado_fecha = df[df[FECHA_COLUMN].dt.date == fecha_dt_seleccionada.date()]


        # --- Renderizado del Dashboard ---
        st.header(f"Análisis para el {fecha_dt_seleccionada.strftime('%d-%m-%Y')}")

        if not df_filtrado_fecha.empty:
            tonelaje_total_dia = df_filtrado_fecha[VOLUME_COLUMN].sum()
            productos_distintos_dia = df_filtrado_fecha[PRODUCTO_COLUMN].nunique()

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label=f"Tonelaje Total del Día ({VOLUME_COLUMN})", value=f"{tonelaje_total_dia:,.2f} Ton")
            with col2:
                st.metric(label=f"{PRODUCTO_COLUMN}s Distintos", value=productos_distintos_dia)

            # --- Agrupación de Datos para Gráficos y Insights ---

            # Inicializar DataFrames que podrían no tener datos o ser calculados condicionalmente
            tonelaje_por_empresa = pd.DataFrame()
            guias_por_empresa = pd.DataFrame()
            empresa_data = pd.DataFrame()
            
            tonelaje_por_destino = pd.DataFrame()
            guias_por_producto = pd.DataFrame()
            tonelaje_por_producto_detail = pd.DataFrame()
            regulaciones_por_producto = pd.DataFrame()
            
            # --- Insights Clave (AHORA CALCULADOS DENTRO DE LOS BLOQUES DE GRÁFICOS) ---

            # --- GRÁFICO 1: TONELAJE Y GUÍAS POR EMPRESA (COMBINADO) ---
            if EMPRESA_COLUMN in df_filtrado_fecha.columns:
                tonelaje_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
                guias_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
                
                if not tonelaje_por_empresa.empty and not guias_por_empresa.empty:
                    empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left').fillna(0)
                
                if not empresa_data.empty:
                    fig_empresa_combinado = px.bar(empresa_data,
                                                   x=EMPRESA_COLUMN,
                                                   y=VOLUME_COLUMN,
                                                   title=f'Tonelaje y Guías por Empresa - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                                   labels={EMPRESA_COLUMN: 'Empresa', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                                   color_discrete_sequence=px.colors.qualitative.Vivid)
                    
                    if 'CANTIDAD_GUIAS' in empresa_data.columns:
                        fig_empresa_combinado.add_scatter(x=empresa_data[EMPRESA_COLUMN], 
                                                          y=empresa_data['CANTIDAD_GUIAS'], 
                                                          mode='lines+markers', 
                                                          name='Guías', 
                                                          yaxis='y2', 
                                                          line=dict(color='firebrick', width=2, dash='dash'))
                        
                        fig_empresa_combinado.update_layout(
                            yaxis=dict(title='Tonelaje (toneladas)', color='blue'),
                            yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right', color='red'),
                            xaxis=dict(title='Empresa')
                        )
                        st.plotly_chart(fig_empresa_combinado, use_container_width=True)
                else:
                    st.warning("No hay datos de tonelaje o guías por empresa para mostrar el gráfico.")
            else:
                st.warning(f"No se encontró la columna '{EMPRESA_COLUMN}'. El gráfico por empresa no se mostrará.")


            # --- GRÁFICO 2: TONELAJE Y GUÍAS POR PRODUCTO (COMBINADO) ---
            if PRODUCTO_COLUMN in df_filtrado_fecha.columns:
                tonelaje_por_producto_detail = df_filtrado_fecha.groupby(PRODUCTO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
                guias_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
                
                if not tonelaje_por_producto_detail.empty and not guias_por_producto.empty:
                    producto_data_combinado = pd.merge(tonelaje_por_producto_detail, guias_por_producto, on=PRODUCTO_COLUMN, how='left').fillna(0)

                    fig_producto_combinado = px.bar(producto_data_combinado,
                                                    x=PRODUCTO_COLUMN,
                                                    y=VOLUME_COLUMN,
                                                    title=f'Tonelaje y Guías por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                                    labels={PRODUCTO_COLUMN: 'Producto', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                    
                    if 'CANTIDAD_GUIAS' in producto_data_combinado.columns:
                        fig_producto_combinado.add_scatter(x=producto_data_combinado[PRODUCTO_COLUMN], 
                                                          y=producto_data_combinado['CANTIDAD_GUIAS'], 
                                                          mode='lines+markers', 
                                                          name='Guías', 
                                                          yaxis='y2', 
                                                          line=dict(color='firebrick', width=2, dash='dash'))
                        
                        fig_producto_combinado.update_layout(
                            yaxis=dict(title='Tonelaje (toneladas)', color='blue'),
                            yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right', color='red'),
                            xaxis=dict(title='Producto')
                        )
                        st.plotly_chart(fig_producto_combinado, use_container_width=True)
                else:
                    st.warning("No hay datos de tonelaje o guías por producto para mostrar el gráfico.")
            else:
                st.warning(f"No se encontró la columna '{PRODUCTO_COLUMN}'. El gráfico por producto no se mostrará.")
            
            
            # --- Tabla de Datos Detallados ---
            # ... (sección de tabla detallada, al final para mostrar todo)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        st.exception(e) # Muestra el traceback completo
else:
    st.info("Carga tu archivo Excel para comenzar.")