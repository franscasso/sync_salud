import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Kiosco App - Login",
    page_icon="🛒",
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
                if username and password:
                    user_db = st.session_state["user_db"]
                    if username in user_db and user_db[username] == password:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.success("¡Inicio de sesión exitoso!")
                    else:
                        st.error("Credenciales inválidas.")
                else:
                    st.error("Por favor completa ambos campos.")
    
    elif auth_mode == "Sign Up":
        with st.form("signup_form"):
            new_user = st.text_input("Nuevo usuario")
            new_pass = st.text_input("Nueva contraseña", type="password")
            confirm_pass = st.text_input("Confirmar contraseña", type="password")
            submitted = st.form_submit_button("Registrarse")
            auth_mode = st.radio("Selecciona una opción:", ["Medico", "Admisiones"])
            
            if submitted:
                if new_user and new_pass and confirm_pass:
                    user_db = st.session_state["user_db"]
                    if new_user in user_db:
                        st.error("Este nombre de usuario ya existe.")
                    elif new_pass != confirm_pass:
                        st.error("Las contraseñas no coinciden.")
                    else:
                        user_db[new_user] = new_pass
                        st.success("¡Usuario registrado con éxito! Ahora puedes iniciar sesión.")
                else:
                    st.error("Completa todos los campos.")
else:
    st.success(f"¡Bienvenido de nuevo, {st.session_state.get('username', 'Usuario')}!")
    st.info("Usa la barra lateral para navegar por la aplicación.")

    if st.button("Cerrar sesión"):
        del st.session_state["logged_in"]
        del st.session_state["username"]
