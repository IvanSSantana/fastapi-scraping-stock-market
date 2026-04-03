import heapq

def filter_events(events: list[dict[str, str]], how_many: int = 10) -> list[dict[str, str]]:
    """Filtra os eventos para manter somente os 10 mais relevantes e impactantes, de acordo com a classificação de importância fornecida pela LLM."""
    
    # Retorna apenas os 10 eventos com menor importância
    return heapq.nsmallest(how_many, events, key=lambda event: int(event["importancia"])) # Pega os 'n' menores de acordo com a chave 'importancia' convertida para inteiro
