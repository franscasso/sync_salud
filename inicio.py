import streamlit as st
from supabase import create_client, Client
import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
from functions import execute_query, add_user

load_dotenv()


# Configuración de la página
st.set_page_config(
    page_title="SyncSalud - Login",
    page_icon="",
    layout="centered"
)

# Simulación de una base de datos simple (puedes reemplazar esto con una DB real)
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {}  # Estructura: {username: password}

# Título de la app
st.title("Bienvenido")

# Si no está logueado
if not st.session_state.get("logged_in", False):
    # Selector para alternar entre login y registro
    auth_mode = st.radio("Selecciona una opción:", ["Login", "Sign Up"])

    if auth_mode == "Login":
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if len(password) < 8 or " " in password:
                    st.error("La contraseña debe tener 8 o más caracteres y no deben poseer espacios")
                elif password and username:
                    check_query = "SELECT * FROM users WHERE nombre_usuario = %s AND contraseña = %s"
                    existing = execute_query(check_query, params=(username, password), is_select=True)
                    if not existing.empty:
                        st.success("¡Inicio de sesión exitoso!")
                    else:
                        st.error("Usuario o contraseña son incorrectas")
                else:
                    st.error("Por favor completa ambos campos.")
                    
    
    elif auth_mode == "Sign Up":
        with st.form("signup_form"):
            id_user = st.text_input("Ingrese su DNI")
            new_user = st.text_input("Nuevo usuario")
            new_pass = st.text_input("Nueva contraseña", type="password")
            confirm_pass = st.text_input("Confirmar contraseña", type="password")
            rol = st.radio("Selecciona una opción:", ["Medico", "Admisiones"])
            submitted = st.form_submit_button("Registrarse")

            if submitted:
                if not all([id_user, new_user, new_pass, confirm_pass]):
                    st.error("Completa todos los campos.")
                elif " " in new_user:
                    st.error("Nombre de usuario no puede contener espacios")
                elif new_pass != confirm_pass:
                    st.error("Las contraseñas no coinciden.")
                elif len(new_pass)< 8 or " " in new_pass:
                    st.error("La contraseña debe tener 8 o más caracteres y no deben poseer espacios")
                else:
                    # Verifica si ya existe el usuario
                    check_query = "SELECT * FROM users WHERE nombre_usuario = %s OR id = %s"
                    existing = execute_query(check_query, params=(new_user, id_user), is_select=True)
                    if not existing.empty:
                        st.error("Este DNI o nombre de usuario ya existe.")
                    else:
                        resultado = add_user(id_user, new_user, new_pass, rol)
                        if resultado:
                            st.success("¡Usuario registrado con éxito! Ahora puedes iniciar sesión.")
                        else:
                            st.error("Error al registrar el usuario.")

else:
    st.success(f"¡Bienvenido de nuevo, {st.session_state.get('username', 'Usuario')}!")
    st.info("Usa la barra lateral para navegar por la aplicación.")

    if st.button("Cerrar sesión"):
        del st.session_state["logged_in"]
        del st.session_state["username"]


