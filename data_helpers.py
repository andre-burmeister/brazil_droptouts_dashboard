import streamlit as st
import pandas as pd
from pathlib import Path

DADOS_ROOT = Path(__file__).parent / "dados"
CO_IES_UFRGS = 581
DEFAULT_YEAR = 2023
EVASAO_FROM_YEAR = 2023
EVASAO_TO_YEAR = 2024

OFFER_KEYS = ["CO_IES", "CO_CURSO", "CO_MUNICIPIO", "TP_DIMENSAO"]
OFFER_KEY_FILL = {"CO_MUNICIPIO": -1}
ID_COLS = [
    "NO_CURSO",
    "SG_UF",
    "NO_UF",
    "CO_UF",
    "NO_MUNICIPIO",
    "NO_REGIAO",
    "CO_REGIAO",
    "TP_MODALIDADE_ENSINO",
    "TP_GRAU_ACADEMICO",
    "TP_NIVEL_ACADEMICO",
    "TP_REDE",
    "TP_CATEGORIA_ADMINISTRATIVA",
]


def data_dir(year: int) -> Path:
    return DADOS_ROOT / f"microdados_censo_da_educacao_superior_{year}"


def cursos_csv_path(year: int) -> Path:
    return data_dir(year) / "dados" / f"MICRODADOS_CADASTRO_CURSOS_{year}.CSV"


def dictionary_path(year: int) -> Path:
    return (
        data_dir(year)
        / "Anexos"
        / "ANEXO I - Dicionário de Dados"
        / "dicionário_dados_educação_superior.xlsx"
    )


@st.cache_data
def load_cursos(year: int = DEFAULT_YEAR):
    return pd.read_csv(
        cursos_csv_path(year), sep=";", encoding="latin-1", low_memory=False
    )


@st.cache_data
def load_column_descriptions(year: int = DEFAULT_YEAR):
    raw = pd.read_excel(dictionary_path(year), sheet_name="cadastro_cursos", header=None)
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


def _mat_suffixes(columns):
    return {
        column[len("QT_MAT_") :]
        for column in columns
        if column.startswith("QT_MAT_")
    }


def _conc_suffixes(columns):
    return {
        column[len("QT_CONC_") :]
        for column in columns
        if column.startswith("QT_CONC_")
    }


def _ing_suffixes(columns):
    return {
        column[len("QT_ING_") :]
        for column in columns
        if column.startswith("QT_ING_")
    }


def demographic_suffixes(df_2023, df_2024):
    """Suffixes with MAT/CONC in 2023 and MAT/ING in 2024 for the stock formula."""
    cols_2023 = set(df_2023.columns)
    cols_2024 = set(df_2024.columns)
    suffixes = (
        _mat_suffixes(cols_2023)
        & _conc_suffixes(cols_2023)
        & _mat_suffixes(cols_2024)
        & _ing_suffixes(cols_2024)
    )
    return sorted(suffixes)


def _with_join_keys(df):
    prepared = df.copy()
    for column, fill_value in OFFER_KEY_FILL.items():
        prepared[column] = prepared[column].fillna(fill_value)
    return prepared


def compute_evasao(df_2023, df_2024):
    """Return QT_EVAS_* = MAT_2023 - CONC_2023 - MAT_2024 + ING_2024.

    Does not modify the input dataframes.
    """
    suffixes = demographic_suffixes(df_2023, df_2024)
    include_total = (
        "QT_MAT" in df_2023.columns
        and "QT_CONC" in df_2023.columns
        and "QT_MAT" in df_2024.columns
        and "QT_ING" in df_2024.columns
    )

    id_cols = [column for column in ID_COLS if column in df_2023.columns]
    mat_conc_2023 = []
    mat_ing_2024 = []
    if include_total:
        mat_conc_2023.extend(["QT_MAT", "QT_CONC"])
        mat_ing_2024.extend(["QT_MAT", "QT_ING"])
    for suffix in suffixes:
        mat_conc_2023.extend([f"QT_MAT_{suffix}", f"QT_CONC_{suffix}"])
        mat_ing_2024.extend([f"QT_MAT_{suffix}", f"QT_ING_{suffix}"])

    left_cols = list(dict.fromkeys(OFFER_KEYS + id_cols + mat_conc_2023))
    right_cols = list(dict.fromkeys(OFFER_KEYS + mat_ing_2024))

    left = _with_join_keys(df_2023.loc[:, left_cols])
    right = _with_join_keys(df_2024.loc[:, right_cols])

    rename_2023 = {}
    rename_2024 = {}
    if include_total:
        rename_2023["QT_MAT"] = "QT_MAT_2023"
        rename_2023["QT_CONC"] = "QT_CONC_2023"
        rename_2024["QT_MAT"] = "QT_MAT_2024"
        rename_2024["QT_ING"] = "QT_ING_2024"
    for suffix in suffixes:
        rename_2023[f"QT_MAT_{suffix}"] = f"QT_MAT_{suffix}_2023"
        rename_2023[f"QT_CONC_{suffix}"] = f"QT_CONC_{suffix}_2023"
        rename_2024[f"QT_MAT_{suffix}"] = f"QT_MAT_{suffix}_2024"
        rename_2024[f"QT_ING_{suffix}"] = f"QT_ING_{suffix}_2024"

    left = left.rename(columns=rename_2023)
    right = right.rename(columns=rename_2024)

    merged = left.merge(right, on=OFFER_KEYS, how="inner")

    quantity_renamed = list(rename_2023.values()) + list(rename_2024.values())
    merged[quantity_renamed] = merged[quantity_renamed].fillna(0)

    evasao_cols = {}
    if include_total:
        evasao_cols["QT_EVAS"] = (
            merged["QT_MAT_2023"]
            - merged["QT_CONC_2023"]
            - merged["QT_MAT_2024"]
            + merged["QT_ING_2024"]
        )
    for suffix in suffixes:
        evasao_cols[f"QT_EVAS_{suffix}"] = (
            merged[f"QT_MAT_{suffix}_2023"]
            - merged[f"QT_CONC_{suffix}_2023"]
            - merged[f"QT_MAT_{suffix}_2024"]
            + merged[f"QT_ING_{suffix}_2024"]
        )
    merged = pd.concat([merged, pd.DataFrame(evasao_cols, index=merged.index)], axis=1)

    if "CO_MUNICIPIO" in merged.columns:
        merged["CO_MUNICIPIO"] = merged["CO_MUNICIPIO"].replace(
            OFFER_KEY_FILL["CO_MUNICIPIO"], pd.NA
        )

    return merged


