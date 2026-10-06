"""Print the head of the course table used by the dropout charts.

Same default recorte as the dashboard: presencial courses, all students.
Reads only the columns that table needs, so it does not start Streamlit.
"""

import logging

import pandas as pd

logging.disable(logging.WARNING)
from data_helpers import (
    EVASAO_FROM_YEAR,
    EVASAO_TO_YEAR,
    MIN_ENROLLED,
    MODALIDADE_PRESENCIAL,
    OFFER_KEY_FILL,
    OFFER_KEYS,
    compute_evasao,
    cursos_csv_path,
    evasao_by_course,
)

logging.disable(logging.NOTSET)

ID_COLUMNS = [
    "CO_IES",
    "CO_CURSO",
    "CO_MUNICIPIO",
    "TP_DIMENSAO",
    "NO_CURSO",
    "TP_MODALIDADE_ENSINO",
    "TP_ORGANIZACAO_ACADEMICA",
    "TP_CATEGORIA_ADMINISTRATIVA",
]

COUNT_COLUMNS = [
    "NO_CURSO",
    "QT_MAT_2023",
    "QT_CONC_2023",
    "QT_ING_2023",
    "QT_MAT_2024",
    "QT_ING_2024",
    "QT_EVAS",
]


def load_year(year, quantity_columns):
    return pd.read_csv(
        cursos_csv_path(year),
        sep=";",
        encoding="latin-1",
        usecols=ID_COLUMNS + quantity_columns,
        low_memory=False,
    )


def print_head(title, offers, min_enrolled, *, inclusive=False, nonzero_graduates=False):
    courses = evasao_by_course(offers.loc[:, COUNT_COLUMNS])
    enrolled = courses["QT_MAT_2023"]
    mask = enrolled >= min_enrolled if inclusive else enrolled > min_enrolled
    if nonzero_graduates:
        mask = mask & courses["QT_CONC_2023"].gt(0)
    courses = (
        courses.loc[mask]
        .sort_values("TX_EVAS", ascending=False)
        .reset_index(drop=True)
    )
    print(title)
    print(courses.head(20))
    print()


offers_2023 = load_year(EVASAO_FROM_YEAR, ["QT_MAT", "QT_CONC", "QT_ING"])
offers_2024 = load_year(EVASAO_TO_YEAR, ["QT_MAT", "QT_ING"])
from_2023 = offers_2023.loc[:, OFFER_KEYS + ["QT_ING", "TP_ORGANIZACAO_ACADEMICA"]].rename(
    columns={"QT_ING": "QT_ING_2023"}
)
from_2023["CO_MUNICIPIO"] = from_2023["CO_MUNICIPIO"].fillna(OFFER_KEY_FILL["CO_MUNICIPIO"])

evasao = compute_evasao(offers_2023, offers_2024)
evasao["CO_MUNICIPIO"] = (
    pd.to_numeric(evasao["CO_MUNICIPIO"], errors="coerce")
    .fillna(OFFER_KEY_FILL["CO_MUNICIPIO"])
    .astype("int64")
)
evasao = evasao.merge(from_2023, on=OFFER_KEYS, how="left")

modalidade = pd.to_numeric(evasao["TP_MODALIDADE_ENSINO"], errors="coerce")
presencial = evasao.loc[modalidade.eq(MODALIDADE_PRESENCIAL)].copy()
organizacao = pd.to_numeric(presencial["TP_ORGANIZACAO_ACADEMICA"], errors="coerce")
categoria = pd.to_numeric(presencial["TP_CATEGORIA_ADMINISTRATIVA"], errors="coerce")

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", 60)

print_head(
    "Presencial, mais de 100 matrículas",
    presencial,
    MIN_ENROLLED,
)
print_head(
    "Universidades federais (organização acadêmica 1 e categoria administrativa 1)",
    presencial.loc[organizacao.eq(1) & categoria.eq(1)],
    MIN_ENROLLED,
)
print_head(
    "Universidades (organização acadêmica 1, 2 ou 3)",
    presencial.loc[organizacao.isin((1, 2, 3))],
    MIN_ENROLLED,
)
print_head(
    "Presencial, pelo menos 1000 matrículas somadas no Brasil",
    presencial,
    1000,
    inclusive=True,
)
print_head(
    "Presencial, pelo menos 1000 matrículas e ao menos um concluinte em 2023",
    presencial,
    1000,
    inclusive=True,
    nonzero_graduates=True,
)




