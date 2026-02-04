"""Groq API client wrapper."""

import json
from typing import Dict, Optional

from groq import Groq


class GroqClient:
    """Wrapper for Groq API using Mixtral-8x7B."""

    def __init__(
        self,
        api_key: str,
        model: str = "mixtral-8x7b-32768"
    ):
        """Initialize Groq client.

        Args:
            api_key: Groq API key
            model: Model to use (default: mixtral-8x7b-32768)
        """
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 800
    ) -> str:
        """Generate response using Generator LLM.

        Args:
            system_prompt: System instruction
            user_prompt: User question
            temperature: Sampling temperature (default: 0.1)
            max_tokens: Max response tokens (default: 800)

        Returns:
            Generated text response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    def validate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1500
    ) -> Dict:
        """Validate response using Validator LLM (JSON mode).

        Args:
            system_prompt: Validator instruction
            user_prompt: Content to validate
            temperature: Sampling temperature (default: 0.0)
            max_tokens: Max response tokens (default: 1500)

        Returns:
            Parsed JSON response as dictionary
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        return json.loads(content)
