from bs4 import Tag # OBS: Decimal funciona como decimal em C#, tem precisão exata.
from communication.exceptions import ScrapingError

def search_one_element_verifier(soup, selector: str) -> Tag:
    """Busca um elemento usando um seletor CSS e verifica se ele existe. 
    Retorna o texto do elemento se encontrado e lança um ScrapingError se não for.
    """

    element = soup.select_one(selector)
    if not element:
        raise ScrapingError(f"Element not found for selector: {selector}")
    return element

def search_indicator(indicator: str, soup, table_selector = "#table-indicators div.cell") -> str:
    """Busca um elemento dentro de uma tabela co múltiplos elelementos e verifica se ele existe. 
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
                
    return "" # Se nenhum indicador for encontrado retorna nada.