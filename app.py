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
VOLUME_COLUMN = 'TONELAJE'           # Columna que contiene el volumen/tonelaje.
# !!! IMPORTANTE: Confirmado que la columna para las empresas es 'EMPRESA DE TRANSPORTE'.
EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE' 
FECHA_COLUMN = 'FECHA'              # Columna que contiene las fechas.
PRODUCTO_COLUMN = 'PRODUCTO'        # Columna que contiene los nombres de los productos.
DESTINO_COLUMN = 'DESTINO'          # Columna que contiene los destinos.
# Columna para identificar guías únicas. Si no hay una columna específica,
# se contarán las filas por producto. Déjala como None si no existe.
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
            df[FECHA_COLUMN] = pd.to_datetime(df[FECHA_COLUMN], format='%d-%m-%Y', errors='coerce')
        except ValueError:
            try:
                df[FECHA_COLUMN] = pd.to_datetime(df[FECHA_COLUMN], errors='coerce') # Intenta parseo automático
            except Exception as e:
                st.error(f"Error al convertir la columna '{FECHA_COLUMN}'. Asegúrate de que tenga un formato de fecha reconocible. Detalle: {e}")
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
        
        # Validar Columna de Empresa - ¡CONFIRMADO COMO 'EMPRESA DE TRANSPORTE'!
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

            # 1. Gráfico por Empresa
            tonelaje_por_empresa = None
            if EMPRESA_COLUMN in df_filtrado_fecha.columns: # Doble chequeo por si acaso
                tonelaje_por_empresa = df_filtrado_fecha.groupby(EMPRESA_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()

            # 2. Gráfico por Destino del Producto
            tonelaje_por_destino = df_filtrado_fecha.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()

            # 3. Gráfico por Cantidad de Guías Emitidas por Producto
            if GUIA_COLUMN_IDENTIFIER and GUIA_COLUMN_IDENTIFIER in df_filtrado_fecha.columns:
                guias_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN)[GUIA_COLUMN_IDENTIFIER].nunique().reset_index(name='CANTIDAD_GUIAS')
            else: # Contar filas si no hay columna específica para guías
                guias_por_producto = df_filtrado_fecha.groupby(PRODUCTO_COLUMN).size().reset_index(name='CANTIDAD_GUIAS')

            # 4. Gráfico por Tonelaje de Cada Producto
            tonelaje_por_producto_detail = df_filtrado_fecha.groupby(PRODUCTO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()

            # 5. Gráfico por Cantidad de Regulaciones que tenga cada Producto
            if all(col in df_filtrado_fecha.columns for col in REGULACION_COLUMNS_TO_COUNT):
                df_temp_regulaciones = df_filtrado_fecha.copy()
                for col in REGULACION_COLUMNS_TO_COUNT:
                    df_temp_regulaciones[f'tiene_{col}'] = df_temp_regulaciones[col].apply(lambda x: 1 if pd.notna(x) else 0)

                columnas_a_sumar = [f'tiene_{col}' for col in REGULACION_COLUMNS_TO_COUNT]
                regulaciones_por_producto = df_temp_regulaciones.groupby(PRODUCTO_COLUMN)[columnas_a_sumar].sum().sum(axis=1).reset_index(name='CANTIDAD_REGULACIONES')
            else:
                regulaciones_por_producto = pd.DataFrame()


            # --- Insights Clave ---
            st.subheader("💡 Insights Clave")

            # Insight 1: Producto con Mayor Tonelaje
            if not tonelaje_por_producto_detail.empty:
                producto_mas_tonelaje_detail = tonelaje_por_producto_detail.iloc[0]
                mayor_tonelaje_prod_detail = producto_mas_tonelaje_detail[VOLUME_COLUMN]
                porcentaje_del_total_detail = (mayor_tonelaje_prod_detail / tonelaje_total_dia) * 100 if tonelaje_total_dia > 0 else 0
                st.markdown(f"- El producto con mayor volumen de tonelaje fue **'{producto_mas_tonelaje_detail[PRODUCTO_COLUMN]}'** con **{mayor_tonelaje_prod_detail:,.2f} toneladas**, representando el **{porcentaje_del_total_detail:.2f}%** del total diario.")
            else:
                st.markdown("- No hay datos de tonelaje por producto para esta fecha.")

            # Insight 2: Producto con Más Guías Emitidas
            if not guias_por_producto.empty:
                producto_mas_guias = guias_por_producto.iloc[0]
                st.markdown(f"- El producto con más guías emitidas fue **'{producto_mas_guias[PRODUCTO_COLUMN]}'** con **{producto_mas_guias['CANTIDAD_GUIAS']} guías**.")
            else:
                st.markdown("- No hay datos de guías por producto para esta fecha.")
                
            # Insight 3: Producto con Más Regulaciones
            if not regulaciones_por_producto.empty and 'CANTIDAD_REGULACIONES' in regulaciones_por_producto.columns:
                producto_mas_reg = regulaciones_por_producto.iloc[0]
                st.markdown(f"- El producto con más regulaciones registradas fue **'{producto_mas_reg[PRODUCTO_COLUMN]}'** con **{producto_mas_reg['CANTIDAD_REGULACIONES']} regulaciones**.")
            else:
                st.markdown("- No hay datos suficientes para determinar el producto con más regulaciones o las columnas de regulación no existen/no tienen datos.")


            # --- Gráficos ---
            st.subheader("📈 Visualizaciones")

            # Gráfico 1: Por Empresa
            if tonelaje_por_empresa is not None and not tonelaje_por_empresa.empty:
                fig_empresa = px.bar(tonelaje_por_empresa,
                                     x=EMPRESA_COLUMN, y=VOLUME_COLUMN,
                                     title=f'Tonelaje por Empresa - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                     labels={EMPRESA_COLUMN: 'Empresa', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                     color_discrete_sequence=px.colors.qualitative.Vivid)
                st.plotly_chart(fig_empresa, use_container_width=True)
            elif EMPRESA_COLUMN in df_filtrado_fecha.columns:
                 st.warning("No hay datos de tonelaje por empresa para mostrar el gráfico.")


            # Gráfico 2: Por Destino del Producto
            if not tonelaje_por_destino.empty:
                fig_destino = px.bar(tonelaje_por_destino,
                                     x=DESTINO_COLUMN, y=VOLUME_COLUMN,
                                     title=f'Tonelaje por Destino - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                     labels={DESTINO_COLUMN: 'Destino', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                     color_discrete_sequence=px.colors.qualitative.Alphabet)
                st.plotly_chart(fig_destino, use_container_width=True)
            else:
                st.warning("No hay datos de tonelaje por destino para mostrar el gráfico.")

            # Gráfico 3: Cantidad de Guías Emitidas por Producto
            if not guias_por_producto.empty:
                fig_guias = px.bar(guias_por_producto,
                                   x=PRODUCTO_COLUMN, y='CANTIDAD_GUIAS',
                                   title=f'Cantidad de Guías por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                   labels={PRODUCTO_COLUMN: 'Producto', 'CANTIDAD_GUIAS': 'Nro. de Guías'},
                                   color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig_guias, use_container_width=True)
            else:
                st.warning("No hay datos de guías por producto para mostrar el gráfico.")

            # Gráfico 4: Tonelaje de Cada Producto
            if not tonelaje_por_producto_detail.empty:
                fig_producto_tonelaje = px.bar(tonelaje_por_producto_detail,
                                                x=PRODUCTO_COLUMN, y=VOLUME_COLUMN,
                                                title=f'Tonelaje por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                                labels={PRODUCTO_COLUMN: 'Producto', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                                color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_producto_tonelaje, use_container_width=True)
            else:
                st.warning("No hay datos de tonelaje por producto para mostrar el gráfico.")

            # Gráfico 5: Cantidad de Regulaciones por Producto
            if not regulaciones_por_producto.empty and 'CANTIDAD_REGULACIONES' in regulaciones_por_producto.columns:
                 fig_regulaciones = px.bar(regulaciones_por_producto,
                                           x=PRODUCTO_COLUMN, y='CANTIDAD_REGULACIONES',
                                           title=f'Regulaciones por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                           labels={PRODUCTO_COLUMN: 'Producto', 'CANTIDAD_REGULACIONES': 'Nro. de Regulaciones'},
                                           color_discrete_sequence=px.colors.qualitative.Plotly)
                 st.plotly_chart(fig_regulaciones, use_container_width=True)
            else:
                st.warning("No se ha podido calcular el gráfico de regulaciones. Verifica la existencia y el contenido de las columnas de regulación.")


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