import json
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from data_helpers import EVASAO_FROM_YEAR, EVASAO_TO_YEAR

GEOJSON_PATH = Path(__file__).parent / "geo" / "brazil_states.geojson"


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


def render(rates: pd.DataFrame, *, map_key: str):
    st.header("Taxa média de evasão por estado")
    st.caption(
        f"Média ponderada pelas matrículas de {EVASAO_FROM_YEAR} em cada oferta do recorte: "
        f"Σ evadidos / Σ matriculados_{EVASAO_FROM_YEAR} "
        f"({EVASAO_FROM_YEAR}→{EVASAO_TO_YEAR}). "
        "Entram todas as ofertas do filtro, sem o corte de 100 matrículas dos gráficos."
    )
    if rates.empty or rates["QT_MAT_2023"].fillna(0).sum() == 0:
        st.info("Nenhuma oferta de curso nesse recorte.")
        return

    st_folium(
        brazil_choropleth(rates),
        height=560,
        use_container_width=True,
        returned_objects=[],
        key=map_key,
    )

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
