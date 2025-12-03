"""
Funciones auxiliares y helpers reutilizables
"""


def format_price(amount):
    """
    Formatea un precio como string con formato CLP.
    """
    return f"${amount:,}".replace(',', '.')


def format_date(date, format_str='%d/%m/%Y'):
    """
    Formatea una fecha según el formato especificado.
    """
    if not date:
        return ""
    return date.strftime(format_str)


# Constantes del sistema
DEFAULT_ITEMS_PER_PAGE = 8
MAX_ITEMS_PER_PAGE = 100
MIN_PASSWORD_LENGTH = 8

