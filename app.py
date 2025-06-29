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

# --- Configuración de Nombres de Columnas (AJUSTADO SEGÚN TU INFORMACIÓN) ---
VOLUME_COLUMN = 'TONELAJE'           # Columna que contiene el volumen/tonelaje.
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE' # Columna que contiene los nombres de las empresas de transporte.
FECHA_COLUMN = 'FECHA'              # Columna que contiene las fechas.
PRODUCTO_COLUMN = 'PRODUCTO'        # Columna que contiene los nombres de los productos.
DESTINO_COLUMN = 'DESTINO'          # Columna que contiene los destinos.
# Columna para identificar guías únicas. Si no hay una columna específica,
# se contarán las filas por producto. Como confirmaste que solo se deben contar filas, se mantiene como None.
GUIA_COLUMN_IDENTIFIER = None       
# Lista de columnas que indican la presencia de una regulación para un producto.
REGULACION_COLUMNS_TO_COUNT = ['REGULACION 1', 'REGULACION 2', 'REGULACION 3'] 

# --- Mapeo de Nombres de Empresas ---
empresa_mapping = {
    "JORQUERA TRANSPORTE S. A.": "JORQUERA TRANSPORTE S. A.",
    "JORQUERA TRANSPORTE S A": "JORQUERA TRANSPORTE S. A.",
    "MINING SERVICES AND DERIVATES": "M S & D SPA",
    "MINING SERVICES AND DERIVATES SPA": "M S & D SPA",
    "M S AND D": "M S & D SPA",
    "M S AND D SPA": "M S & D SPA",
    "MSANDD SPA": "M S & D SPA",
    "M S D": "M S & D SPA",
    "M S D SPA": "M S & D SPA",
    "M S & D": "M S & D SPA",
    "MS&D SPA": "M S & D SPA",
    "M AND Q SPA": "M&Q SPA",
    "M AND Q": "M&Q SPA",
    "M Q SPA": "M&Q SPA",
    "MQ SPA": "M&Q SPA",
    "MANDQ SPA": "M&Q SPA",
    "MINING AND QUARRYING SPA": "M&Q SPA",
    "MINING AND QUARRYNG SPA": "M&Q SPA",
    "AG SERVICE SPA": "AG SERVICES SPA",
    "AG SERVICES SPA": "AG SERVICES SPA",
    "COSEDUCAM S A": "COSEDUCAM S A",
    "COSEDUCAM": "COSEDUCAM S A"
}

