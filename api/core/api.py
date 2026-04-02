from fastapi import FastAPI, Response, status
from fastapi.responses import StreamingResponse, FileResponse
from communication.exceptions import NoDataForExportError
from services.scraping.scraping import search_asset, search_pdfs_asset
from services.ai.ai_services import summarize_documents_to_events, generate_conclusion
from services.files.files_services import export_to_csv, read_pdf, generate_markdown_report, save_markdown_report
from utils.ai.chunking import batch_chunks, chunk
from utils.typing.typing_utils import clean_json_from_ai
from utils.files.filter_events import filter_events
import asyncio
from datetime import datetime

app = FastAPI()

#TODO: Implementar autenticação e autorização para proteger as rotas de acesso aos dados dos ativos.

@app.get("/api/v1/{ticker}", status_code=status.HTTP_200_OK)
async def get_asset(ticker: str, response: Response):
    """Rota para buscar os dados de um ativo específico."""
    try:
        response.status_code = status.HTTP_200_OK
        return search_asset(ticker)
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": str(e)}
    
@app.get("/api/v1/csv/{ticker}", status_code=status.HTTP_200_OK)
async def get_asset_csv(ticker: str, response: Response):
    """Rota para exportar os dados de um ativo específico em formato CSV."""
    try:
        stock = await search_asset(ticker)

        output = export_to_csv(stock)

        response.status_code = status.HTTP_200_OK
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={ticker}_{datetime.now().month}-{datetime.now().year}.csv"
            }
        )
    
    except NoDataForExportError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": str(e)}
    
@app.get("/api/v1/report/{ticker}")
async def get_report(ticker: str, response: Response):
    #TODO: Salvar relatórios já gerados do mês e redefinir banco de dados ao virar mês
    try:
        print("Extraindo indicadores do ativo")
        stock_task = search_asset(ticker)

        print("Procurando relatórios")
        pdfs_urls_task = search_pdfs_asset(ticker)

        stock, pdfs_urls = await asyncio.gather( # Faz elas rodarem concomitantemente (concorrência)
            stock_task,
            pdfs_urls_task
        ) 
        
        print("Lendo PDFs")
        all_events = []
        
        for url in pdfs_urls: 
            
            print(f"URL: {url}")
            doc = read_pdf(url)

            print("Chunkeando os documentos")
            chunks = chunk(doc)

            print("Batcheando os documentos")

            for i, batch in enumerate(batch_chunks(chunks)):
                #  print(f"Batch {i}")

                #TODO: Implementar concorrência para processar batches simultaneamente, otimizando perfomance
                # Chamada da IA
                event = summarize_documents_to_events(batch)
                print(f"EVENTO {i}: {event}") # PARA DEBUG

                all_events.append(event)

        print("Limpando eventos")
        cleaned_all_events = []

        for event in all_events:
            cleaned_event = clean_json_from_ai(event)
            cleaned_all_events.extend(cleaned_event)

        print("Filtrando 10 eventos mais relevantes")
        filtered_events = filter_events(cleaned_all_events)

        print("Gerando relatório final")

        string_report = generate_markdown_report(
            stock.ticker, 
            stock.segment, # type: ignore
            stock.model_dump(), 
            events=filtered_events
        )
        
        file_report_path = save_markdown_report(string_report, stock.ticker)

        response.status_code = status.HTTP_200_OK
        response.status_code = status.HTTP_200_OK
        return FileResponse(
            path=file_report_path,
            media_type="text/markdown",
            filename=file_report_path.name
        )
    
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": str(e)}

#TODO: Rota POST que recebe um JSON com múltiplos tickers.
#TODO: Rota POST que recebe um CSV e tem a capacidade de atualizar dados, criar novos registros de variação de preços etc..
#TODO: Rota padrão que busca o ticker mais próximo do que o usuário digitou, caso o ticker exato não seja encontrado.