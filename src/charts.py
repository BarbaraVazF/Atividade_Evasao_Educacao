"""Gráficos interativos em Plotly."""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from src.config import (
    AMARELO_ESCURO, AMARELO_LAPIS, AZUL_LOUSA, CINZA_LINHA, CINZA_MEDIO, CORES_REGIAO, GRAFITE,
)

FONTE = "Avenir, Avenir Next, Nunito Sans, system-ui, sans-serif"

# Barra de ferramentas do gráfico (zoom, baixar PNG...)
PLOTLY_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}


def _layout_base(fig: go.Figure, altura: int) -> go.Figure:
    """Estilo comum a todos os gráficos."""
    fig.update_layout(
        height=altura,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",      # fundo transparente: usa o do card
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONTE, color=GRAFITE, size=13),
        separators=",.",                     # vírgula decimal, ponto de milhar
        hoverlabel=dict(bgcolor="white", bordercolor=CINZA_LINHA,
                        font=dict(family=FONTE, color=GRAFITE)),
    )
    return fig


def grafico_renda_abandono(serie: pd.DataFrame, ano_destaque: int) -> go.Figure:
    """Linhas de taxa de abandono (eixo esquerdo) e renda média (eixo direito)."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Linha da taxa de abandono
    fig.add_trace(
        go.Scatter(
            x=serie["Ano"], y=serie["Taxa"], name="Taxa de abandono (%)",
            mode="lines+markers",
            line=dict(color=AZUL_LOUSA, width=3, shape="spline", smoothing=0.6),
            marker=dict(size=7, color=AZUL_LOUSA, line=dict(color="white", width=1.5)),
            hovertemplate="Abandono: <b>%{y:.2f}%</b><extra></extra>",
        ),
        secondary_y=False,
    )

    # Linha da renda média
    fig.add_trace(
        go.Scatter(
            x=serie["Ano"], y=serie["Renda"], name="Renda média (R$/mês)",
            mode="lines+markers",
            line=dict(color=AMARELO_LAPIS, width=3),
            marker=dict(size=7, color=AMARELO_LAPIS, line=dict(color="white", width=1.5)),
            hovertemplate="Renda: <b>R$ %{y:,.0f}</b><extra></extra>",
        ),
        secondary_y=True,
    )

    _layout_base(fig, 400)
    fig.update_layout(
        hovermode="x unified",               # uma caixa com as duas séries do ano
        legend=dict(orientation="h", y=1.08, x=0, font=dict(size=12)),
    )
    fig.update_xaxes(tickmode="linear", dtick=1, showgrid=False, linecolor=CINZA_LINHA)
    fig.update_yaxes(
        secondary_y=False, ticksuffix="%", tickformat=".1f",
        gridcolor=CINZA_LINHA, zeroline=False, tickfont=dict(color=AZUL_LOUSA),
    )
    fig.update_yaxes(
        secondary_y=True, tickprefix="R$ ", tickformat=",.0f",
        showgrid=False, zeroline=False, tickfont=dict(color=AMARELO_ESCURO),
    )
    return fig

def grafico_ranking_ufs(ufs: pd.DataFrame, top_n: int) -> go.Figure:
    """Barras horizontais com as UFs de maior abandono, coloridas por região."""
    dados = ufs.head(top_n).iloc[::-1]   # inverte para a maior ficar no topo

    fig = go.Figure()

    # Uma série por região, para a legenda mostrar as cores
    for regiao, cor in CORES_REGIAO.items():
        parte = dados[dados["Regiao"].eq(regiao)]
        if parte.empty:
            continue
        fig.add_trace(
            go.Bar(
                x=parte["Taxa"],
                y=parte["Sigla"],
                orientation="h",
                name=regiao,
                marker=dict(color=cor, cornerradius=4),
                text=[f"{v:.1f}%".replace(".", ",") for v in parte["Taxa"]],
                textposition="outside",
                cliponaxis=False,
                customdata=parte[["Unidade_Geografica", "Renda"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b>"
                    "<br>Abandono: %{x:.2f}%"
                    "<br>Renda média: R$ %{customdata[1]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

    # Altura cresce com o número de UFs
    _layout_base(fig, 400)
    fig.update_layout(
        barmode="overlay",
        bargap=0.35,
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, font=dict(size=12)),
    )
    # Mantém a ordem do ranking (sem isso o Plotly agruparia por região)
    fig.update_yaxes(categoryorder="array", categoryarray=dados["Sigla"].tolist(), showgrid=False)
    # Esconde o eixo X e deixa folga à direita para o rótulo do valor
    fig.update_xaxes(visible=False, range=[0, dados["Taxa"].max() * 1.18])
    return fig

# ---------------------------------------------------------
# Detalhamento
# ---------------------------------------------------------
def grafico_dispersao(ufs: pd.DataFrame) -> go.Figure:
    """Renda (X) x abandono (Y) por UF, com linha de tendência."""
    fig = go.Figure()

    for regiao, cor in CORES_REGIAO.items():
        parte = ufs[ufs["Regiao"].eq(regiao)]
        if parte.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=parte["Renda"], y=parte["Taxa"], mode="markers", name=regiao,
                marker=dict(size=12, color=cor, line=dict(color="white", width=1.5)),
                customdata=parte[["Unidade_Geografica"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>Renda: R$ %{x:,.0f}"
                    "<br>Abandono: %{y:.2f}%<extra></extra>"
                ),
            )
        )

    if len(ufs) >= 3:
        a, b = np.polyfit(ufs["Renda"], ufs["Taxa"], 1)
        x = np.array([ufs["Renda"].min(), ufs["Renda"].max()])
        fig.add_trace(
            go.Scatter(
                x=x, y=a * x + b, mode="lines", name="Tendência",
                line=dict(color=GRAFITE, width=2, dash="dash"), hoverinfo="skip",
            )
        )

    _layout_base(fig, 380)
    fig.update_layout(legend=dict(orientation="h", y=1.08, x=0, font=dict(size=12)))
    fig.update_xaxes(title="Renda média (R$/mês)", tickprefix="R$ ", tickformat=",.0f",
                     gridcolor=CINZA_LINHA, zeroline=False)
    fig.update_yaxes(title="Taxa de abandono (%)", ticksuffix="%", tickformat=".1f",
                     gridcolor=CINZA_LINHA, zeroline=False, rangemode="tozero")
    return fig


def _eixos_limpos(fig: go.Figure) -> go.Figure:
    """Sem linhas de grade: só os eixos esquerdo e de baixo, em linha contínua."""
    estilo = dict(showgrid=False, showline=True, linecolor=CINZA_MEDIO, linewidth=1, zeroline=False)
    fig.update_xaxes(**estilo)
    fig.update_yaxes(**estilo)
    return fig


def grafico_series(series: pd.DataFrame) -> go.Figure:
    """Taxa de cada série escolar: Fundamental em azul, Médio em amarelo."""
    cores = np.where(series["Etapa"].eq("Ensino Médio"), AMARELO_LAPIS, AZUL_LOUSA)
    fig = go.Figure(
        go.Bar(
            x=series["Serie"], y=series["Taxa"],
            marker=dict(color=cores, cornerradius=4),
            text=[f"{v:.1f}%".replace(".", ",") for v in series["Taxa"]],
            textposition="outside", cliponaxis=False,
            textfont=dict(size=11), constraintext="none",
            customdata=series[["Grupo_de_Abandono"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Abandono: %{y:.2f}%<extra></extra>",
        )
    )

    _layout_base(fig, 340)
    fig.update_layout(bargap=0.35, showlegend=False)
    _eixos_limpos(fig)
    # Rótulos em duas linhas ("1º" em cima, "EF" embaixo) para caber na metade da tela
    fig.update_xaxes(
        tickangle=0,
        tickvals=series["Serie"],
        ticktext=[t.replace(" ", "<br>") for t in series["Serie"]],
    )
    fig.update_yaxes(ticksuffix="%", range=[0, series["Taxa"].max() * 1.25],
                     showgrid=True, gridcolor=CINZA_LINHA, griddash="solid")

    # Linha tracejada onde começa o Ensino Médio (barras amarelas)
    medio = series[series["Etapa"].eq("Ensino Médio")]
    if not medio.empty and len(medio) < len(series):
        posicao = series["Serie"].tolist().index(medio["Serie"].iloc[0]) - 0.5
        fig.add_vline(x=posicao, line=dict(color=GRAFITE, width=1.5, dash="dash"))
        fig.add_annotation(
            x=posicao, y=1, yref="paper", text="Ensino Médio", showarrow=False,
            xanchor="left", xshift=6, font=dict(size=12, color=GRAFITE),
        )
    return fig


def grafico_regioes(serie: pd.DataFrame, destaque: str) -> go.Figure:
    """Uma linha por região, ano a ano. Com uma região filtrada, as outras ficam apagadas."""
    fig = go.Figure()
    for regiao, cor in CORES_REGIAO.items():
        parte = serie[serie["Regiao"].eq(regiao)].sort_values("Ano")
        if parte.empty:
            continue
        ativo = destaque in ("Todas", regiao)
        fig.add_trace(
            go.Scatter(
                x=parte["Ano"], y=parte["Taxa"], name=regiao, mode="lines+markers",
                line=dict(color=cor, width=3 if ativo else 2),
                marker=dict(size=6, color=cor, line=dict(color="white", width=1)),
                opacity=1 if ativo else 0.25,
                hovertemplate=f"<b>{regiao}</b>: %{{y:.2f}}%<extra></extra>",
            )
        )

    _layout_base(fig, 340)
    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.15, x=0, font=dict(size=12)),  # legenda embaixo
    )
    _eixos_limpos(fig)
    fig.update_xaxes(tickmode="linear", dtick=1)
    fig.update_yaxes(ticksuffix="%", tickformat=".0f", rangemode="tozero",
                     showgrid=True, gridcolor=CINZA_LINHA, griddash="solid")
    return fig

# ---------------------------------------------------------
# Insights
# ---------------------------------------------------------
def grafico_correlacao_tempo(corr: pd.DataFrame) -> go.Figure:
    """Correlação (r) ano a ano, com reta de tendência e as faixas forte/moderada/fraca."""
    fig = go.Figure()

    # Limites das faixas de intensidade
    for y, rotulo in [(-0.5, "forte ↓  |  moderada ↑"), (-0.3, "moderada ↓  |  fraca ↑")]:
        fig.add_hline(y=y, line=dict(color=CINZA_MEDIO, width=1, dash="dot"),
                      annotation_text=rotulo, annotation_position="top left",
                      annotation_font=dict(size=11, color=GRAFITE))
    fig.add_hline(y=0, line=dict(color=GRAFITE, width=1))   # r = 0: nenhuma relação

    # Reta de tendência
    a, b = np.polyfit(corr["Ano"], corr["r"], 1)
    fig.add_trace(go.Scatter(
        x=corr["Ano"], y=a * corr["Ano"] + b, mode="lines", name="Tendência",
        line=dict(color=AMARELO_LAPIS, width=2, dash="dash"), hoverinfo="skip",
    ))

    # Valores de r
    fig.add_trace(go.Scatter(
        x=corr["Ano"], y=corr["r"], mode="lines+markers+text", name="r (Pearson)",
        line=dict(color=AZUL_LOUSA, width=3),
        marker=dict(size=8, color=AZUL_LOUSA, line=dict(color="white", width=1.5)),
        text=[f"{v:.2f}".replace(".", ",").replace("-", "−") for v in corr["r"]],
        textposition="bottom center", textfont=dict(size=11, color=AZUL_LOUSA),
        hovertemplate="%{x}: r = %{y:.2f}<extra></extra>",
    ))

    _layout_base(fig, 360)
    fig.update_layout(legend=dict(orientation="h", y=1.1, x=0, font=dict(size=12)))
    estilo = dict(showline=True, linecolor=CINZA_MEDIO, zeroline=False)
    fig.update_xaxes(tickmode="linear", dtick=1, showgrid=False, **estilo)
    fig.update_yaxes(range=[-0.8, 0.1], dtick=0.1, tickformat=".1f", showgrid=False, **estilo)
    return fig