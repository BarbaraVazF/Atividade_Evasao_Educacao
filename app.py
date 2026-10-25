"""Ponto de entrada do dashboard."""
import streamlit as st

st.set_page_config(
    page_title="Abandono escolar e renda",
    page_icon="🎓",
    layout="wide",
)

from src import ui  # noqa: E402
from src.data import carregar_dados  # noqa: E402
from views import detalhamento, insights, visao_geral  # noqa: E402

ui.aplicar_css()
df = carregar_dados()

pagina = ui.sidebar()

ROTAS = {
    "visao": visao_geral.render,
    "detalhe": detalhamento.render,
    "insights": insights.render,
}
ROTAS[pagina](df)