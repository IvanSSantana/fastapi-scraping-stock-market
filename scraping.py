import requests
from bs4 import BeautifulSoup
from responses import StockResponse
from utils import price_sanitizer, search_element_verifier, search_indicator

def search_asset(ticker: str):
    url = f"https://investidor10.com.br/acoes/{ticker}/"

    headers = {
    "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ValueError("Error while accessing the website")

    # Setup do leitor/parser do BeautifulSoup para ler o HTML da página.
    global soup # Exportação para utils.py, ciente de ser má prática, mas foi a solução que pensei
    soup = BeautifulSoup(response.text, "html.parser")

    # Procura dos atributos para o StockResponse Model
    try:
        site_ticker = search_element_verifier(soup, ".name-ticker h1")
        price = price_sanitizer(search_element_verifier(soup, "div._card.cotacao div._card-body div span.value"))
        variation = price_sanitizer(search_element_verifier(soup, "div._card.pl div._card-body div span"))

        img_variation = soup.select_one("div._card.pl div._card-body div img")
        if img_variation:
            src = img_variation.get("src") or ""
            if "seta-down" in src:
                variation = -variation

        table_indicators = "#table-indicators div.cell"
        pl = price_sanitizer(search_indicator("P/L", soup, table_indicators))
        pvp = price_sanitizer(search_indicator("P/VP", soup, table_indicators))
        dividend_yield = price_sanitizer(search_indicator("Dividend Yield", soup, table_indicators))
        roe = price_sanitizer(search_indicator("ROE", soup, table_indicators))
        roic = price_sanitizer(search_indicator("ROIC", soup, table_indicators))
        net_debt_to_EBITDA = price_sanitizer(search_indicator("Dívida Líquida / EBITDA", soup, table_indicators))
        ev_to_EBITDA = price_sanitizer(search_indicator("EV/EBITDA", soup, table_indicators))
        profit_cagr = price_sanitizer(search_indicator("CAGR Lucros ", soup, table_indicators))
        payout = price_sanitizer(search_indicator("Payout", soup, table_indicators))
        net_margin = price_sanitizer(search_indicator("Margem Líquida", soup, table_indicators))
        ebit_margin = price_sanitizer(search_indicator("Margem Ebit", soup, table_indicators))

        segment = search_indicator("Setor", soup, "#table-indicators-company div.cell")

    except ValueError as error:
        raise ValueError(error)

    stock_response = StockResponse(
        ticker=site_ticker,
        price=price,
        value_variation=variation,
        pl=pl,
        pvp=pvp,
        dividend_yield=dividend_yield,
        roe=roe,
        roic=roic,
        net_debt_to_EBITDA=net_debt_to_EBITDA,
        ev_to_EBITDA=ev_to_EBITDA,
        profit_cagr=profit_cagr,
        payout=payout,
        net_margin=net_margin,
        ebit_margin=ebit_margin,
        segment=segment
    )

    return stock_response


# Para testes
print(search_asset("PETR4").model_dump_json(indent=4))