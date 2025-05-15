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


# Inicializa estado de sesión
# Inicializa estado de sesión
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 👉 Solo mostrar login/sign-up si el usuario NO está logueado
if not st.session_state.logged_in:

    # 🔄 Botón superior para cambiar entre Login y Sign Up, con cambio inmediato
    if st.session_state.auth_mode == "Login":
        if st.button("¿No tienes cuenta? Regístrate aquí"):
            st.session_state.auth_mode = "Sign Up"
            st.rerun()
    else:
        if st.button("¿Ya tienes cuenta? Inicia sesión aquí"):
            st.session_state.auth_mode = "Login"
            st.rerun()

    # 🧾 Formulario de LOGIN
    if st.session_state.auth_mode == "Login":
        st.subheader("Iniciar sesión")
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if len(password) < 8 or " " in password:
                    st.error("La contraseña debe tener 8 o más caracteres y no debe contener espacios")
                elif username and password:
                    check_query = "SELECT * FROM users WHERE nombre_usuario = %s AND contraseña = %s"
                    existing = execute_query(check_query, params=(username, password), is_select=True)
                    if not existing.empty:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.rol = existing["rol"][0]
                        st.success("¡Inicio de sesión exitoso!")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
                else:
                    st.error("Por favor completa ambos campos.")

    # 🧾 Formulario de SIGN UP
    elif st.session_state.auth_mode == "Sign Up":
        st.subheader("Crear una cuenta")
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
                    st.error("El nombre de usuario no puede contener espacios")
                elif new_pass != confirm_pass:
                    st.error("Las contraseñas no coinciden.")
                elif len(new_pass) < 8 or " " in new_pass:
                    st.error("La contraseña debe tener 8 o más caracteres y no debe contener espacios")
                else:
                    check_query = "SELECT * FROM users WHERE nombre_usuario = %s OR id = %s"
                    existing = execute_query(check_query, params=(new_user, id_user), is_select=True)
                    if not existing.empty:
                        st.error("Este DNI o nombre de usuario ya existe.")
                    else:
                        resultado = add_user(id_user, new_user, new_pass, rol)
                        if resultado:
                            st.success("¡Usuario registrado con éxito! Ahora puedes iniciar sesión.")
                            st.session_state.auth_mode = "Login"
                            st.rerun()
                        else:
                            st.error("Error al registrar el usuario.")



if st.session_state.get("logged_in"):
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()



# Solo ejecuta este bloque si el usuario está autenticado
if st.session_state.get("logged_in"):
    st.sidebar.write(f"Usuario: {st.session_state.username}")
    st.sidebar.write(f"Rol: {st.session_state.rol}")
else:
    st.warning("Por favor inicia sesión para acceder al contenido.")






