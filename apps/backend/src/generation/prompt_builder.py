"""Prompt builder for variable injection."""

from pathlib import Path
from typing import List, Dict


class PromptBuilder:
    """Builds prompts with variable injection."""

    def __init__(self, prompts_dir: str = None):
        """Initialize prompt builder.

        Args:
            prompts_dir: Directory containing prompt templates
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent / "prompts"
        self.prompts_dir = Path(prompts_dir)

    def _load_template(self, filename: str) -> str:
        """Load prompt template from file."""
        path = self.prompts_dir / filename
        return path.read_text(encoding='utf-8')

    def build_generator_prompt(
        self,
        context_chunks: List[Dict],
        question: str,
        mode: str
    ) -> tuple[str, str]:
        """Build generator prompt with context injection.

        Args:
            context_chunks: List of retrieved chunks with metadata
            question: User's question
            mode: "TÉCNICO" or "SIMPLIFICADO"

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_template = self._load_template("generator.txt")

        # Build context string from chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            citation = f"[{chunk['metadata']['artigo']}"
            if chunk['metadata'].get('paragrafo'):
                citation += f", {chunk['metadata']['paragrafo']}"
            citation += f" — {chunk['metadata']['source_id']}]"

            context_parts.append(f"Fonte {i} {citation}:\n{chunk['text']}\n")

        context_str = "\n".join(context_parts)

        # Inject variables into system prompt
        system_prompt = system_template.replace("{MODE}", mode)

        # Build user prompt with context + question
        user_prompt = f"""CONTEXTO:
{context_str}

PERGUNTA DO USUÁRIO:
{question}

Responda à pergunta usando APENAS as informações do contexto acima. Inclua citações inline."""

        return system_prompt, user_prompt

    def build_validator_prompt(
        self,
        context_chunks: List[Dict],
        question: str,
        generated_response: str,
        mode: str
    ) -> tuple[str, str]:
        """Build validator prompt for response verification.

        Args:
            context_chunks: List of retrieved chunks
            question: User's question
            generated_response: Generated response to validate
            mode: "TÉCNICO" or "SIMPLIFICADO"

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_template = self._load_template("validator.txt")

        # Build context string (same as generator)
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            citation = f"[{chunk['metadata']['artigo']}"
            if chunk['metadata'].get('paragrafo'):
                citation += f", {chunk['metadata']['paragrafo']}"
            citation += f" — {chunk['metadata']['source_id']}]"

            context_parts.append(f"Fonte {i} {citation}:\n{chunk['text']}\n")

        context_str = "\n".join(context_parts)

        # Inject mode into system prompt
        system_prompt = system_template.replace("{MODE}", mode)

        # Build user prompt with context + question + response
        user_prompt = f"""CONTEXTO:
{context_str}

PERGUNTA DO USUÁRIO:
{question}

RESPOSTA GERADA:
{generated_response}

Valide a resposta e retorne JSON com veredicto, severidade e detalhes."""

        return system_prompt, user_prompt
