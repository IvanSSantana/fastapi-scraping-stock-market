from fastapi import FastAPI
from fastapi.responses import FileResponse
from scraping import search_asset

app = FastAPI()

@app.get("/api/v1/{ticker}")
async def get_asset(ticker: str):

    # return FileResponse(search_asset(ticker), filename=f"{ticker}.csv", media_type="text/csv") 
    return
#TODO: Rota POST que recebe um JSON com múltiplos tickers.
#TODO: Rota padrão que busca o ticker mais próximo do que o usuário digitou, caso o ticker exato não seja encontrado.