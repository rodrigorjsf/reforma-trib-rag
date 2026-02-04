"""Generation pipeline for RAG system."""

from typing import Dict, List, Optional
import logging

from .groq_client import GroqClient
from .prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class GenerationPipeline:
    """Pipeline for retrieving, generating, and validating responses."""

    def __init__(
        self,
        groq_client: GroqClient,
        query_engine,  # Will integrate with retrieval module
        prompt_builder: Optional[PromptBuilder] = None
    ):
        """Initialize generation pipeline.

        Args:
            groq_client: Groq API client
            query_engine: Query engine for context retrieval
            prompt_builder: Prompt builder (creates default if None)
        """
        self.groq = groq_client
        self.query_engine = query_engine
        self.prompt_builder = prompt_builder or PromptBuilder()

    def answer_question(
        self,
        question: str,
        mode: str = "TÉCNICO",
        top_k: int = 5
    ) -> Dict:
        """Generate and validate answer to user question.

        Args:
            question: User's question
            mode: Response mode ("TÉCNICO" or "SIMPLIFICADO")
            top_k: Number of context chunks to retrieve

        Returns:
            Dictionary with:
                - status: "OK", "WARNING", or "BLOCKED"
                - response: Generated response text
                - sources: Retrieved context chunks
                - validation: Validation details (if applicable)
        """
        # Step 1: Retrieve context
        try:
            context_chunks = self.query_engine.search(question, top_k=top_k)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {
                "status": "BLOCKED",
                "response": self._generate_fallback_message(question),
                "error": "Sistema de busca temporariamente indisponível",
                "sources": []
            }

        # Edge case: No context found
        if not context_chunks or len(context_chunks) == 0:
            return {
                "status": "BLOCKED",
                "response": self._generate_fallback_message(question),
                "reason": "Nenhum contexto relevante encontrado",
                "sources": []
            }

        # Step 2: Build generator prompt
        system_prompt, user_prompt = self.prompt_builder.build_generator_prompt(
            context_chunks=context_chunks,
            question=question,
            mode=mode
        )

        # Step 3: Generate response
        try:
            generated_response = self.groq.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "status": "BLOCKED",
                "response": self._generate_fallback_message(question),
                "error": "Falha na geração da resposta",
                "sources": context_chunks
            }

        # Step 4: Build validator prompt
        val_system, val_user = self.prompt_builder.build_validator_prompt(
            context_chunks=context_chunks,
            question=question,
            generated_response=generated_response,
            mode=mode
        )

        # Step 5: Validate response
        try:
            validation_result = self.groq.validate(
                system_prompt=val_system,
                user_prompt=val_user
            )
        except Exception as e:
            logger.warning(f"Validation failed: {e}, assuming PASS")
            validation_result = {
                "veredicto": "PASS",
                "severidade": "AVISO",
                "detalhes": "Validação falhou - aceitando resposta"
            }

        # Step 6: Decision logic
        severity = validation_result.get("severidade", "AVISO")
        verdict = validation_result.get("veredicto", "PASS")

        if severity == "CRITICO" or verdict == "FAIL":
            # Block response
            return {
                "status": "BLOCKED",
                "response": self._generate_fallback_message(question),
                "validation": validation_result,
                "sources": context_chunks,
                "blocked_response": generated_response  # For debugging
            }
        elif severity == "AVISO":
            # Send with warning
            return {
                "status": "WARNING",
                "response": generated_response,
                "validation": validation_result,
                "sources": context_chunks
            }
        else:
            # OK - send normally
            return {
                "status": "OK",
                "response": generated_response,
                "validation": validation_result,
                "sources": context_chunks
            }

    def _generate_fallback_message(self, question: str) -> str:
        """Generate fallback message when response is blocked.

        Args:
            question: User's question

        Returns:
            Fallback message
        """
        return (
            "Desculpe, não foi possível encontrar informações suficientes "
            "sobre sua pergunta na base de conhecimento atual da reforma tributária. "
            "Por favor, reformule sua pergunta ou consulte diretamente os documentos oficiais."
        )
