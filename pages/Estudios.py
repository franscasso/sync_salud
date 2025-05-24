import streamlit as st
import pandas as pd
from supabase import create_client
import datetime

# --- [Tu configuración de Supabase permanece igual] ---
url = "https://oubnxmdpdosmyrorjiqp.supabase.co"  # Reemplaza con tu URL de Supabase
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im91Ym54bWRwZG9zbXlyb3JqaXFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4MjUzMjcsImV4cCI6MjA2MDQwMTMyN30.4yszlmTe3NkDLAss6HACnfGlxprHyJLQYTLRrgRmj04"  # Reemplaza con tu API key de Supabase
supabase = create_client(url, key)

# Configuración de la página
st.set_page_config(page_title="Gestión de Estudios Médicos", layout="wide")

# Inicializar el estado de la sesión para el rol de usuario si no existe

# --- CSS personalizado: Aquí hacemos los ajustes clave para la estética ---
st.markdown("""
<style>
    /* Estilos base para todos los st.text_input para eliminar el borde y el fondo predeterminado */
    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 20px; /* Bordes redondeados */
        border: 1px solid #ccc; /* Borde sutil */
        background-color: white; /* Fondo blanco por defecto */
        font-size: 16px;
        color: #333;
        box-shadow: none;
        padding-left: 15px; /* Espacio normal a la izquierda */
        height: 45px; /* Altura estándar para inputs */
    }

    /* Estilos específicos para el DNI de búsqueda principal */
    /* Este es el que debe tener la lupa y el fondo gris claro */
    div[data-testid="stTextInput"] input[aria-label="ingresar DNI del paciente"] {
        padding-left: 40px; /* Espacio para el ícono de la lupa */
        background-color: #F0F2F6; /* Fondo gris claro */
    }

    /* Pseudo-elemento para la lupa, SOLO en el DNI de búsqueda principal */
    div[data-testid="stTextInput"] div.stTextInput:has(input[aria-label="ingresar DNI del paciente"])::before {
        content: "🔍"; /* El ícono de la lupa */
        position: absolute;
        left: 15px; /* Posición del ícono */
        top: 50%;
        transform: translateY(-50%);
        color: #555;
        font-size: 20px;
        z-index: 1; /* Asegurar que esté por encima del input */
        pointer-events: none; /* Crucial para que no interfiera con el input */
    }
    
    /* Ocultar el label predeterminado de Streamlit para el DNI de búsqueda */
    div[data-testid="stTextInput"] label:has(+ div > div > input[aria-label="ingresar DNI del paciente"]) {
        display: none;
    }

    /* Ajustar tamaño de los text_input en el formulario de agregar estudio */
    /* Apuntamos a los inputs específicos del formulario para asegurar los estilos */
    div[data-testid="stTextInput"] input[aria-label="DNI del Paciente"],
    div[data-testid="stTextInput"] input[aria-label="Nombre del Médico"],
    div[data-testid="stTextInput"] input[aria-label="Nombre del Hospital"] {
        height: 45px; /* Altura deseada para estos campos */
        padding-left: 15px; /* No lupa, padding normal */
        background-color: white; /* Asegurar fondo blanco */
        border: 1px solid #ccc; /* Borde sutil */
        border-radius: 20px; /* Bordes redondeados */
    }

    /* Ajuste para el st.text_area de Observaciones */
    div[data-testid="stTextarea"] textarea {
        border-radius: 20px;
        border: 1px solid #ccc;
        background-color: white;
        padding: 15px; /* Aumentar padding para que se vea más grande */
        min-height: 120px; /* Altura mínima para el text area */
        font-size: 16px;
    }

    /* Asegurar que los selectbox mantengan su estilo */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border-radius: 20px;
        border: 1px solid #ccc;
        background-color: white;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 20px;
        background-color: white;
        padding: 10px 15px; /* Ajustar padding */
        min-height: 45px; /* Asegurar una altura similar a los inputs */
    }

    /* Estilos para la tabla */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 16px;
        text-align: left;
        border: 2px solid black;
    }
    .styled-table th {
        background-color: white;
        color: black;
        font-weight: bold;
        padding: 12px 15px;
        border: 1px solid black;
    }
    .styled-table td {
        padding: 12px 15px;
        border: 1px solid black;
    }
    
    /* Títulos */
    h1 {
        font-size: 36px;
        font-weight: bold;
    }
    h3 {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* Contenedor de filtros */
    .filter-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 20px;
    }
    .filter-item {
        flex: 1;
        min-width: 150px;
    }

    /* Estilo para el botón "agregar estudio" */
    div[data-testid="stButton"] button[data-testid="st-b-btn_agregar_estudio_fixed"] {
        position: fixed;
        bottom: 40px;
        left: 40px;
        background-color: #2C3E50;
        color: white;
        border: none;
        border-radius: 30px;
        padding: 15px 30px;
        font-size: 18px;
        cursor: pointer;
        z-index: 10000;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transition: background-color 0.3s ease;
    }
    div[data-testid="stButton"] button[data-testid="st-b-btn_agregar_estudio_fixed"]:hover {
        background-color: #34495E;
    }
</style>
""", unsafe_allow_html=True)

