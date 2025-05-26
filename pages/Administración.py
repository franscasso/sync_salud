import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from functions import get_connection
# Función para conectarse a la base de datos



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
def insertar_medico(nombre, licencia, id_hospital, id_categoria):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO MEDICOS(nombre, licencia, id_hospital, id_categoria)
        VALUES (%s, %s, %s, %s) RETURNING id_medico
    """, (nombre,licencia, id_hospital, id_categoria))
    id_medico = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return id_medico


# Función para obtener las categorías
def obtener_categorias():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id_tipo_categoria, nombre_categoria FROM Categorias")
    categorias = cur.fetchall()
    cur.close()
    conn.close()
    return [(c["id_tipo_categoria"], c['nombre_categoria']) for c in categorias]

# Función para obtener los hospitales
def obtener_hospitales():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id_hospital,nombre_hospital FROM Hospital")
    hospitales = cur.fetchall()
    cur.close()
    conn.close()
    return [(h["id_hospital"], h['nombre_hospital']) for h in hospitales]

#Esto es para que no accesa a la pagina si no es de admisiones
<<<<<<< Updated upstream
if not st.session_state.logged_in:
=======
if st.session_state.logged_in == False:
>>>>>>> Stashed changes
    st.error("Debes iniciar sesion para acceder a esta página")

else:

    if st.session_state.rol != "Admisiones":
        st.error("No tienes acceso a esta página")
    else:
        st.title("Administración")
        st.markdown("### ¿Qué desea agregar?")

# Opción para elegir entre paciente o médico
        opcion = st.radio("Seleccione qué desea agregar", ("Paciente", "Médico"))

        opciones_sangre = ["", "A+","A-", "B+","B-","AB+", "AB-","O+", "O-"]

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
                grupo_sanguineo = st.selectbox("Grupo Sanguíneo", opciones_sangre)
        
                submitted = st.form_submit_button("Agregar Paciente")
                if submitted:
                    insertar_paciente(dni, nombre_completo, obra_social, fecha_nacimiento,
                              sexo, telefono, contacto_emergencia, grupo_sanguineo)
                    st.success("Paciente agregado correctamente.")

# Formulario para agregar un médico
        elif opcion == "Médico":
            with st.form("Agregar Médico"):
                nombre_apellido = st.text_input("Nombre y Apellido")
                numero_licencia = st.text_input("Número de Licencia")

                categorias = obtener_categorias()
                opciones_categoria=[ nombre for _, nombre in categorias]

                categoria_seleccionada = st.selectbox("Selecciona la Categoría del Médico", opciones_categoria)
                id_categoria= next((id for id, nombre in categorias if nombre ==categoria_seleccionada), None)

                hospitales = obtener_hospitales()
                opciones_hospital =[nombre for _, nombre in hospitales]

                hospital_seleccionado= st.selectbox("Hospital donde atiende", opciones_hospital)
                id_hospital = next((id for id, nombre in hospitales if nombre == hospital_seleccionado), None)


                submitted = st.form_submit_button("Agregar Médico")
                if submitted:
                    insertar_medico(nombre_apellido, numero_licencia,id_hospital, id_categoria)
                    st.success("Médico agregado correctamente")




        