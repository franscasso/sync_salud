import streamlit as st

st.title("Estudios")

dni_pac= st.text_input("Ingresar dni de paciente: ")

tipo_estudio= st.selectbox("Seleccione tipo de estudio:", ["",
"Estudios de imagen", 
"Estudios de laboratorio", 
"Estudios cardiológicos"])

opciones_estudios = {
    "Estudios de imagen": ["","Radiografía", "Tomografía", "Resonancia magnética", "Ecografía"],
    "Estudios de laboratorio": ["", "Biometría hemática", "Química sanguínea", "Análisis de orina"],
    "Estudios cardiológicos": ["", "Electrocardiograma", "Ecocardiograma", "Prueba de esfuerzo"]
}

if tipo_estudio in opciones_estudios:
    subtipo = st.selectbox("Seleccione el estudio específico:", opciones_estudios[tipo_estudio])
else:
    subtipo = None