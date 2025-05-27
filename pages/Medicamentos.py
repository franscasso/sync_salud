import streamlit as st
import pandas as pd
import plotly.express as px
import time
import sys
import os

#Este codigo del principio hace que la pagina se bloquee si no sos Medico
if not st.session_state.logged_in:
    st.error("Debes iniciar sesion para acceder a esta página")
else:
    if st.session_state.rol != "Medico":
        st.error("No tienes acceso a esta página")
    else: #Todo tiene que estar adentro de este else
        st.title("Medicamentos")
