import streamlit as st

from data_helpers import (
    CO_IES_UFRGS,
    EVASAO_FROM_YEAR,
    EVASAO_TO_YEAR,
    evasao_by_course,
    evasao_by_course_state,
    evasao_by_state,
    evasao_ufrgs,
    load_column_descriptions,
    load_evasao,
    slice_evasao,
)
from tab1_dataframes import column_config_for, descriptions_table

EVASAO_COUNT_COLS = (
    "QT_EVAS",
    "QT_MAT_2023",
    "QT_MAT_2024",
    "QT_CONC_2023",
    "QT_ING_2024",
)


def evasao_column_descriptions(base_descriptions):
    """Describe the total evasion counts and the rate after aggregation."""
    descriptions = {}
    formula = (
        f"matriculados_{EVASAO_FROM_YEAR} − concluintes_{EVASAO_FROM_YEAR} "
        f"− matriculados_{EVASAO_TO_YEAR} + ingressantes_{EVASAO_TO_YEAR}"
    )
    descriptions["QT_EVAS"] = f"Quantidade de alunos evadidos ({formula})"
    descriptions["TX_EVAS"] = (
        f"Taxa de evasão: QT_EVAS / QT_MAT_{EVASAO_FROM_YEAR}"
    )
    descriptions["QT_MAT_2023"] = (
        base_descriptions.get("QT_MAT", "Quantidade de matrículas")
        + f" ({EVASAO_FROM_YEAR})"
    )
    descriptions["QT_MAT_2024"] = (
        base_descriptions.get("QT_MAT", "Quantidade de matrículas")
        + f" ({EVASAO_TO_YEAR})"
    )
    descriptions["QT_CONC_2023"] = (
        base_descriptions.get("QT_CONC", "Quantidade de concluintes")
        + f" ({EVASAO_FROM_YEAR})"
    )
    descriptions["QT_ING_2024"] = (
        base_descriptions.get("QT_ING", "Quantidade de ingressantes")
        + f" ({EVASAO_TO_YEAR})"
    )
    return descriptions


def render():
    df = slice_evasao(load_evasao(), None, with_rate=False)
    base_descriptions = load_column_descriptions(EVASAO_FROM_YEAR)
    descriptions = {**base_descriptions, **evasao_column_descriptions(base_descriptions)}

    st.header("Dicionário de variáveis (evasão)")
    evasao_names = list(EVASAO_COUNT_COLS) + ["TX_EVAS"]
    dicionario = descriptions_table(
        {name: descriptions[name] for name in evasao_names if name in descriptions}
    )
    st.caption(
        f"{len(dicionario)} variáveis de evasão · {EVASAO_FROM_YEAR}→{EVASAO_TO_YEAR} · "
        f"fórmula: matriculados_{EVASAO_FROM_YEAR} − concluintes_{EVASAO_FROM_YEAR} − "
        f"matriculados_{EVASAO_TO_YEAR} + ingressantes_{EVASAO_TO_YEAR}"
    )
    st.dataframe(dicionario, width="stretch", hide_index=True)

    st.header("1. Universidade Federal do Rio Grande do Sul")
    ufrgs = evasao_ufrgs(df)
    st.caption(
        f"{len(ufrgs)} linhas · código da IES {CO_IES_UFRGS} · "
        "ofertas com pareamento nos dois censos"
    )
    st.dataframe(
        ufrgs,
        column_config=column_config_for(ufrgs, descriptions),
        width="stretch",
    )

    st.header("2. Um curso em cada estado")
    por_curso_estado = evasao_by_course_state(df)
    st.caption(
        f"{len(por_curso_estado)} linhas · quantidades somadas por NO_CURSO e SG_UF "
        "(taxa calculada após a soma)"
    )
    st.dataframe(
        por_curso_estado,
        column_config=column_config_for(por_curso_estado, descriptions),
        width="stretch",
    )

    st.header("3. Um curso, todos os estados")
    por_curso = evasao_by_course(df)
    st.caption(
        f"{len(por_curso)} linhas · quantidades somadas por NO_CURSO "
        "(taxa calculada após a soma)"
    )
    st.dataframe(
        por_curso,
        column_config=column_config_for(por_curso, descriptions),
        width="stretch",
    )

    st.header("4. Um estado, todos os cursos")
    por_estado = evasao_by_state(df)
    st.caption(
        f"{len(por_estado)} linhas · quantidades somadas por SG_UF "
        "(taxa calculada após a soma)"
    )
    st.dataframe(
        por_estado,
        column_config=column_config_for(por_estado, descriptions),
        width="stretch",
    )
