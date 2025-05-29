import streamlit as st
import pandas as pd
from datetime import datetime, date
import supabase
from typing import Optional, List, Dict, Any

# Verificar autenticación
if not st.session_state.logged_in:
    st.error("Debes iniciar sesión para acceder a esta página")
else:
    if st.session_state.rol != "Medico":
        st.error("No tienes acceso a esta página")
    else:
        # Configuración de la página
        st.set_page_config(
            page_title="Sistema Médico - Estudios",
            page_icon="🏥",
            layout="wide"
        )

        # Inicializar cliente de Supabase
        @st.cache_resource
        def init_supabase():
            url = "https://oubnxmdpdosmyrorjiqp.supabase.co"
            key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im91Ym54bWRwZG9zbXlyb3JqaXFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4MjUzMjcsImV4cCI6MjA2MDQwMTMyN30.4yszlmTe3NkDLAss6HACnfGlxprHyJLQYTLRrgRmj04"
            return supabase.create_client(url, key)

        # Funciones para obtener datos
        @st.cache_data(ttl=300)  # Cache por 5 minutos
        def get_patient_by_dni(dni: str) -> Optional[Dict]:
            """Buscar paciente por DNI"""
            try:
                client = init_supabase()
                response = client.table('pacientes').select('*').eq('dni_paciente', dni).execute()
                return response.data[0] if response.data else None
            except Exception as e:
                st.error(f"Error al buscar paciente: {str(e)}")
                return None

        @st.cache_data(ttl=300)
        def get_patient_studies(dni_paciente: str) -> List[Dict]:
            """Obtener todos los estudios de un paciente usando dni_paciente"""
            try:
                client = init_supabase()
                
                # Primero obtener el id_paciente usando el dni_paciente
                patient_response = client.table('pacientes').select('dni_paciente').execute()
                
                if not patient_response.data:
                    return []
                
                patient_id = patient_response.data[0]['dni_paciente']
                
                # Ahora buscar los estudios usando id_paciente
                response = client.table('estudios_realizados').select('*').eq('dni_paciente', patient_id).execute()
                studies = response.data
                
                if not studies:
                    return []
                
                # Obtener datos relacionados
                hospitals = {h['id_hospital']: h['nombre_hospital'] for h in get_hospitals()}
                doctors = {d['id_medico']: d['nombre'] for d in get_doctors()}
                estudios_data = {e['id_estudio']: e for e in get_estudios()}
                categories = {c['id_categoria_estudio']: c['tipo_de_estudio'] for c in get_categories()}
                
                # Enriquecer los estudios con datos relacionados
                for study in studies:
                    # Información del hospital
                    hospital_id = study.get('id_hospital')
                    study['hospital'] = {'nombre_hospital': hospitals.get(hospital_id, 'N/A')}
                    
                    # Información del médico
                    medico_id = study.get('id_medico')
                    study['medicos'] = {'nombre': doctors.get(medico_id, 'N/A')}
                    
                    # Información del estudio
                    estudio_id = study.get('id_estudio')
                    estudio_info = estudios_data.get(estudio_id, {})
                    
                    # Obtener la categoría del estudio
                    tipo_estudio_id = estudio_info.get('tipo_estudio')
                    categoria_nombre = categories.get(tipo_estudio_id, 'N/A')
                    
                    study['estudios'] = {
                        'nombre_estudio': estudio_info.get('nombre_estudio', 'N/A'),
                        'tipo_estudio': {'tipo_de_estudio': categoria_nombre}
                    }
                
                return studies
                
            except Exception as e:
                st.error(f"Error al obtener estudios: {str(e)}")
                return []

        @st.cache_data(ttl=600)  # Cache por 10 minutos
        def get_hospitals() -> List[Dict]:
            """Obtener lista de hospitales"""
            try:
                client = init_supabase()
                response = client.table('hospital').select('id_hospital, nombre_hospital').execute()
                return response.data
            except Exception as e:
                st.error(f"Error al obtener hospitales: {str(e)}")
                return []

        @st.cache_data(ttl=600)
        def get_doctors() -> List[Dict]:
            """Obtener lista de médicos"""
            try:
                client = init_supabase()
                response = client.table('medicos').select('id_medico, nombre').execute()
                return response.data
            except Exception as e:
                st.error(f"Error al obtener médicos: {str(e)}")
                return []

        @st.cache_data(ttl=600)
        def get_categories() -> List[Dict]:
            """Obtener categorías de estudios (tipo_estudio)"""
            try:
                client = init_supabase()
                response = client.table('tipo_estudio').select('id_categoria_estudio, tipo_de_estudio').execute()
                return response.data
            except Exception as e:
                st.error(f"Error al obtener categorías: {str(e)}")
                return []

        @st.cache_data(ttl=600)
        def get_estudios() -> List[Dict]:
            """Obtener lista de estudios específicos"""
            try:
                client = init_supabase()
                response = client.table('estudios').select('*').execute()
                return response.data
            except Exception as e:
                st.error(f"Error al obtener estudios: {str(e)}")
                return []

        def get_estudios_by_category(categoria_id: int) -> List[Dict]:
            """Obtener estudios filtrados por categoría"""
            try:
                client = init_supabase()
                response = client.table('estudios').select('*').eq('tipo_estudio', categoria_id).execute()
                return response.data
            except Exception as e:
                st.error(f"Error al obtener estudios por categoría: {str(e)}")
                return []

        def filter_studies(studies: List[Dict], hospital_filter: str, doctor_filter: str, 
                          category_filter: str, date_from: date, date_to: date) -> List[Dict]:
            """Aplicar filtros a los estudios"""
            filtered_studies = studies.copy()
            
            if hospital_filter != "Todos":
                filtered_studies = [s for s in filtered_studies if s.get('hospital', {}).get('nombre_hospital') == hospital_filter]
            
            if doctor_filter != "Todos":
                filtered_studies = [s for s in filtered_studies if s.get('medicos', {}).get('nombre') == doctor_filter]
            
            if category_filter != "Todos":
                filtered_studies = [
                    s for s in filtered_studies 
                    if s.get('estudios', {}).get('tipo_estudio', {}).get('tipo_de_estudio') == category_filter
                ]
            
            # Filtrar por fecha
            if date_from and date_to:
                filtered_studies = [
                    s for s in filtered_studies 
                    if date_from <= datetime.strptime(s['fecha'], '%Y-%m-%d').date() <= date_to
                ]
            
            return filtered_studies

        def add_new_study(dni_paciente: str, doctor_id: int, hospital_id: int, id_categoria_estudio: int, estudio_id: int, 
                 study_date: date, observations: str) -> bool:
            """Agregar nuevo estudio usando dni_paciente directamente"""
            try:
                client = init_supabase()

                # ✅ Verificar que el paciente existe CON FILTRO
                patient_response = client.table('pacientes').select('dni_paciente').eq('dni_paciente', dni_paciente).execute()
                
                if not patient_response.data:
                    st.error("No se encontró el paciente")
                    return False
                
                # ✅ Usar dni_paciente directamente con la columna correcta
                new_study = {
                    'dni_paciente': dni_paciente,
                    'id_medico': doctor_id,
                    'id_hospital': hospital_id,
                    'id_categoria_estudio': id_categoria_estudio,  # ✅ Ahora coincide con tu tabla
                    'id_estudio': estudio_id,
                    'fecha': study_date.strftime('%Y-%m-%d'),
                    'observaciones': observations
                }
                
                response = client.table('estudios_realizados').insert(new_study).execute()
                
                if response.data:
                    st.success("Estudio agregado exitosamente")
                    # Limpiar cache para mostrar el nuevo estudio inmediatamente
                    st.cache_data.clear()
                    return True
                else:
                    st.error("Error al insertar el estudio")
                    return False
                
            except Exception as e:
                st.error(f"Error al agregar estudio: {str(e)}")
                return False
    
        # Interfaz principal
        def main():
            st.title("🏥 Sistema de Gestión de Estudios Médicos")
            st.markdown("---")
            
            # Sección de búsqueda
            st.subheader("🔍 Buscar Estudios")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_dni = st.text_input(
                    "Ingrese DNI del paciente:",
                    placeholder="Ej: 12345678",
                    help="Ingrese el número de DNI del paciente para buscar sus estudios"
                )
            
            with col2:
                st.write("")  # Espaciado
                search_button = st.button("🔍 Buscar", type="primary", use_container_width=True)
            
            # Procesar búsqueda
            if search_dni and (search_button or 'current_patient' in st.session_state):
                if search_button or st.session_state.get('current_dni') != search_dni:
                    patient = get_patient_by_dni(search_dni)
                    st.session_state['current_patient'] = patient
                    st.session_state['current_dni'] = search_dni
                else:
                    patient = st.session_state.get('current_patient')
                
                if patient:
                    # Mostrar información del paciente
                    st.success(f"✅ Paciente encontrado: **{patient['nombre']}**")
                    
                    # Obtener estudios usando dni_paciente
                    studies = get_patient_studies(patient['dni_paciente'])
                    
                    # Botón para agregar nuevo estudio
                    st.markdown("---")
                    st.subheader("➕ Agregar Nuevo Estudio")
                    
                    with st.expander("Agregar Estudio", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        # Obtener datos para los selectores
                        hospitals = get_hospitals()
                        doctors = get_doctors()
                        categories = get_categories()
                        
                        with col1:
                            # Selector de médico
                            current_doctor = st.selectbox(
                                "👨‍⚕️ Médico:",
                                options=[(d['id_medico'], d['nombre']) for d in doctors],
                                format_func=lambda x: x[1],
                                help="Seleccione el médico que realizará el estudio"
                            )
                            
                            selected_hospital = st.selectbox(
                                "🏥 Hospital:",
                                options=[(h['id_hospital'], h['nombre_hospital']) for h in hospitals],
                                format_func=lambda x: x[1],
                                help="Seleccione el hospital donde se realizará el estudio"
                            )
                        
                        with col2:
                            # Selector de categoría primero
                            selected_category = st.selectbox(
                                "📋 Categoría de Estudio:",
                                options=[(c['id_categoria_estudio'], c['tipo_de_estudio']) for c in categories],
                                format_func=lambda x: x[1],
                                help="Seleccione primero la categoría del estudio"
                            )
                            
                            # Obtener estudios de la categoría seleccionada
                            estudios_filtered = get_estudios_by_category(selected_category[0])
                            
                            if estudios_filtered:
                                selected_estudio = st.selectbox(
                                    "🔬 Estudio:",
                                    options=[(e['id_estudio'], e['nombre_estudio']) for e in estudios_filtered],
                                    format_func=lambda x: x[1],
                                    help="Seleccione el tipo de estudio específico a realizar"
                                )
                            else:
                                st.warning("No hay estudios disponibles para esta categoría")
                                selected_estudio = None
                            
                            study_date = st.date_input(
                                "📅 Fecha del Estudio:",
                                value=date.today(),
                                help="Seleccione la fecha en que se realizó o realizará el estudio"
                            )
                        
                        observations = st.text_area(
                            "📝 Observaciones:",
                            placeholder="Ingrese observaciones sobre el estudio...",
                            height=100,
                            help="Agregue cualquier observación relevante sobre el estudio"
                        )
                        
                        if st.button("💾 Guardar Estudio", type="primary"):
                            if selected_estudio and hospitals and doctors:
                                # Usar directamente el dni_paciente
                                success = add_new_study(
                                    dni_paciente=patient['dni_paciente'],
                                    doctor_id=current_doctor[0],
                                    hospital_id=selected_hospital[0],
                                    id_categoria_estudio=selected_category[0],
                                    estudio_id=selected_estudio[0],
                                    study_date=study_date,
                                    observations=observations
                                )
                                
                                if success:
                                    st.success("✅ Estudio agregado exitosamente!")
                                    # Limpiar cache y recargar
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error("❌ Error al agregar el estudio")
                            else:
                                st.error("❌ Por favor complete todos los campos obligatorios")
                    
                    if studies:
                        st.markdown("---")
                        st.subheader("📋 Filtros de Búsqueda")
                        
                        # Filtros
                        col1, col2, col3, col4 = st.columns(4)
                        
                        # Obtener datos para filtros
                        hospitals = get_hospitals()
                        doctors = get_doctors()
                        categories = get_categories()
                        
                        with col1:
                            hospital_options = ["Todos"] + [h['nombre_hospital'] for h in hospitals]
                            hospital_filter = st.selectbox("🏥 Hospital:", hospital_options)
                        
                        with col2:
                            doctor_options = ["Todos"] + [d['nombre'] for d in doctors]
                            doctor_filter = st.selectbox("👨‍⚕️ Médico:", doctor_options)
                        
                        with col3:
                            category_options = ["Todos"] + [c['tipo_de_estudio'] for c in categories]
                            category_filter = st.selectbox("🔬 Tipo de Estudio:", category_options)
                        
                        with col4:
                            date_filter = st.date_input(
                                "📅 Rango de Fechas:",
                                value=(date.today().replace(year=date.today().year-1), date.today()),
                                help="Seleccione el rango de fechas para filtrar"
                            )
                        
                        # Aplicar filtros
                        if len(date_filter) == 2:
                            date_from, date_to = date_filter
                        else:
                            date_from = date_to = date.today()
                        
                        filtered_studies = filter_studies(
                            studies, hospital_filter, doctor_filter,
                            category_filter, date_from, date_to
                        )
                        
                        st.markdown("---")
                        
                        if filtered_studies:
                            # Mostrar estudios
                            st.subheader(f"📊 Estudios Encontrados ({len(filtered_studies)})")
                            
                            # Crear cards para cada estudio (más visual que tabla)
                            for i, study in enumerate(filtered_studies):
                                with st.container():
                                    col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
                                    
                                    with col1:
                                        st.write(f"**📅 Fecha:** {study['fecha']}")
                                        st.write(f"**🏥 Hospital:** {study.get('hospital', {}).get('nombre_hospital', 'N/A')}")
                                    
                                    with col2:
                                        st.write(f"**👨‍⚕️ Médico:** {study.get('medicos', {}).get('nombre', 'N/A')}")
                                        st.write(f"**🔬 Tipo:** {study.get('estudios', {}).get('tipo_estudio', {}).get('tipo_de_estudio', 'N/A')}")
                                    
                                    with col3:
                                        st.write(f"**📋 Estudio:** {study.get('estudios', {}).get('nombre_estudio', 'N/A')}")
                                    
                                    with col4:
                                        observaciones = study.get('observaciones', 'Sin observaciones')
                                        if len(observaciones) > 50:
                                            observaciones = observaciones[:50] + "..."
                                        st.write(f"**📝 Observaciones:** {observaciones}")
                                    
                                    if i < len(filtered_studies) - 1:
                                        st.divider()
                        else:
                            st.warning("🔍 No se encontraron estudios con los filtros aplicados")
                            st.info("💡 Intente modificar los filtros o agregar un nuevo estudio")
                    
                    else:
                        st.warning("📋 Este paciente no tiene estudios registrados")
                        st.info("💡 Puede agregar un nuevo estudio usando el formulario de arriba")
                
                else:
                    st.error("❌ No se encontró ningún paciente con ese DNI")
                    st.info("💡 Verifique que el DNI esté correctamente ingresado")
            
            elif search_dni and not search_button:
                st.info("💡 Presione 'Buscar' para encontrar al paciente")

        if __name__ == "__main__":
            main()