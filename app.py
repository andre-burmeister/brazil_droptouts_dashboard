import streamlit as st

from dashboard import render as render_dashboard
from tab1_dataframes import render as render_dataframes
from tab3_evasao_dataframes import render as render_evasao

st.set_page_config(layout="wide")
st.title("Censo da Educação Superior — Cursos e evasão")

tab_dashboard, tab_evasao, tab_brutos = st.tabs(
    ["Dashboards", "Dados de Evasão", "Dados Inalterados"]
)

with tab_dashboard:
    render_dashboard()

with tab_evasao:
    render_evasao()

with tab_brutos:
    render_dataframes()
