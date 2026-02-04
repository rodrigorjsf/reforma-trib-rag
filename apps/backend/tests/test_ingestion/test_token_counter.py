import pytest
from src.ingestion.token_counter import TokenCounter


@pytest.fixture
def counter():
    return TokenCounter()


def test_count_tokens_simple(counter):
    """Test token counting for simple text"""
    text = "Art. 46. A alíquota do CBS será de 7%"
    count = counter.count(text)
    assert count > 0
    assert count < 20  # Should be around 12-15 tokens


def test_count_tokens_empty(counter):
    """Test token counting for empty text"""
    assert counter.count("") == 0


def test_count_tokens_portuguese(counter):
    """Test token counting for Portuguese text"""
    text = "A Contribuição sobre Bens e Serviços (CBS) é um imposto federal."
    count = counter.count(text)
    assert count > 10
    assert count < 25
