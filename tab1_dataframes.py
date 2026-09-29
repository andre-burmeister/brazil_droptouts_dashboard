import streamlit as st

from data_helpers import (
    courses_by_state,
    courses_total,
    load_column_descriptions,
    load_cursos,
    states_total,
    ufrgs_courses,
    CO_IES_UFRGS,
)


def column_config_for(df, descriptions):
    return {
        column: st.column_config.Column(column, help=descriptions[column])
        for column in df.columns
        if descriptions.get(column)
    }


def render():
    df = load_cursos()
    descriptions = load_column_descriptions()

    st.header("1. Universidade Federal do Rio Grande do Sul")
    ufrgs = ufrgs_courses(df)
    st.caption(f"{len(ufrgs)} linhas · código da IES {CO_IES_UFRGS}")
    st.dataframe(
        ufrgs,
        column_config=column_config_for(ufrgs, descriptions),
        width='stretch',
    )

    st.header("2. Um curso em cada estado")
    por_curso_estado = courses_by_state(df)
    st.caption(
        f"{len(por_curso_estado)} linhas · quantidades (QT_) somadas por NO_CURSO e SG_UF"
    )
    st.dataframe(
        por_curso_estado,
        column_config=column_config_for(por_curso_estado, descriptions),
        width='stretch',
    )

    st.header("3. Um curso, todos os estados")
    por_curso = courses_total(df)
    st.caption(f"{len(por_curso)} linhas · quantidades (QT_) somadas por NO_CURSO")
    st.dataframe(
        por_curso,
        column_config=column_config_for(por_curso, descriptions),
        width='stretch',
    )

    st.header("4. Um estado, todos os cursos")
    por_estado = states_total(df)
    st.caption(f"{len(por_estado)} linhas · quantidades (QT_) somadas por SG_UF")
    st.dataframe(
        por_estado,
        column_config=column_config_for(por_estado, descriptions),
        width='stretch',
    )
