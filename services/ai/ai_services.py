from utils.ai.ai_query import local_query, query
# Principais Funções
#TODO: Uso futuro em análise de gráficos: img_prompt = "Analise a imagem/gráfico e forneça todos os dados que ela(e) contém, com precisão númerica e observando atentamente as legendas (se houver). Por exemplo: 'Gráfico de Lucros da empresa Petrobras, revelando uma fatia de 37\\% correspondente a petróleo, 23\\% de alimentos e 40% de conservantes.'. Caso a imagem não seja um gráfico ou texto pertinente a área de finanças, por exemplo, um ícone ou imagem de pessoa, simplesmente retorne somente: 'Irrelevante'."

def summarize_documents_to_events(raw_documents: list, local: bool = True) -> str | None:
    #TODO: Enviar para outra LLM simplificar ou  os eventos ao leitor leigo
    #TODO: Filtrar, simplificar e enviar para o template_report na seção eventos de maneira formatada
    """
    Recebe os os chunkings dos textos 'crus' do Docling e gera um resumo baseado em eventos
    """ 

    content = ""

    prompt = f"""
        Você é um extrator de eventos corporativos.

        OBJETIVO:
        Extrair os 3 eventos corporativos mais relevantes e impactantes de cada batch.

        REGRAS OBRIGATÓRIAS:
        - Responda SOMENTE em Português do Brasil.
        - NUNCA responda em inglês.
        - NUNCA escreva introduções.
        - NUNCA escreva frases como "Aqui está o resumo".
        - Ignore nomes de pessoas, exceto se houver mudança relevante de cargo.
        - Preserve todos os valores numéricos, percentuais, datas, indicadores e quantias monetárias.
        - Foque somente em movimentos, decisões, resultados e mudanças da empresa.
        - Se nenhum dado for fornecido, responda exatamente:
        "Nenhum dado fornecido."
        - Se o conteúdo não tiver nada relevante, responda exatamente:
        "."

        FORMATO DE SAÍDA:
        SEMPRE Retorne SOMENTE JSON válido.
        NÃO escreva markdown.
        NUNCA use ```json.

        Formato JSON OBRIGATÓRIO:
        {{
            "titulo": "Título do evento",
            "descricao": "Descrição do evento",
            "impacto": "Impacto do evento para a corporação"
        }}
        Exemplo:
        ""
        [
        {{
            "titulo": "Compra de Imóvel",
            "descricao": "O imóvel 'Jor Mansions' foi adquirido por 10 bilhões de dólares.",
            "impacto": "Possível ampliação operacional e aumento de ativos."
        }},
        {{
            "titulo": "Expansão de setor",
            "descricao": "A empresa irá expandir em um novo setor, em imóveis, além dos lanches.",
            "impacto": "Ampliação de mercado clara com provável aumento de distribuição de cotas, entretanto existe risco de fracasso."
        }}
        ]
        ""
        """

    for i, doc in enumerate(raw_documents):
        content += f"""
            BATCH {i+1}:
            {doc}\n
        """

    print("CALLING AI FOR SUMMARIZE\n")
    
    if local:
        summarize = local_query(
            persona=prompt,
            content=content,
            temperature=0.08,
            max_tokens=400
        )

    else:
        summarize = query(
                content=prompt + content,
                temperature=0.37,
                max_tokens=400
            )

    return summarize


def generate_conclusion(content: str, local: bool = True) -> str | None: 
    #TODO: Refatorar prompt
    print("CALLING GEMINI\n")
    
    prompt = f"""
        Gere um relatório financeiro simplificado que pessoas que não entendem de finanças corporativas possam entender.
        Você SEMPRE deve utilizar o formato: evento simplfiicado -> consequência.
        Alguns trechos de exemplo: 'A dívida líquida em 7B da empresa Itaú é considerada alta, o que pode proporcionar queda/subida do ativo.';
        'O indicador Lucro / CAGR é resumidamente o lucro da empresa, e nessas condições demonstra a maturidade e evolução da corporação.'. 
        Separe o documento em seções como: Situação Geral da Empresa, Decisões / Movimentos Corporativos, Lucros, Dívidas, Indicadores e Conclusão.
        SEMPRE mantenha consistência de estrutura.
        NÃO escreva frases como: 'Aqui está sua resposta' ou 'Aqui está o resumo'.
        NÃO faça introduções desnecessárias.
        Escreva SEMPRE em Português do Brasil.
        NUNCA responda em inglês.
        Mesmo que o documento esteja parcialmente em inglês, traduza e responda somente em Português do Brasil, mantendo somente os termos técnicos que já são em inglês na lingua inglesa.
        SEMPRE IGNORE nomes de pessoas, foque nos movimentos da empresa como um todo.
        SEMPRE mostre o impacto dos dados, e NUNCA eles devem ser 'soltos'.
        SEMPRE mostre os principais insights dos documentos, focando no desempenho e mudança corporativa.
        Os eventos são:
        {content}"""
    
    if local:
        report = local_query(
                persona=prompt,
                content=content,
                temperature=0.17,
                max_tokens=3_000
            )   
    else:
        ...
        # report = query(
        #         persona=prompt,
        #         content=content,
        #         temperature=0.17,
        #         max_tokens=10_000
        #     )

    return report
    ...
# TODO: Serviço de IA fria que lerá os dados de relatórios gerenciais e gerará insights, análises e previsões com base nesses dados.