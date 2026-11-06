



import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from io import BytesIO


# ==================================================
# 1. CONFIGURAÇÕES
# ==================================================

st.set_page_config(
    page_title="Consulta Fácil CNQ",
    page_icon="📚",
    layout="wide"
)

caminho_banco = Path(__file__).resolve().parent / "consulta_facil_cnq.db"


# ==================================================
# 2. IDENTIDADE VISUAL
# ==================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F1F6FA;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    h1 {
        color: #102A43;
        font-weight: 800;
        letter-spacing: -1px;
    }

    h2, h3 {
        color: #173F5F;
        font-weight: 700;
    }

    p {
        color: #486581;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D9E5EF;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(16, 42, 67, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: #627D98;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #168AAD;
        font-weight: 800;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        border-radius: 10px;
        background-color: #FFFFFF;
        border-color: #C9D8E5;
    }

    .stDownloadButton button {
        background-color: #168AAD;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }

    .stDownloadButton button:hover {
        background-color: #126782;
        color: white;
        border: none;
    }

    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #D9E5EF;
        border-radius: 14px;
        overflow: hidden;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 3. CABEÇALHO
# ==================================================

st.markdown("""
<div style="background: linear-gradient(120deg, #102A43, #168AAD);
padding: 30px; border-radius: 18px; margin-bottom: 25px;">

<div style="font-size: 14px; color: #B9E6F2;
letter-spacing: 2px; font-weight: bold;">
CATÁLOGO NACIONAL DE QUALIFICAÇÕES
</div>

<h1 style="color: white; margin: 10px 0;">
📚 Consulta Fácil CNQ
</h1>

<p style="color: #E5F3F8; font-size: 16px; margin-bottom: 0;">
Consulte Unidades de Formação, Unidades de Competência,
qualificações e áreas de formação de forma simples e organizada.
</p>

</div>
""", unsafe_allow_html=True)


# ==================================================
# 4. VERIFICAR BANCO
# ==================================================

if not caminho_banco.exists():
    st.error("O banco de dados não foi encontrado.")
    st.stop()


# ==================================================
# 5. INDICADORES
# ==================================================

try:
    with sqlite3.connect(caminho_banco) as conexao:

        total_ufcd = pd.read_sql_query(
            "SELECT COUNT(*) AS total FROM dados_originais",
            conexao
        ).iloc[0]["total"]

        total_ucs = pd.read_sql_query(
            "SELECT COUNT(*) AS total FROM ucs_originais",
            conexao
        ).iloc[0]["total"]

        total_qualificacoes = pd.read_sql_query(
            "SELECT COUNT(*) AS total FROM qualificacoes_lista",
            conexao
        ).iloc[0]["total"]

        total_areas = pd.read_sql_query(
            "SELECT COUNT(DISTINCT \"Código Área de Formação\") AS total FROM dados_originais",
            conexao
        ).iloc[0]["total"]

except Exception as erro:
    st.error(f"Erro ao acessar o banco de dados: {erro}")
    st.stop()


col1, col2, col3, col4 = st.columns(4)

col1.metric("Registros UFCD", f"{total_ufcd:,}".replace(",", "."))
col2.metric("Registros UC", f"{total_ucs:,}".replace(",", "."))
col3.metric("Qualificações", total_qualificacoes)
col4.metric("Áreas de formação", total_areas)

st.divider()


# ==================================================
# 6. PESQUISA E FILTROS
# ==================================================

st.subheader("🔎 Pesquisar no catálogo")

st.write(
    "Pesquise UFCDs, Unidades de Competência ou qualificações "
    "pelo código ou pelo nome."
)

st.caption(
    "Digite um código ou uma palavra para encontrar os registros."
)

termo = st.text_input(
    "Código ou nome",
    placeholder="Ex.: 0349, Ambiente ou Técnico de Informática",
    help="A pesquisa procura nas listas de UFCDs, UCs e qualificações."
)


# ==================================================
# 7. FILTROS
# ==================================================

with sqlite3.connect(caminho_banco) as conexao:

    areas_ufcd = pd.read_sql_query("""
        SELECT DISTINCT "Designação Área de Formação" AS area
        FROM dados_originais
        WHERE "Designação Área de Formação" IS NOT NULL
    """, conexao)

    areas_uc = pd.read_sql_query("""
        SELECT DISTINCT "Designação Área de Formação" AS area
        FROM ucs_originais
        WHERE "Designação Área de Formação" IS NOT NULL
    """, conexao)

    areas_qualificacoes = pd.read_sql_query("""
        SELECT DISTINCT "Área de Formação" AS area
        FROM qualificacoes_lista
        WHERE "Área de Formação" IS NOT NULL
    """, conexao)

    niveis_ufcd = pd.read_sql_query("""
        SELECT DISTINCT CAST("Nível QNQ" AS TEXT) AS nivel
        FROM dados_originais
        WHERE "Nível QNQ" IS NOT NULL
    """, conexao)

    niveis_uc = pd.read_sql_query("""
        SELECT DISTINCT CAST("Nível QNQ" AS TEXT) AS nivel
        FROM ucs_originais
        WHERE "Nível QNQ" IS NOT NULL
    """, conexao)

    niveis_qualificacoes = pd.read_sql_query("""
        SELECT DISTINCT CAST("Nível QNQ" AS TEXT) AS nivel
        FROM qualificacoes_lista
        WHERE "Nível QNQ" IS NOT NULL
    """, conexao)


todas_areas = set(
    areas_ufcd["area"].dropna().tolist()
    + areas_uc["area"].dropna().tolist()
    + areas_qualificacoes["area"].dropna().tolist()
)

todos_niveis = set(
    niveis_ufcd["nivel"].dropna().tolist()
    + niveis_uc["nivel"].dropna().tolist()
    + niveis_qualificacoes["nivel"].dropna().tolist()
)

opcoes_areas = ["Todas as áreas"] + sorted(todas_areas)
opcoes_niveis = ["Todos os níveis"] + sorted(todos_niveis)

col_area, col_nivel = st.columns(2)

with col_area:
    area_selecionada = st.selectbox(
        "Área de formação",
        opcoes_areas
    )

with col_nivel:
    nivel_selecionado = st.selectbox(
        "Nível QNQ",
        opcoes_niveis
    )


# ==================================================
# 8. CONSULTA UNIFICADA
# ==================================================

if termo.strip():

    pesquisa = f"%{termo.strip()}%"

    consulta_sql = """
    SELECT
        'UFCD' AS Tipo,
        CAST("Código UFCD" AS TEXT) AS Código,
        "UFCD" AS Designação,
        "Carga Horária UFCD" AS Horas,
        NULL AS Créditos,
        "Componente" AS Componente,
        "Código Área de Formação" AS Código_Area,
        "Designação Área de Formação" AS Área,
        "Código Qualificação" AS Código_Qualificação,
        "Qualificação" AS Qualificação,
        CAST("Nível QNQ" AS TEXT) AS QNQ,
        CAST("Nível QEQ" AS TEXT) AS QEQ
    FROM dados_originais

    UNION ALL

    SELECT
        'UC' AS Tipo,
        CAST("Código UC" AS TEXT) AS Código,
        "UC" AS Designação,
        NULL AS Horas,
        "Pontos de Crédito UC" AS Créditos,
        "Componente" AS Componente,
        "Código Área de Formação" AS Código_Area,
        "Designação Área de Formação" AS Área,
        "Código Qualificação" AS Código_Qualificação,
        "Qualificação" AS Qualificação,
        CAST("Nível QNQ" AS TEXT) AS QNQ,
        CAST("Nível QEQ" AS TEXT) AS QEQ
    FROM ucs_originais

    UNION ALL

    SELECT
        'Qualificação' AS Tipo,
        CAST("Código Qualificação" AS TEXT) AS Código,
        "Qualificação" AS Designação,
        NULL AS Horas,
        NULL AS Créditos,
        NULL AS Componente,
        "Código Área de Formação" AS Código_Area,
        "Área de Formação" AS Área,
        "Código Qualificação" AS Código_Qualificação,
        "Qualificação" AS Qualificação,
        CAST("Nível QNQ" AS TEXT) AS QNQ,
        CAST("Nível QEQ" AS TEXT) AS QEQ
    FROM qualificacoes_lista
    """

    consulta_completa = f"""
    SELECT *
    FROM ({consulta_sql}) AS catalogo
    WHERE (
        Código LIKE ?
        OR Designação LIKE ?
        OR Código_Qualificação LIKE ?
        OR Qualificação LIKE ?
    )
    AND (
        ? = 'Todas as áreas'
        OR Área = ?
    )
    AND (
        ? = 'Todos os níveis'
        OR QNQ = ?
    )
    ORDER BY Tipo, Código
    """

    try:
        with sqlite3.connect(caminho_banco) as conexao:

            resultado = pd.read_sql_query(
                consulta_completa,
                conexao,
                params=(
                    pesquisa,
                    pesquisa,
                    pesquisa,
                    pesquisa,
                    area_selecionada,
                    area_selecionada,
                    nivel_selecionado,
                    nivel_selecionado
                )
            )

        st.divider()

        if resultado.empty:

            st.warning(
                "Nenhum resultado encontrado. "
                "Experimente outro código ou palavra."
            )

        else:

            st.subheader("📋 Resultados da pesquisa")

            st.success(
                f"{len(resultado):,} registros encontrados.".replace(",", ".")
            )

            st.dataframe(
                resultado,
                use_container_width=True,
                hide_index=True,
                height=450,
                column_config={

                    "Tipo": st.column_config.TextColumn(
                        "Tipo",
                        width="small"
                    ),

                    "Código": st.column_config.TextColumn(
                        "Código",
                        width="small"
                    ),

                    "Designação": st.column_config.TextColumn(
                        "Nome",
                        width="large"
                    ),

                    "Horas": st.column_config.TextColumn(
                        "Carga horária"
                    ),

                    "Créditos": st.column_config.TextColumn(
                        "Pontos de crédito"
                    ),

                    "Componente": st.column_config.TextColumn(
                        "Componente"
                    ),

                    "Código_Area": st.column_config.TextColumn(
                        "Código da área"
                    ),

                    "Área": st.column_config.TextColumn(
                        "Área de formação",
                        width="medium"
                    ),

                    "Código_Qualificação": st.column_config.TextColumn(
                        "Código da qualificação"
                    ),

                    "Qualificação": st.column_config.TextColumn(
                        "Qualificação",
                        width="large"
                    ),

                    "QNQ": st.column_config.TextColumn(
                        "Nível QNQ"
                    ),

                    "QEQ": st.column_config.TextColumn(
                        "Nível QEQ"
                    )
                }
            )


            # ==================================================
            # 9. EXPORTAR PARA EXCEL
            # ==================================================

            arquivo_excel = BytesIO()

            with pd.ExcelWriter(
                arquivo_excel,
                engine="openpyxl"
            ) as escritor:

                resultado.to_excel(
                    escritor,
                    index=False,
                    sheet_name="Resultados CNQ"
                )

            st.download_button(
                label="📥 Baixar resultados em Excel",
                data=arquivo_excel.getvalue(),
                file_name="consulta_facil_cnq.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


    except Exception as erro:

        st.error(f"Não foi possível realizar a pesquisa: {erro}")

else:

    st.info(
        "Digite um código ou nome para iniciar a pesquisa."
    )


# ==================================================
# 10. RODAPÉ
# ==================================================

st.divider()

st.markdown("""
<div style="
    text-align: center;
    color: #829AB1;
    font-size: 13px;
    padding: 10px;
">
    <strong>Consulta Fácil CNQ</strong><br>
    Ferramenta de consulta do Catálogo Nacional de Qualificações<br>
    Projeto de extensão – 100 horas
</div>
""", unsafe_allow_html=True)
