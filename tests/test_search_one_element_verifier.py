import pytest # type: ignore
from exceptions import ScrapingError
from utils.typing import search_one_element_verifier, search_indicator
from bs4 import BeautifulSoup


def test_search_element_verifier_should_return_text_when_element_exists():
    html = """
    <html>
        <body>
            <div id="container">
                <p class="message">   Hello, world!   </p>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    # selector matches the <p> element and surrounding whitespace should be stripped
    result = search_one_element_verifier(soup, "p.message").get_text(strip=True)
    assert result == "Hello, world!"


def test_search_element_verifier_should_raise_scraping_error_when_not_found():
    html = "<div><span>something</span></div>"
    soup = BeautifulSoup(html, "html.parser")

    with pytest.raises(ScrapingError) as error:
        search_one_element_verifier(soup, ".does-not-exist").get_text(strip=True)

    assert str(error.value) == "Element not found for selector: .does-not-exist"
    assert error.type == ScrapingError

