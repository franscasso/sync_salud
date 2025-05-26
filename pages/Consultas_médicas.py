import streamlit as st
import pandas as pd
import plotly.express as px
import time
import sys
import os
from functions import get_connection


def obtener_historial_legible_por_dni(dni):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT 
        cm.detalle_consulta,
        cm.clasificacion,
        h.nombre_hospital,
        c.nombre_categoria,
        m.nombre AS nombre_medico
    FROM consulta_medica cm
    JOIN pacientes p ON p.dni_paciente = %s
    JOIN hospital h ON h.id = cm.id_hospital
    JOIN categorias c ON c.id_tipo_categoria = cm.id_categoria
    JOIN medicos m ON m.id_medico = cm.id_medico
    WHERE cm.id_paciente = p.id_paciente;
    """

    cur.execute(query, (dni,))
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    if not resultados:
        return "Este paciente no posee un historial."

    return pd.DataFrame(resultados)


# Añadir la ruta del directorio .streamlit al sistema para poder importar módulos
<<<<<<< Updated upstream
if not st.session_state.logged_in:
    st.error("Debes iniciar sesión para acceder a esta página")
else:
    if st.session_state.rol != "Medico":
        st.error("No tienes acceso a esta página")
    else:
        st.title("Consultas médicas")
        st.markdown("### ¿Qué acción desea realizar?")

        opcion = st.radio("Seleccione operación", ("Ver historial", "Agregar consulta"))

        if opcion == "Ver historial":
            with st.form("Historial de consultas"):
                dni_paciente= st.text_input("DNI de paciente")
=======
if st.session_state.rol != "Medico":
    st.error("No tienes acceso a esta página")
else:
    st.title("Consultas médicas")
    st.markdown("### ¿Qué acción desea realizar?")

    opcion = st.radio("Seleccione operación", ("Ver historial", "Agregar consulta"))

    if opcion == "Ver historial":
        with st.form("Historial de consultas"):
            dni_paciente= st.text_input("DNI de paciente")
>>>>>>> Stashed changes

