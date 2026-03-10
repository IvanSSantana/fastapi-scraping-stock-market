import pytest # type: ignore
from utils import search_indicator
from bs4 import BeautifulSoup


def test_search_indicator_finds_value_in_div_value_span():
    html = """
    <div id="table-indicators">
        <div class="cell">
            <span>Interest Rate</span>
            <div class="value"><span>5.25%</span></div>
        </div>
        <div class="cell">
            <span>Other</span>
            <div class="value"><span>ignored</span></div>
        </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")

    # indicator matching should be case-insensitive and whitespace trimmed
    result = search_indicator("interest rate", soup)
    assert result == "5.25%"


def test_search_indicator_finds_value_in_span_value():
    html = """
    <div id="table-indicators">
        <div class="cell">
            <span>GDP</span>
            <span class="value">1.234</span>
        </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = search_indicator("gdp", soup)
    assert result == "1.234"


def test_search_indicator_raises_when_not_found():
    html = """
    <div id="table-indicators">
        <div class="cell">
            <span>Something</span>
            <div class="value"><span>10</span></div>
        </div>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")

    assert search_indicator("nonexistent", soup) == ""