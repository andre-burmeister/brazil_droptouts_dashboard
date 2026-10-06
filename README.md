# Censo da Educação Superior — Cursos e evasão

Dashboard em [Streamlit](https://streamlit.io/) para explorar os microdados de cursos do [Censo da Educação Superior](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior), publicados pelo INEP.

As tabelas da aba Dados usam o cadastro de cursos de **2023**. A evasão 2023→2024 é calculada em memória (cache Streamlit) a partir dos dois anos, sem alterar os CSVs originais:

`evadidos = matriculados_2023 − concluintes_2023 − matriculados_2024 + ingressantes_2024`

Os microdados não entram no repositório. É preciso baixá-los no site do INEP e colocá-los na pasta `dados/`, como descrito abaixo.

## Requisitos

- Python 3.10 ou superior

## Baixar o projeto

```bash
git clone git@github.com:andre-burmeister/brazil_droptouts_dashboard.git
cd brazil_droptouts_dashboard
```

## Baixar os microdados

1. Abra a página de microdados do Censo da Educação Superior:  
   [https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior)
2. Baixe os microdados de **2023** e de **2024** (cada um é um `.zip` grande).
3. Extraia os zips de forma que as pastas fiquem dentro de `dados/`, na raiz deste projeto.

```text
dados/
├── microdados_censo_da_educacao_superior_2023/
│   ├── dados/
│   │   └── MICRODADOS_CADASTRO_CURSOS_2023.CSV
│   └── Anexos/
│       └── ANEXO I - Dicionário de Dados/
│           └── dicionário_dados_educação_superior.xlsx
└── microdados_censo_da_educacao_superior_2024/
    ├── dados/
    │   └── MICRODADOS_CADASTRO_CURSOS_2024.CSV
    └── Anexos/
        └── ANEXO I - Dicionário de Dados/
            └── dicionário_dados_educação_superior.xlsx
```

Os CSVs usam separador `;` e codificação Latin-1. O dicionário é a planilha `cadastro_cursos` do anexo em Excel.

## Executar localmente

Na raiz do projeto, com a pasta `dados/` já preenchida:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O Streamlit abre o dashboard em [http://localhost:8501](http://localhost:8501). A primeira carga lê os CSVs e pode levar alguns segundos; as leituras e o cálculo de evasão ficam em cache enquanto o processo estiver no ar.

A aba **Evasão** repete os recortes da aba Dados com as colunas `QT_EVAS_*` (e taxas após agregação). A aba **Mapa** mostra a taxa média de evasão por UF (média ponderada pelas matrículas de 2023), em um mapa Folium.

Para encerrar, use `Ctrl+C` no terminal.





## TODO:

1. Verificar os dados (dados negativos, dados acima de 100%):
Provavelmente é por causa de cursos que recém começaram, ou que tem poucos alunos.
Filtros:
- Número mínimo de estudantes no curos. acima de 1000 estudantes em todo o Brasil
- C

2. Criar um dashboard completo: 

- Barra leteral para os filtros
- Uma aba para cada tipo de filtro (sexo, idade, ...)
- Uma aba para comparação entre cursos


- Gráficos focando na UFRGS (podendo escolher a faculdade, mas a UFRGS é o default)

- Reformular as perguntas do trabalho 1 
- Focar o dashboard para responder as perguntas
- Colocar uma explicação

- Lado esquerdo:
	- Filtro por região do Brasil