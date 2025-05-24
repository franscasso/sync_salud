import streamlit as st
import pandas as pd
import plotly.express as px
import time
import sys
import os


if st.session_state.rol != "Medico":
    st.error("No tienes acceso a esta página")
else:
    st.title("Consultas médicas")