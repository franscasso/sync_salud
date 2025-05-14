import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

def show():
    st.title("Página de Administracion")
    st.write("Aquí va el contenido completo que quieras mostrar.")
    # Podés seguir usando componentes de Streamlit acá normalmente

# Función para conectarse a la base de datos
def get_connection():
    return psycopg2.connect(
        host="aws-0-us-east-1.pooler.supabase.com",
        database="postgres",
        user="postgres.oubnxmdpdosmyrorjiqp",
        password="$EB6Y5rbR#z8_qh",
        port="5432"
    )

def insertar_paciente(dni, nombre_completo, obra_social, fecha_nacimiento,
                      sexo, telefono, contacto_emergencia, grupo_sanguineo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO PACIENTES (id_paciente, nombre, obra_social, fecha_nacimiento,
        sexo, telefono, contacto_emergencia, grupo_sanguineo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (dni, nombre_completo, obra_social, fecha_nacimiento,
          sexo, telefono, contacto_emergencia, grupo_sanguineo))
    conn.commit()
    cur.close()
    conn.close()



# Función para insertar un médico
def insertar_medico(nombre_apellido, especialidad, numero_licencia, email_profesional, telefono):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO MEDICO (nombre_apellido, especialidad, numero_licencia, email_profesional, telefono)
        VALUES (%s, %s, %s, %s, %s) RETURNING id_medico
    """, (nombre_apellido, especialidad, numero_licencia, email_profesional, telefono))
    id_medico = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return id_medico

# Función para obtener las categorías
def obtener_categorias():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nombre_categoria FROM Categorias")
    categorias = cur.fetchall()
    cur.close()
    conn.close()
    return [(c['id'], c['nombre_categoria']) for c in categorias]

# Función para obtener los hospitales
def obtener_hospitales():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nombre_hospital FROM Hospital")
    hospitales = cur.fetchall()
    cur.close()
    conn.close()
    return [(h['id'], h['nombre_hospital']) for h in hospitales]

# Página de administración
st.title("Administración: ¿Qué desea agregar?")

# Opción para elegir entre paciente o médico
opcion = st.radio("Seleccione qué desea agregar", ("Paciente", "Médico"))


# Formulario para agregar un paciente
if opcion == "Paciente":
    with st.form("Agregar Paciente"):
        dni = st.text_input("DNI")
        nombre_completo = st.text_input("Nombre y Apellido")
        obra_social = st.text_input("Obra Social")
        fecha_nacimiento = st.date_input("Fecha de nacimiento")
        sexo = st.selectbox("Sexo", ["M", "F", "Otro"])
        telefono = st.text_input("Teléfono")
        contacto_emergencia = st.text_input("Contacto de Emergencia")
        grupo_sanguineo = st.text_input("Grupo Sanguíneo")
        
        submitted = st.form_submit_button("Agregar Paciente")
        if submitted:
            insertar_paciente(dni, nombre_completo, obra_social, fecha_nacimiento,
                              sexo, telefono, contacto_emergencia, grupo_sanguineo)
            st.success("Paciente agregado correctamente.")

# Formulario para agregar un médico
elif opcion == "Médico":
    with st.form("Agregar Médico"):
        nombre_apellido = st.text_input("Nombre y Apellido")
        especialidad = st.text_input("Especialidad")
        numero_licencia = st.text_input("Número de Licencia")
        email_profesional = st.text_input("Email Profesional")
        telefono = st.text_input("Teléfono")

        categorias = obtener_categorias()
        opciones_categoria = [f"{id} - {nombre}" for id, nombre in categorias]

        categoria_seleccionada = st.selectbox("Selecciona la Categoría del Médico", opciones_categoria) if categorias else None

        if categoria_seleccionada:
            id_categoria = int(categoria_seleccionada.split(" - ")[0])

            nombre_usuario = st.text_input("Nombre de Usuario para el Médico")
            contraseña = st.text_input("Contraseña para el Médico", type="password")
            rol = 'medico'

            submitted = st.form_submit_button("Agregar Médico")
            if submitted:
                # Crear usuario
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO Users (Nombre_usuario, Contraseña, Rol)
                    VALUES (%s, %s, %s) RETURNING ID
                """, (nombre_usuario, contraseña, rol))
                id_usuario = cur.fetchone()[0]
                conn.commit()
                cur.close()
                conn.close()

                # Insertar médico
                id_medico = insertar_medico(nombre_apellido, especialidad, numero_licencia, email_profesional, telefono)

                hospitales = obtener_hospitales()
                opciones_hospital = [f"{id} - {nombre}" for id, nombre in hospitales]
                seleccionados_hospitales = st.multiselect("Hospitales donde atiende", opciones_hospital)

                dias = st.text_input("Días de Atención (Ej: Lun, Mie, Vie)")
                horarios = st.text_input("Horarios (Ej: 9:00-12:00)")

                if seleccionados_hospitales:
                    for sel in seleccionados_hospitales:
                        id_hospital = int(sel.split(" - ")[0])
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO Medico_Hospital (id_medico, id_hospital)
                            VALUES (%s, %s)
                        """, (id_medico, id_hospital))
                        conn.commit()
                        cur.close()
                        conn.close()

                    st.success("Médico agregado correctamente.")
                else:
                    st.error("Por favor, selecciona al menos un hospital.")
        else:
            st.error("Por favor, selecciona una categoría para el médico.")