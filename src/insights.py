"""Cálculos da página Insights."""
import numpy as np
import pandas as pd

from src import data
from src.config import ETAPAS

AMBAS = ETAPAS["Fundamental + Médio"]


def _brasil(df: pd.DataFrame, ano: int, localizacao: str = "Total",
            dependencia: str = "Total") -> pd.DataFrame:
    """Linhas do Brasil (Fundamental e Médio) em um ano."""
    return df[
        df["Nivel"].eq("Brasil") & df["Ano"].eq(ano)
        & df["Localizacao"].eq(localizacao)
        & df["Dependencia_Administrativa"].eq(dependencia)
        & df["Grupo_de_Abandono"].isin(AMBAS)
    ]


def correlacao_por_ano(df: pd.DataFrame) -> pd.DataFrame:
    """Correlação de Pearson (renda x abandono entre as UFs) em cada ano."""
    base = data.filtrar_base(df, "Total", "Fundamental + Médio")
    linhas = []
    for ano in sorted(df["Ano"].unique()):
        ufs = data.tabela_ufs(base, int(ano), "Todas")
        linhas.append({"Ano": int(ano), "r": ufs["Taxa"].corr(ufs["Renda"])})
    return pd.DataFrame(linhas)


def estatisticas_correlacao(df: pd.DataFrame, ano: int) -> dict:
    """Correlação do ano e testes para ver se ela é confiável."""
    base = data.filtrar_base(df, "Total", "Fundamental + Médio")
    ufs = data.tabela_ufs(base, ano, "Todas")
    r = ufs["Taxa"].corr(ufs["Renda"])
    rica = ufs.loc[ufs["Renda"].idxmax()]
    sem_rica = ufs[ufs["Sigla"] != rica["Sigla"]]
    return {
        "ufs": ufs,
        "n": len(ufs),
        "r": r,
        "r2": r ** 2,                                   # parte da variação explicada pela renda
        # Spearman = Pearson sobre as posições (ranks); não precisa de scipy
        "spearman": ufs["Taxa"].rank().corr(ufs["Renda"].rank()),
        "uf_rica": rica["Sigla"],
        "r_sem_rica": sem_rica["Taxa"].corr(sem_rica["Renda"]),
        # quanto a taxa muda, em média, a cada R$ 1.000 a mais de renda
        "inclinacao_mil": float(np.polyfit(ufs["Renda"], ufs["Taxa"], 1)[0] * 1000),
    }


def tendencia(corr: pd.DataFrame) -> float:
    """Inclinação da reta de tendência do r (quanto ele muda por ano, em média)."""
    return float(np.polyfit(corr["Ano"], corr["r"], 1)[0])


def queda_por_renda(df: pd.DataFrame, ano_ini: int, ano_fim: int) -> tuple[float, float]:
    """Queda média do abandono (p.p.) nas UFs abaixo e acima da mediana de renda."""
    base = data.filtrar_base(df, "Total", "Fundamental + Médio")
    ini = data.tabela_ufs(base, ano_ini, "Todas").set_index("Sigla")
    fim = data.tabela_ufs(base, ano_fim, "Todas").set_index("Sigla")
    queda = ini["Taxa"] - fim["Taxa"]
    pobres = ini["Renda"] < ini["Renda"].median()
    return float(queda[pobres].mean()), float(queda[~pobres].mean())


def regioes(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Taxa (média EF + EM) e renda de cada região, da maior para a menor taxa."""
    sel = df[
        df["Nivel"].eq("Região") & df["Ano"].eq(ano)
        & df["Localizacao"].eq("Total") & df["Dependencia_Administrativa"].eq("Total")
        & df["Grupo_de_Abandono"].isin(AMBAS)
    ]
    return (
        sel.groupby("Unidade_Geografica")
        .agg(Taxa=("Taxa_Abandono", "mean"), Renda=("Renda_Media", "mean"))
        .sort_values("Taxa", ascending=False)
    )


def redes(df: pd.DataFrame, ano: int) -> pd.Series:
    """Taxa (média EF + EM) do Brasil por dependência administrativa."""
    sel = df[
        df["Nivel"].eq("Brasil") & df["Ano"].eq(ano) & df["Localizacao"].eq("Total")
        & df["Grupo_de_Abandono"].isin(AMBAS)
        & df["Dependencia_Administrativa"].isin(["Estadual", "Municipal", "Federal", "Privada"])
    ]
    return (
        sel.groupby("Dependencia_Administrativa")["Taxa_Abandono"]
        .mean()
        .sort_values(ascending=False)
    )


def territorio(df: pd.DataFrame, ano: int) -> dict:
    """Taxa (média EF + EM) do Brasil na zona urbana e na rural."""
    return {loc: _brasil(df, ano, loc)["Taxa_Abandono"].mean() for loc in ["Urbana", "Rural"]}

def maiores_quedas(df: pd.DataFrame, ano_ini: int, ano_fim: int, n: int = 2) -> pd.DataFrame:
    """UFs com a maior queda de abandono (p.p.) entre dois anos."""
    base = data.filtrar_base(df, "Total", "Fundamental + Médio")
    ini = data.tabela_ufs(base, ano_ini, "Todas").set_index("Unidade_Geografica")["Taxa"]
    fim = data.tabela_ufs(base, ano_fim, "Todas").set_index("Unidade_Geografica")["Taxa"]
    return (ini - fim).sort_values(ascending=False).head(n).rename("Queda").reset_index()

def rural_por_regiao(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Taxa (média EF + EM) urbana e rural de cada região, com a razão rural/urbana."""
    linhas = []
    for regiao in ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]:
        t = (data.taxa_por_grupo(df, ano, regiao, "Localizacao", ["Urbana", "Rural"],
                                 {"Dependencia_Administrativa": "Total"})
             .groupby("Categoria")["Taxa"].mean())
        linhas.append({"Regiao": regiao, "Urbana": t.get("Urbana"), "Rural": t.get("Rural")})
    tabela = pd.DataFrame(linhas).set_index("Regiao")
    tabela["Razao"] = tabela["Rural"] / tabela["Urbana"]
    return tabela.sort_values("Razao", ascending=False)