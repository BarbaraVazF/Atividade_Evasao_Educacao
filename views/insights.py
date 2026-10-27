"""Página: Insights."""
import pandas as pd
import streamlit as st

from src import charts, data, insights, ui
from src.formatters import num, pct, reais, sinal

EF, EM = "Ensino Fundamental", "Ensino Médio"


def _forca(r: float) -> str:
    """Classifica a correlação pelo valor absoluto."""
    a = abs(r)
    return "forte" if a >= 0.5 else "moderada" if a >= 0.3 else "fraca"


def _cor(texto: str, cor: str) -> str:
    """Destaca uma palavra: azul, verde, vermelho ou amarelo (ver CSS .realce-...)."""
    return f'<span class="realce-{cor}">{texto}</span>'


def _juntar(nomes: list[str]) -> str:
    """'Sul' ou 'Sul e no Sudeste' (para usar depois de 'no')."""
    return " e no ".join(nomes)


def render(df: pd.DataFrame) -> None:
    ano = int(df["Ano"].max())          # sempre o ano mais recente da base

    with st.container(key="insights_titulo"):
        ui.titulo_pagina("Insights", "lightbulb")

    # Números
    # Correlação
    est = insights.estatisticas_correlacao(df, ano)
    ufs, r = est["ufs"], est["r"]
    corr = insights.correlacao_por_ano(df).set_index("Ano")["r"]
    ano_ini = int(corr.index.min())
    r_ini = corr[ano_ini]
    incl = insights.tendencia(corr.reset_index())
    salto = corr[ano] - corr[ano - 1]
    queda_pobres, queda_ricos = insights.queda_por_renda(df, ano - 1, ano)
    quedas = insights.maiores_quedas(df, ano - 1, ano)

    # Trajetória do Brasil e das regiões
    serie = (data.serie_anual(data.filtrar_base(df, "Total", "Fundamental + Médio"), "Todas")
             .set_index("Ano"))
    taxa_ini, taxa_fim = serie.loc[ano_ini, "Taxa"], serie.loc[ano, "Taxa"]
    renda_ini, renda_fim = serie.loc[ano_ini, "Renda"], serie.loc[ano, "Renda"]
    ano_vale = int(serie["Taxa"].idxmin())                      # ano com a menor taxa (2020)
    pos_vale = serie.loc[ano_vale + 1: ano - 1, "Taxa"]          # anos entre o vale e o último
    reg_ini, reg = insights.regioes(df, ano_ini), insights.regioes(df, ano)

    # Estados
    top = ufs.sort_values("Taxa", ascending=False)
    rank_renda = ufs["Renda"].rank(ascending=False).astype(int)
    rico_no_top = top.head(5).loc[rank_renda[top.head(5).index].idxmin()]   # mais rico entre os 5 piores
    pobre_baixo = ufs[ufs["Renda"] < ufs["Renda"].median()].sort_values("Taxa").iloc[0]
    comum = sorted(set(top.head(5)["Regiao"]) & set(top.tail(5)["Regiao"]))  # região nas duas pontas

    # Etapa, rede e território
    series = (data.taxa_por_serie(data.filtrar_detalhe(df, "Total", "Total"), ano, "Todas")
              .set_index("Serie")["Taxa"])
    iniciais = series[[f"{i}º EF" for i in range(1, 6)]]
    etapa = insights.por_etapa(df, ano, "Localizacao", ["Total"],
                               {"Dependencia_Administrativa": "Total"}).loc["Total"]
    rede = insights.por_etapa(df, ano, "Dependencia_Administrativa",
                              ["Pública", "Estadual", "Municipal", "Federal", "Privada"],
                              {"Localizacao": "Total"})
    local = insights.por_etapa(df, ano, "Localizacao", ["Urbana", "Rural"],
                               {"Dependencia_Administrativa": "Total"})
    rural_reg = insights.rural_por_regiao(df, ano)
    reg_rural = rural_reg.index[0]
    rural_mais = [x for x in rural_reg.index[1:] if rural_reg.loc[x, "Razao"] >= 1.05]
    rural_igual = [x for x in rural_reg.index if 0.95 <= rural_reg.loc[x, "Razao"] < 1.05]
    rural_menos = [x for x in rural_reg.index if rural_reg.loc[x, "Razao"] < 0.95]
    rural_total, urbana_total = local.mean(axis=1)["Rural"], local.mean(axis=1)["Urbana"]

    def uf(linha: pd.Series) -> str:
        """Nome do estado em negrito, com a taxa."""
        return f"<b>{linha['Unidade_Geografica']}</b> ({pct(linha['Taxa'])})"

    def queda(i: int) -> str:
        return f"{quedas.iloc[i]['Unidade_Geografica']} ({sinal(-quedas.iloc[i]['Queda'], 1)} p.p.)"

    # Linha 1: renda x abandono
    with st.container(key="card_correlacao"):
        ui.card_cabecalho("Renda × abandono", "scatter", f"r = {sinal(r)} em {ano}", amarela=True)
        col_txt, col_graf = st.columns([1, 1.25], gap="medium")
        with col_txt:
            ui.html(
                f"""
                <p class="insight-texto">Em {ano}, a correlação de Pearson entre renda média e taxa de abandono
                nas {est['n']} UFs foi de <b>r = {sinal(r)}</b>, numa escala de −1 a +1, ou seja, muito próxima
                de zero. Isso significa que a renda de um estado quase não ajuda a prever o seu abandono: ela
                explica só {num(est['r2'] * 100, 1)}% das diferenças entre os estados (r²).</p>
                <p class="insight-texto">Isso é {_cor('positivo', 'verde')}: o abandono deixou de acompanhar a renda,
                e estados de renda baixa, como {pobre_baixo['Unidade_Geografica']} ({pct(pobre_baixo['Taxa'])}),
                estão entre os que menos evadem.</p>
                <p class="insight-texto">Em {ano_ini}, a relação era {_cor(_forca(r_ini), 'vermelho')}
                (r = {sinal(r_ini)}). Desde então, o r {_cor('vem subindo', 'verde')} em direção a zero, em média
                {sinal(incl, 2)} por ano.</p>
                """
            )
        with col_graf:
            fig = charts.grafico_correlacao_tempo(corr.reset_index())
            fig.update_layout(height=320)
            st.plotly_chart(fig, width="stretch", config=charts.PLOTLY_CONFIG)

    # Linha 2: trajetória + estados
    col_traj, col_onde = st.columns(2, gap="small")

    with col_traj, st.container(key="card_trajetoria"):
        ui.card_cabecalho("A trajetória do abandono", "trending_down", f"{ano_ini} – {ano}")
        reducao = (1 - taxa_fim / taxa_ini) * 100
        ui.html(
            f"""
            <p class="insight-texto">Entre {ano_ini} e {ano}, a taxa de abandono do Brasil caiu de
            {pct(taxa_ini)} para {pct(taxa_fim)}, {_cor(f"{num(reducao, 0)}% a menos", 'verde')}, enquanto a renda
            média ficou praticamente estável ({reais(renda_ini)} para {reais(renda_fim)},
            {sinal((renda_fim / renda_ini - 1) * 100, 1)}%).</p>
            <p class="insight-texto">A queda não foi contínua. Em {ano_vale}, a taxa chegou a {pct(serie.loc[ano_vale, 'Taxa'])},
            {_cor('provável efeito da pandemia', 'amarelo')} no registro do abandono, com ensino remoto e
            aprovação flexibilizada, e voltou a subir ({', '.join(pct(v) for v in pos_vale)}) antes de cair
            de novo.</p>
            <p class="insight-texto">As regiões seguiram o mesmo caminho e ficaram mais parecidas. Em {ano_ini},
            o {reg_ini.index[0]} ({pct(reg_ini['Taxa'].iloc[0])}) estava {num(reg_ini['Taxa'].iloc[0] - reg_ini['Taxa'].iloc[-1], 1)}
            p.p. acima do {reg_ini.index[-1]}; em {ano}, a distância entre a maior e a menor região é de
            {_cor(f"{num(reg['Taxa'].iloc[0] - reg['Taxa'].iloc[-1], 1)} p.p.", 'azul')}.</p>
            """
        )

    with col_onde, st.container(key="card_onde"):
        ui.card_cabecalho("Onde o abandono pesa", "map_pin", str(ano))

        # Posição do estado rico no ranking de abandono (1 = maior taxa)
        pos_rico = list(top.index).index(rico_no_top.name) + 1

        # Exemplo de estados da mesma região em pontas opostas
        exemplo = ""
        if comum:
            alto = top.head(5)[top.head(5)["Regiao"].eq(comum[0])].iloc[0]
            baixo = top.tail(5)[top.tail(5)["Regiao"].eq(comum[0])].iloc[0]
            exemplo = (f" Já no {comum[0]}, {alto['Unidade_Geografica']} ({pct(alto['Taxa'])}) e "
                       f"{baixo['Unidade_Geografica']} ({pct(baixo['Taxa'])}) ficam em pontas opostas.")

        ui.html(
            f"""
            <p class="insight-texto">O {_cor(reg.index[0], 'azul')} tem a maior taxa de abandono entre as regiões
            ({pct(reg['Taxa'].iloc[0])}), mas as regiões estão próximas umas das outras. A grande diferença
            está {_cor('entre os estados', 'amarelo')}: a taxa vai de {pct(top['Taxa'].iloc[0])}
            ({top['Unidade_Geografica'].iloc[0]}) a {pct(top['Taxa'].iloc[-1])}
            ({top['Unidade_Geografica'].iloc[-1]}).</p>
            <p class="insight-texto">E essa diferença não segue a renda. O {rico_no_top['Unidade_Geografica']}
            tem a {_cor(f"{rank_renda[rico_no_top.name]}ª maior renda", 'vermelho')} do país e, mesmo assim,
            a {pos_rico}ª maior taxa de abandono ({pct(rico_no_top['Taxa'])}).{exemplo}</p>
            """
        )

    # Linha 3: etapa + rede + território
    col_etapa, col_rede, col_terr = st.columns(3, gap="small")

    with col_etapa, st.container(key="card_etapa"):
        ui.card_cabecalho("A etapa crítica", "graduation", str(ano))
        ui.html(
            f"""
            <p class="insight-texto">O abandono é baixo nos anos iniciais, começa a subir no 6º ano ({pct(series['6º EF'])}) e
            {_cor(f"salta {num(series['1º EM'] / series['9º EF'], 1)} vezes", 'vermelho')} do 9º ano
            ({pct(series['9º EF'])}) para o 1º ano do Médio ({pct(series['1º EM'])}), o ponto mais alto da
            trajetória escolar.</p>
            <p class="insight-texto">No Ensino Médio como um todo, a taxa é {num(etapa[EM] / etapa[EF], 1)} vezes a
            do Fundamental. Nessa etapa, o aluno costuma ter entre 15 e 17 anos e passa a sentir a {_cor('pressão para trabalhar', 'vermelho')} e ajudar na renda da
            família. Somada à troca de escola e de rede, essa combinação torna a entrada no Médio o momento
            mais frágil da trajetória.</p>
            """
        )

    with col_rede, st.container(key="card_rede"):
        ui.card_cabecalho("Rede de ensino", "school", str(ano))
        ui.html(
            f"""
            <p class="insight-texto">No Ensino Médio, a rede {_cor('estadual', 'vermelho')} tem o maior abandono
            ({pct(rede.loc['Estadual', EM])}), {num(rede.loc['Estadual', EM] / rede.loc['Municipal', EM], 1)}
            vez o da municipal ({pct(rede.loc['Municipal', EM])}). As redes federal ({pct(rede.loc['Federal', EM])})
            e privada ({pct(rede.loc['Privada', EM])}) ficam bem abaixo.</p>
            <p class="insight-texto">No Fundamental, as redes ficam mais próximas (estadual
            {pct(rede.loc['Estadual', EF])}, municipal {pct(rede.loc['Municipal', EF])}). Como a estadual concentra
            o Médio, é ela que puxa a taxa da rede {_cor('pública', 'azul')} no Médio
            ({pct(rede.loc['Pública', EM])}).</p>
            """
        )

    with col_terr, st.container(key="card_territorio"):
        ui.card_cabecalho("Campo e cidade", "building", str(ano))
        frases = []
        if rural_mais:
            razoes = ", ".join(f"{num(rural_reg.loc[x, 'Razao'], 1)} vez" for x in rural_mais)
            frases.append(f"No {_juntar(rural_mais)}, o campo também evade mais, mas pouco ({razoes}).")
        if rural_igual:
            frases.append(f"No {_juntar(rural_igual)}, campo e cidade se igualam.")
        if rural_menos:
            frases.append(f"Já no {_juntar(rural_menos)}, o campo evade menos.")
        ui.html(
            f"""
            <p class="insight-texto">A zona {_cor('rural', 'azul')} evade mais que a urbana ({pct(rural_total)}
            contra {pct(urbana_total)}), e a diferença está no Fundamental ({pct(local.loc['Rural', EF])} contra
            {pct(local.loc['Urbana', EF])}); no Médio, as duas quase se igualam.</p>
            <p class="insight-texto">O peso do campo depende da região: no <b>{reg_rural}</b>, ele evade
            {num(rural_reg.loc[reg_rural, 'Razao'], 1)} vezes mais que a cidade. {' '.join(frases)}</p>
            """
        )

    # Linha 4: resumo
    with st.container(key="card_conclusao"):
        ui.card_cabecalho("Em resumo", "lightbulb")
        ui.html(
            f"""
            <p class="insight-texto">Entre {ano_ini} e {ano}, o abandono escolar caiu
            {_cor(f"{num(reducao, 0)}%", 'verde')} no Brasil sem que a renda mudasse, e caiu mais nos estados mais
            pobres. Por isso, a renda, que em {ano_ini} estava associada a {num(r_ini ** 2 * 100, 0)}% das
            diferenças entre os estados, em 2023 associada a {_cor('menos de 1%', 'azul')}. O abandono restante
            se concentra na {_cor('entrada do Ensino Médio', 'vermelho')}, na rede estadual, no campo do
            {reg_rural} e em estados específicos, inclusive ricos. Com base no observado, reduzir o abandono hoje depende menos da renda
            das famílias e mais de {_cor('políticas educacionais', 'verde')} voltadas à transição para o Médio,
            às redes estaduais e às escolas rurais.</p>
            """
        )