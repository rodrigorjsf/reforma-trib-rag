"""Token counting utility using tiktoken."""

import tiktoken


class TokenCounter:
    """Count tokens in text using OpenAI's tiktoken."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize token counter.

        Args:
            encoding_name: Tiktoken encoding (default: cl100k_base for GPT-4)
        """
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
