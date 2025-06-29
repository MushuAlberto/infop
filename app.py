import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🐞 Módulo de Depuración de Datos")
st.header("Por favor, carga tu archivo Excel para analizar su estructura.")

# --- Configuración de Nombres de Columnas (SOLO PARA REFERENCIA, no se usa aún) ---
# Aquí están los nombres que HEMOS INTENTADO USAR:
# VOLUME_COLUMN = 'TONELAJE'
# EMPRESA_COLUMN = 'EMPRESA DE TRANSPORTE'  # También hemos probado 'L' y 'PATENTE'
# FECHA_COLUMN = 'FECHA'
# PRODUCTO_COLUMN = 'PRODUCTO'
# DESTINO_COLUMN = 'DESTINO'

# --- Carga de Datos ---
uploaded_file = st.sidebar.file_uploader(
    "Carga tu archivo Excel para diagnóstico (.xlsx)",
    type=["xlsx"]
)

if uploaded_file is not None:
    st.success("✅ **Archivo cargado!** Procediendo a analizarlo...")

    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ **Pandas leyó el archivo Excel exitosamente!**")
        st.balloons() # Pequeña celebración

        # --- ANÁLISIS DE ESTRUCTURA ---
        st.subheader("1. Nombres de Columnas Detectados")
        st.info("Esta es la lista de los nombres de columnas EXACTOS que Pandas encontró en tu archivo. ¡Esta es la información más importante!")
        
        columnas_detectadas = df.columns.tolist()
        st.code(columnas_detectadas) # Muestra las columnas en un formato de código para copiar fácil

        st.subheader("2. Información General del DataFrame")
        st.text("Aquí vemos los tipos de datos que Pandas asignó a cada columna.")
        st.code(str(df.info(verbose=True, show_counts=True)))

        st.subheader("3. Primeras 10 Filas del Archivo Cargado")
        st.info("Así es como se ven las primeras 10 filas de tus datos después de cargarlos.")
        st.dataframe(df.head(10))

    except Exception as e:
        st.error(f"❌ **Ocurrió un error al intentar leer o procesar el archivo Excel.**")
        st.exception(e) # Muestra el traceback completo del error

else:
    st.info("Esperando que cargues un archivo Excel para poder analizarlo...")