@st.cache_data
def load_evasao(
    from_year: int = EVASAO_FROM_YEAR, to_year: int = EVASAO_TO_YEAR
):
    return compute_evasao(load_cursos(from_year), load_cursos(to_year))


def evasao_quantity_columns(df):
    return [
        column
        for column in df.columns
        if column.startswith("QT_MAT_")
        or column.startswith("QT_CONC_")
        or column.startswith("QT_ING_")
        or column.startswith("QT_EVAS")
        or column
        in {
            "QT_MAT_2023",
            "QT_MAT_2024",
            "QT_CONC_2023",
            "QT_ING_2024",
            "QT_EVAS",
        }
    ]


def evasao_suffixes(df):
    """Demographic suffixes present as QT_EVAS_<suffix> in an evasion dataframe."""
    return sorted(
        column[len("QT_EVAS_") :]
        for column in df.columns
        if column.startswith("QT_EVAS_")
    )


def sum_evasao_by(df, keys, *, with_rates=True):
    """Aggregate evasion counts by keys; optionally add TX_EVAS_* after summing."""
    value_cols = [column for column in evasao_quantity_columns(df) if column in df.columns]
    grouped = (
        df.groupby(keys, as_index=False, dropna=False)[value_cols]
        .sum()
        .sort_values(keys)
        .reset_index(drop=True)
    )
    if with_rates:
        grouped = add_evasao_rates(grouped)
    return grouped


def add_evasao_rates(df):
    """Add TX_EVAS_* = QT_EVAS_* / QT_MAT_*_2023 after aggregation (new dataframe)."""
    rate_cols = {}
    if "QT_EVAS" in df.columns and "QT_MAT_2023" in df.columns:
        rate_cols["TX_EVAS"] = df["QT_EVAS"] / df["QT_MAT_2023"].replace(0, pd.NA)
    for suffix in evasao_suffixes(df):
        mat_col = f"QT_MAT_{suffix}_2023"
        evas_col = f"QT_EVAS_{suffix}"
        if mat_col in df.columns and evas_col in df.columns:
            rate_cols[f"TX_EVAS_{suffix}"] = df[evas_col] / df[mat_col].replace(
                0, pd.NA
            )
    if not rate_cols:
        return df.copy()
    return pd.concat([df, pd.DataFrame(rate_cols, index=df.index)], axis=1)


def evasao_by_course_state(df):
    return sum_evasao_by(df[df["SG_UF"].notna()], ["NO_CURSO", "SG_UF"])


def evasao_by_course(df):
    return sum_evasao_by(df, ["NO_CURSO"])


def evasao_by_state(df):
    return sum_evasao_by(df[df["SG_UF"].notna()], ["SG_UF"])


def evasao_ufrgs(df):
    return df[df["CO_IES"] == CO_IES_UFRGS]


def slice_evasao(df, suffix, *, with_rate=True):
    """Narrow an evasion dataframe to one demographic suffix (counts + optional rate)."""
    id_cols = [
        column
        for column in OFFER_KEYS + ID_COLS
        if column in df.columns
    ]
    if suffix is None or suffix == "":
        cols = id_cols + [
            column
            for column in (
                "QT_MAT_2023",
                "QT_MAT_2024",
                "QT_CONC_2023",
                "QT_ING_2024",
                "QT_EVAS",
            )
            if column in df.columns
        ]
        out = df.loc[:, cols].copy()
        if with_rate and "QT_EVAS" in out.columns and "QT_MAT_2023" in out.columns:
            out["TX_EVAS"] = out["QT_EVAS"] / out["QT_MAT_2023"].replace(0, pd.NA)
        return out

    cols = id_cols + [
        column
        for column in (
            f"QT_MAT_{suffix}_2023",
            f"QT_MAT_{suffix}_2024",
            f"QT_CONC_{suffix}_2023",
            f"QT_ING_{suffix}_2024",
            f"QT_EVAS_{suffix}",
        )
        if column in df.columns
    ]
    out = df.loc[:, cols].copy()
    if with_rate:
        mat_col = f"QT_MAT_{suffix}_2023"
        evas_col = f"QT_EVAS_{suffix}"
        if mat_col in out.columns and evas_col in out.columns:
            out[f"TX_EVAS_{suffix}"] = out[evas_col] / out[mat_col].replace(0, pd.NA)
    return out
