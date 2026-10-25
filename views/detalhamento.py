"""Página: Detalhamento."""
import pandas as pd
import streamlit as st

from src import charts, data, ui
from src.config import (
    CORES_DEPENDENCIA, CORES_LOCALIZACAO, DEPENDENCIAS, ETAPAS, LOCALIZACOES, REGIOES,
)
from src.formatters import sinal


# ---------------------------------------------------------
# Filtros
# ---------------------------------------------------------
def _filtros(df: pd.DataFrame) -> tuple[int, str, str, str]:
    """Desenha a barra de filtros e devolve os valores escolhidos.

    Usa chaves próprias (d_...) para não interferir nos filtros da Visão Geral.
    """
    padroes = {
        "d_ano": int(df["Ano"].max()),
        "d_regiao": "Todas",
        "d_local": "Total",
        "d_dep": "Total",
    }
    for chave, valor in padroes.items():
        st.session_state.setdefault(chave, valor)

    anos = sorted(df["Ano"].unique(), reverse=True)

    with st.container(key="filtros"):
        c1, c2, c3, c4 = st.columns([0.8, 1.1, 1, 1.1])
        ano = c1.selectbox("ANO", anos, key="d_ano")
        regiao = c2.selectbox("REGIÃO", ["Todas", *REGIOES], key="d_regiao")
        local = c3.selectbox("LOCALIZAÇÃO", LOCALIZACOES, key="d_local")
        dep = c4.selectbox("DEPENDÊNCIA", DEPENDENCIAS, key="d_dep")

    return int(ano), regiao, local, dep


# ---------------------------------------------------------
# Página
# ---------------------------------------------------------
def render(df: pd.DataFrame) -> None:
    # ---------- Título e filtros ----------
    col_titulo, col_filtros = st.columns([1.5, 2.1], vertical_alignment="center")
    with col_titulo:
        ui.titulo_pagina("Detalhamento", "scatter")
    with col_filtros:
        ano, regiao, local, dep = _filtros(df)

    # Base com a localização e a dependência escolhidas (todas as etapas e séries)
    base = data.filtrar_detalhe(df, local, dep)
    # Só Fundamental e Médio, para a dispersão e o ranking
    base_etapas = base[base["Grupo_de_Abandono"].isin(ETAPAS["Fundamental + Médio"])]

    # ---------- Linha 1: renda e abandono por ano (largura toda) ----------
    with st.container(key="card_linha"):
        serie = data.serie_anual(data.filtrar_base(df, local, "Fundamental + Médio", dep), regiao)
        ui.card_titulo(
            "Renda média e abandono por ano",
            f"{int(df['Ano'].min())} – {int(df['Ano'].max())}",
        )
        if serie.empty:
            st.info("Sem dados para esta combinação de filtros. Troque a localização ou a dependência.")
        else:
            st.plotly_chart(charts.grafico_renda_abandono(serie, ano), width="stretch",
                            config=charts.PLOTLY_CONFIG)

    # ---------- Linha 2: dispersão (2/3) e ranking de UFs (1/3) ----------
    ufs = data.tabela_ufs(base_etapas, ano, regiao)
    col_disp, col_rank = st.columns([2, 1], gap="small")

    # Renda x abandono por UF
    with col_disp, st.container(key="card_dispersao"):
        if len(ufs) >= 3:
            r = ufs["Taxa"].corr(ufs["Renda"])
            detalhe = f"{len(ufs)} UFs · r = {sinal(r)}" if pd.notna(r) else f"{len(ufs)} UFs"
        else:
            detalhe = f"{len(ufs)} UFs"
        ui.card_titulo("Renda média × abandono por UF", detalhe)

        if ufs.empty:
            st.info("Sem dados de UFs para esta combinação. Troque a localização ou a dependência.")
        else:
            st.plotly_chart(charts.grafico_dispersao(ufs), width="stretch",
                            config=charts.PLOTLY_CONFIG)
            st.caption(
                f"Cada ponto é uma UF em {ano}. Taxa = média de Fundamental e Médio. "
                "A linha tracejada mostra a tendência (regressão linear)."
            )

    # Top 10 UFs com maior abandono
    with col_rank, st.container(key="card_ranking"):
        ui.card_titulo("UFs com maior abandono", str(ano))
        if ufs.empty:
            st.info("Sem dados de UFs para esta combinação.")
        else:
            st.plotly_chart(charts.grafico_ranking_ufs(ufs, top_n=10), width="stretch",
                            config=charts.PLOTLY_CONFIG)

    # ---------- Linha 3: por série e por região (metade cada) ----------
    col_serie, col_regiao = st.columns(2, gap="small")

    # Abandono em cada série escolar (1º EF ao 3º EM)
    with col_serie, st.container(key="card_series"):
        series = data.taxa_por_serie(base, ano, regiao)
        ui.card_titulo("Abandono por série", str(ano))
        if series.empty:
            st.info("Sem dados por série para esta combinação.")
        else:
            st.plotly_chart(charts.grafico_series(series), width="stretch",
                            config=charts.PLOTLY_CONFIG)

    # Abandono de cada região ao longo dos anos
    with col_regiao, st.container(key="card_regioes"):
        serie_reg = data.serie_regioes(base)
        ui.card_titulo(
            "Abandono por região",
            f"{int(df['Ano'].min())} – {int(df['Ano'].max())}",
        )
        if serie_reg.empty:
            st.info("Sem dados por região para esta combinação.")
        else:
            st.plotly_chart(charts.grafico_regioes(serie_reg, regiao), width="stretch",
                            config=charts.PLOTLY_CONFIG)

    # ---------- Linha 4: por localização e por dependência (metade cada) ----------
    col_loc, col_dep = st.columns(2, gap="small")

    # Urbana x Rural, barras verticais (usa a dependência escolhida; ignora o filtro de localização)
    with col_loc, st.container(key="card_localizacao"):
        loc = data.taxa_por_grupo(df, ano, regiao, "Localizacao", ["Urbana", "Rural"],
                                  {"Dependencia_Administrativa": dep})
        ui.card_titulo("Abandono por localização", str(ano))
        if loc.empty:
            st.info("Sem dados por localização para esta combinação.")
        else:
            st.plotly_chart(charts.grafico_barras_categoria(loc, CORES_LOCALIZACAO, vertical=True),
                            width="stretch", config=charts.PLOTLY_CONFIG)

    # Redes de ensino, barras horizontais (usa a localização escolhida; ignora o filtro de dependência)
    with col_dep, st.container(key="card_dependencia"):
        redes = data.taxa_por_grupo(df, ano, regiao, "Dependencia_Administrativa",
                                    ["Pública", "Estadual", "Municipal", "Federal", "Privada"],
                                    {"Localizacao": local})
        ui.card_titulo("Abandono por dependência", str(ano))
        if redes.empty:
            st.info("Sem dados por dependência para esta combinação.")
        else:
            st.plotly_chart(charts.grafico_barras_categoria(redes, CORES_DEPENDENCIA),
                            width="stretch", config=charts.PLOTLY_CONFIG)