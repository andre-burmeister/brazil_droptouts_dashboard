import streamlit as st

from tab1_dataframes import render as render_dataframes
from tab2_map import render as render_map

st.title("Censo da Educação Superior 2024 — Cursos")

tab_dados, tab_mapa = st.tabs(["Dados", "Mapa"])

with tab_dados:
    render_dataframes()

with tab_mapa:
    render_map()
