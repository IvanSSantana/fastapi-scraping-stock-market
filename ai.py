import re
from env import AI_API_KEY
from google import genai
from openai import OpenAI
from google.genai import types
from token_count import TokenCount

# Clients
client = genai.Client(api_key=AI_API_KEY)
local_client = OpenAI(
    base_url='http://localhost:11434/v1/', # Porta padrão que roda o Ollama localmente
    api_key='ollama',  # Necessário, mas ignorado pelo Ollama)
)

# Queries
def query(contents: str, temperature: float=0.5, max_tokens: int=400) -> str | None:
    """
    Wrapper para chamadas ao Gemini.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
    )

    return response.text

def local_query(contents: str, temperature: float=0.5, max_tokens: int=400) -> str | None:
     #TODO: Configurar IA local para rodar na GPU AMD RX 580
    """
    Wrapper para chamadas locais para IA do Llama3.
    """

    response = local_client.chat.completions.create(
            model="llama3",  
            messages=[
                {"role": "user",
                 "content": contents},
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

    return response.choices[0].message.content

# Principais Funções
#TODO: Uso futuro em análise de gráficos: img_prompt = "Analise a imagem/gráfico e forneça todos os dados que ela(e) contém, com precisão númerica e observando atentamente as legendas (se houver). Por exemplo: 'Gráfico de Lucros da empresa Petrobras, revelando uma fatia de 37\\% correspondente a petróleo, 23\\% de alimentos e 40% de conservantes.'. Caso a imagem não seja um gráfico ou texto pertinente a área de finanças, por exemplo, um ícone ou imagem de pessoa, simplesmente retorne somente: 'Irrelevante'."

def summarize_documents(raw_documents: list, local: bool = True) -> str | None:
    """
    Recebe os textos 'crus' do Docling e gera um resumo geral de todos
    #TODO: Já está funcionando, entretanto será necessário forçar o uso de IA local para evitar estourar tokens.

    """ 

    content = ""

    prompt = f"""
        Atue como resumidor de relatórios financeiros para pessoas leigas.
        Você não deve explicar termos, mas deve mostrar como ele impacta de forma direta e prática, por exemplo: 'O P / VP alto indica que o ativo está mais caro do que o mercado está disposto a pagar.'.
        Para cada DOCUMENTO forneça apenas o resumo.
        Não escreva introduções.
        Não escreva frases como "Aqui está o resumo".
        Caso nenhum dado seja fornecido somente retorne "Nenhum dado fornecido."
        Sintetize mantendo somente os 3 insights mais relevantes e impactantes por documento.
        Mantenha valores númericos, dados e derivados todos preservados para melhor apuração futura dos fatos ocorridos.
        Estruture a resposta em documentos.
        Separe a resposta em seções por numeração dos documentos, como a seguir:
        Formato:

        DOCUMENTO 1:
        ...

        DOCUMENTO 2:
        ...

        DOCUMENTO 3:
        ...
        """

    for i, doc in enumerate(raw_documents):
        content += f"""
            DOCUMENTO {i+1}:
            {doc}\n
        """

    print("CALLING AI FOR SUMMARIZE\n")
    
    if local:
        summarize = local_query(
            contents=prompt + content,
            temperature=0.44,
            max_tokens=3000
        )

    else:
        summarize = query(
                contents=prompt + content,
                temperature=0.44,
                max_tokens=3000
            )

    return summarize


def generate_report(data) -> str | None:
    print("CALLING GEMINI\n")
    
    report_prompt = """
        Gere um relatório financeiro simplificado que pessoas que não entendem de finanças corporativas possam entender.
        Alguns trechos de exemplo: 'A dívida líquida em 7B da empresa Itaú é considerada alta, o que pode proporcionar queda/subida do ativo.';
        'O indicador Lucro / CAGR é resumidamente o lucro da empresa, e nessas condições demonstra a maturidade e evolução da corporação.'. 
        Separe o documento em seções por ordem de relevância. 
        Os dados são: """

    return 
    ...
# TODO: Serviço de IA fria que lerá os dados de relatórios gerenciais e gerará insights, análises e previsões com base nesses dados.