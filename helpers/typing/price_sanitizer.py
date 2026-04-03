from decimal import Decimal, InvalidOperation

def price_sanitizer(price_str: str) -> Decimal | None:
    """
    Converte uma string de preço para um float, removendo símbolos de moeda e separadores.
    Exemplo:"R$ 1.234,56" -> 1234.56
    """

    if not price_str:
        return None

    # Ajusta valores monetários a tipo flutuante
    price_str = price_str.replace("R$", "").strip()
    price_str = price_str.replace(".", "").replace(",", ".")

    price_str = price_str.replace("%", "").strip() # Para casos com procentagem.
    
    if "-" in price_str.strip():
        price_str = price_str.replace("-", "").strip()

        try:
            return -Decimal(price_str)  # Verifica se a string é um número válido e aplica o sinal negativo
        except InvalidOperation:
            return None
        
    elif "+" in price_str.strip():
        price_str = price_str.replace("+", "").strip()
    
    try:
        return Decimal(price_str)  # Verifica se a string é um número válido
    except InvalidOperation:
        return None
    