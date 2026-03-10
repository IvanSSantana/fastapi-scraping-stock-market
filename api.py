from fastapi import FastAPI
from fastapi.responses import FileResponse
from scraping import search_asset

app = FastAPI()

@app.get("/api/v1/{ticker}")
async def get_asset(ticker: str):
    try:
        return search_asset(ticker)
    except ValueError as e:
        return {"error": str(e)}
#TODO: Rota POST que recebe um JSON com múltiplos tickers.
#TODO: Rota POST que recebe um CSV e tem a capacidade de atualizar dados, criar novos registros de variação de preços etc..
#TODO: Rota padrão que busca o ticker mais próximo do que o usuário digitou, caso o ticker exato não seja encontrado.