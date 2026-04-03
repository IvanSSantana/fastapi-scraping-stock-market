from helpers.ai.ai_query import local_query, query
from helpers.typing.list_dicts_to_string import list_dicts_to_string

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
        Extrair ATÉ 3 eventos corporativos mais relevantes e impactantes de cada batch, priorizando eventos que realmente possam afetar a percepção do investidor, os resultados da empresa ou o valor do ativo.

        REGRAS OBRIGATÓRIAS:
        - Responda SOMENTE em Português do Brasil.
        - NUNCA responda em inglês.
        - NUNCA escreva introduções.
        - NUNCA escreva frases como "Aqui está o resumo".
        - Ignore nomes de pessoas, incluindo cargos e eleições.
        - Preserve todos os valores numéricos, percentuais, datas, indicadores e quantias monetárias.
        - Foque somente em movimentos, decisões, resultados e mudanças da empresa.
        - Priorize eventos que realmente possam afetar a percepção do investidor, os resultados da empresa ou o valor do ativo.
        - Priorize eventos que envolvam estatísticas, números, indicadores, resultados e decisões.
        - Dê mais importância aos eventos com indicadores fundamentalistas, como crescimento de receita, abatimento de dívidas, ROIC, EBITDA etc.
        - Os impactos também podem ser negativos.
        - Considere relevante somente o que tiver impacto econômico concreto e atual como lucro, dívida, dividendos, expansão, risco jurídico/regulatório etc.
        - Ignore eventos burocráticos, societários, administrativos como assembleias, reuniões, eleições, comitês, comunicados protocolares etc. ou voltados ao público como Investor Day, a menos que o texto explicite uma consequência econômica objetiva e material.
        - Todos os eventos SEMPRE devem ter importância diferentes.
        - Se o conteúdo não contiver eventos suficientes, retorne menos eventos.
        - Cada evento retornado deve ser rastreável diretamente ao texto fornecido.

        CLASSIFICAÇÃO DE IMPORTÂNCIA:
        A importância vai de 1 a 10:
        - 1 = altíssimo impacto econômico 
        - 10 = impacto praticamente nulo

        - Se nenhum dado for fornecido, responda exatamente:
        "[{{"importancia": "10"}}]"
        - Se o conteúdo não tiver nada relevante, responda exatamente:
        "[{{"importancia": "10"}}]"
        - Se o conteúdo somente envolve nomes de pessoas ou cargos, responda exatamente:
        "[{{"importancia": "10"}}]"
        
        FORMATO DE SAÍDA:
        SEMPRE Retorne SOMENTE JSON válido.
        NÃO escreva markdown.
        NUNCA use ```json.

        Formato JSON OBRIGATÓRIO:
        {{
            "titulo": "Título do evento",
            "descricao": "Descrição do evento",
            "impacto": "Impacto do evento para a corporação",
            "importancia": "5"
        }}
        Exemplo:
        ""
        [
        {{
            "titulo": "Compra de Imóvel",
            "descricao": "O imóvel 'Jor Mansions' foi adquirido por 10 bilhões de dólares.",
            "impacto": "Possível ampliação operacional e aumento de ativos.",
            "importancia": "1"
        }},
        {{
            "titulo": "Expansão de setor",
            "descricao": "A empresa irá expandir em um novo setor, em imóveis, além dos lanches.",
            "impacto": "Ampliação de mercado clara com provável aumento de distribuição de cotas, entretanto existe risco de fracasso.",
            "importancia": "3"
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
            temperature=0.13,
            max_tokens=400
        )

    else:
        summarize = query(
                content=prompt + content,
                temperature=0.11,
                max_tokens=300
            )

    return summarize


def generate_conclusion_of_events(events: list[dict[str, str]], local: bool = True) -> str | None: 
    #TODO: Refatorar prompt
    print("CALLING GEMINI\n")
    
    prompt = f"""
        Você é um analista de conclusão financeira simplificada.

        OBJETIVO:
        Gerar uma conclusão financeira clara, curta e útil para pessoas que não entendem finanças corporativas, com base SOMENTE nos eventos e indicadores fornecidos.

        REGRAS OBRIGATÓRIAS:
        - Responda SOMENTE em Português do Brasil.
        - NUNCA responda em inglês.
        - NUNCA escreva introduções.
        - NUNCA escreva frases como "Aqui está o resumo" ou "Aqui está a análise".
        - Explique tudo da forma mais simples possível.
        - Sempre traduza ideias complexas para linguagem leiga.
        - Foque SOMENTE em fatos e impactos práticos para o investidor.
        - Preserve todos os valores numéricos, percentuais, datas e indicadores relevantes.
        - NUNCA deixe números soltos; SEMPRE explique o que eles significam.
        - SEMPRE ignore nomes de pessoas.
        - Considere tanto impactos positivos quanto negativos.
        - Não invente informações que não estejam presentes nos eventos ou indicadores fornecidos.
        - Cada afirmação relevante deve ser justificável diretamente pelos dados ou contexto recebidos.
        - Priorize impacto com base em indicadores financeiros e dados concretos.
        - Caso existam sinais mistos, deixe isso explícito.
        - SEMPRE indique o impacto direto dos eventos no valor do ativo como "tendência de subida", "indicação de queda", "estabilidade" etc.

        INTERPRETAÇÃO ESPERADA:
        Você deve transformar eventos e indicadores em leitura prática.
        Exemplos do raciocínio esperado:
        - "A empresa reduziu dívida; isso pode melhorar a saúde financeira, reduzir risco e aumentar o valor do ativo."
        - "A empresa expandiu operação; isso pode aumentar receita no futuro, mas também traz risco atual, podendo ter queda temporária do valor do ativo, mas com subida futura."
        - "Dividend Yield alto; isso pode ser atrativo para renda, e mediante o contexto de solidez fornecido, indica valorização do ativo."
        - "Margens caindo; isso pode indicar queda do valor do ativo."
        - "Lucro crescendo; isso tende a melhorar a percepção do mercado, aumentando o valor do ativo."
        - "A empresa reduziu sua alavancagem; isso pode diminuir o risco financeiro, indicando maior estabilidade do valor do ativo."
        - "O lucro cresceu no período; "isso tende a melhorar a percepção do mercado, tendendo a subida do valor do ativo."
        - "A companhia expandiu operação; "isso pode abrir espaço para mais receita no futuro, entretanto traz risco atual, podendo causar queda temporária do valor do ativo, mas com subida futura."
        - "A margem caiu; isso pode indicar pior eficiência operacional, gerando tendência de queda do valor do ativo."
    """
    
    events_string = list_dicts_to_string(events)

    if local:
        report = local_query(
                persona=prompt,
                content=events_string,
                temperature=0.14,
                max_tokens=750
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