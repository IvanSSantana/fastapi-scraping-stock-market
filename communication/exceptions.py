class ScrapingError(Exception):
    """Exceção para erros relacionados à raspagem de dados."""
    pass

class NoDataForExportError(Exception):
    """Exceção para indicar que não há dados disponíveis para a geração do arquivo de exportação (CSV, Excel, etc.)."""
    pass