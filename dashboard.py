import streamlit as st

from data_helpers import (
    EVASAO_FROM_YEAR,
    EVASAO_TO_YEAR,
    MODALIDADE_EAD,
    MODALIDADE_PRESENCIAL,
    dropout_rankings,
    evasao_by_state,
    evasao_suffixes,
    load_evasao,
    population_evasao,
)
from evasao_charts import MIN_ENROLLED, render as render_charts
from tab2_map import render as render_map

# Partitions and single characteristics from the INEP course census.
# Categories inside one group can be summed. Groups are not combined with each other.
DEMOGRAPHIC_GROUPS = [
    (
        "Sexo",
        [("FEM", "Feminino"), ("MASC", "Masculino")],
    ),
    (
        "Faixa etária",
        [
            ("0_17", "Até 17 anos"),
            ("18_24", "18 a 24 anos"),
            ("25_29", "25 a 29 anos"),
            ("30_34", "30 a 34 anos"),
            ("35_39", "35 a 39 anos"),
            ("40_49", "40 a 49 anos"),
            ("50_59", "50 a 59 anos"),
            ("60_MAIS", "60 anos ou mais"),
        ],
    ),
    (
        "Cor/raça",
        [
            ("BRANCA", "Branca"),
            ("PRETA", "Preta"),
            ("PARDA", "Parda"),
            ("AMARELA", "Amarela"),
            ("INDIGENA", "Indígena"),
            ("CORND", "Não declarada"),
        ],
    ),
    (
        "Nacionalidade",
        [("NACBRAS", "Brasileira"), ("NACESTRANG", "Estrangeira")],
    ),
    (
        "Turno",
        [("DIURNO", "Diurno"), ("NOTURNO", "Noturno")],
    ),
    (
        "Escola de origem",
        [
            ("PROCESCPUBLICA", "Ensino médio público"),
            ("PROCESCPRIVADA", "Ensino médio privado"),
            ("PROCNAOINFORMADA", "Não informada"),
        ],
    ),
    ("Alunos com deficiência", [("DEFICIENTE", "Com deficiência")]),
    ("Financiamento estudantil", [("FINANC", "Com financiamento")]),
    ("Reserva de vagas", [("RESERVA_VAGA", "Com reserva de vaga")]),
    ("PARFOR", [("PARFOR", "PARFOR")]),
    ("Apoio social", [("APOIO_SOCIAL", "Com apoio social")]),
    (
        "Atividade extracurricular",
        [("ATIV_EXTRACURRICULAR", "Com atividade extracurricular")],
    ),
    ("Mobilidade acadêmica", [("MOB_ACADEMICA", "Em mobilidade acadêmica")]),
]


def available_groups(suffixes):
    present = set(suffixes)
    groups = []
    for name, items in DEMOGRAPHIC_GROUPS:
        kept = [(suffix, label) for suffix, label in items if suffix in present]
        if kept:
            groups.append((name, kept))
    return groups


def recorte_text(modalidades, group, labels):
    chosen = set(modalidades)
    if chosen == {MODALIDADE_PRESENCIAL}:
        modo = "apenas cursos presenciais"
    elif chosen == {MODALIDADE_EAD}:
        modo = "apenas cursos a distância"
    elif chosen == {MODALIDADE_PRESENCIAL, MODALIDADE_EAD}:
        modo = "cursos presenciais e a distância"
    else:
        modo = "nenhuma modalidade de ensino"
    if group and labels:
        demo = f"{group} ({', '.join(labels)})"
    else:
        demo = "todos os alunos"
    return f"Recorte: {modo}; {demo}."


def render_filters(groups):
    with st.container(border=True):
        st.markdown("**Modalidade de ensino**")
        presencial_col, ead_col = st.columns(2)
        with presencial_col:
            presencial = st.checkbox(
                "Presencial", value=True, key="filtro_presencial"
            )
        with ead_col:
            ead = st.checkbox("A distância", value=False, key="filtro_ead")

        options = ["Todos os alunos", *[name for name, _items in groups]]
        group_name = st.selectbox(
            "Categoria demográfica",
            options,
            index=0,
            key="filtro_demografia",
            help=(
                "A taxa passa a usar as matrículas e os evadidos dessas categorias. "
                "Dentro da mesma categoria, os grupos marcados são somados."
            ),
        )
        selected = []
        labels = []
        if group_name != "Todos os alunos":
            items = dict(groups)[group_name]
            if len(items) == 1:
                selected = [items[0][0]]
                labels = [items[0][1]]
            else:
                st.caption("Marque as categorias que entram na soma.")
                n_cols = 4 if len(items) >= 4 else len(items)
                columns = st.columns(n_cols)
                for index, (suffix, label) in enumerate(items):
                    with columns[index % n_cols]:
                        if st.checkbox(label, value=True, key=f"filtro_demo_{suffix}"):
                            selected.append(suffix)
                            labels.append(label)

    modalidades = []
    if presencial:
        modalidades.append(MODALIDADE_PRESENCIAL)
    if ead:
        modalidades.append(MODALIDADE_EAD)
    if group_name == "Todos os alunos":
        suffixes = ()
    elif selected:
        suffixes = tuple(selected)
    else:
        suffixes = None
    return tuple(modalidades), suffixes, group_name if suffixes else None, labels


@st.cache_data
def load_dashboard(modalidades: tuple[int, ...], suffixes: tuple[str, ...]):
    population = population_evasao(load_evasao(), modalidades, suffixes)
    courses, areas = dropout_rankings(population, MIN_ENROLLED)
    by_state = evasao_by_state(population)
    rates = by_state.loc[:, ["SG_UF", "QT_MAT_2023", "QT_EVAS", "TX_EVAS"]].copy()
    return courses, areas, rates


def render():
    groups = available_groups(evasao_suffixes(load_evasao()))
    modalidades, suffixes, group_name, labels = render_filters(groups)
    if not modalidades:
        st.info("Marque ao menos uma modalidade de ensino.")
        return
    if suffixes is None:
        st.info("Marque ao menos uma categoria demográfica.")
        return

    recorte = recorte_text(modalidades, group_name, labels)
    st.caption(
        f"{recorte} Taxa = evadidos / matrículas de {EVASAO_FROM_YEAR} "
        f"({EVASAO_FROM_YEAR}→{EVASAO_TO_YEAR}). "
        "Os filtros atualizam os gráficos e o mapa automaticamente."
    )

    courses, areas, rates = load_dashboard(tuple(sorted(modalidades)), suffixes)
    map_key = "mapa-" + "-".join(str(item) for item in sorted(modalidades))
    map_key += "-" + ("-".join(suffixes) if suffixes else "total")

    charts_col, map_col = st.columns([1.25, 1], gap="large")
    with charts_col:
        render_charts(courses, areas)
    with map_col:
        render_map(rates, map_key=map_key)
