from fastapi import FastAPI, Response, status
from fastapi.responses import FileResponse
from scraping import search_asset

app = FastAPI()

@app.get("/api/v1/{ticker}", status_code=status.HTTP_200_OK)
async def get_asset(ticker: str, response: Response):
    try:
        response.status_code = status.HTTP_200_OK
        return search_asset(ticker)
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": str(e)}
#TODO: Rota POST que recebe um JSON com múltiplos tickers.
#TODO: Rota POST que recebe um CSV e tem a capacidade de atualizar dados, criar novos registros de variação de preços etc..
#TODO: Rota padrão que busca o ticker mais próximo do que o usuário digitou, caso o ticker exato não seja encontrado.