import json
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from data_helpers import EVASAO_FROM_YEAR, EVASAO_TO_YEAR, evasao_by_state, load_evasao

GEOJSON_PATH = Path(__file__).parent / "geo" / "brazil_states.geojson"


@st.cache_data
def state_dropout_rates():
    """Student-weighted mean dropout rate per state: Σ QT_EVAS / Σ QT_MAT_2023."""
    by_state = evasao_by_state(load_evasao())
    return by_state.loc[:, ["SG_UF", "QT_MAT_2023", "QT_EVAS", "TX_EVAS"]].copy()


def brazil_choropleth(rates: pd.DataFrame) -> folium.Map:
    display = rates.copy()
    display["TX_EVAS_PCT"] = (display["TX_EVAS"] * 100).round(2)
    rate_by_uf = display.set_index("SG_UF")["TX_EVAS_PCT"].to_dict()
    mat_by_uf = display.set_index("SG_UF")["QT_MAT_2023"].to_dict()

    with open(GEOJSON_PATH, encoding="utf-8") as handle:
        geojson = json.load(handle)

    for feature in geojson["features"]:
        sigla = feature["properties"]["sigla"]
        taxa = rate_by_uf.get(sigla)
        matriculas = mat_by_uf.get(sigla)
        feature["properties"]["taxa"] = (
            f"{taxa:.2f}%" if taxa is not None and pd.notna(taxa) else "sem dados"
        )
        feature["properties"]["matriculas"] = (
            f"{int(matriculas):,}".replace(",", ".")
            if matriculas is not None and pd.notna(matriculas)
            else "—"
        )

    mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

    folium.Choropleth(
        geo_data=geojson,
        data=display,
        columns=["SG_UF", "TX_EVAS_PCT"],
        key_on="feature.properties.sigla",
        fill_color="YlOrRd",
        fill_opacity=0.75,
        line_opacity=0.6,
        nan_fill_color="lightgray",
        legend_name=(
            f"Taxa média ponderada de evasão {EVASAO_FROM_YEAR}→{EVASAO_TO_YEAR} (%)"
        ),
        highlight=True,
    ).add_to(mapa)

    folium.GeoJson(
        geojson,
        style_function=lambda _: {
            "fillColor": "transparent",
            "color": "transparent",
            "fillOpacity": 0,
            "weight": 0,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "sigla", "taxa", "matriculas"],
            aliases=[
                "Estado:",
                "UF:",
                "Taxa ponderada:",
                f"Matrículas {EVASAO_FROM_YEAR}:",
            ],
            sticky=True,
        ),
    ).add_to(mapa)

    return mapa


def render():
    st.header("Taxa média de evasão por estado")
    st.caption(
        f"Média ponderada pelo número de matrículas de {EVASAO_FROM_YEAR} em cada "
        f"oferta de curso: Σ evadidos / Σ matriculados_{EVASAO_FROM_YEAR} "
        f"({EVASAO_FROM_YEAR}→{EVASAO_TO_YEAR})."
    )

    rates = state_dropout_rates()
    st_folium(brazil_choropleth(rates), width="stretch", height=560, returned_objects=[])

    table = rates.copy()
    table["Taxa (%)"] = (table["TX_EVAS"] * 100).round(2)
    table = table.rename(
        columns={
            "SG_UF": "UF",
            "QT_MAT_2023": f"Matrículas {EVASAO_FROM_YEAR}",
            "QT_EVAS": "Evadidos",
        }
    ).loc[:, ["UF", f"Matrículas {EVASAO_FROM_YEAR}", "Evadidos", "Taxa (%)"]]
    st.dataframe(
        table.sort_values("Taxa (%)", ascending=False),
        hide_index=True,
        width="stretch",
    )
