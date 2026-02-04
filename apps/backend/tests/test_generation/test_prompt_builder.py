import pytest
from pathlib import Path
from src.generation.prompt_builder import PromptBuilder


@pytest.fixture
def prompt_builder():
    return PromptBuilder()


@pytest.fixture
def sample_chunks():
    return [
        {
            "text": "Art. 46. A alíquota do CBS será de 7%",
            "metadata": {
                "artigo": "Art. 46",
                "paragrafo": None,
                "source_id": "LC_214_2024"
            }
        }
    ]


def test_prompt_builder_initialization(prompt_builder):
    """Test PromptBuilder initializes with prompts directory"""
    assert prompt_builder.prompts_dir.exists()
    assert (prompt_builder.prompts_dir / "generator.txt").exists()
    assert (prompt_builder.prompts_dir / "validator.txt").exists()


def test_build_generator_prompt(prompt_builder, sample_chunks):
    """Test building generator prompt with context"""
    system_prompt, user_prompt = prompt_builder.build_generator_prompt(
        context_chunks=sample_chunks,
        question="Qual é a alíquota do CBS?",
        mode="TÉCNICO"
    )

    assert "TÉCNICO" in system_prompt
    assert "Art. 46" in user_prompt
    assert "LC_214_2024" in user_prompt
    assert "Qual é a alíquota do CBS?" in user_prompt


def test_build_validator_prompt(prompt_builder, sample_chunks):
    """Test building validator prompt"""
    system_prompt, user_prompt = prompt_builder.build_validator_prompt(
        context_chunks=sample_chunks,
        question="Qual é a alíquota?",
        generated_response="A alíquota é 7% [Art. 46 — LC 214/2024]",
        mode="SIMPLIFICADO"
    )

    assert "SIMPLIFICADO" in system_prompt
    assert "Art. 46" in user_prompt
    assert "A alíquota é 7%" in user_prompt
