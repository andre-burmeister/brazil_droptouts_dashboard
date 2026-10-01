import streamlit as st

from tab1_dataframes import render as render_dataframes
from tab2_map import render as render_map
from tab3_evasao_dataframes import render as render_evasao

st.title("Censo da Educação Superior — Cursos e evasão")

tab_dados, tab_evasao, tab_mapa = st.tabs(["Dados", "Evasão", "Mapa"])

with tab_dados:
    render_dataframes()

with tab_evasao:
    render_evasao()

with tab_mapa:
    render_map()
