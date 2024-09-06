import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import sys

# Configuración de la conexión a la base de datos con manejo de errores
@st.cache_resource
def init_connection():
    try:
        st.write("Iniciando conexión a la base de datos...")
        conn = mysql.connector.connect(
            host="chatgpt-do-user-3243287-0.c.db.ondigitalocean.com",
            port=25060,  # Añadido el puerto correcto
            user="doadmin",
            password="AVNS_Vfn884XHZhbBRmGnXLo",
            database="defaultdb"
        )
        st.success("Conexión establecida exitosamente!")
        return conn
    except mysql.connector.Error as err:
        st.error(f"Error al conectar a la base de datos: {err}")
        st.error(f"Error tipo: {type(err).__name__}")
        st.error(f"Error args: {err.args}")
        st.stop()
    except Exception as e:
        st.error(f"Error inesperado: {e}")
        st.error(f"Error tipo: {type(e).__name__}")
        st.error(f"Error args: {e.args}")
        st.stop()

# Función para ejecutar consultas SQL con manejo de errores
@st.cache_data
def run_query(query):
    try:
        st.write(f"Ejecutando consulta: {query}")
        with conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
        st.success("Consulta ejecutada exitosamente!")
        return results
    except mysql.connector.Error as err:
        st.error(f"Error al ejecutar la consulta: {err}")
        st.error(f"Error tipo: {type(err).__name__}")
        st.error(f"Error args: {err.args}")
        st.stop()
    except Exception as e:
        st.error(f"Error inesperado: {e}")
        st.error(f"Error tipo: {type(e).__name__}")
        st.error(f"Error args: {e.args}")
        st.stop()

# Título de la aplicación
st.title('Visualización de Datos de MySQL')

# Iniciar conexión
conn = init_connection()

# Selector de tabla
table_name = st.selectbox(
    "Selecciona la tabla a visualizar",
    ("MegaTime2022", "MegaTime2023", "MegaTime2024")
)

# Definir el nombre de la columna del mes según la tabla seleccionada
if table_name in ["MegaTime2022", "MegaTime2024"]:
    mes_column = "Mes Nombre"
else:  # MegaTime2023
    mes_column = "Mes"

# Ejecutar la consulta con la tabla seleccionada
query = f"SELECT Año, `{mes_column}`, valor FROM {table_name} ORDER BY Año, `{mes_column}`;"
rows = run_query(query)

if rows:
    # Convertir los resultados a un DataFrame de pandas
    df = pd.DataFrame(rows, columns=['Año', 'Mes', 'Valor'])

    # Crear una columna de fecha combinando Año y Mes
    df['Fecha'] = pd.to_datetime(df['Año'].astype(str) + '-' + df['Mes'], format='%Y-%B', errors='coerce')

    # Ordenar el DataFrame por la nueva columna Fecha
    df = df.sort_values('Fecha')

    # Crear el gráfico con Plotly
    fig = px.line(df, x='Fecha', y='Valor', title=f'Valores a lo largo del tiempo - {table_name}')

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    # Mostrar los datos en una tabla
    st.write(f"Datos de la tabla {table_name}:")
    st.dataframe(df)

    # Añadir un selector de rango de fechas
    date_range = st.date_input("Selecciona un rango de fechas",
                               [df['Fecha'].min(), df['Fecha'].max()],
                               min_value=df['Fecha'].min(),
                               max_value=df['Fecha'].max())

    # Filtrar los datos según el rango de fechas seleccionado
    filtered_df = df[(df['Fecha'] >= pd.to_datetime(date_range[0])) & 
                     (df['Fecha'] <= pd.to_datetime(date_range[1]))]

    # Actualizar el gráfico con los datos filtrados
    fig_filtered = px.line(filtered_df, x='Fecha', y='Valor', title=f'Valores en el rango seleccionado - {table_name}')
    st.plotly_chart(fig_filtered)
else:
    st.warning("No se encontraron datos en la tabla seleccionada.")

# Mostrar información de versiones
st.write("Versiones de las bibliotecas:")
st.write(f"Python: {sys.version}")
st.write(f"Streamlit: {st.__version__}")
st.write(f"mysql-connector-python: {mysql.connector.__version__}")
st.write(f"pandas: {pd.__version__}")
st.write(f"plotly: {px.__version__}")
