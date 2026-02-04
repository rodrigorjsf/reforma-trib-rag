import pytest
from unittest.mock import Mock, MagicMock
from src.generation.pipeline import GenerationPipeline


@pytest.fixture
def mock_query_engine():
    """Mock query engine"""
    engine = Mock()
    engine.search.return_value = [
        {
            "text": "Art. 46. A alíquota do CBS será de 7%",
            "metadata": {
                "artigo": "Art. 46",
                "paragrafo": None,
                "source_id": "LC_214_2024"
            }
        }
    ]
    return engine


@pytest.fixture
def mock_groq():
    """Mock Groq client"""
    client = Mock()
    client.generate.return_value = "A alíquota é 7% [Art. 46 — LC 214/2024]"
    client.validate.return_value = {
        "veredicto": "PASS",
        "severidade": "OK",
        "detalhes": "Resposta válida"
    }
    return client


@pytest.fixture
def pipeline(mock_groq, mock_query_engine):
    """Create pipeline with mocked dependencies"""
    return GenerationPipeline(
        groq_client=mock_groq,
        query_engine=mock_query_engine
    )


def test_answer_question_success(pipeline, mock_groq, mock_query_engine):
    """Test successful answer generation"""
    result = pipeline.answer_question(
        question="Qual é a alíquota do CBS?",
        mode="TÉCNICO"
    )

    assert result["status"] == "OK"
    assert "7%" in result["response"]
    assert len(result["sources"]) > 0
    mock_query_engine.search.assert_called_once()
    mock_groq.generate.assert_called_once()
    mock_groq.validate.assert_called_once()


def test_answer_question_blocked_critical(pipeline, mock_groq, mock_query_engine):
    """Test response blocked due to critical validation failure"""
    # Mock critical validation failure
    mock_groq.validate.return_value = {
        "veredicto": "FAIL",
        "severidade": "CRITICO",
        "detalhes": "Citação fabricada"
    }

    result = pipeline.answer_question("Test question", mode="TÉCNICO")

    assert result["status"] == "BLOCKED"
    assert "não foi possível" in result["response"]
    assert result["validation"]["severidade"] == "CRITICO"


def test_answer_question_warning(pipeline, mock_groq, mock_query_engine):
    """Test response sent with warning"""
    # Mock warning validation
    mock_groq.validate.return_value = {
        "veredicto": "PASS",
        "severidade": "AVISO",
        "detalhes": "Resposta parcialmente suportada"
    }

    result = pipeline.answer_question("Test question", mode="TÉCNICO")

    assert result["status"] == "WARNING"
    assert "7%" in result["response"]


def test_answer_question_no_context(pipeline, mock_query_engine):
    """Test fallback when no context found"""
    mock_query_engine.search.return_value = []

    result = pipeline.answer_question("Test question", mode="TÉCNICO")

    assert result["status"] == "BLOCKED"
    assert "não foi possível" in result["response"]
    assert result["reason"] == "Nenhum contexto relevante encontrado"
