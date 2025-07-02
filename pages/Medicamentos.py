import streamlit as st
from datetime import date
from psycopg2.extras import RealDictCursor
from functions import get_connection, execute_query

# --- Funciones ---
def obtener_pacientes():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT dni_paciente, nombre FROM pacientes")
    pacientes = cur.fetchall()
    cur.close()
    conn.close()
    return [(p['dni_paciente'], p['nombre']) for p in pacientes]

def obtener_medicamentos():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id_medicamento, nombre FROM medicamentos")
    medicamentos = cur.fetchall()
    cur.close()
    conn.close()
    return medicamentos

def insertar_medicamento_recetado(id_paciente, id_medico, id_medicamento, indicaciones, fecha_inicio, fecha_fin):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO medicamento_recetado 
        (id_paciente, id_medico, id_medicamento, indicaciones, fecha_inicio_medicamento, fecha_terminacion_medicamento)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id_paciente, id_medico, id_medicamento, indicaciones, fecha_inicio, fecha_fin))
    conn.commit()
    cur.close()
    conn.close()

def obtener_id_medico_por_dni(dni):
    query = "SELECT id_medico FROM medicos WHERE dni = %s"
    resultado = execute_query(query, params=(dni,), is_select=True)

    if resultado.empty:
        return {
            'success': False,
            'id_medico': None,
            'message': 'No se encontró ningún médico con ese DNI.'
        }

    return {
        'success': True,
        'id_medico': int(resultado.iloc[0]['id_medico']),
        'message': 'ID del médico encontrado correctamente.'
    }

def obtener_medicacion_actual(dni_paciente):
    query = """
        SELECT m.nombre AS nombre_medicamento, m.tipo AS tipo_medicamento,
               mr.indicaciones, mr.fecha_inicio_medicamento, mr.fecha_terminacion_medicamento
        FROM medicamento_recetado mr
        JOIN medicamentos m ON mr.id_medicamento = m.id_medicamento
        WHERE mr.id_paciente = %s
        AND (mr.fecha_terminacion_medicamento IS NULL OR mr.fecha_terminacion_medicamento >= CURRENT_DATE)
        AND mr.fecha_inicio_medicamento <= CURRENT_DATE
        ORDER BY mr.fecha_inicio_medicamento DESC
    """
    resultado = execute_query(query, params=(dni_paciente,), is_select=True)
    return resultado.to_dict("records") if not resultado.empty else []

def obtener_medicacion_anterior(dni_paciente):
    query = """
        SELECT m.nombre AS nombre_medicamento, m.tipo AS tipo_medicamento,
               mr.indicaciones, mr.fecha_inicio_medicamento, mr.fecha_terminacion_medicamento
        FROM medicamento_recetado mr
        JOIN medicamentos m ON mr.id_medicamento = m.id_medicamento
        WHERE mr.id_paciente = %s
        AND mr.fecha_terminacion_medicamento < CURRENT_DATE
        ORDER BY mr.fecha_terminacion_medicamento DESC
    """
    resultado = execute_query(query, params=(dni_paciente,), is_select=True)
    return resultado.to_dict("records") if not resultado.empty else []

# --- Interfaz ---
if not st.session_state.get("logged_in", False):
    st.error("Debes iniciar sesión para acceder a esta página")

elif st.session_state.get("rol", "") != "Médico":
    st.error("No tienes acceso a esta página")

else:
    st.title("💊 Recetar medicamentos")

    dni_medico = st.session_state.dni
    buscar_id_medico = obtener_id_medico_por_dni(dni_medico)

    if not buscar_id_medico["success"]:
        st.error("No se encontró el ID del médico. Verificá que estés registrado correctamente.")
    else:
        id_medico = buscar_id_medico["id_medico"]

        with st.form("form_receta"):
            pacientes = obtener_pacientes()
            opciones_pacientes = [f"{dni} - {nombre}" for dni, nombre in pacientes]
            paciente_sel = st.selectbox("👤 Seleccione paciente", opciones_pacientes)

            medicamentos = obtener_medicamentos()
            opciones_medicamentos = {med['nombre']: med['id_medicamento'] for med in medicamentos}

            st.subheader("Seleccioná uno o más medicamentos")
            meds_seleccionados = st.multiselect(
                "Busca y selecciona medicamentos",
                options=list(opciones_medicamentos.keys()),
                help="Podés escribir para buscar"
            )

            fecha_inicio = st.date_input("📅 Fecha de inicio del medicamento", value=date.today())
            fecha_fin = st.date_input("📅 Fecha de finalización del medicamento", value=date.today())

            st.subheader("✍ Indicaciones")
            indicaciones = st.text_area("Escribí las indicaciones para los medicamentos seleccionados")

            enviar = st.form_submit_button("💾 Guardar receta")

        if enviar:
            if not meds_seleccionados:
                st.warning("⚠ Debes seleccionar al menos un medicamento.")
            elif fecha_fin < fecha_inicio:
                st.error("❌ La fecha de terminación no puede ser anterior a la de inicio.")
            elif not indicaciones.strip():
                st.warning("⚠ Debes ingresar indicaciones.")
            else:
                try:
                    id_paciente = paciente_sel.split(" - ")[0]
                    for med_nombre in meds_seleccionados:
                        id_medicamento = opciones_medicamentos[med_nombre]
                        insertar_medicamento_recetado(id_paciente, id_medico, id_medicamento, indicaciones, fecha_inicio, fecha_fin)
                    st.success("✅ Receta guardada correctamente.")
                except Exception as e:
                    st.error(f"❌ Error al guardar la receta: {e}")

        # --- Ver medicación actual e historial ---
        if paciente_sel:
            dni_paciente = paciente_sel.split(" - ")[0]

            st.subheader("💊 Medicación actual")
            meds_actuales = obtener_medicacion_actual(dni_paciente)
            if not meds_actuales:
                st.info("No hay medicamentos activos actualmente.")
            else:
                for m in meds_actuales:
                    st.markdown(f"""
                        - *{m['nombre_medicamento']}* ({m['tipo_medicamento']})  
                          {m['indicaciones']}  
                          *Inicio:* {m['fecha_inicio_medicamento']}  
                          *Fin:* {m['fecha_terminacion_medicamento'] or 'No especificado'}
                    """)

            with st.expander("🔽 Ver historial de medicamentos anteriores"):
                meds_pasados = obtener_medicacion_anterior(dni_paciente)
                if not meds_pasados:
                    st.info("No hay medicamentos anteriores registrados.")
                else:
                    for m in meds_pasados:
                        st.markdown(f"""
                            - *{m['nombre_medicamento']}* ({m['tipo_medicamento']})  
                              {m['indicaciones']}  
                              *Inicio:* {m['fecha_inicio_medicamento']}  
                              *Fin:* {m['fecha_terminacion_medicamento'] or 'No especificado'}
                        """)
