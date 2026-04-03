import re
import json
from helpers.ai.ai_query import local_query
    
def clean_json_from_ai(ai_response: str) -> list[dict[str, str]]:
    """Limpa as resposta de IA que devem ter estrutura JSON fixa, retorne uma lista de dicionários e as limpa com Regex e até com IA se a anterior falhar."""
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
                - SEMPRE mantenha os dados e conteúdos intactos.
                - O JSON SEMPRE deve ter o campo "importancia", se nenhum dado relacionado for informado dê seu valor "10".""",
                f"Converta o texto a seguir para uma lista JSON válida:\n\n{ai_response}"
            )

            parsed_json = json.loads(fixed_json)  # type: ignore

            return parsed_json