#Este codigo del principio hace que la pagina se bloquee si no sos Medico
if not st.session_state.logged_in:
    st.error("Debes iniciar sesion para acceder a esta página")

else:

    if st.session_state.rol != "Medico":
        st.error("No tienes acceso a esta página")
    else: #Todo tiene que estar adentro de este else
# Título de la página
        st.markdown("<h1>Buscar estudios:</h1>", unsafe_allow_html=True)

# Campo de búsqueda principal del DNI
        dni_paciente_busqueda = st.text_input("", placeholder="ingresar DNI del paciente", key="dni_consulta_v6")

        # Guardar el DNI y el ID del paciente buscado en el estado de la sesión
        if 'dni_paciente_actual' not in st.session_state:
            st.session_state.dni_paciente_actual = ""
        if 'id_paciente_actual' not in st.session_state:
            st.session_state.id_paciente_actual = None
        if 'nombre_paciente_actual' not in st.session_state:
            st.session_state.nombre_paciente_actual = ""

        # Lógica para manejar el DNI ingresado en la búsqueda
        if dni_paciente_busqueda:
            paciente_query = supabase.table("pacientes").select("id, nombre").eq("dni_paciente", dni_paciente_busqueda).execute()
            
            if paciente_query.data:
                st.session_state.id_paciente_actual = paciente_query.data[0]['id']
                st.session_state.nombre_paciente_actual = paciente_query.data[0]['nombre']
                st.session_state.dni_paciente_actual = dni_paciente_busqueda # Guardar el DNI para el formulario
                
                st.markdown(f"<h3>Estudios de {st.session_state.nombre_paciente_actual}:</h3>", unsafe_allow_html=True)
                
                estudios_query = supabase.table("estudios_realizados").select("*").eq("id_paciente", st.session_state.id_paciente_actual).execute()
                
                if estudios_query.data:
                    estudios_completos = []
                    for estudio in estudios_query.data:
                        id_estudio = estudio.get('id_estudio')
                        estudio_info = supabase.table("estudios").select("nombre_estudio").eq("id_estudio", id_estudio).execute()
                        nombre_estudio = estudio_info.data[0]['nombre_estudio'] if estudio_info.data else "Sin nombre"
                        
                        id_hospital = estudio.get('id_hospital')
                        hospital_info = supabase.table("hospital").select("nombre_hospital").eq("id", id_hospital).execute()
                        nombre_hospital = hospital_info.data[0]['nombre_hospital'] if hospital_info.data else "Sin hospital"
                        
                        id_medico = estudio.get('id_medico')
                        medico_info = supabase.table("medicos").select("nombre").eq("id_medico", id_medico).execute()
                        nombre_medico = medico_info.data[0]['nombre'] if medico_info.data else "Sin médico"
                        
                        id_categoria = estudio.get('id_categoria')
                        categoria_info = supabase.table("tipo_estudio").select("tipo_de_estudio").eq("id_categoria_estudio", id_categoria).execute()
                        tipo_estudio = categoria_info.data[0]['tipo_de_estudio'] if categoria_info.data else "Sin categoría"
                        
                        estudios_completos.append({
                            "id_estudio_realizado": estudio.get('id_estudio_realizado'),
                            "Estudio": nombre_estudio,
                            "Hospital": nombre_hospital,
                            "Medico": nombre_medico,
                            "Fecha": estudio.get('fecha'),
                            "Observaciones": estudio.get('detalle', ''),
                            "Tipo_Estudio": tipo_estudio
                        })
                    
                    df_estudios = pd.DataFrame(estudios_completos)
                    
                    st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown("<div class='filter-item'>", unsafe_allow_html=True)
                        hospitales_unicos = sorted(df_estudios['Hospital'].unique())
                        hospital_seleccionado = st.multiselect("Hospital", options=hospitales_unicos)
                        st.markdown("</div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div class='filter-item'>", unsafe_allow_html=True)
                        medicos_unicos = sorted(df_estudios['Medico'].unique())
                        medico_seleccionado = st.multiselect("Médico", options=medicos_unicos)
                        st.markdown("</div>", unsafe_allow_html=True)
                    with col3:
                        st.markdown("<div class='filter-item'>", unsafe_allow_html=True)
                        fechas_unicas = sorted(df_estudios['Fecha'].unique())
                        fecha_seleccionada = st.multiselect("Fecha", options=fechas_unicas)
                        st.markdown("</div>", unsafe_allow_html=True)
                    with col4:
                        st.markdown("<div class='filter-item'>", unsafe_allow_html=True)
                        tipos_unicos = sorted(df_estudios['Tipo_Estudio'].unique())
                        tipo_seleccionado = st.multiselect("Tipo de Estudio", options=tipos_unicos)
                        st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    df_filtrado = df_estudios.copy()
                    if hospital_seleccionado:
                        df_filtrado = df_filtrado[df_filtrado['Hospital'].isin(hospital_seleccionado)]
                    if medico_seleccionado:
                        df_filtrado = df_filtrado[df_filtrado['Medico'].isin(medico_seleccionado)]
                    if fecha_seleccionada:
                        df_filtrado = df_filtrado[df_filtrado['Fecha'].isin(fecha_seleccionada)]
                    if tipo_seleccionado:
                        df_filtrado = df_filtrado[df_filtrado['Tipo_Estudio'].isin(tipo_seleccionado)]
                    
                    if not df_filtrado.empty:
                        tabla_datos = df_filtrado[['Estudio', 'Hospital', 'Medico', 'Fecha', 'Observaciones']].copy()
                        tabla_html = """
                        <table class="styled-table">
                            <thead>
                                <tr>
                                    <th>Estudio</th>
                                    <th>Hospital</th>
                                    <th>Medico</th>
                                    <th>Fecha</th>
                                    <th>Observaciones</th>
                                </tr>
                            </thead>
                            <tbody>
                        """
                        for _, row in tabla_datos.iterrows():
                            tabla_html += f"""
                            <tr>
                                <td>{row['Estudio']}</td>
                                <td>{row['Hospital']}</td>
                                <td>{row['Medico']}</td>
                                <td>{row['Fecha']}</td>
                                <td>{row['Observaciones']}</td>
                            </tr>
                            """
                        tabla_html += """
                            </tbody>
                        </table>
                        """
                        st.markdown(tabla_html, unsafe_allow_html=True)
                    else:
                        st.info("No se encontraron estudios con los filtros seleccionados.")
                else:
                    st.info("El paciente no tiene estudios registrados.")
            else:
                # Si el DNI de la búsqueda no encuentra paciente, reseteamos el estado.
                st.session_state.id_paciente_actual = None
                st.session_state.nombre_paciente_actual = ""
                st.session_state.dni_paciente_actual = ""
                if dni_paciente_busqueda: # Solo mostrar error si se ingresó algo y no se encontró
                    st.error("No se encontró ningún paciente con el DNI proporcionado.")

        # --- Botón "agregar estudio" ---
        if st.session_state.user_role == "medico":
            if st.button("agregar estudio", key="btn_agregar_estudio_fixed"): 
                st.session_state.mostrar_form_estudio = True
        else:
            pass

        # --- Formulario "Agregar nuevo estudio" ---
        if st.session_state.mostrar_form_estudio and st.session_state.user_role == "medico":
            with st.form("formulario_nuevo_estudio", border=True):
                st.subheader("Agregar nuevo estudio")
                
                # Precargar DNI del paciente si se encontró uno en la búsqueda principal
                dni_paciente_nuevo = st.text_input(
                    "DNI del Paciente", 
                    value=st.session_state.dni_paciente_actual, 
                    key="dni_nuevo_form",
                    disabled=(st.session_state.dni_paciente_actual != "") 
                )
                
                # Campos de texto para Hospital y Médico
                medico_nombre_input = st.text_input("Nombre del Médico", key="medico_nombre_input_form")
                hospital_nombre_input = st.text_input("Nombre del Hospital", key="hospital_nombre_input_form")
                
                # SELECTBOX para Tipo de Estudio y Estudio
                # Lógica para cargar opciones de Tipo de Estudio
                try:
                    tipos_estudio_query = supabase.table("tipo_estudio").select("id_categoria_estudio, tipo_de_estudio").execute()
                    tipos_estudio = {item['tipo_de_estudio']: item['id_categoria_estudio'] 
                                    for item in tipos_estudio_query.data} if tipos_estudio_query.data else {}
                    tipo_estudio_options = sorted(list(tipos_estudio.keys())) if tipos_estudio else ["No hay tipos disponibles"]
                    tipo_estudio_seleccionado = st.selectbox("Tipo de Estudio", options=tipo_estudio_options, key="tipo_estudio_select")
                except Exception as e:
                    st.error(f"Error al cargar tipos de estudio: {e}. Por favor, verifica la tabla 'tipo_estudio'.")
                    tipo_estudio_options = ["No hay tipos disponibles"]
                    tipo_estudio_seleccionado = "No hay tipos disponibles" # Fallback
                    tipos_estudio = {}

                # Lógica para cargar opciones de Estudio
                try:
                    estudios_query = supabase.table("estudios").select("id_estudio, nombre_estudio").execute()
                    estudios = {item['nombre_estudio']: item['id_estudio'] 
                                for item in estudios_query.data} if estudios_query.data else {}
                    estudio_options = sorted(list(estudios.keys())) if estudios else ["No hay estudios disponibles"]
                    estudio_seleccionado = st.selectbox("Estudio", options=estudio_options, key="estudio_select")
                except Exception as e:
                    st.error(f"Error al cargar estudios: {e}. Por favor, verifica la tabla 'estudios'.")
                    estudio_options = ["No hay estudios disponibles"]
                    estudio_seleccionado = "No hay estudios disponibles" # Fallback
                    estudios = {}

                fecha_estudio = st.date_input("Fecha del Estudio", value=datetime.date.today())
                detalle = st.text_area("Observaciones", height=150) # Mantenemos text_area para observaciones
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Guardar")
                with col2:
                    cancelar = st.form_submit_button("Cancelar")
                
                if cancelar:
                    st.session_state.mostrar_form_estudio = False
                    st.rerun()
                
                if submitted:
                    # --- Lógica de obtención de IDs ---
                    id_paciente = st.session_state.id_paciente_actual # Tomamos el ID del paciente directamente del estado de la sesión
                    id_medico = None
                    id_hospital = None
                    id_categoria_estudio = None
                    id_estudio = None

                    # Validar que tengamos un ID de paciente (del DNI de arriba o del campo si se modificó)
                    if not id_paciente:
                        st.error("No se ha seleccionado un paciente válido. Por favor, ingrese un DNI válido en la búsqueda principal.")
                        st.stop()
                    
                    # Buscar ID de médico (por nombre ingresado)
                    if medico_nombre_input:
                        medico_data = supabase.table("medicos").select("id_medico").eq("nombre", medico_nombre_input).execute().data
                        if medico_data:
                            id_medico = medico_data[0]['id_medico']
                        else:
                            st.error(f"Médico '{medico_nombre_input}' no encontrado. Asegúrese de que el nombre coincide exactamente con el de la base de datos.")
                            st.stop()
                    else:
                        st.warning("Por favor, ingrese el nombre del médico.")
                        st.stop()

                    # Buscar ID de hospital (por nombre ingresado)
                    if hospital_nombre_input:
                        # ATENCION: si la columna 'id' no existe o se llama diferente, ajusta aquí.
                        hospital_data = supabase.table("hospital").select("id").eq("nombre_hospital", hospital_nombre_input).execute().data
                        if hospital_data:
                            id_hospital = hospital_data[0]['id']
                        else:
                            st.error(f"Hospital '{hospital_nombre_input}' no encontrado. Asegúrese de que el nombre coincide exactamente con el de la base de datos.")
                            st.stop()
                    else:
                        st.warning("Por favor, ingrese el nombre del hospital.")
                        st.stop()

                    # Obtener ID de tipo de estudio (desde selectbox)
                    if tipo_estudio_seleccionado and tipo_estudio_seleccionado != "No hay tipos disponibles":
                        id_categoria_estudio = tipos_estudio.get(tipo_estudio_seleccionado)
                    else:
                        st.warning("Por favor, seleccione un Tipo de Estudio válido.")
                        st.stop()

                    # Obtener ID de estudio (desde selectbox)
                    if estudio_seleccionado and estudio_seleccionado != "No hay estudios disponibles":
                        id_estudio = estudios.get(estudio_seleccionado)
                    else:
                        st.warning("Por favor, seleccione un Estudio válido.")
                        st.stop()

                    # Si todos los IDs se encontraron, proceder con la inserción
                    if all([id_paciente, id_medico, id_hospital, id_categoria_estudio, id_estudio]):
                        nuevo_estudio = {
                            "id_paciente": id_paciente, # Usamos el ID del paciente ya obtenido
                            "id_medico": id_medico,
                            "id_hospital": id_hospital,
                            "id_categoria": id_categoria_estudio,
                            "id_estudio": id_estudio,
                            "fecha": str(fecha_estudio), # Se mantiene como string para la base de datos
                            "detalle": detalle
                        }
                        
                        result = supabase.table("estudios_realizados").insert(nuevo_estudio).execute()
                        
                        if result.data:
                            st.success("Estudio agregado correctamente")
                            st.session_state.mostrar_form_estudio = False
                            # Opcional: limpiar los campos del formulario o el DNI de búsqueda
                            st.session_state.dni_paciente_actual = "" 
                            st.session_state.id_paciente_actual = None
                            st.session_state.nombre_paciente_actual = ""
                            st.rerun()
                        else:
                            st.error(f"Error al agregar el estudio: {result.status_code} - {result.text}")
                    else:
                        st.error("Hubo un problema al obtener todos los IDs. Por favor, verifica los datos ingresados y seleccionados.")