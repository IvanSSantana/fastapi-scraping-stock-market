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

def extract_relevant_lines(document):
    """Processa os documentos localmente com Regex mantendo somente linhas relevantes, usando algoritmo de palavras-chave + linhas com números"""
    #TODO: Ainda precisa de ajustes ao novo modelo de documentos
    
    return ...

#TODO: Exportar para Excel