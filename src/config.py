"""Constantes do projeto: caminhos, paleta de cores e opções dos filtros."""
from pathlib import Path

# ---------------------------------------------------------
# Caminhos
# ---------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "AbandonoEscolar_RendaMedia_2013_2023.csv"
ASSETS = ROOT / "assets"
CSS_PATH = ASSETS / "styles.css"

# Foto do banner: usa o primeiro arquivo que existir
BANNER_CANDIDATES = [ASSETS / "banner.jpg", ASSETS / "banner.png", ASSETS / "banner.webp"]

# ---------------------------------------------------------
# Paleta "Sala de Aula"
# ---------------------------------------------------------
# Cores principais
AZUL_LOUSA = "#1F3A6B"      # cor institucional, menu lateral, títulos
VERDE_QUADRO = "#3E8A6E"    # métricas positivas, gráficos secundários
AMARELO_LAPIS = "#F2C14E"   # detalhes, destaques e alertas
GRAFITE = "#2A3550"         # texto corrido
FUNDO = "#F4F6FA"           # fundo da página

# Tons de apoio
CINZA_GIZ = "#A9B4C8"       # subtítulos e textos secundários sobre fundo escuro
CINZA_LINHA = "#E3E7EF"     # bordas e linhas de grade
GRAFITE_SUAVE = "#6B7489"   # rótulos e textos secundários sobre fundo claro
CINZA_CLARO = "#EEF1F6"     # fundo das caixas de filtro
CINZA_MEDIO = "#C5CCD8"     # bordas das caixas de filtro, barra "Total" nos gráficos
AMARELO_ESCURO = "#B8891A"  # números do eixo da renda (amarelo legível sobre branco)
AZUL_MEDIO = "#3B6FB6"      # região Norte, rede estadual
VERDE_MENTA = "#8DBFA8"     # região Sul, rede federal

# Selos de variação (seta verde = melhorou, vermelha = piorou)
VERDE_CLARO = "#E3F2EC"     # fundo do selo positivo
VERMELHO_ALERTA = "#B5452F" # texto do selo negativo e palavras de alerta
VERMELHO_CLARO = "#FBEBE6"  # fundo do selo negativo

# ---------------------------------------------------------
# Cores por categoria nos gráficos (sempre a partir da paleta acima)
# ---------------------------------------------------------
CORES_REGIAO = {
    "Norte": AZUL_MEDIO,
    "Nordeste": AMARELO_LAPIS,
    "Centro-Oeste": VERDE_QUADRO,
    "Sudeste": AZUL_LOUSA,
    "Sul": VERDE_MENTA,
}

# Total em cinza, como referência
CORES_LOCALIZACAO = {
    "Total": CINZA_MEDIO,
    "Urbana": AZUL_LOUSA,
    "Rural": VERDE_QUADRO,
}

CORES_DEPENDENCIA = {
    "Total": CINZA_MEDIO,
    "Pública": AZUL_LOUSA,
    "Estadual": AZUL_MEDIO,
    "Municipal": VERDE_QUADRO,
    "Federal": VERDE_MENTA,
    "Privada": AMARELO_LAPIS,
}

# ---------------------------------------------------------
# Opções dos filtros
# ---------------------------------------------------------
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
LOCALIZACOES = ["Total", "Urbana", "Rural"]
DEPENDENCIAS = ["Total", "Pública", "Estadual", "Municipal", "Privada", "Federal"]

# Cada etapa aponta para os valores da coluna Grupo_de_Abandono.
# "Fundamental + Médio" é a combinação usada nos cálculos (no filtro, aparece como "Todas").
ETAPAS = {
    "Fundamental + Médio": ["Ensino Fundamental", "Ensino Médio"],
    "Ensino Fundamental": ["Ensino Fundamental"],
    "Ensino Médio": ["Ensino Médio"],
}

# Séries escolares na ordem do gráfico (nome no CSV -> rótulo curto)
SERIES = {
    "1º Ano do Ensino Fundamental": "1º EF",
    "2º Ano do Ensino Fundamental": "2º EF",
    "3º Ano do Ensino Fundamental": "3º EF",
    "4º Ano do Ensino Fundamental": "4º EF",
    "5º Ano do Ensino Fundamental": "5º EF",
    "6º Ano do Ensino Fundamental": "6º EF",
    "7º Ano do Ensino Fundamental": "7º EF",
    "8º Ano do Ensino Fundamental": "8º EF",
    "9º Ano do Ensino Fundamental": "9º EF",
    "1º Ano do Ensino Médio": "1º EM",
    "2º Ano do Ensino Médio": "2º EM",
    "3º Ano do Ensino Médio": "3º EM",
}

# ---------------------------------------------------------
# Siglas das UFs (usadas no ranking e nos textos)
# ---------------------------------------------------------
UF_SIGLAS = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA",
    "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO",
    "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG", "Pará": "PA", "Paraíba": "PB", "Paraná": "PR",
    "Pernambuco": "PE", "Piauí": "PI", "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS", "Rondônia": "RO",
    "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE",
    "Tocantins": "TO",
}