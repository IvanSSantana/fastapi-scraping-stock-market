def list_dicts_to_string(list_dicts: list[dict[str, str]]) -> str:
    """Converte uma lista de dicionários em uma string formatada, onde cada dicionário é representado por suas chaves e valores."""
    
    result = ""
    for dict_ in list_dicts: # Itera cada evento

        for key, value in dict_.items(): # Itera cada chave-valor do evento
            result += f"{key}: {value}\n"
            
    return result