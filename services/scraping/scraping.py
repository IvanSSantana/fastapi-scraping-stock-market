from urllib import response
from bs4 import BeautifulSoup
from communication.exceptions import ScrapingError
from communication.responses import StockResponse
from utils.typing.typing_utils import price_sanitizer
from utils.scraping.searching import search_one_element_verifier, search_indicator
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service 
from selenium.webdriver.firefox.webdriver import WebDriver 
from selenium.webdriver.firefox.options import Options 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime, timedelta
import requests

# SETUP PARA RODAR NO COLAB
# import google_colab_selenium as gs
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service 
# from selenium.webdriver.chrome.webdriver import WebDriver 

async def search_asset(ticker: str) -> StockResponse:
    url = f"https://investidor10.com.br/acoes/{ticker}/"

    # SETUP DO BEAUTIFULSOUP
    headers = {
    "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"  # Define a codificação correta para lidar com caracteres acentuados

    if response.status_code != 200:
        raise ValueError("Error while accessing the website")

    # Setup do leitor/parser do BeautifulSoup para ler o HTML da página.
    soup = BeautifulSoup(response.text, "html.parser")

    #TODO: Otimizar velocidade com Selenium
    # SETUP DO SELENIUM
    options = Options()
    options.add_argument("--headless") 
    driver = WebDriver(service=Service(GeckoDriverManager().install()), options=options)
    # driver = gs.Chrome()
    driver.get(url)

    # Procura dos atributos para o StockResponse Model
    #TODO: Criar um log para monitoramento de erros.
    try:
        site_ticker = search_one_element_verifier(soup, ".name-ticker h1").get_text(strip=True)
        price = price_sanitizer(search_one_element_verifier(soup, "div._card.cotacao div._card-body div span.value").get_text(strip=True))
        variation_1y = price_sanitizer(search_one_element_verifier(soup, "div._card.pl div._card-body div span").get_text(strip=True))

        img_variation = soup.select_one("div._card.pl div._card-body div img")
        if img_variation:
            src = img_variation.get("src") or ""
            if "seta-down" in src:
                variation_1y = -variation_1y if variation_1y else None 
                
        # Para variação de 1 mês, é necessário clicar no botão correspondente via Selenium para carregar os dados.
        selector_1m_variation = "//a[contains(@class,'nav-link') and contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'30 dias')]"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
            selector_1m_variation))
        )

        button_1m_variation = driver.find_element(
            By.XPATH,
            selector_1m_variation
        )
        button_1m_variation.click()
        
        # Aguardar o carregamento da variação de 1 mês após clicar no botão.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".info-percentage"))
        )

        variation_text = driver.find_element(
            By.CSS_SELECTOR,
            "span.info-percentage"
        ).text

        variation_1m = price_sanitizer(variation_text)

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
    
    except ScrapingError as error:
        raise ScrapingError(error)
    
    finally:        
        driver.quit()

    stock_response = StockResponse(
        ticker=site_ticker,
        price=price,
        value_variation_1y=variation_1y,
        value_variation_1m=variation_1m,
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
    #TODO: Limitar requisição por mês, evitando criar CSVs desnecessários e sobrecarregar o site. Criar um log para monitoramento de erros e requisições.

async def search_pdfs_asset(ticker: str):
    url = f"https://investidor10.com.br/acoes/{ticker}/"

    # SETUP DO REQUESTS PARA EVITAR BLOQUEIOS DE ACESSO
    headers = {
        "User-Agent": "Mozilla/5.0",
        # "content-type": "application/pdf"
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    
    if response.status_code != 200:
        raise ScrapingError("Error while accessing the website")

    # Setup do leitor/parser do BeautifulSoup para ler o HTML da página
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        # Procura dos PDFs na seção de comunicações
        pdfs_area = search_one_element_verifier(soup, "section#communications-section div.content div.row")

        files_elements = pdfs_area.select("div.col-12 div.communication-card")
        
        pdfs_urls = []
        
        for file in files_elements:
            date_of_report = file.select_one("div.card-date span.card-date--content")
            date_of_report_text = date_of_report.get_text(strip=True) # type: ignore

            if date_of_report:
                date_of_report = datetime.strptime(date_of_report_text, "%d/%m/%Y")

                if date_of_report < datetime.now() - timedelta(days=30): # Descarta relatórios com mais de 1 mês
                    continue

            file_button = file.select_one("a.btn-download-communication")

            if file_button:
                file_pdf_link = file_button.get("href")

                if file_pdf_link:
                    pdfs_urls. append(file_pdf_link)

        return pdfs_urls

    except ScrapingError as error:
        raise ScrapingError(error)
    except Exception as e:
        raise ScrapingError(f"Error while searching for PDFs of management reports: {str(e)}")

# Para debug manual
if __name__ == "__main__":
    import asyncio
    ...
    # print(search_asset("PETR4").model_dump_json(indent=4))
    # print(search_asset("TAEE4").model_dump_json(indent=4))
    # print(search_asset("RAIZ4").model_dump_json(indent=4))
    petr4 = asyncio.run(search_pdfs_asset("PETR4"))
    print(petr4)