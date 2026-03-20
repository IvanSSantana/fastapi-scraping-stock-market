# fastapi-scraping-py-csv
Uma API escrita em Python com FastAPI que faz um scraping do site investidor10.com.br e tem a capacidade de exportar para arquivos CSV relatórios sobre ativos.

## Planos:
1. Criar front-end React para consumo da API.
2. Integrar IA para ler relatórios gerenciais de fundos imobiliários e gerar resumos + predição.

## Atual Pipeline:
1. API recebe o ticker;
2. Scraping busca principais indicadores e os últimos relatórios;
3. Docling extrai todo conteúdo dos PDFs em string;
4. Fazer chunking dos documentos (quebrar PDFs em blocos menores, resumir cada bloco e sintetizar tudo num bloco de resumo final)
4. IA gera resumo com capacidade avaliativa;
