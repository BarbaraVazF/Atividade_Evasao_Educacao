"""Leitura do CSV e cálculos dos indicadores.

Estrutura do arquivo:
- Regiao == "Brasil"  -> linhas agregadas (Unidade_Geografica = Brasil ou nome da região)
- Regiao != "Brasil"  -> linhas por UF (Unidade_Geografica = nome do estado)
- Renda_Media é única por UF/ano (repete em todas as categorias).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st

from src.config import DATA_PATH, ETAPAS, SERIES, UF_SIGLAS

@st.cache_data(show_spinner="Carregando dados...")
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="utf-8")

    # Nível de cada linha: Brasil, Região ou UF
    eh_agregado = df["Regiao"].eq("Brasil")
    df["Nivel"] = np.select(
        [eh_agregado & df["Unidade_Geografica"].eq("Brasil"), eh_agregado],
        ["Brasil", "Região"],
        default="UF",
    )
    df["Sigla"] = df["Unidade_Geografica"].map(UF_SIGLAS)
    return df


def filtrar_base(df: pd.DataFrame, localizacao: str, etapa: str) -> pd.DataFrame:
    """Rede total (todas as dependências), na localização e etapa escolhidas."""
    return df[
        df["Dependencia_Administrativa"].eq("Total")
        & df["Localizacao"].eq(localizacao)
        & df["Grupo_de_Abandono"].isin(ETAPAS[etapa])
    ]


def serie_anual(base: pd.DataFrame, regiao: str) -> pd.DataFrame:
    """Taxa e renda por ano do Brasil ou de uma região (linhas agregadas oficiais)."""
    unidade = "Brasil" if regiao == "Todas" else regiao
    sel = base[base["Nivel"].isin(["Brasil", "Região"]) & base["Unidade_Geografica"].eq(unidade)]
    return (
        sel.groupby("Ano", as_index=False)
        .agg(Taxa=("Taxa_Abandono", "mean"), Renda=("Renda_Media", "mean"))
        .sort_values("Ano")
    )


def tabela_ufs(base: pd.DataFrame, ano: int, regiao: str) -> pd.DataFrame:
    """Taxa e renda de cada UF no ano escolhido, da maior para a menor taxa."""
    sel = base[base["Nivel"].eq("UF") & base["Ano"].eq(ano)]
    if regiao != "Todas":
        sel = sel[sel["Regiao"].eq(regiao)]
    return (
        sel.groupby(["Unidade_Geografica", "Sigla", "Regiao"], as_index=False)
        .agg(Taxa=("Taxa_Abandono", "mean"), Renda=("Renda_Media", "first"))
        .dropna(subset=["Taxa"])
        .sort_values("Taxa", ascending=False)
    )


@dataclass
class KPIs:
    taxa: float | None
    taxa_delta_pp: float | None      # variação em pontos percentuais vs ano anterior
    renda: float | None
    renda_delta_pct: float | None    # variação em % vs ano anterior
    correlacao: float | None
    n_ufs: int
    critico_nome: str
    critico_taxa: float | None
    critico_rotulo: str


def calcular_kpis(base: pd.DataFrame, ano: int, regiao: str) -> KPIs:
    # Taxa e renda do ano escolhido e do ano anterior
    serie = serie_anual(base, regiao).set_index("Ano")
    atual = serie.loc[ano] if ano in serie.index else None
    anterior = serie.loc[ano - 1] if (ano - 1) in serie.index else None

    taxa = float(atual["Taxa"]) if atual is not None else None
    renda = float(atual["Renda"]) if atual is not None else None
    taxa_delta = taxa - float(anterior["Taxa"]) if (anterior is not None and taxa is not None) else None
    renda_delta = (
        (renda / float(anterior["Renda"]) - 1) * 100
        if (anterior is not None and renda is not None)
        else None
    )

    # Correlação de Pearson entre renda e abandono, comparando as UFs
    ufs = tabela_ufs(base, ano, regiao)
    corr = float(ufs["Taxa"].corr(ufs["Renda"])) if len(ufs) >= 3 else None

    # Mais crítica: região (se "Todas") ou UF (se uma região foi escolhida)
    if regiao == "Todas":
        reg = base[base["Nivel"].eq("Região") & base["Ano"].eq(ano)]
        por_regiao = reg.groupby("Unidade_Geografica")["Taxa_Abandono"].mean().dropna()
        nome = por_regiao.idxmax() if not por_regiao.empty else "—"
        valor = float(por_regiao.max()) if not por_regiao.empty else None
        rotulo = "Região mais crítica"
    else:
        nome = ufs.iloc[0]["Unidade_Geografica"] if not ufs.empty else "—"
        valor = float(ufs.iloc[0]["Taxa"]) if not ufs.empty else None
        rotulo = "UF mais crítica"

    return KPIs(taxa, taxa_delta, renda, renda_delta, corr, len(ufs), nome, valor, rotulo)

# ---------------------------------------------------------
# Detalhamento
# ---------------------------------------------------------
def filtrar_detalhe(df: pd.DataFrame, localizacao: str, dependencia: str) -> pd.DataFrame:
    """Localização e dependência escolhidas, com todas as etapas e séries."""
    return df[
        df["Localizacao"].eq(localizacao)
        & df["Dependencia_Administrativa"].eq(dependencia)
    ]


def taxa_por_regiao(base: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Taxa média (Fundamental + Médio) de cada região no ano, da maior para a menor."""
    sel = base[
        base["Nivel"].eq("Região")
        & base["Ano"].eq(ano)
        & base["Grupo_de_Abandono"].isin(ETAPAS["Fundamental + Médio"])
    ]
    return (
        sel.groupby("Unidade_Geografica", as_index=False)
        .agg(Taxa=("Taxa_Abandono", "mean"))
        .rename(columns={"Unidade_Geografica": "Regiao"})
        .dropna(subset=["Taxa"])
        .sort_values("Taxa", ascending=False)
    )


def taxa_por_serie(base: pd.DataFrame, ano: int, regiao: str) -> pd.DataFrame:
    """Taxa de cada série escolar (1º EF ao 3º EM) no Brasil ou na região."""
    unidade = "Brasil" if regiao == "Todas" else regiao
    sel = base[
        base["Nivel"].isin(["Brasil", "Região"])
        & base["Unidade_Geografica"].eq(unidade)
        & base["Ano"].eq(ano)
        & base["Grupo_de_Abandono"].isin(SERIES.keys())
    ][["Grupo_de_Abandono", "Taxa_Abandono"]].dropna()

    sel = sel.assign(
        Serie=sel["Grupo_de_Abandono"].map(SERIES),
        Etapa=np.where(
            sel["Grupo_de_Abandono"].str.contains("Médio"), "Ensino Médio", "Ensino Fundamental"
        ),
        Ordem=sel["Grupo_de_Abandono"].map({k: i for i, k in enumerate(SERIES)}),
    )
    return sel.sort_values("Ordem").rename(columns={"Taxa_Abandono": "Taxa"})

def serie_regioes(base: pd.DataFrame) -> pd.DataFrame:
    """Taxa média (Fundamental + Médio) de cada região em cada ano."""
    sel = base[
        base["Nivel"].eq("Região")
        & base["Grupo_de_Abandono"].isin(ETAPAS["Fundamental + Médio"])
    ]
    return (
        sel.groupby(["Ano", "Unidade_Geografica"], as_index=False)
        .agg(Taxa=("Taxa_Abandono", "mean"))
        .rename(columns={"Unidade_Geografica": "Regiao"})
        .dropna(subset=["Taxa"])
    )