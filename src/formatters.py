"""Formatação no padrão brasileiro (vírgula decimal, ponto de milhar)."""


def _br(texto: str) -> str:
    """Troca 1,234.56 por 1.234,56."""
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def num(valor: float | None, casas: int = 2) -> str:
    return "—" if valor is None else _br(f"{valor:,.{casas}f}")


def pct(valor: float | None, casas: int = 2) -> str:
    return "—" if valor is None else f"{num(valor, casas)}%"


def reais(valor: float | None) -> str:
    return "—" if valor is None else f"R$ {num(valor, 0)}"


def sinal(valor: float, casas: int = 2) -> str:
    """Número com sinal: +1,23 ou −1,23 (com o sinal de menos tipográfico)."""
    s = num(abs(valor), casas)
    return f"+{s}" if valor > 0 else (f"−{s}" if valor < 0 else s)