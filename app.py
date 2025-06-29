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
st.markdown("### Análisis de Tonelaje por Fecha, Producto y Sector")

# --- Carga de Datos ---

# Variable para almacenar el DataFrame
df = None

# Widget para subir archivos
uploaded_file = st.sidebar.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

# --- Preprocesamiento de Datos ---

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("Archivo cargado correctamente!")

        # 1. Convertir la columna 'FECHA' a formato datetime
        # Asumiendo que tu fecha está en formato DD-MM-YYYY.
        # Si tu formato es diferente, ajústalo en `format=`.
        # Intenta con formatos comunes si el primero falla.
        try:
            df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d-%m-%Y', errors='coerce')
        except ValueError:
            try:
                df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce') # Intenta con parseo automático
            except Exception as e:
                st.error(f"Error al convertir la columna 'FECHA'. Asegúrate de que tenga un formato de fecha reconocible. Detalle: {e}")
                st.stop()

        # Eliminar filas donde la conversión de fecha falló
        df.dropna(subset=['FECHA'], inplace=True)

        # 2. Limpiar y convertir la columna de volumen/tonelaje
        # ASUME que tu columna de volumen se llama 'TONELAJE'.
        # Si se llama diferente (ej: 'Volumen', 'Cantidad'), cámbialo aquí:
        VOLUME_COLUMN = 'TONELAJE' # <-- CAMBIA ESTO SI TU COLUMNA SE LLAMA DIFERENTE

        if VOLUME_COLUMN not in df.columns:
            st.error(f"Error: No se encontró la columna '{VOLUME_COLUMN}'. Por favor, verifica el nombre de la columna en tu archivo Excel y ajústalo en la variable `VOLUME_COLUMN` en este script.")
            st.stop()

        df[VOLUME_COLUMN] = pd.to_numeric(df[VOLUME_COLUMN], errors='coerce')
        df.dropna(subset=[VOLUME_COLUMN], inplace=True)

        # Asegurarse de que las columnas de agrupación existan
        if 'PRODUCTO' not in df.columns:
            st.error("Error: No se encontró la columna 'PRODUCTO' en el archivo Excel.")
            st.stop()
        if 'SECTOR' not in df.columns:
            st.warning("Advertencia: No se encontró la columna 'SECTOR'. Algunas visualizaciones y análisis no estarán disponibles.")

        # --- Filtro por Fecha ---
        st.sidebar.header("Filtros de Datos")

        # Obtener las fechas únicas disponibles para el selector
        fechas_disponibles = df['FECHA'].dt.date.unique()
        fechas_disponibles_ordenadas = sorted(fechas_disponibles)

        if not fechas_disponibles_ordenadas:
            st.warning("No se encontraron fechas válidas en el archivo cargado.")
            st.stop()

        # Establecer una fecha por defecto, si es posible, la primera disponible en los datos
        fecha_por_defecto = fechas_disponibles_ordenadas[0]

        fecha_seleccionada = st.sidebar.date_input(
            "Selecciona una Fecha:",
            value=fecha_por_defecto,
            min_value=fechas_disponibles_ordenadas[0],
            max_value=fechas_disponibles_ordenadas[-1]
        )

        # Convertir la fecha seleccionada por el usuario a un formato comparable con la columna 'FECHA'
        fecha_dt_seleccionada = pd.to_datetime(fecha_seleccionada)

        # Filtrar el DataFrame según la fecha seleccionada
        df_filtrado_fecha = df[df['FECHA'].dt.date == fecha_dt_seleccionada.date()]

        # --- Renderizado del Dashboard ---
        st.header(f"Análisis para el {fecha_dt_seleccionada.strftime('%d-%m-%Y')}")

        if not df_filtrado_fecha.empty:
            tonelaje_total_dia = df_filtrado_fecha[VOLUME_COLUMN].sum()
            productos_distintos_dia = df_filtrado_fecha['PRODUCTO'].nunique()
            sectores_presentes = df_filtrado_fecha['SECTOR'].nunique() if 'SECTOR' in df_filtrado_fecha.columns else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Tonelaje Total del Día", value=f"{tonelaje_total_dia:,.2f} Ton")
            with col2:
                st.metric(label="Productos Distintos", value=productos_distintos_dia)
            if 'SECTOR' in df_filtrado_fecha.columns:
                with col3:
                    st.metric(label="Sectores Presentes", value=sectores_presentes)

            # --- Agrupación de Datos para Gráficos y Insights ---
            tonelaje_por_producto = df_filtrado_fecha.groupby('PRODUCTO')[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
            tonelaje_por_sector = None
            if 'SECTOR' in df_filtrado_fecha.columns:
                tonelaje_por_sector = df_filtrado_fecha.groupby('SECTOR')[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()

            # --- Insights Clave ---
            st.subheader("💡 Insights Clave")

            # Insight 1: Producto con Mayor Tonelaje
            if not tonelaje_por_producto.empty:
                producto_mas_tonelaje = tonelaje_por_producto.iloc[0]
                mayor_tonelaje_prod = producto_mas_tonelaje[VOLUME_COLUMN]
                porcentaje_del_total = (mayor_tonelaje_prod / tonelaje_total_dia) * 100 if tonelaje_total_dia > 0 else 0
                st.markdown(f"- El producto con mayor volumen de tonelaje fue **'{producto_mas_tonelaje['PRODUCTO']}'** con **{mayor_tonelaje_prod:,.2f} toneladas**, representando el **{porcentaje_del_total:.2f}%** del total diario.")
            else:
                st.markdown("- No hay datos de tonelaje por producto para esta fecha.")

            # Insight 2: Sector con Mayor Tonelaje
            if tonelaje_por_sector is not None and not tonelaje_por_sector.empty:
                sector_mas_tonelaje = tonelaje_por_sector.iloc[0]
                st.markdown(f"- El sector que movió más tonelaje fue **'{sector_mas_tonelaje['SECTOR']}'** con **{sector_mas_tonelaje[VOLUME_COLUMN]:,.2f} toneladas**.")
            elif 'SECTOR' in df_filtrado_fecha.columns:
                st.markdown("- No hay datos de sector disponibles para el análisis.")

            # --- Gráficos ---
            st.subheader("📈 Visualizaciones")

            # Gráfico de Barras: Tonelaje por Producto
            if not tonelaje_por_producto.empty:
                fig_producto = px.bar(tonelaje_por_producto,
                                        x='PRODUCTO',
                                        y=VOLUME_COLUMN,
                                        title=f'Tonelaje por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                        labels={'PRODUCTO': 'Producto', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                        color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_producto.update_layout(xaxis_title="Producto", yaxis_title="Tonelaje (toneladas)")
                st.plotly_chart(fig_producto, use_container_width=True)
            else:
                st.warning("No hay datos de tonelaje por producto para mostrar el gráfico.")

            # Gráfico de Barras: Tonelaje por Sector
            if tonelaje_por_sector is not None and not tonelaje_por_sector.empty:
                fig_sector = px.bar(tonelaje_por_sector,
                                    x='SECTOR',
                                    y=VOLUME_COLUMN,
                                    title=f'Tonelaje por Sector - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
                                    labels={'SECTOR': 'Sector', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                                    color_discrete_sequence=px.colors.qualitative.Set3)
                fig_sector.update_layout(xaxis_title="Sector", yaxis_title="Tonelaje (toneladas)")
                st.plotly_chart(fig_sector, use_container_width=True)
            elif 'SECTOR' in df_filtrado_fecha.columns:
                st.warning("No hay datos de tonelaje por sector para mostrar el gráfico.")

            # --- Tabla de Datos Filtrados ---
            st.subheader("📋 Tabla de Datos Detallados")
            columnas_tabla = ['SECTOR', 'PRODUCTO', 'DESTINO', VOLUME_COLUMN]
            columnas_existentes_tabla = [col for col in columnas_tabla if col in df_filtrado_fecha.columns]
            st.dataframe(df_filtrado_fecha[columnas_existentes_tabla], use_container_width=True)

        else:
            st.warning(f"No se encontraron datos para la fecha seleccionada: {fecha_dt_seleccionada.strftime('%d-%m-%Y')}")
            st.info("Por favor, selecciona otra fecha del menú lateral.")

    except Exception as e:
        st.error(f"Ocurrió un error durante el procesamiento de los datos: {e}")

else:
    st.info("Por favor, carga tu archivo Excel (.xlsx) en la barra lateral para comenzar.")

# --- Pie de Página ---
st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado con Streamlit, Pandas y Plotly.")