import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de la conexión a la base de datos
@st.cache_resource
def init_connection():
    try:
        return mysql.connector.connect(
            host="chatgpt-do-user-3243287-0.c.db.ondigitalocean.com",
            port=25060,
            user="doadmin",
            password="AVNS_Vfn884XHZhbBRmGnXLo",
            database="OrigenMedios"
        )
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        st.stop()

# Función para ejecutar consultas SQL
@st.cache_data
def run_query(query):
    conn = init_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        st.stop()
    finally:
        conn.close()

# Función para convertir nombres de meses en español a números
def mes_a_numero(mes):
    meses = {
        'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
        'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
        'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
    }
    return meses.get(mes, 0)

# Título de la aplicación
st.title('Visualización de Datos de OrigenMedios')

# Selector de tabla
table_name = st.selectbox(
    "Selecciona la tabla a visualizar",
    ("MegaTime2022", "MegaTime2023", "MegaTime2024")
)

# Definir el nombre de la columna del mes según la tabla seleccionada
mes_column = "Mes Nombre" if table_name in ["MegaTime2022", "MegaTime2024"] else "Mes"

# Ejecutar la consulta con la tabla seleccionada
query = f"SELECT Año, `{mes_column}`, `Inversion MP` FROM {table_name} ORDER BY Año, `{mes_column}`;"
rows = run_query(query)

if rows:
    # Convertir los resultados a un DataFrame de pandas
    df = pd.DataFrame(rows, columns=['Año', 'Mes', 'Inversion MP'])
    
    # Corregir el formato del año y convertir a entero
    df['Año'] = df['Año'].astype(str).str.replace(',', '').astype(int)
    
    # Convertir mes a número
    df['Mes_Numero'] = df['Mes'].apply(mes_a_numero)
    
    # Crear una columna de fecha combinando Año y Mes
    df['Fecha'] = pd.to_datetime(df['Año'].astype(str) + '-' + df['Mes_Numero'].astype(str).str.zfill(2) + '-01')
    
    # Ordenar el DataFrame por la nueva columna Fecha
    df = df.sort_values('Fecha')
    
    # Crear el gráfico con Plotly
    fig = px.line(df, x='Fecha', y='Inversion MP', title=f'Inversión MP a lo largo del tiempo - {table_name}')
    
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
    filtered_df = df[(df['Fecha'].dt.date >= date_range[0]) & 
                     (df['Fecha'].dt.date <= date_range[1])]
    
    # Actualizar el gráfico con los datos filtrados
    fig_filtered = px.line(filtered_df, x='Fecha', y='Inversion MP', title=f'Inversión MP en el rango seleccionado - {table_name}')
    st.plotly_chart(fig_filtered)
else:
    st.warning("No se encontraron datos en la tabla seleccionada.")
