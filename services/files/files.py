import io
import csv
from typing import List
from exceptions import NoDataForExportError
from docling.document_converter import DocumentConverter
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from responses import StockResponse
from docling_core.types.doc.document import DoclingDocument
from pathlib import Path
from datetime import datetime

def read_pdf(pdf_url) -> DoclingDocument: # type: ignore
    """Lê PDF usando Docling e retorna documento estruturado."""

    # Configurando opções do pipeline do conversor
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False  # Desativa OCR
    pipeline_options.do_table_structure = False  # Desativa estruturação de tabelas

    # Configurando uso de GPU
    accelerator_options = AcceleratorOptions(
        device=AcceleratorDevice.CUDA 
    )

    pipeline_options.accelerator_options = accelerator_options
    

    converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
    
    result = converter.convert(pdf_url)
    document = result.document  # objeto estruturado

    return document

def export_to_csv(stock : StockResponse | List[StockResponse]):
    """Exporta um objeto StockResponse para CSV"""

    if not stock:
        raise NoDataForExportError("No data provided")

    # Permite passar um único StockResponse
    if hasattr(stock, "model_dump"): # Verifica se o modelo pode ser convertido para dicionário
        stock_dumped = [stock.model_dump()] # type: ignore

    #TODO: Permitir passar múltiplos ticker para exportação de CSV
    # Permite passar lista de StockResponse
    # elif hasattr(stock[0], "model_dump"): # type: ignore
    #     stock_dumped = [item.model_dump() for item in stock] # type: ignore

    field_names = stock_dumped[0].keys() # type: ignore

    output = io.StringIO() # Memória temporária para armazenar o CSV gerado

    writer = csv.DictWriter(
        output,
        fieldnames=field_names
    )

    writer.writeheader()
    writer.writerow(stock_dumped[0]) 

    output.seek(0) # Volta para o início do arquivo para leitura para a response
    
    return output

def structures_events_to_markdown(events: list[dict]) -> str:
    """Gera as linhas dos eventos recebidos de forma já limpa."""
    markdown_lines = []

    for event in events:
        title = event.get("titulo")
        description = event.get("descricao")
        impact = event.get("impacto")

        markdown_lines.append(f"- **{title}** - {description}; {impact}")

    return "\n".join(markdown_lines)

def generate_markdown_report(
    ticker: str,
    segmento: str,
    # descricao_resumida: str,
    indicadores: dict,
    eventos: list[dict],
    # interpretacao_indicadores: str,
    # analise_ia: str,
    # conclusao: str,
    template_path: str = "templates/relatorio_acao.md"
) -> str:
    """
    Gera o relatório final em Markdown a partir de um template.
    """

    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read() # Arquivo Markdown em String

    eventos_md = structures_events_to_markdown(eventos)

    replacements = {
        "{{TICKER}}": ticker,
        "{{DATA_ATUAL}}": datetime.now().strftime("%d/%m/%Y"),
        "{{SEGMENTO}}": segmento,
        # "{{DESCRICAO_RESUMIDA}}": descricao_resumida,

        "{{PL}}": str(indicadores.get("pl")),
        # "{{PL_ANALISE}}": str(indicadores.get("pl_analise")),

        "{{PVP}}": str(indicadores.get("pvp")),
        # "{{PVP_ANALISE}}": str(indicadores.get("pvp_analise")),

        "{{DY}}": str(indicadores.get("dividend_yield")),
        # "{{DY_ANALISE}}": str(indicadores.get("dy_analise")),

        "{{ROE}}": str(indicadores.get("roe")),
        # "{{ROE_ANALISE}}": str(indicadores.get("roe_analise")),

        "{{ROIC}}": str(indicadores.get("roic")),
        # "{{ROIC_ANALISE}}": str(indicadores.get("roic_analise")),

        # "{{INTERPRETACAO_INDICADORES}}": interpretacao_indicadores,
        "{{EVENTOS}}": eventos_md,
        # "{{ANALISE_IA}}": analise_ia,
        # "{{CONCLUSAO}}": conclusao,
    }

    for placeholder, value in replacements.items(): # Itera as chaves dos dicionários
        template = template.replace(placeholder, value)

    return template # Markdown em formato String

def save_markdown_report(markdown_string: str, ticker: str) -> str | None:
    """
    Salva o relatório Markdown string em reports_db/ como arquivo.
    """
    reports_folder = Path("reports_db")
    reports_folder.mkdir(exist_ok=True)

    file_name = f"{ticker.upper()}_{datetime.now().strftime('%Y-%m-%d')}.md"
    file_path = reports_folder / file_name

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(markdown_string)

    print(file_path)
    return str(file_path)

#TODO: Exportar para Excel

if __name__ == "__main__":
    ...
    # eventos_mock = [
    #     {
    #         "titulo": "Expansão de Negócio",
    #         "descricao": "A empresa anunciou investimentos em novas operações logísticas com expectativa de ganho de eficiência nos próximos anos.",
    #         "impacto": "Dominação em massa da empresa."
    #     },
    #     {
    #         "titulo": "Redução de Dívida",
    #         "descricao": "A companhia reduziu sua alavancagem financeira em relação ao trimestre anterior.",
    #         "impacto": "Crescimento monstruoso da corporação."
    #     }
    # ]

    # indicadores_mock = {
    #     "pl": "8.32",
    #     "pvp": "1.12",
    #     "dividend_yield": "7.8",
    #     "roe": "14.5",
    #     "roic": "11.2",
    # }

    # markdown = generate_markdown_report(
    #     ticker="LREN3",
    #     segmento="Varejo",
    #     indicadores=indicadores_mock,
    #     eventos=eventos_mock,
    # )

    # saved_path = save_markdown_report(markdown, "LREN3")

    # print("Relatório salvo em:", saved_path)