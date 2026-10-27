"""Componentes visuais reaproveitáveis."""
import base64
import mimetypes

import streamlit as st

from src.config import BANNER_CANDIDATES, CSS_PATH

# Ícones
_ICONES = {
    "school": '<path d="M14 21v-3a2 2 0 0 0-4 0v3"/><path d="M18 5v16"/><path d="m4 6 7.106-3.79a2 2 0 0 1 1.788 0L20 6"/><path d="m6 11-3.52 2.147a1 1 0 0 0-.48.854V19a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-5a1 1 0 0 0-.48-.853L18 11"/><path d="M6 5v16"/><circle cx="12" cy="9" r="2"/>',
    "grid": '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/>',
    "building": '<rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/><path d="M12 10h.01"/><path d="M12 14h.01"/><path d="M16 10h.01"/><path d="M16 14h.01"/><path d="M8 10h.01"/><path d="M8 14h.01"/>',
    "graduation": '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
    "lightbulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "trending_down": '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "scatter": '<circle cx="7.5" cy="7.5" r="1"/><circle cx="18.5" cy="5.5" r="1"/><circle cx="11.5" cy="11.5" r="1"/><circle cx="7.5" cy="16.5" r="1"/><circle cx="17.5" cy="14.5" r="1"/><path d="M3 3v16a2 2 0 0 0 2 2h16"/>',
    "map_pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "up_right": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "down_right": '<path d="m7 7 10 10"/><path d="M17 7v10H7"/>',
}


def icone(nome: str, tamanho: int = 20, classe: str = "", traco: float = 2) -> str:
    """Devolve o SVG de um ícone do dicionário _ICONES."""
    return (
        f'<svg class="{classe}" xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{traco}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_ICONES[nome]}</svg>'
    )


# Utilitários
def html(conteudo: str) -> None:
    """Renderiza HTML sem indentação e sem linhas em branco.

    Evita que o Markdown do Streamlit transforme trechos em bloco de código.
    """
    linhas = (linha.strip() for linha in conteudo.splitlines())
    st.markdown("\n".join(l for l in linhas if l), unsafe_allow_html=True)


def aplicar_css() -> None:
    """Carrega o assets/styles.css na página."""
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# Navegação e menu lateral
PAGINAS = {
    "visao": ("Visão Geral", ":material/dashboard:"),
    "detalhe": ("Detalhamento", ":material/scatter_plot:"),
    "insights": ("Insights", ":material/lightbulb:"),
}


def ir_para(chave: str) -> None:
    """Troca de página. Usada pelas abas do menu e pelos botões da Visão Geral."""
    st.session_state["pagina"] = chave


def sidebar() -> str:
    """Desenha o menu lateral e devolve a chave da página escolhida."""
    st.session_state.setdefault("pagina", "visao")

    with st.sidebar:
        html(
            f"""
            <div class="brand">
                {icone("school", 34, "brand-logo", traco=1.8)}
                <div class="brand-text">
                    <div class="brand-title">Dashboard</div>
                    <div class="brand-sub">Educação & Evasão</div>
                </div>
            </div>
            """
        )

        for chave, (rotulo, simbolo) in PAGINAS.items():
            st.button(
                rotulo,
                icon=simbolo,
                key=f"nav_{chave}",
                width="stretch",
                type="primary" if st.session_state["pagina"] == chave else "secondary",
                on_click=ir_para,
                args=(chave,),
            )

        html('<div class="credito">By Bárbara Vaz Ferreira</div>')

    return st.session_state["pagina"]


# Título da página e banner
def titulo_pagina(texto: str, nome_icone: str = "grid") -> None:
    """Título da página com ícone num quadrado azul lousa."""
    html(
        f"""
        <div class="page-title">
            <span class="page-title-icon">{icone(nome_icone, 22)}</span>
            <h1>{texto}</h1>
        </div>
        """
    )

@st.cache_data
def _banner_base64() -> str | None:
    """Converte a foto do banner em texto para usar dentro do HTML."""
    for caminho in BANNER_CANDIDATES:
        if caminho.exists():
            mime = mimetypes.guess_type(caminho.name)[0] or "image/jpeg"
            return f"data:{mime};base64,{base64.b64encode(caminho.read_bytes()).decode()}"
    return None

def banner(ano_min: int, ano_max: int, titulo: str) -> None:
    """Faixa azul com foto, período da base e título."""
    img = _banner_base64()
    fundo = f"background-image: url('{img}');" if img else ""
    html(
        f"""
        <div class="hero">
            <div class="hero-photo" style="{fundo}"></div>
            <div class="hero-content">
                <span class="hero-pill">Base histórica · {ano_min} – {ano_max}</span>
                <h2>{titulo}</h2>
            </div>
        </div>
        """
    )

# Cards
def kpi_card(rotulo: str, valor: str, nome_icone: str, acento: str,
             rodape: str = "", delta: str | None = None, delta_bom: bool | None = None) -> str:
    """HTML de um card de indicador. 'acento' é a cor da borda de cima."""
    selo = ""
    if delta is not None:
        classe = "chip-bom" if delta_bom else "chip-ruim"
        seta = icone("up_right" if delta.startswith("+") else "down_right", 13)
        selo = f'<span class="chip {classe}">{seta}{delta}</span>'
    return f"""
    <div class="kpi" style="--acento:{acento}">
        <div class="kpi-top">
            <span class="kpi-label">{rotulo}</span>
            <span class="kpi-icon">{icone(nome_icone, 18)}</span>
        </div>
        <div class="kpi-value">{valor}</div>
        <div class="kpi-foot">{selo}<span>{rodape}</span></div>
    </div>
    """


def card_titulo(titulo: str, detalhe: str = "", nome_icone: str | None = None,
                amarela: bool = False) -> None:
    """Cabeçalho dos cards: título à esquerda e etiqueta à direita.

    Com nome_icone, o título ganha um ícone (estilo da página Insights).
    A etiqueta é azul, ou amarela com amarela=True; vazia, ela não aparece.
    """
    classe_etiqueta = "etiqueta-amarela" if amarela else ""
    if nome_icone:
        esquerda = (f'<div class="card-head-left"><span class="card-icon">{icone(nome_icone, 18)}</span>'
                    f"<h3>{titulo}</h3></div>")
        classe_head = "card-head card-head-icone"
    else:
        esquerda, classe_head = f"<h3>{titulo}</h3>", "card-head"
    html(f'<div class="{classe_head}">{esquerda}<span class="{classe_etiqueta}">{detalhe}</span></div>')


def card_cabecalho(titulo: str, nome_icone: str, etiqueta: str = "", amarela: bool = False) -> None:
    """Atalho usado na página Insights: cabeçalho com ícone."""
    card_titulo(titulo, etiqueta, nome_icone, amarela)