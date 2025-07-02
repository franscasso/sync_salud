import streamlit as st
import pandas as pd
from psycopg2.extras import RealDictCursor
from functions import get_connection, execute_query
import os
from Inicio import crear_logo, manage_page_access
from datetime import date

# --- Fix visual para texto blanco en fondo blanco dentro de expanders ---
st.markdown("""
    <style>
    .streamlit-expanderContent {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

def obtener_pacientes():
    """
    Obtiene lista de pacientes con DNI y nombre
    """
    query = "SELECT dni_paciente, nombre FROM pacientes"
    resultado = execute_query(query, is_select=True)
    return [(row['dni_paciente'], row['nombre']) for _, row in resultado.iterrows()]

def obtener_hospitales():
    """
    Obtiene lista de hospitales
    """
    query = "SELECT id_hospital, nombre_hospital FROM hospital"
    resultado = execute_query(query, is_select=True)
    return [(row['id_hospital'], row['nombre_hospital']) for _, row in resultado.iterrows()]

def obtener_categorias_estudio():
    """
    Obtiene categorías de estudios
    """
    query = "SELECT id_categoria_estudio, tipo_de_estudio FROM tipo_estudio"
    resultado = execute_query(query, is_select=True)
    return [(row['id_categoria_estudio'], row['tipo_de_estudio']) for _, row in resultado.iterrows()]

def obtener_estudios_por_categoria(categoria_id):
    """
    Obtiene estudios específicos por categoría
    """
    query = "SELECT id_estudio, nombre_estudio FROM estudios WHERE tipo_estudio = %s"
    resultado = execute_query(query, params=(categoria_id,), is_select=True)
    return [(row['id_estudio'], row['nombre_estudio']) for _, row in resultado.iterrows()]

def obtener_id_medico_por_dni(dni):
    """
    Obtiene el ID del médico por su DNI
    """
    query = "SELECT id_medico FROM medicos WHERE dni = %s"
    resultado = execute_query(query, params=(dni,), is_select=True)
    
    if resultado.empty:
        return {
            'success': False,
            'id_medico': None,
            'message': 'No se encontró ningún médico con ese DNI.'
        }
    
    id_medico = int(resultado.iloc[0]['id_medico'])
    return {
        'success': True,
        'id_medico': id_medico,
        'message': 'ID del médico encontrado correctamente.'
    }

def insertar_estudio(dni_paciente, id_medico, id_hospital, id_categoria_estudio, id_estudio, fecha, observaciones):
    """
    Inserta nuevo estudio en la base de datos
    """
    query = """
        INSERT INTO estudios_realizados 
        (dni_paciente, id_medico, id_hospital, id_categoria_estudio, id_estudio, fecha, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        execute_query(query, params=(dni_paciente, id_medico, id_hospital, id_categoria_estudio, id_estudio, fecha, observaciones))
        return True
    except Exception as e:
        st.error(f"Error al insertar estudio: {str(e)}")
        return False

# -- INTERFAZ --

if not st.session_state.get("logged_in", False):
    st.error("Debes iniciar sesión para acceder a esta página")
else:
    if st.session_state.get("rol", "") != "Médico":
        st.error("No tienes acceso a esta página")
    else:
        st.title("🔬 Estudios médicos")
        st.markdown("### ¿Qué acción desea realizar?")

        opcion = st.radio("Seleccione operación", ("📄 Ver estudios", "➕ Agregar estudio"))

        if opcion == "📄 Ver estudios":
            with st.form("form_estudios"):
                dni_paciente = st.text_input("🆔 DNI del paciente")
                btn_buscar = st.form_submit_button("🔍 Buscar estudios")

            if btn_buscar:
                if dni_paciente.strip() == "":
                    st.warning("Por favor ingrese un DNI.")
                else:
                    # Importar la función desde functions.py
                    from functions import obtener_estudios_por_dni
                    df_estudios = obtener_estudios_por_dni(dni_paciente.strip())
                    
                    if isinstance(df_estudios, str):
                        st.info(df_estudios)
                    else:
                        # Mostrar información del paciente encontrado
                        st.success(f"✅ Estudios encontrados para el paciente con DNI: *{dni_paciente}*")
                        
                        # Sección de filtros
                        st.markdown("---")
                        st.subheader("📋 Filtros de Búsqueda")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Filtro por hospital
                            hospitales_unicos = ["Todos"] + sorted(df_estudios['hospital'].unique().tolist())
                            hospital_filtro = st.selectbox("🏥 Hospital:", hospitales_unicos)
                        
                        with col2:
                            # Filtro por médico
                            medicos_unicos = ["Todos"] + sorted(df_estudios['medico'].unique().tolist())
                            medico_filtro = st.selectbox("👨‍⚕ Médico:", medicos_unicos)
                        
                        with col3:
                            # Filtro por tipo de estudio
                            categorias_unicas = ["Todos"] + sorted(df_estudios['categoria'].unique().tolist())
                            categoria_filtro = st.selectbox("🔬 Tipo de Estudio:", categorias_unicas)
                        
                        # Aplicar filtros
                        df_filtrado = df_estudios.copy()
                        
                        if hospital_filtro != "Todos":
                            df_filtrado = df_filtrado[df_filtrado['hospital'] == hospital_filtro]
                        
                        if medico_filtro != "Todos":
                            df_filtrado = df_filtrado[df_filtrado['medico'] == medico_filtro]
                        
                        if categoria_filtro != "Todos":
                            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]
                        
                        st.markdown("---")
                        
                        if not df_filtrado.empty:
                            # Mostrar tabla resumen
                            st.subheader(f"📊 Estudios Encontrados ({len(df_filtrado)} de {len(df_estudios)})")
                            st.dataframe(df_filtrado[["fecha", "categoria", "estudio", "hospital"]])

                            st.markdown("### 🗂 Detalles adicionales por estudio")
                            for idx, row in df_filtrado.iterrows():
                                with st.expander(f"🗓 {row['fecha']} | {row['estudio']}"):
                                    st.write(f"🔬 Tipo de estudio: {row['categoria']}")
                                    st.write(f"📋 Estudio: {row['estudio']}")
                                    st.write(f"👩‍⚕ Médico: {row['medico']}")
                                    st.write(f"🏥 Hospital: {row['hospital']}")
                                    st.write(f"📅 Fecha: {row['fecha']}")
                                    st.write(f"📝 Observaciones: {row['observaciones'] if row['observaciones'] else 'Sin observaciones'}")
                        else:
                            st.warning("🔍 No se encontraron estudios con los filtros aplicados")
                            st.info("💡 Intente modificar los filtros para ver más resultados")

        elif opcion == "➕ Agregar estudio":
            st.title("➕ Nuevo estudio médico")
            
            # Obtener ID del médico logueado
            dni_medico = st.session_state.dni  # Este valor debería venir del login
            buscar_id_medico = obtener_id_medico_por_dni(dni_medico)
            id_medico = buscar_id_medico["id_medico"]
            
            # Mostrar información del médico
            if buscar_id_medico["success"]:
                st.info(f"👨‍⚕ Médico: {st.session_state.username} (ID: {id_medico})")
            else:
                st.error("No se pudo obtener la información del médico logueado")
                st.stop()

            with st.form("form_estudio"):
                # Selector de paciente
                pacientes = obtener_pacientes()
                opciones_pacientes = [f"{dni} - {nombre}" for dni, nombre in pacientes]
                paciente_sel = st.selectbox("👤 Paciente", opciones_pacientes)

                # Selector de hospital
                hospitales = obtener_hospitales()
                opciones_hosp = [f"{id_h} - {nombre}" for id_h, nombre in hospitales]
                hospital_sel = st.selectbox("🏥 Hospital", opciones_hosp)

                # Selector de categoría de estudio
                categorias = obtener_categorias_estudio()
                opciones_cat = [f"{id_c} - {nombre}" for id_c, nombre in categorias]
                categoria_sel = st.selectbox("📚 Tipo de estudio", opciones_cat)

                # Selector de estudio específico (dinámico basado en categoría)
                if categoria_sel:
                    id_categoria = int(categoria_sel.split(" - ")[0])
                    estudios_especificos = obtener_estudios_por_categoria(id_categoria)
                    
                    if estudios_especificos:
                        opciones_estudios = [f"{id_e} - {nombre}" for id_e, nombre in estudios_especificos]
                        estudio_sel = st.selectbox("🔬 Estudio específico", opciones_estudios)
                    else:
                        st.warning("No hay estudios disponibles para esta categoría")
                        estudio_sel = None

                col1, col2 = st.columns(2)
                with col1:
                    fecha_estudio = st.date_input("📅 Fecha del estudio", value=date.today())
                with col2:
                    st.write("")  # Espaciado

                observaciones = st.text_area("📝 Observaciones del estudio")

                enviar = st.form_submit_button("💾 Guardar estudio")

                if enviar:
                    try:
                        if not estudio_sel:
                            st.error("❌ Por favor seleccione un estudio específico")
                        else:
                            dni_paciente = paciente_sel.split(" - ")[0]
                            id_hospital = int(hospital_sel.split(" - ")[0])
                            id_categoria_estudio = int(categoria_sel.split(" - ")[0])
                            id_estudio = int(estudio_sel.split(" - ")[0])

                            success = insertar_estudio(
                                dni_paciente, 
                                id_medico, 
                                id_hospital, 
                                id_categoria_estudio, 
                                id_estudio, 
                                fecha_estudio, 
                                observaciones
                            )
                            
                            if success:
                                st.success("✅ Estudio médico agregado correctamente.")
                            else:
                                st.error("❌ Error al guardar el estudio")
                                
                    except Exception as e:
                        st.error(f"❌ Error al guardar el estudio: {e}")

# Sidebar con información del usuario
if st.session_state.get("logged_in"):
    with st.sidebar:
        st.markdown(f'<div class="logo-container">{crear_logo()}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"👤 Usuario:** {st.session_state.username}")
        st.markdown(f"👥 Rol:** {st.session_state.rol}")
        st.markdown("---")
        
        # Mostrar información sobre páginas accesibles
        if st.session_state.rol == "Médico":
            st.success("✅ Tienes acceso a: Consultas médicas, Estudios, Medicamentos e Historial clínico")
            st.error("❌ No tienes acceso a: Administración")
        elif st.session_state.rol == "Admisiones":
            st.success("✅ Tienes acceso a: Administración")
            st.error("❌ No tienes acceso a: Consultas médicas, Estudios, Medicamentos e Historial clínico")
        
        st.markdown("---")
        if st.button("🚪 Cerrar sesión"):
            # Restablecer estado y bloquear páginas
            st.session_state.clear()
            try:
                manage_page_access()
            except:
                pass
            st.rerun()