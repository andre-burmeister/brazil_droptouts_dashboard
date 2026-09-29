import streamlit as st
import pandas as pd
from pathlib import Path

DATA_DIR = (
    Path(__file__).parent
    / "dados"
    / "microdados_censo_da_educacao_superior_2024"
)
CSV_PATH = DATA_DIR / "dados" / "MICRODADOS_CADASTRO_CURSOS_2024.CSV"
DICT_PATH = (
    DATA_DIR
    / "Anexos"
    / "ANEXO I - Dicionário de Dados"
    / "dicionário_dados_educação_superior.xlsx"
)
CO_IES_UFRGS = 581


@st.cache_data
def load_cursos():
    return pd.read_csv(CSV_PATH, sep=";", encoding="latin-1", low_memory=False)


@st.cache_data
def load_column_descriptions():
    raw = pd.read_excel(DICT_PATH, sheet_name="cadastro_cursos", header=None)
    header_idx = raw.index[
        raw.iloc[:, 1].astype(str).str.strip().eq("Nome da Variável")
    ][0]
    dictionary = raw.iloc[header_idx + 1 :].copy()
    dictionary.columns = [
        str(column).strip() if pd.notna(column) else ""
        for column in raw.iloc[header_idx]
    ]
    names = dictionary["Nome da Variável"].astype(str).str.strip()
    descriptions = dictionary["Descrição da Variável"].fillna("").astype(str).str.strip()
    variables = names.str.fullmatch(r"[A-Z][A-Z0-9_]*")
    return dict(zip(names[variables], descriptions[variables]))


def quantity_columns(df):
    return [column for column in df.columns if column.startswith("QT_")]


def sum_by(df, keys):
    grouped = df.groupby(keys, as_index=False, dropna=False)[quantity_columns(df)].sum()
    return grouped.sort_values(keys).reset_index(drop=True)


def ufrgs_courses(df):
    return df[df["CO_IES"] == CO_IES_UFRGS]


def courses_by_state(df):
    return sum_by(df[df["SG_UF"].notna()], ["NO_CURSO", "SG_UF"])


def courses_total(df):
    return sum_by(df, ["NO_CURSO"])


def states_total(df):
    return sum_by(df[df["SG_UF"].notna()], ["SG_UF"])
