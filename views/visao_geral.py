"""Página: Visão Geral."""
import pandas as pd
import streamlit as st

from src import charts, data, ui
from src.config import (
    AMARELO_LAPIS, AZUL_LOUSA, DEPENDENCIAS, LOCALIZACOES, REGIOES, VERDE_QUADRO,
)
from src.formatters import pct, reais, sinal

# Opções do filtro Etapa. "Todas" corresponde à combinação Fundamental + Médio dos cálculos.
OPCOES_ETAPA = ["Todas", "Ensino Fundamental", "Ensino Médio"]


# ---------------------------------------------------------
# Filtros
# ---------------------------------------------------------
def _padroes(df: pd.DataFrame) -> dict:
    """Valores iniciais dos filtros."""
    return {
        "f_ano": int(df["Ano"].max()),
        "f_regiao": "Todas",
        "f_local": "Total",
        "f_dep": "Total",
        "f_etapa": "Todas",
    }


def _filtros(df: pd.DataFrame) -> tuple[int, str, str, str, str]:
    """Desenha a barra de filtros e devolve os valores escolhidos."""
    for chave, valor in _padroes(df).items():
        st.session_state.setdefault(chave, valor)

    # Se a sessão guardou um valor antigo que não existe mais na lista, volta para "Todas"
    if st.session_state["f_etapa"] not in OPCOES_ETAPA:
        st.session_state["f_etapa"] = "Todas"

    anos = sorted(df["Ano"].unique(), reverse=True)

    with st.container(key="filtros"):
        c1, c2, c3, c4, c5 = st.columns([0.8, 1.1, 1, 1.1, 1.2])
        ano = c1.selectbox("ANO", anos, key="f_ano")
        regiao = c2.selectbox("REGIÃO", ["Todas", *REGIOES], key="f_regiao")
        local = c3.selectbox("LOCALIZAÇÃO", LOCALIZACOES, key="f_local")
        dep = c4.selectbox("DEPENDÊNCIA", DEPENDENCIAS, key="f_dep")
        etapa = c5.selectbox("ETAPA", OPCOES_ETAPA, key="f_etapa")

    # "Todas" corresponde à combinação Fundamental + Médio usada nos cálculos
    etapa_calculo = "Fundamental + Médio" if etapa == "Todas" else etapa
    return int(ano), regiao, local, dep, etapa_calculo


# ---------------------------------------------------------
# Página
# ---------------------------------------------------------
def render(df: pd.DataFrame) -> None:
    # ---------- Título e filtros ----------
    col_titulo, col_filtros = st.columns([1, 2.6], vertical_alignment="center")
    with col_titulo:
        ui.titulo_pagina("Visão Geral")
    with col_filtros:
        ano, regiao, local, dep, etapa = _filtros(df)

    # ---------- Banner (o título acompanha a região escolhida) ----------
    escopo = "no Brasil" if regiao == "Todas" else f"na região {regiao}"
    ui.banner(
        int(df["Ano"].min()),
        int(df["Ano"].max()),
        f"Abandono escolar e renda média {escopo}",
    )

    # ---------- Cards de indicadores ----------
    base = data.filtrar_base(df, local, etapa, dep)
    k = data.calcular_kpis(base, ano, regiao)

    cards = [
        ui.kpi_card(
            "Taxa média de abandono", pct(k.taxa), "trending_down", AZUL_LOUSA,
            rodape=f"vs {ano - 1}" if k.taxa_delta_pp is not None else "sem ano anterior",
            delta=None if k.taxa_delta_pp is None else f"{sinal(k.taxa_delta_pp)} p.p.",
            delta_bom=None if k.taxa_delta_pp is None else k.taxa_delta_pp <= 0,
        ),
        ui.kpi_card(
            "Renda média mensal", reais(k.renda), "wallet", AMARELO_LAPIS,
            rodape=f"vs {ano - 1}" if k.renda_delta_pct is not None else "sem ano anterior",
            delta=None if k.renda_delta_pct is None else f"{sinal(k.renda_delta_pct)}%",
            delta_bom=None if k.renda_delta_pct is None else k.renda_delta_pct >= 0,
        ),
        ui.kpi_card(
            "Correlação renda × abandono",
            "—" if k.correlacao is None else f"r = {sinal(k.correlacao)}",
            "scatter", VERDE_QUADRO,
            rodape=f"Pearson entre {k.n_ufs} UFs em {ano}",
        ),
        ui.kpi_card(
            k.critico_rotulo, k.critico_nome, "map_pin", AMARELO_LAPIS,
            rodape=f"{pct(k.critico_taxa)} de abandono médio",
        ),
    ]
    for coluna, card in zip(st.columns(4), cards):
        with coluna:
            ui.html(card)

    # ---------- Gráfico: renda e abandono por ano (largura toda) ----------
    with st.container(key="card_linha"):
        serie = data.serie_anual(base, regiao)
        ui.card_titulo(
            "Renda média e abandono por ano",
            f"{int(df['Ano'].min())} – {int(df['Ano'].max())}",
        )
        if serie.empty:
            st.info("Sem dados para esta combinação de filtros. "
                    "Troque a localização, a dependência ou a etapa.")
        else:
            st.plotly_chart(
                charts.grafico_renda_abandono(serie, ano),
                width="stretch",
                config=charts.PLOTLY_CONFIG,
            )