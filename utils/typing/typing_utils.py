from decimal import Decimal, InvalidOperation
import re
import json
from utils.ai.ai_query import local_query

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
    
def clean_json_from_ai(ai_response: str) -> list[dict]:
    """Limpa as resposta de IA que devem ter estrutura JSON fixa e as limpa com Regex e até com IA se a anterior falhar."""
    try:
        parsed_json = json.loads(ai_response)

        return parsed_json

    except json.JSONDecodeError:
        print("Erro durante conversão para JSON, uma tentativa de limpeza será iniciada.")

        # Remove blocos markdown ```json ... ``` OBS: Regex criado por IA
        cleaned_ai_response_with_regex = re.sub(r"^```json\s*|\s*```$", "", ai_response.strip(), flags=re.IGNORECASE | re.DOTALL)

        try:
            parsed_json = json.loads(cleaned_ai_response_with_regex)

            return parsed_json

        except json.JSONDecodeError:
            print("Falha após limpeza com Regex. Tentando corrigir com IA...")

            fixed_json = local_query(
                """
                - Você é um conversor de texto para lista JSON válida. 
                - Retorne SOMENTE JSON válido. 
                - Não use ```json, não use markdown, não explique nada.
                - SEMPRE mantenha os dados e conteúdos intactos.""",
                f"Converta o texto a seguir para uma lista JSON válida:\n\n{ai_response}"
            )

            parsed_json = json.loads(fixed_json)  # type: ignore

            return parsed_json