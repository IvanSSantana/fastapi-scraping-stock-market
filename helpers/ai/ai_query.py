from env import AI_API_KEY
from google import genai
from openai import OpenAI
from google.genai import types

# Clients
client = genai.Client(api_key=AI_API_KEY)
local_client = OpenAI(
    base_url='http://localhost:11434/v1/', # Porta padrão que roda o Ollama localmente
    api_key='ollama',  # Necessário, mas ignorado pelo Ollama)
)

# Queries
def query(content: str, temperature: float=0.5, max_tokens: int=400) -> str | None:
    #TODO: Corrigir estrutura da maneira que 'contents' é enviado, separando-o do prompt
    """
    Wrapper para chamadas ao Gemini.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=content,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
    )

    return response.text

def local_query(persona: str, content: str, temperature: float=0.5, max_tokens: int=400) -> str | None:
    """
    Wrapper para chamadas locais para IA.
    """

    response = local_client.chat.completions.create(
            model="qwen2.5:7b",  
            messages=[
                {
                    "role": "system",
                    "content": persona},
                {
                    "role": "user",
                    "content": content}
            ],
            temperature=temperature,
            max_completion_tokens=max_tokens
        )

    return response.choices[0].message.content