# --- Carga de Datos ---
df = None
uploaded_file = st.sidebar.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("Archivo cargado correctamente!")

        # --- Preprocesamiento de Datos ---
        # 1. Convertir FECHA
        if FECHA_COLUMN not in df.columns:
            st.error(f"Error: No se encontró la columna '{FECHA_COLUMN}'. Por favor, asegúrate de que exista y se llame exactamente '{FECHA_COLUMN}'.")
            st.stop()
        try:
            # Formato de fecha confirmado: DD-MM-YYYY
            df[FECHA_COLUMN] = pd.to_datetime(df[FECHA_COLUMN], format='%d-%m-%Y', errors='coerce')
        except ValueError:
            try:
                df[FECHA_COLUMN] = pd.to_datetime(df[FECHA_COLUMN], errors='coerce') # Intenta parseo automático como fallback
            except Exception as e:
                st.error(f"Error al convertir la columna '{FECHA_COLUMN}'. Asegúrate de que tenga un formato de fecha reconocible (ej. DD-MM-YYYY). Detalle: {e}")
                st.stop()
        df.dropna(subset=[FECHA_COLUMN], inplace=True)

        # 2. Validar VOLUME_COLUMN
        if VOLUME_COLUMN not in df.columns:
            st.error(f"Error: No se encontró la columna '{VOLUME_COLUMN}'. Por favor, verifica el nombre de la columna en tu archivo Excel y ajústalo en la variable `VOLUME_COLUMN`.")
            st.stop()
        df[VOLUME_COLUMN] = pd.to_numeric(df[VOLUME_COLUMN], errors='coerce')
        df.dropna(subset=[VOLUME_COLUMN], inplace=True)

        # 3. Validar columnas clave
        if PRODUCTO_COLUMN not in df.columns:
            st.error(f"Error: No se encontró la columna '{PRODUCTO_COLUMN}'.")
            st.stop()
        
        if EMPRESA_COLUMN not in df.columns:
            st.error(f"Error: No se encontró la columna '{EMPRESA_COLUMN}'. Por favor, verifica que la columna para las empresas se llame exactamente '{EMPRESA_COLUMN}'.")
            st.stop()

        # Aplicar el mapeo de nombres de empresas
        df[EMPRESA_COLUMN] = df[EMPRESA_COLUMN].map(empresa_mapping).fillna(df[EMPRESA_COLUMN])


        # 4. Validar columnas de regulación
        for col in REGULACION_COLUMNS_TO_COUNT:
            if col not in df.columns:
                st.warning(f"Advertencia: No se encontró la columna de regulación '{col}'. El análisis de regulaciones podría verse afectado.")

        # --- Filtro por Fecha ---
        st.sidebar.header("Filtros de Datos")
        fechas_disponibles = df[FECHA_COLUMN].dt.date.unique()
        fechas_disponibles_ordenadas = sorted(fechas_disponibles)

        if not fechas_disponibles_ordenadas:
            st.warning("No se encontraron fechas válidas en el archivo cargado.")
            st.stop()

        fecha_por_defecto = fechas_disponibles_ordenadas[0]
        fecha_seleccionada = st.sidebar.date_input(
            f"Selecciona una {FECHA_COLUMN}:",
            value=fecha_por_defecto,
            min_value=fechas_disponibles_ordenadas[0],
            max_value=fechas_disponibles_ordenadas[-1]
        )
        fecha_dt_seleccionada = pd.to_datetime(fecha_seleccionada)
        df_filtrado_fecha = df[df[FECHA_COLUMN].dt.date == fecha_dt_seleccionada.date()]

        # --- Renderizado del Dashboard ---
        st.header(f"Análisis para el {fecha_ dt_seleccionada.strftime('%d-%m-%Y')}")

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
            empresa_data = pd.DataFrame() # Para el gráfico combinado de empresa
            
            tonelaje_por_destino = pd.DataFrame()
            guias_por_producto = pd.DataFrame()
            tonelaje_por_producto_detail = pd.DataFrame()
            regulaciones_por_producto = pd.DataFrame()

            # 1. Datos para Gráfico Combinado por Empresa (Tonelaje y Guías)
            if EMPRESA_COLUMN in df_filtrado_fecha.columns:
                tonelaje_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
                
                if GUIA_COLUMN_IDENTIFIER and GUIA_COLUMN_IDENTIFIER in df_filtrado_fecha.columns:
                    guias_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN)[GUIA_COLUMN_IDENTIFIER].nunique().reset_index(name='CANTIDAD_GUIAS')
                else: # Contar filas si no hay columna específica para guías
                    guias_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')
                
                if not tonelaje_por_empresa.empty and not guias_por_empresa.empty:
                    empresa_data = pd.merge(tonelaje_por_empresa, guias_por_empresa, on=EMPRESA_COLUMN, how='left')
                    empresa_data.fillna(0, inplace=True)
                elif not tonelaje_por_empresa.empty:
                    empresa_data = tonelaje_por_empresa
                    empresa_data['CANTIDAD_GUIAS'] = 0
                elif not guias_por_empresa.empty:
                    empresa_data = guias_por_empresa
                    empresa_data[VOLUME_COLUMN] = 0
            

            # 2. Gráfico por Destino del Producto (solo barras de tonelaje)
            if DESTINO_COLUMN in df_filtrado_fecha.columns:
                tonelaje_por_destino = df_filtrado_fecha.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
                if not tonelaje_por_destino.empty:
                    fig_destino = px.bar(tonelaje_por_destino,
                                         x=DESTINO_COLUMN, y=VOLUME_COLUMN,
                                         title=f'Tonelaje por Destino - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                         labels={DESTINO_COLUMN: 'Destino', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                         color_discrete_sequence=px.colors.qualitative.Alphabet)
                    st.plotly_chart(fig_destino, use_container_width=True)
                else:
                    st.warning("No hay datos de tonelaje por destino para mostrar el gráfico.")
            else:
                st.warning(f"No se encontró la columna '{DESTINO_COLUMN}'. El gráfico por destino no se mostrará.")

            # 3. Gráfico por Cantidad de Guías Emitidas por Producto
            if GUIA_COLUMN_IDENTIFIER and GUIA_COLUMN_IDENTIFIER in df_filtrado_fecha.columns:
                guias_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN)[GUIA_COLUMN_IDENTIFIER].nunique().reset_index(name='CANTIDAD_GUIAS')
            else: # Contar filas si no hay columna específica para guías
                guias_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')

            if not guias_por_producto.empty:
                fig_guias_producto = px.bar(guias_por_producto,
                                   x=PRODUCTO_COLUMN, y='CANTIDAD_GUIAS',
                                   title=f'Cantidad de Guías por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                   labels={PRODUCTO_COLUMN: 'Producto', 'CANTIDAD_GUIAS': 'Nro. de Guías'},
                                   color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig_guias_producto, use_container_width=True)
            else:
                st.warning("No hay datos de guías por producto para mostrar el gráfico.")

            # 4. Gráfico por Tonelaje de Cada Producto
            tonelaje_por_producto_detail = df_filtrado_fecha.groupby(PRODUCTO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
            if not tonelaje_por_producto_detail.empty:
                fig_producto_tonelaje = px.bar(tonelaje_por_producto_detail,
                                                x=PRODUCTO_COLUMN, y=VOLUME_COLUMN,
                                                title=f'Tonelaje por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                                labels={PRODUCTO_COLUMN: 'Producto', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                                color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_producto_tonelaje, use_container_width=True)
            else:
                st.warning("No hay datos de tonelaje por producto para mostrar el gráfico.")

            # 5. Gráfico por Cantidad de Regulaciones por Producto
            if all(col in df_filtrado_fecha.columns for col in REGULACION_COLUMNS_TO_COUNT):
                df_temp_regulaciones = df_filtrado_fecha.copy()
                for col in REGULACION_COLUMNS_TO_COUNT:
                    df_temp_regulaciones[f'tiene_{col}'] = df_temp_regulaciones[col].apply(lambda x: 1 if pd.notna(x) else 0)

                columnas_a_sumar = [f'tiene_{col}' for col in REGULACION_COLUMNS_TO_COUNT]
                regulaciones_por_producto = df_temp_regulaciones.groupby(PRODUCTO_COLUMN)[columnas_a_sumar].sum().sum(axis=1).reset_index(name='CANTIDAD_REGULACIONES')
                
                if not regulaciones_por_producto.empty and 'CANTIDAD_REGULACIONES' in regulaciones_por_producto.columns:
                    fig_regulaciones = px.bar(regulaciones_por_producto,
                                              x=PRODUCTO_COLUMN, y='CANTIDAD_REGULACIONES',
                                              title=f'Regulaciones por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                              labels={PRODUCTO_COLUMN: 'Producto', 'CANTIDAD_REGULACIONES': 'Nro. de Regulaciones'},
                                              color_discrete_sequence=px.colors.qualitative.Plotly)
                    st.plotly_chart(fig_regulaciones, use_container_width=True)
                else:
                    st.warning("No hay datos suficientes para calcular el gráfico de regulaciones.")
            else:
                st.warning("No se han encontrado las columnas necesarias para el gráfico de regulaciones.")


            # --- Gráfico Combinado: Tonelaje y Guías por Producto ---
            if not tonelaje_por_producto_detail.empty and not guias_por_producto.empty:
                # Aseguramos que ambos dataframes tengan las mismas columnas para el merge
                # Si uno está vacío, lo creamos con las columnas necesarias y ceros.
                if 'CANTIDAD_GUIAS' not in guias_por_producto.columns:
                    guias_por_producto['CANTIDAD_GUIAS'] = 0
                
                # Unir los datos de tonelaje y guías por producto
                producto_data_combinado = pd.merge(tonelaje_por_producto_detail, guias_por_producto, on=PRODUCTO_COLUMN, how='left')
                producto_data_combinado.fillna(0, inplace=True) # Rellenar NaN si alguna métrica falta

                if not producto_data_combinado.empty:
                    # Creamos el gráfico de barras para el tonelaje
                    fig_producto_combinado = px.bar(producto_data_combinado,
                                                    x=PRODUCTO_COLUMN,
                                                    y=VOLUME_COLUMN,
                                                    title=f'Tonelaje y Guías por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                                    labels={PRODUCTO_COLUMN: 'Producto', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                    
                    # Añadimos la línea para la cantidad de guías
                    if 'CANTIDAD_GUIAS' in producto_data_combinado.columns:
                        fig_producto_combinado.add_scatter(x=producto_data_combinado[PRODUCTO_COLUMN], 
                                                          y=producto_data_combinado['CANTIDAD_GUIAS'], 
                                                          mode='lines+markers', 
                                                          name='Guías', 
                                                          yaxis='y2', # Usar un eje Y secundario para las guías
                                                          line=dict(color='firebrick', width=2, dash='dash'))
                        
                        # Configuramos los dos ejes Y
                        fig_producto_combinado.update_layout(
                            yaxis=dict(title='Tonelaje (toneladas)', color='blue'),
                            yaxis2=dict(title='Cantidad de Guías', overlaying='y', side='right', color='red'),
                            xaxis=dict(title='Producto')
                        )
                        st.plotly_chart(fig_producto_combinado, use_container_width=True)
                    else:
                        st.warning("La columna 'CANTIDAD_GUIAS' no se pudo generar correctamente. El gráfico combinado de producto no se mostrará.")
                else:
                    st.warning("No hay datos combinados para mostrar el gráfico de producto.")
            elif PRODUCTO_COLUMN in df_filtrado_fecha.columns:
                 st.warning("No hay datos de tonelaje o guías por producto para mostrar el gráfico.")


            # --- Tabla de Datos Filtrados ---
            st.subheader("📋 Tabla de Datos Detallados")
            columnas_tabla = [FECHA_COLUMN, PRODUCTO_COLUMN, DESTINO_COLUMN, EMPRESA_COLUMN, VOLUME_COLUMN]
            columnas_existentes_tabla = [col for col in columnas_tabla if col in df_filtrado_fecha.columns]
            st.dataframe(df_filtrado_fecha[columnas_existentes_tabla], use_container_width=True)

        else:
            st.warning(f"No se encontraron datos para la fecha seleccionada: {fecha_dt_seleccionada.strftime('%d-%m-%Y')}")
            st.info("Por favor, selecciona otra fecha del menú lateral.")

    except Exception as e:
        st.error(f"Ocurrió un error durante el procesamiento de los datos: {e}")
        st.exception(e)

else:
    st.info("Por favor, carga tu archivo Excel (.xlsx) en la barra lateral para comenzar.")

# --- Pie de Página ---
st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado con Streamlit, Pandas y Plotly.")