from decimal import Decimal # OBS: Decimal funciona como decimal em C#, tem precisão exata.
from exceptions import ScrapingError

def price_sanitizer(price_str: str) -> Decimal:
    """
    Converte uma string de preço para um float, removendo símbolos de moeda e separadores.
    Exemplo:"R$ 1.234,56" -> 1234.56
    """

    # Ajusta valores monetários a tipo flutuante
    price_str = price_str.replace("R$", "").strip()
    price_str = price_str.replace(".", "").replace(",", ".")

    price_str = price_str.replace("%", "").strip() # Para caso com procentagem.
    
    try:
        return Decimal(price_str)  # Verifica se a string é um número válido
    except ValueError:
        raise ValueError("Error while sanitizing price")    

def search_element_verifier(soup, selector: str) -> str:
    """Busca um elemento usando um seletor CSS e verifica se ele existe. 
    Retorna o texto do elemento se encontrado e lança um ValueError se não for.
    """

    element = soup.select_one(selector)
    if not element:
        raise ScrapingError(f"Element not found for selector: {selector}")
    return element.get_text(strip=True)

def search_indicator(indicator: str, soup, table_selector = "#table-indicators div.cell") -> str:
    """Busca um elemento usando um seletor CSS e verifica se ele existe. 
    Retorna o texto do elemento se encontrado e lança um ScrapingError se não for.
    """

    table = soup.select(table_selector)
    for cell in table:
        title = cell.select_one("span")
        title_text = title.get_text(strip=True) if title else ""

        if indicator.lower() in title_text.lower():
            value = cell.select_one("div.value span")

            if value:
                indicator_value = value.text.strip()
                return indicator_value
            
            elif not value:
                value = cell.select_one("span.value")

                if value:
                    indicator_value = value.text.strip()
                    return indicator_value
                
    raise ScrapingError(f"Indicator '{indicator}' not found in the table.") 