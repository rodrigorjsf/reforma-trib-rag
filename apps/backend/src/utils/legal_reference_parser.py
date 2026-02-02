import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class LegalReference:
    """Represents a normalized legal reference."""
    normalized: str
    type: str  # LC, LEI, DEC, MP, CF, EC
    number: Optional[str] = None
    year: Optional[str] = None
    article: Optional[str] = None
    original: Optional[str] = None


class LegalReferenceParser:
    """Parser and normalizer for Brazilian legal references."""

    # Regex patterns for different types of legal references
    PATTERNS = {
        'lei_complementar': r'Lei\s+Complementar\s+n[º°]?\s*(\d+)[/,]\s*(?:de\s+)?(\d{4})',
        'lc_short': r'LC\s+n?[º°]?\s*(\d+)[/,]\s*(?:de\s+)?(\d{4})',
        'lei': r'Lei\s+n[º°]?\s*(\d+)[/,]\s*(?:de\s+)?(\d{4})',
        'decreto': r'Decreto\s+n?[º°]?\s*([\d.]+)[/,]\s*(?:de\s+)?(\d{4})',
        'medida_provisoria': r'(?:Medida\s+Provisória|MP)\s+n?[º°]?\s*(\d+)[/,]\s*(?:de\s+)?(\d{4})',
        'cf_article': r'Art\.?\s*(\d+[-A-Z]*)\s*da\s*(?:Constituição\s+Federal|CF)',
        'emenda_constitucional': r'Emenda\s+Constitucional\s+n[º°]?\s*(\d+)',
    }

    def normalize(self, reference: str) -> Optional[LegalReference]:
        """
        Normalize a legal reference to standard format.

        Args:
            reference: Raw legal reference string

        Returns:
            LegalReference object or None if not recognized
        """
        reference = reference.strip()

        # Try Lei Complementar patterns
        for pattern_name in ['lei_complementar', 'lc_short']:
            match = re.search(self.PATTERNS[pattern_name], reference, re.IGNORECASE)
            if match:
                number = match.group(1)
                year = match.group(2)
                return LegalReference(
                    normalized=f"LC-{number}-{year}",
                    type="LC",
                    number=number,
                    year=year,
                    original=reference
                )

        # Try regular Lei
        match = re.search(self.PATTERNS['lei'], reference, re.IGNORECASE)
        if match:
            number = match.group(1)
            year = match.group(2)
            return LegalReference(
                normalized=f"LEI-{number}-{year}",
                type="LEI",
                number=number,
                year=year,
                original=reference
            )

        # Try Decreto
        match = re.search(self.PATTERNS['decreto'], reference, re.IGNORECASE)
        if match:
            number = match.group(1).replace('.', '')
            year = match.group(2)
            return LegalReference(
                normalized=f"DEC-{number}-{year}",
                type="DEC",
                number=number,
                year=year,
                original=reference
            )

        # Try Medida Provisória
        match = re.search(self.PATTERNS['medida_provisoria'], reference, re.IGNORECASE)
        if match:
            number = match.group(1)
            year = match.group(2)
            return LegalReference(
                normalized=f"MP-{number}-{year}",
                type="MP",
                number=number,
                year=year,
                original=reference
            )

        # Try CF Article
        match = re.search(self.PATTERNS['cf_article'], reference, re.IGNORECASE)
        if match:
            article = match.group(1).replace('-', '')
            return LegalReference(
                normalized=f"CF-art-{article}",
                type="CF",
                article=article,
                original=reference
            )

        # Try Emenda Constitucional
        match = re.search(self.PATTERNS['emenda_constitucional'], reference, re.IGNORECASE)
        if match:
            number = match.group(1)
            return LegalReference(
                normalized=f"EC-{number}",
                type="EC",
                number=number,
                original=reference
            )

        return None
