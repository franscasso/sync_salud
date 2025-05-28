import streamlit as st
from supabase import create_client, Client
import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
from functions import execute_query, add_user, autenticar_usuario, buscar_rol, verificar_medico_por_dni, obtener_dni_por_usuario
from functions import get_connection

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
        background-color: transparent; /* Cambiar a transparente para quitar el cuadrado blanco */
        padding: 0; /* Quitar padding */
        border-radius: 0; /* Quitar border-radius */
        box-shadow: none; /* Quitar sombra */
    }
    .info-card {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1a73e8;
    }
    .info-card ul {
        list-style-type: disc;
        padding-left: 20px;
        margin-top: 10px;
    }
    .info-card li {
        margin-bottom: 5px;
        padding-left: 5px;
    }
    .guide-container {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .guide-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .guide-icon {
        font-size: 2rem;
        margin-right: 10px;
    }
    
    .guide-title {
        margin: 0;
        color: #1a73e8;
        font-size: 1.8rem;
    }
    
    .guide-description {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 20px;
        color: #333;
    }
    
    .info-section {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .info-title {
        color: #495057;
        margin-bottom: 15px;
        font-size: 1.2rem;
    }
    
    .info-list {
        list-style: none;
        padding: 0;
    }
    
    .info-item {
        padding: 8px 0;
        display: flex;
        align-items: center;
        font-size: 15px;
    }
    
    .item-icon {
        margin-right: 10px;
        font-size: 1.1rem;
    }
    
    .gravity-levels {
        margin-top: 15px;
    }
    
    .level-5 {
        background: linear-gradient(135deg, #dc3545, #c82333);
        color: white;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 14px;
    }
    
    .level-4 {
        background: linear-gradient(135deg, #fd7e14, #e8590c);
        color: white;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 14px;
    }
    
    .level-3 {
        background: linear-gradient(135deg, #ffc107, #e0a800);
        color: #212529;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 14px;
    }
    
    .level-2 {
        background: linear-gradient(135deg, #17a2b8, #138496);
        color: white;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 14px;
    }
    
    .level-1 {
        background: linear-gradient(135deg, #28a745, #1e7e34);
        color: white;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 14px;
    }
    
    .level-title {
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .level-description {
        font-size: 13px;
        opacity: 0.9;
    }
    
    .tip-section {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin-top: 20px;
    }
    
    .tip-text {
        margin: 0;
        font-style: italic;
        color: #1976d2;
    }
    .contact-card {
        background-color: #fff3e0;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ff9800;
    }
    .logo-container {
        text-align: center; /* Centrar el logo */
        margin-bottom: 2rem;
    }
    .auth-button-container {
        text-align: center; /* Centrar el botón */
        margin-bottom: 1rem;
    }
    .welcome-text {
        text-align: center;
        color: #1a73e8;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .guide-container {
        background-color: #f3e8ff;
        padding: 20px;
        border-radius: 12px;
        font-family: sans-serif;
        color: #333;
    }
    .guide-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .guide-icon {
        font-size: 32px;
        margin-right: 10px;
    }
    .level-5, .level-4, .level-3, .level-2, .level-1 {
        margin: 10px 0;
        padding: 10px;
        border-radius: 8px;
    }
    .level-5 { background-color: #f8d7da; }
    .level-4 { background-color: #fff3cd; }
    .level-3 { background-color: #d1ecf1; }
    .level-2 { background-color: #d4edda; }
    .level-1 { background-color: #e2e3e5; }
</style>
""", unsafe_allow_html=True)

# Función para generar el logo (SVG)
def crear_logo():
    return """
    <svg width="300" height="80" viewBox="0 0 300 80" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="15" width="50" height="50" rx="12" fill="#1a73e8"/>
        <path d="M30 30 L30 45 L45 45 M30 37.5 L37.5 37.5" stroke="white" stroke-width="4" stroke-linecap="round"/>
        <text x="75" y="55" font-family="Arial, sans-serif" font-size="36" font-weight="bold" fill="#1a73e8">SyncSalud</text>
    </svg>
    """



# Simulación de funciones de base de datos
def manage_page_access():
    # Definir permisos por rol
    role_permissions = {
        "Medico": ["Consultas_médicas.py", "Estudios.py", "Medicamentos.py"],
        "Admisiones": ["Administración.py"]
    }
    
    # Lista de todas las páginas
    all_pages = ["Administración.py", "Consultas_médicas.py", "Estudios.py", "Medicamentos.py"]
    
    # Crear archivo .streamlit/config.toml si no existe
    os.makedirs(".streamlit", exist_ok=True)
    
    if not st.session_state.get("logged_in", False):
        # Si no está logueado, bloquear todas las páginas
        with open(".streamlit/config.toml", "w") as f:
            for page in all_pages:
                page_name = page.replace(".py", "").replace("_", " ")
                f.write(f'[browser.gatherUsageStats]\n')
                f.write(f'enabled = false\n\n')
                f.write(f'[pages]\n')
                for p in all_pages:
                    f.write(f'[pages.{p.replace(".py", "").replace("_", "")}]\n')
                    f.write(f'disabled = true\n\n')
    else:
        # Si está logueado, permitir solo las páginas según el rol
        rol = st.session_state.get("rol", "")
        allowed_pages = role_permissions.get(rol, [])
        
        with open(".streamlit/config.toml", "w") as f:
            f.write(f'[browser.gatherUsageStats]\n')
            f.write(f'enabled = false\n\n')
            f.write(f'[pages]\n')
            for page in all_pages:
                page_key = page.replace(".py", "").replace("_", "")
                if page in allowed_pages:
                    f.write(f'[pages.{page_key}]\n')
                    f.write(f'disabled = false\n\n')
                else:
                    f.write(f'[pages.{page_key}]\n')
                    f.write(f'disabled = true\n\n')
    
    # Notificar a Streamlit que debe recargar la configuración
    st.rerun()


# Inicializa estado de sesión
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "rol" not in st.session_state:
    st.session_state.rol = None

# Página de Login/Registro
if not st.session_state.logged_in:
    # Logo en la parte superior (ahora alineado a la izquierda)
    st.markdown(f'<div class="logo-container">{crear_logo()}</div>', unsafe_allow_html=True)
    
    # Contenedor de login (sin fondo blanco)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Botón para cambiar entre Login y Sign Up (alineado a la izquierda)
    st.markdown('<div class="auth-button-container">', unsafe_allow_html=True)
    if st.session_state.auth_mode == "Login":
        if st.button("¿No tienes cuenta? Regístrate aquí", key="switch_to_signup"):
            st.session_state.auth_mode = "Sign Up"
            st.rerun()
    else:
        if st.button("¿Ya tienes cuenta? Inicia sesión aquí", key="switch_to_login"):
            st.session_state.auth_mode = "Login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
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
                    if username and password:
                        resultado = autenticar_usuario(username, password)
                        if resultado['success']:
                            buscar_dni = obtener_dni_por_usuario(username)
                            saber_rol = buscar_rol(username, password)
                            if buscar_dni["success"]:
                                dni = buscar_dni["dni"]
                                rol = saber_rol["message"]
                                st.session_state.logged_in = True
                                st.session_state.username = username
                                st.session_state.dni = dni
                                st.session_state.rol = rol
                                st.success("¡Inicio de sesión exitoso!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error(resultado['message'])
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
            if rol == "Médico":
                respuesta = verificar_medico_por_dni(id_user)
                if respuesta["success"] == True:
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
                            nueva_cuenta= add_user(id_user, new_user, new_pass, rol)
                            if nueva_cuenta:
                                st.success("¡Usuario registrado con éxito! Ahora puedes iniciar sesión.")
                                st.session_state.auth_mode = "Login"
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Ocurrió un error, intente nuevamente")
                else:
                    st.error("No se encuentra registrado en la base de datos")
            else:
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
                        nueva_cuenta= add_user(id_user, new_user, new_pass, rol)
                        if nueva_cuenta:
                            st.success("¡Usuario registrado con éxito! Ahora puedes iniciar sesión.")
                            st.session_state.auth_mode = "Login"
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Ocurrió un error, intente nuevamente")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.warning("🔒 Todas las páginas están bloqueadas hasta que inicies sesión.")

# Página Principal (Usuario logueado)
if st.session_state.get("logged_in"):
    # Sidebar con información del usuario
    with st.sidebar:
        st.markdown(f'<div class="logo-container">{crear_logo()}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**👤 Usuario:** {st.session_state.username}")
        st.markdown(f"**👥 Rol:** {st.session_state.rol}")
        st.markdown("---")
        
        # Mostrar información sobre páginas accesibles
        if st.session_state.rol == "Medico":
            st.success("✅ Tienes acceso a: Consultas médicas, Estudios y Medicamentos")
            st.error("❌ No tienes acceso a: Administración")
        elif st.session_state.rol == "Admisiones":
            st.success("✅ Tienes acceso a: Administración")
            st.error("❌ No tienes acceso a: Consultas médicas, Estudios y Medicamentos")
        
        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            # Restablecer estado y bloquear páginas
            st.session_state.clear()
            try:
                manage_page_access()
            except:
                pass
            st.rerun()
    # Mensaje de bienvenida personalizado
    st.markdown(f'<div class="welcome-text">¡Bienvenido a SyncSalud, {st.session_state.username}! 👋</div>', unsafe_allow_html=True)
    if st.session_state.rol == "Medico":
        st.markdown("""
        <div style="
            background-color: #e0f7fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid #00acc1;
            margin-bottom: 20px;
            font-family: sans-serif;
        ">
            <h4 style="margin-top: 0;">¿Es tu primera vez usando la plataforma?</h4>
            <p style="margin-bottom: 10px;">
                <strong>No te preocupes</strong> te preparamos una guía rápida sobre las distintas secciones disponibles para el personal médico. Seleccioná una página para conocer qué podés hacer en ella.
            </p>
        </div>
        """, unsafe_allow_html=True)
        page_analisis = st.selectbox("📂 Seleccioná una sección para explorar su función", 
                                 ["", "Consultas médicas", "Estudios", "Medicamentos"])
        if page_analisis == "Consultas médicas":
            st.markdown("""
        <div class="guide-container">
            <div class="guide-header">
                <div class="guide-icon">🏥</div>
                <h3>Consultas médicas</h3>
            </div>  
            <p>
                En esta página podrás <strong>visualizar consultas médicas pasadas</strong> o <strong>agregar una consulta actual</strong> 
                del paciente utilizando su número de DNI.
            </p>
            <div>
                <h4>📊 Información obtenida en cada consulta:</h4>
                <ul>
                    <li>📅 <strong>Fecha</strong></li>
                    <li>👨‍⚕️ <strong>Médico</strong></li>
                    <li>🎯 <strong>Especialidad del profesional</strong></li>
                    <li>🏥 <strong>Hospital</strong></li>
                    <li>📝 <strong>Breve detalle de la consulta</strong></li>
                    <li>⚠️ <strong>Escala de gravedad:</strong>
                        <div class="level-5">
                            <strong>🚨 Nivel 5: RESUCITACIÓN</strong><br>
                            Paciente en estado crítico, con riesgo vital inmediato que requiere atención médica inmediata y reanimación.
                        </div>
                        <div class="level-4">
                            <strong>🔥 Nivel 4: EMERGENCIA</strong><br>
                            Paciente con riesgo vital inminente, pero que requiere atención médica dentro de 15 minutos.
                        </div>
                        <div class="level-3">
                            <strong>⚡ Nivel 3: URGENTE</strong><br>
                            Paciente que necesita atención médica en un plazo de 30 minutos a 1 hora.
                        </div>
                        <div class="level-2">
                            <strong>📋 Nivel 2: POCO URGENTE</strong><br>
                            Puede esperar hasta 2 horas sin riesgo para la vida.
                        </div>
                        <div class="level-1">
                            <strong>✅ Nivel 1: NO URGENTE</strong><br>
                            Situación no urgente, puede ser atendida más adelante.
                        </div>
                    </li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        elif page_analisis == "Estudios":
            pass
        elif page_analisis == "Medicamentos":
            pass
            # Información sobre la empresa
    else:
        pass
    st.markdown("""
    <div class="info-card">
        <h3>🏥 Sobre SyncSalud</h3>
        <p>SyncSalud es una plataforma innovadora diseñada para transformar la gestión clínica y hospitalaria. 
        Nuestra misión es optimizar la eficiencia de las consultas médicas, reducir los tiempos de espera y 
        digitalizar la historia clínica de los pacientes, garantizando su preservación en el tiempo y su acceso ágil y seguro.</p>
        <h4>✨ Beneficios clave:</h4>
        <ul>
            <li>Gestión digital de historias clínicas</li>
            <li>Prescripción electrónica de medicamentos</li>
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
            <p>📧 Email:</strong> soporte@syncsalud.com</p>
            <p>☎️ Teléfono:</strong> +54 11 1234-5678</p>
            <p>💬 WhatsApp:</strong> +54 9 11 5678-9012</p>
            <p>🕐 Horario:</strong> Lunes a Viernes, 8:00 - 20:00</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Gráfico de mejora en la eficacia
    st.markdown("### 📊 Impacto de SyncSalud en la Eficiencia Médica")
    
    # Datos para el gráfico
    data = {
        'Métrica': ['Tiempo de consulta', 'Satisfacción del paciente', 'Precisión diagnóstica'],
        'Antes de SyncSalud': [45, 65, 80],
        'Con SyncSalud': [30, 92, 95]
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
            label="⏱️ Aceleración de trabajo",
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