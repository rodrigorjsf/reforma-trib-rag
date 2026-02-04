import pytest
from unittest.mock import Mock, patch, MagicMock
from src.generation.groq_client import GroqClient


@pytest.fixture
def mock_groq():
    """Mock Groq API client"""
    with patch('src.generation.groq_client.Groq') as mock:
        # Mock the client instance
        mock_instance = MagicMock()
        mock.return_value = mock_instance

        # Mock chat.completions.create response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_instance.chat.completions.create.return_value = mock_response

        yield mock_instance


def test_groq_client_initialization(mock_groq):
    """Test GroqClient initializes with API key"""
    client = GroqClient(api_key="test_key")
    assert client.model == "mixtral-8x7b-32768"


def test_generate_response(mock_groq):
    """Test generate method for generator LLM"""
    client = GroqClient(api_key="test_key")

    result = client.generate(
        system_prompt="You are a helper",
        user_prompt="Hello"
    )

    assert result == "Test response"
    # Verify it was called with correct temperature
    mock_groq.chat.completions.create.assert_called_once()
    call_args = mock_groq.chat.completions.create.call_args
    assert call_args[1]['temperature'] == 0.1
    assert call_args[1]['max_tokens'] == 800


def test_validate_response(mock_groq):
    """Test validate method for validator LLM (JSON mode)"""
    # Update mock to return JSON
    mock_groq.chat.completions.create.return_value.choices[0].message.content = '{"verdict": "PASS"}'

    client = GroqClient(api_key="test_key")

    result = client.validate(
        system_prompt="You are a validator",
        user_prompt="Validate this"
    )

    assert result == {"verdict": "PASS"}
    # Verify JSON mode enabled
    call_args = mock_groq.chat.completions.create.call_args
    assert call_args[1]['temperature'] == 0.0
    assert call_args[1]['max_tokens'] == 1500
    assert call_args[1]['response_format'] == {"type": "json_object"}
