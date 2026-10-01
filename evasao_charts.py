import altair as alt
import pandas as pd
import streamlit as st
from branca.utilities import color_brewer

from data_helpers import EVASAO_FROM_YEAR

MIN_ENROLLED = 100
LARGEST_IN_AREA = 3
CHART_VIEWPORT_PX = 480


def cine_area_palette(n: int) -> list[str]:
    """ColorBrewer Paired via branca (dependência do Folium), sem o amarelo claro.

    Os seis tons escuros vêm primeiro para as barras do topo continuarem legíveis.
    """
    paired = color_brewer("Paired", n=12)
    dark = [paired[i] for i in (1, 3, 5, 7, 9, 11)]
    light = [paired[i] for i in (0, 2, 4, 6, 8)]
    palette = dark + light
    if n > len(palette):
        raise ValueError(
            f"A paleta Paired tem {len(palette)} cores úteis e há {n} áreas."
        )
    return palette[:n]


def _plot_frame(df, name_col):
    plot = pd.DataFrame(
        {
            "nome": df[name_col].astype(str),
            "area": df["NO_CINE_AREA_GERAL"].fillna("Sem área").astype(str),
            "taxa": (df["TX_EVAS"] * 100).astype(float),
            "matriculas": df["QT_MAT_2023"].round().astype(int),
            "evadidos": df["QT_EVAS"].round().astype(int),
        }
    )
    plot["rotulo"] = plot["taxa"].map(lambda value: f"{value:.1f}%")
    return plot


