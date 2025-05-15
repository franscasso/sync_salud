import streamlit as st
from supabase import create_client, Client
import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
from functions import execute_query, add_user

#pip install streamlit plotly pandas
load_dotenv()


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# Configuración de la página
st.set_page_config(
    page_title="SyncSalud - Login",
    page_icon="🏥",
    layout="centered"
)

# CSS Personalizado
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton>button {
        background-color: #1a73e8;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1557b0;
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
    .login-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .info-card {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1a73e8;
    }
    .contact-card {
        background-color: #fff3e0;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ff9800;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    .welcome-text {
        text-align: center;
        color: #1a73e8;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Función para generar el logo (SVG)
def crear_logo():
    return """
    <svg width="200" height="60" viewBox="0 0 200 60" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="10" width="40" height="40" rx="10" fill="#1a73e8"/>
        <path d="M25 25 L25 35 L35 35 M25 30 L30 30" stroke="white" stroke-width="3" stroke-linecap="round"/>
        <text x="60" y="40" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#1a73e8">SyncSalud</text>
    </svg>
    """

# Simulación de funciones de base de datos
def execute_query(query, params=None, is_select=False):
    # Simular consulta a BD - reemplazar con tu lógica real
    if is_select:
        return pd.DataFrame()
    return True

def add_user(id_user, username, password, rol):
    # Simular registro de usuario - reemplazar con tu lógica real
    return True

# Inicializa estado de sesión
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Página de Login/Registro
if not st.session_state.logged_in:
    # Logo en la parte superior
    st.markdown(f'<div class="logo-container">{crear_logo()}</div>', unsafe_allow_html=True)
    
    # Contenedor de login
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Botón para cambiar entre Login y Sign Up
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.auth_mode == "Login":
            if st.button("¿No tienes cuenta? Regístrate aquí", key="switch_to_signup"):
                st.session_state.auth_mode = "Sign Up"
                st.rerun()
        else:
            if st.button("¿Ya tienes cuenta? Inicia sesión aquí", key="switch_to_login"):
                st.session_state.auth_mode = "Login"
                st.rerun()
    
    # Formulario de LOGIN
    if st.session_state.auth_mode == "Login":
        st.markdown("### 🔐 Iniciar sesión")
        with st.form("login_form"):
            username = st.text_input("👤 Usuario")
            password = st.text_input("🔑 Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar sesión")
            
            if submitted:
                if len(password) < 8 or " " in password:
                    st.error("La contraseña debe tener 8 o más caracteres y no debe contener espacios")
                elif username and password:
                    # Simulación de login exitoso
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.rol = "Medico"  # Ejemplo
                    st.success("¡Inicio de sesión exitoso!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Por favor completa ambos campos.")
    
    # Formulario de SIGN UP
    elif st.session_state.auth_mode == "Sign Up":
        st.markdown("### 📝 Crear una cuenta")
        with st.form("signup_form"):
            id_user = st.text_input("🆔 Ingrese su DNI")
            new_user = st.text_input("👤 Nuevo usuario")
            new_pass = st.text_input("🔑 Nueva contraseña", type="password")
            confirm_pass = st.text_input("🔑 Confirmar contraseña", type="password")
            rol = st.radio("👥 Selecciona tu rol:", ["Medico", "Admisiones"])
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
                    # Simulación de registro exitoso
                    st.success("¡Usuario registrado con éxito! Ahora puedes iniciar sesión.")
                    st.session_state.auth_mode = "Login"
                    time.sleep(1)
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Página Principal (Usuario logueado)
if st.session_state.get("logged_in"):
    # Sidebar con información del usuario
    with st.sidebar:
        st.markdown(f'<div class="logo-container">{crear_logo()}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**👤 Usuario:** {st.session_state.username}")
        st.markdown(f"**👥 Rol:** {st.session_state.rol}")
        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            st.session_state.clear()
            st.rerun()
    
    # Mensaje de bienvenida personalizado
    st.markdown(f'<div class="welcome-text">¡Bienvenido a SyncSalud, {st.session_state.username}! 👋</div>', unsafe_allow_html=True)
    
    # Información sobre la empresa
    st.markdown("""
    <div class="info-card">
        <h3>🏥 Sobre SyncSalud</h3>
        <p>SyncSalud es una plataforma innovadora diseñada para revolucionar la gestión clínica y hospitalaria. 
        Nuestra misión es mejorar la eficiencia en las consultas médicas, reducir los tiempos de espera y 
        optimizar la experiencia tanto para profesionales de la salud como para pacientes.</p>
        
        <h4>✨ Beneficios clave:</h4>
        <ul>
            <li>Gestión digital de historias clínicas</li>
            <li>Programación inteligente de turnos</li>
            <li>Comunicación fluida entre departamentos</li>
            <li>Acceso rápido a información crítica del paciente</li>
            <li>Reducción del 40% en tiempos administrativos</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sección de contacto
    st.markdown("""
    <div class="contact-card">
        <h3>📞 ¿Necesitas ayuda?</h3>
        <p>Nuestro equipo de soporte está siempre disponible para asistirte:</p>
        <p><strong>📧 Email:</strong> soporte@syncsalud.com</p>
        <p><strong>☎️ Teléfono:</strong> +54 11 1234-5678</p>
        <p><strong>💬 WhatsApp:</strong> +54 9 11 5678-9012</p>
        <p><strong>🕐 Horario:</strong> Lunes a Viernes, 8:00 - 20:00</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Gráfico de mejora en la eficacia
    st.markdown("### 📊 Impacto de SyncSalud en la Eficiencia Médica")
    
    # Datos para el gráfico
    data = {
        'Métrica': ['Tiempo de consulta', 'Satisfacción del paciente', 'Precisión diagnóstica', 
                    'Gestión de turnos', 'Comunicación interdepartamental'],
        'Antes de SyncSalud': [45, 65, 80, 60, 55],
        'Con SyncSalud': [30, 92, 95, 88, 90]
    }
    
    df = pd.DataFrame(data)
    
    # Crear gráfico de barras comparativo
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Antes de SyncSalud',
        x=df['Métrica'],
        y=df['Antes de SyncSalud'],
        marker_color='#ff7f0e'
    ))
    
    fig.add_trace(go.Bar(
        name='Con SyncSalud',
        x=df['Métrica'],
        y=df['Con SyncSalud'],
        marker_color='#1a73e8'
    ))
    
    fig.update_layout(
        title='Mejora en Métricas Clave',
        xaxis_title='Métricas',
        yaxis_title='Eficiencia (%)',
        barmode='group',
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas de impacto
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="⏱️ Reducción tiempo consulta",
            value="33%",
            delta="15 min menos",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="😊 Satisfacción pacientes",
            value="92%",
            delta="+27%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="🎯 Precisión diagnóstica",
            value="95%",
            delta="+15%",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="📅 Eficiencia en turnos",
            value="88%",
            delta="+28%",
            delta_color="normal"
        )
    
    # Pie de página
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 14px;'>
        <p>© 2024 SyncSalud. Todos los derechos reservados.</p>
        <p>Transformando la salud con tecnología 🚀</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Mensaje cuando no está logueado
    st.info("👆 Por favor inicia sesión para acceder al contenido de SyncSalud.")

# Spinner personalizado para procesos de carga
def loading_animation(texto="Procesando..."):
    with st.spinner(texto):
        time.sleep(1)
    return