"""Página: Insights."""
import pandas as pd
import streamlit as st

from src import charts, data, insights, ui
from src.formatters import num, pct, sinal

EF, EM = "Ensino Fundamental", "Ensino Médio"


def _forca(r: float) -> str:
    """Classifica a correlação pelo valor absoluto."""
    a = abs(r)
    return "forte" if a >= 0.5 else "moderada" if a >= 0.3 else "fraca"


def _cor(texto: str, cor: str) -> str:
    """Destaca uma palavra: azul, verde, vermelho ou amarelo (ver CSS .realce-...)."""
    return f'<span class="realce-{cor}">{texto}</span>'


def render(df: pd.DataFrame) -> None:
    ano = int(df["Ano"].max())          # sempre o ano mais recente da base

    with st.container(key="insights_titulo"):
        ui.titulo_pagina("Insights", "lightbulb")

    # ---------- Correlação e evolução ----------
    est = insights.estatisticas_correlacao(df, ano)
    ufs, r = est["ufs"], est["r"]
    corr = insights.correlacao_por_ano(df).set_index("Ano")["r"]
    ano_ini = int(corr.index.min())
    r_ini = corr[ano_ini]
    incl = insights.tendencia(corr.reset_index())
    salto = corr[ano] - corr[ano - 1]
    queda_pobres, queda_ricos = insights.queda_por_renda(df, ano - 1, ano)
    quedas = insights.maiores_quedas(df, ano - 1, ano)
    serie = (data.serie_anual(data.filtrar_base(df, "Total", "Fundamental + Médio"), "Todas")
             .set_index("Ano"))

    # ---------- Regiões e estados ----------
    reg = insights.regioes(df, ano)
    top = ufs.sort_values("Taxa", ascending=False)
    rank_renda = ufs["Renda"].rank(ascending=False).astype(int)
    rico_no_top = top.head(5).loc[rank_renda[top.head(5).index].idxmin()]   # mais rico entre os 5 piores
    pobre_baixo = ufs[ufs["Renda"] < ufs["Renda"].median()].sort_values("Taxa").iloc[0]

    # ---------- Etapa, rede e território ----------
    series = (data.taxa_por_serie(data.filtrar_detalhe(df, "Total", "Total"), ano, "Todas")
              .set_index("Serie")["Taxa"])
    por_etapa = (data.taxa_por_grupo(df, ano, "Todas", "Localizacao", ["Total"],
                                     {"Dependencia_Administrativa": "Total"})
                 .set_index("Etapa")["Taxa"])
    por_rede = (data.taxa_por_grupo(df, ano, "Todas", "Dependencia_Administrativa",
                                    ["Estadual", "Municipal", "Federal", "Privada"], {"Localizacao": "Total"})
                .pivot(index="Categoria", columns="Etapa", values="Taxa"))
    por_local = (data.taxa_por_grupo(df, ano, "Todas", "Localizacao", ["Urbana", "Rural"],
                                     {"Dependencia_Administrativa": "Total"})
                 .pivot(index="Categoria", columns="Etapa", values="Taxa"))
    rural_reg = insights.rural_por_regiao(df, ano)
    reg_rural = rural_reg.index[0]                                   # região onde o campo mais pesa
    campo_menor = rural_reg[rural_reg["Razao"] < 1].index.tolist()   # regiões onde o campo evade menos

    def uf(i: int) -> str:
        """Estado na posição i do ranking, em negrito, com a taxa."""
        return f"<b>{top.iloc[i]['Unidade_Geografica']}</b> ({pct(top.iloc[i]['Taxa'])})"

    def queda(i: int) -> str:
        """Estado com a i-ésima maior queda no último ano."""
        return f"{quedas.iloc[i]['Unidade_Geografica']} ({sinal(-quedas.iloc[i]['Queda'], 1)} p.p.)"

    # ---------- Linha 1: renda x abandono (texto + gráfico, largura toda) ----------
    with st.container(key="card_correlacao"):
        ui.card_cabecalho("Renda × abandono", "scatter", f"r = {sinal(r)} em {ano}", amarela=True)
        col_txt, col_graf = st.columns([1, 1.25], gap="medium")
        with col_txt:
            ui.html(
                f"""
                <p class="insight-texto">Em {ano}, a correlação de Pearson entre renda média e taxa de abandono
                (média do Fundamental e do Médio) nas {est['n']} UFs foi de <b>r = {sinal(r)}</b>, numa escala de
                −1 a +1. O valor é {_cor(_forca(r), 'azul')} e quase zero: a renda explica só
                <b>{num(est['r2'] * 100, 1)}%</b> das diferenças de abandono entre os estados.</p>
                <p class="insight-texto">Isso é {_cor('positivo', 'verde')}: o abandono deixou de acompanhar a renda,
                e estados de renda baixa, como {pobre_baixo['Unidade_Geografica']} ({pct(pobre_baixo['Taxa'])}),
                estão entre os que menos evadem.</p>
                <p class="insight-texto">Em {ano_ini}, a relação era {_cor(_forca(r_ini), 'vermelho')}
                (r = {sinal(r_ini)}). Desde então, o r {_cor('sobe', 'verde')} em média {sinal(incl, 2)} por ano
                rumo a zero. A maior mudança veio de {ano - 1} para {ano} ({sinal(salto)}), quando o abandono caiu
                {sinal(-queda_pobres, 1)} p.p. nos estados de renda abaixo da mediana e {sinal(-queda_ricos, 1)} p.p.
                nos demais, com quedas fortes em {queda(0)} e {queda(1)}.</p>
                """
            )
        with col_graf:
            fig = charts.grafico_correlacao_tempo(corr.reset_index())
            fig.update_layout(height=320)
            st.plotly_chart(fig, width="stretch", config=charts.PLOTLY_CONFIG)

    # ---------- Linha 2: onde pesa + etapa + rede e território ----------
    col_onde, col_etapa, col_rede = st.columns(3, gap="small")

    with col_onde, st.container(key="card_onde"):
        ui.card_cabecalho("Onde o abandono pesa", "map_pin", str(ano))
        ui.html(
            f"""
            <p class="insight-texto">O {_cor(reg.index[0], 'azul')} tem a maior taxa regional
            ({pct(reg['Taxa'].iloc[0])}), mas as cinco regiões estão a só
            {num(reg['Taxa'].max() - reg['Taxa'].min(), 1)} p.p. umas das outras: a diferença está
            {_cor('entre estados', 'amarelo')}. {uf(0)}, {uf(1)} e {uf(2)} lideram, e
            {rico_no_top['Unidade_Geografica']} tem a
            {_cor(f"{rank_renda[rico_no_top.name]}ª maior renda", 'vermelho')} do país.
            No outro extremo estão {uf(-1)} e {uf(-2)}.</p>
            """
        )

    with col_etapa, st.container(key="card_etapa"):
        ui.card_cabecalho("A etapa crítica", "graduation", str(ano))
        ui.html(
            f"""
            <p class="insight-texto">Se não é a renda, a pista está na {_cor('trajetória escolar', 'azul')}.
            O abandono {_cor(f"salta {num(series['1º EM'] / series['9º EF'], 1)}×", 'vermelho')} do 9º ano
            ({pct(series['9º EF'])}) para o 1º ano do Médio ({pct(series['1º EM'])}), o ponto mais alto de toda
            a trajetória. No Ensino Médio como um todo, a taxa é {num(por_etapa[EM] / por_etapa[EF], 1)}× a do
            Fundamental: a entrada nessa etapa, muitas vezes com troca de escola e de rede, é o momento
            mais frágil.</p>
            """
        )

    with col_rede, st.container(key="card_rede"):
        ui.card_cabecalho("Rede e território", "school", str(ano))
        regioes_campo = " e ".join(f"no {rg}" for rg in campo_menor) or "em nenhuma região"
        ui.html(
            f"""
            <p class="insight-texto">Mesmo comparando a mesma etapa, a rede {_cor('estadual', 'vermelho')} tem
            mais abandono: no Médio, {pct(por_rede.loc['Estadual', EM])}, contra
            {pct(por_rede.loc['Municipal', EM])} na municipal, {pct(por_rede.loc['Federal', EM])} na federal e
            {pct(por_rede.loc['Privada', EM])} na privada. Na zona rural, a diferença aparece
            {_cor('no Fundamental', 'azul')} ({pct(por_local.loc['Rural', EF])} contra
            {pct(por_local.loc['Urbana', EF])} na urbana) e é regional: no {reg_rural}, o campo evade
            {num(rural_reg.loc[reg_rural, 'Razao'], 1)}× mais que a cidade, enquanto {regioes_campo}
            o campo evade menos.</p>
            """
        )

    # ---------- Linha 3: resumo geral ----------
    with st.container(key="card_conclusao"):
        ui.card_cabecalho("Em resumo", "lightbulb")
        ui.html(
            f"""
            <p class="insight-texto">Entre {ano_ini} e {ano}, o abandono escolar no Brasil caiu de
            {pct(serie.loc[ano_ini, 'Taxa'])} para {pct(serie.loc[ano, 'Taxa'])} sem que a renda média do país
            mudasse, e a queda foi maior justamente nos estados mais pobres. Por isso, a renda, que em {ano_ini}
            explicava {num(r_ini ** 2 * 100, 0)}% das diferenças entre os estados, hoje explica
            {_cor('menos de 1%', 'azul')}. O abandono que resta não está onde há menos renda, e sim na
            {_cor('entrada do Ensino Médio', 'vermelho')}, na rede estadual, no campo do {reg_rural} e em estados
            específicos, inclusive ricos. A conclusão geral é que reduzir o abandono hoje depende menos da renda
            das famílias e mais de {_cor('políticas educacionais', 'verde')} voltadas à transição para o Médio
            e às redes estaduais.</p>
            """
        )