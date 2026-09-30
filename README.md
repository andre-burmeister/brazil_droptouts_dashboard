# Censo da Educação Superior 2024 — Cursos

Dashboard em [Streamlit](https://streamlit.io/) para explorar os microdados de cursos do [Censo da Educação Superior 2024](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior), publicados pelo INEP.

O aplicativo lê o cadastro de cursos (`MICRODADOS_CADASTRO_CURSOS_2024.CSV`) e usa o dicionário oficial de variáveis para mostrar a descrição de cada coluna ao passar o mouse.

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
2. Na seção **2024**, baixe **Microdados do Censo da Educação Superior 2024**. O arquivo é um `.zip` grande.
3. Extraia o zip de forma que a pasta `microdados_censo_da_educacao_superior_2024` fique dentro de `dados/`, na raiz deste projeto.

O aplicativo usa dois arquivos dessa pasta. O restante do pacote (questionários, leia-me e demais CSVs) pode permanecer no lugar; não é necessário reorganizar arquivo por arquivo.

```text
dados/
└── microdados_censo_da_educacao_superior_2024/
    ├── dados/
    │   └── MICRODADOS_CADASTRO_CURSOS_2024.CSV
    └── Anexos/
        └── ANEXO I - Dicionário de Dados/
            └── dicionário_dados_educação_superior.xlsx
```

O CSV usa separador `;` e codificação Latin-1. O dicionário é a planilha `cadastro_cursos` do anexo em Excel.

## Executar localmente

Na raiz do projeto, com a pasta `dados/` já preenchida:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O Streamlit abre o dashboard em [http://localhost:8501](http://localhost:8501). A primeira carga lê o CSV inteiro e pode levar alguns segundos; as leituras seguintes ficam em cache enquanto o processo estiver no ar.

Para encerrar, use `Ctrl+C` no terminal.