def _pt_int(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


def _largest_courses_by_area(courses, n=LARGEST_IN_AREA):
    """Três maiores cursos de cada área, pelo total nacional de matrículas do nome.

    O curso entra na área geral CINE com mais matrículas. O tamanho é a soma das
    matrículas de todas as ofertas daquele NO_CURSO no Brasil.
    """
    frame = pd.DataFrame(
        {
            "area": courses["NO_CINE_AREA_GERAL"].fillna("Sem área").astype(str),
            "nome_curso": courses["NO_CURSO"].astype(str),
            "matriculas_curso": courses["QT_MAT_2023"].fillna(0).round().astype(int),
        }
    )
    frame = frame.sort_values(
        ["area", "matriculas_curso", "nome_curso"],
        ascending=[True, False, True],
    )
    frame["rank"] = frame.groupby("area", sort=False).cumcount() + 1
    top = frame.loc[frame["rank"] <= n].copy()
    top["rotulo"] = (
        top["nome_curso"]
        + " ("
        + top["matriculas_curso"].map(_pt_int)
        + " matrículas)"
    )
    wide = top.pivot(index="area", columns="rank", values="rotulo")
    for rank in range(1, n + 1):
        if rank not in wide.columns:
            wide[rank] = pd.NA
    wide = wide.loc[:, list(range(1, n + 1))]
    wide.columns = [f"curso_{rank}" for rank in range(1, n + 1)]
    return wide.reset_index()


def _with_largest_courses(area_plot, courses):
    largest = _largest_courses_by_area(courses)
    merged = area_plot.merge(largest, on="area", how="left")
    for rank in range(1, LARGEST_IN_AREA + 1):
        column = f"curso_{rank}"
        merged[column] = merged[column].fillna("—")
    return merged


def _tooltips(nome_title, data):
    fields = [
        alt.Tooltip("nome:N", title=nome_title),
        alt.Tooltip("area:N", title="Área geral (CINE)"),
        alt.Tooltip("taxa:Q", title="Taxa de evasão (%)", format=".1f"),
        alt.Tooltip(
            "matriculas:Q",
            title=f"Matrículas {EVASAO_FROM_YEAR}",
            format=",.0f",
        ),
        alt.Tooltip("evadidos:Q", title="Evadidos", format=",.0f"),
    ]
    titles = {
        1: "1º maior curso",
        2: "2º maior curso",
        3: "3º maior curso",
    }
    for rank, title in titles.items():
        column = f"curso_{rank}"
        if column in data.columns:
            fields.append(alt.Tooltip(f"{column}:N", title=title))
    return fields


def _color(domain, colors, legend):
    return alt.Color(
        "area:N",
        title="Área geral (CINE)",
        scale=alt.Scale(domain=domain, range=colors),
        legend=legend,
    )


def _horizontal_bars(data, domain, colors, *, legend, nome_title):
    xmax = float(data["taxa"].max()) if len(data) else 1
    ranked = (
        data.sort_values("taxa", ascending=False, kind="mergesort")["nome"]
        .drop_duplicates()
        .tolist()
    )
    base = alt.Chart(data).encode(
        y=alt.Y(
            "nome:N",
            sort=ranked,
            title=None,
            axis=alt.Axis(labelLimit=220),
        ),
        x=alt.X(
            "taxa:Q",
            title="Taxa de evasão (%)",
            scale=alt.Scale(domain=[0, xmax * 1.18], nice=False),
            axis=alt.Axis(format=".0f"),
        ),
        tooltip=_tooltips(nome_title, data),
    )
    bars = base.mark_bar().encode(color=_color(domain, colors, legend))
    labels = base.mark_text(align="left", dx=4, fontSize=11, color="#243037").encode(
        text="rotulo:N"
    )
    return (
        (bars + labels)
        .properties(
            width="container",
            height=alt.Step(30),
            padding={"right": 72, "top": 6, "bottom": 4},
            # fit-x ajusta só a largura. A altura continua sendo uma faixa por barra.
            autosize=alt.AutoSizeParams(
                type="fit-x", contains="padding", resize=True
            ),
        )
        .configure_view(strokeWidth=0)
        .configure_axis(labelFontSize=12, titleFontSize=13)
        .configure_axisY(grid=False)
    )


def render(courses, areas):
    if courses.empty or areas.empty:
        st.info(
            f"Nenhum curso com mais de {MIN_ENROLLED} matrículas em {EVASAO_FROM_YEAR} "
            "nesse recorte."
        )
        return

    course_plot = _plot_frame(courses, "NO_CURSO")
    area_plot = _with_largest_courses(
        _plot_frame(areas, "NO_CINE_AREA_GERAL"), courses
    )
    domain = list(dict.fromkeys([*area_plot["area"], *course_plot["area"]]))
    colors = cine_area_palette(len(domain))
    legend = alt.Legend(orient="bottom", columns=1, labelLimit=280)

    st.header("Cursos com maior taxa de evasão")
    st.caption(
        f"Todos os cursos com mais de {MIN_ENROLLED} matrículas em {EVASAO_FROM_YEAR} "
        "no recorte, somadas em todo o Brasil, da maior taxa para a menor. "
        "A cor da barra é a área geral CINE com mais matrículas naquele curso. "
        "Role o gráfico para ver a lista completa."
    )
    _show_chart(
        _horizontal_bars(
            course_plot, domain, colors, legend=legend, nome_title="Curso"
        )
    )

    st.header("Áreas com maior taxa de evasão")
    st.caption(
        f"Todas as áreas gerais CINE desses cursos. A taxa é a soma dos evadidos "
        f"dividida pela soma das matrículas de {EVASAO_FROM_YEAR}. "
        "O mouse em cada barra mostra também os três maiores cursos da área, "
        "pelo total de matrículas desse curso no Brasil. "
        "As cores são as mesmas do gráfico de cursos."
    )
    _show_chart(
        _horizontal_bars(
            area_plot, domain, colors, legend=None, nome_title="Área"
        )
    )


def _show_chart(chart):
    # A altura fixa no st.altair_chart faz o Vega comprimir as barras.
    # O gráfico fica na altura natural e a rolagem fica neste contêiner.
    with st.container(height=CHART_VIEWPORT_PX, border=True):
        st.altair_chart(chart, width="stretch", theme=None)
