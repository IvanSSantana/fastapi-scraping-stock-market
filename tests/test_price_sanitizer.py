import pytest # type: ignore
from utils import price_sanitizer
from decimal import Decimal

def test_should_remove_rs():
    assert price_sanitizer("R$ 1900,50") == Decimal("1900.5")

def test_should_remove_dot():
    assert price_sanitizer("5.000.300,75") == Decimal("5000300.75")

def test_should_remove_percent():
    assert price_sanitizer("50%") == Decimal("50")

def test_should_return_0_for_not_numbers():
    assert price_sanitizer("Olá máquina!") == Decimal("0")