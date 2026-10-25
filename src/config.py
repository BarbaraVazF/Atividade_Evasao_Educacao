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
AZUL_LOUSA = "#1F3A6B"      # cor institucional, menu lateral, títulos
VERDE_QUADRO = "#3E8A6E"    # métricas positivas, gráficos secundários
AMARELO_LAPIS = "#F2C14E"   # detalhes, destaques e alertas
GRAFITE = "#2A3550"         # texto corrido
FUNDO = "#F4F6FA"           # fundo da página

CINZA_GIZ = "#A9B4C8"       # subtítulos e textos secundários sobre fundo escuro
CINZA_LINHA = "#E3E7EF"     # bordas e linhas de grade
GRAFITE_SUAVE = "#6B7489"   # rótulos e textos secundários sobre fundo claro
CINZA_CLARO = "#EEF1F6"     # fundo das caixas de filtro
CINZA_MEDIO = "#C5CCD8"     # bordas das caixas de filtro
AMARELO_ESCURO = "#B8891A"  # números do eixo da renda (amarelo legível sobre branco)

# Selos de variação (seta verde = melhorou, vermelha = piorou)
VERDE_CLARO = "#E3F2EC"     # fundo do selo positivo
VERMELHO_ALERTA = "#B5452F" # texto do selo negativo
VERMELHO_CLARO = "#FBEBE6"  # fundo do selo negativo

# Cores usadas só no ranking
AZUL_MEDIO = "#3B6FB6"      # região Norte
VERDE_MENTA = "#8DBFA8"     # região Sul

# Cor de cada região no ranking (precisa vir depois das cores acima)
CORES_REGIAO = {
    "Norte": AZUL_MEDIO,
    "Nordeste": AMARELO_LAPIS,
    "Centro-Oeste": VERDE_QUADRO,
    "Sudeste": AZUL_LOUSA,
    "Sul": VERDE_MENTA,
}

# ---------------------------------------------------------
# Opções dos filtros
# ---------------------------------------------------------
REGIOES = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
LOCALIZACOES = ["Total", "Urbana", "Rural"]

# Cada etapa do filtro aponta para os valores da coluna Grupo_de_Abandono
ETAPAS = {
    "Fundamental + Médio": ["Ensino Fundamental", "Ensino Médio"],
    "Ensino Fundamental": ["Ensino Fundamental"],
    "Ensino Médio": ["Ensino Médio"],
}

DEPENDENCIAS = ["Total", "Pública", "Estadual", "Municipal", "Privada", "Federal"]

# Séries escolares na ordem do gráfico (nome no CSV -> rótulo curto)
SERIES = {
    "1º Ano do Ensino Fundamental": "1º EF", "2º Ano do Ensino Fundamental": "2º EF",
    "3º Ano do Ensino Fundamental": "3º EF", "4º Ano do Ensino Fundamental": "4º EF",
    "5º Ano do Ensino Fundamental": "5º EF", "6º Ano do Ensino Fundamental": "6º EF",
    "7º Ano do Ensino Fundamental": "7º EF", "8º Ano do Ensino Fundamental": "8º EF",
    "9º Ano do Ensino Fundamental": "9º EF", "1º Ano do Ensino Médio": "1º EM",
    "2º Ano do Ensino Médio": "2º EM", "3º Ano do Ensino Médio": "3º EM",
}

# ---------------------------------------------------------
# Siglas das UFs (usadas no ranking)
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