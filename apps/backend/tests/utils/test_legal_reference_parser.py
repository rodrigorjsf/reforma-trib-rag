import pytest
from src.utils.legal_reference_parser import LegalReferenceParser, LegalReference


class TestLegalReferenceParser:
    def test_normalize_lei_complementar_standard(self):
        parser = LegalReferenceParser()
        result = parser.normalize("Lei Complementar nº 227/2026")
        assert result.normalized == "LC-227-2026"
        assert result.type == "LC"
        assert result.number == "227"
        assert result.year == "2026"

    def test_normalize_lei_complementar_short(self):
        parser = LegalReferenceParser()
        result = parser.normalize("LC 227/2026")
        assert result.normalized == "LC-227-2026"

    def test_normalize_constituicao_federal_article(self):
        parser = LegalReferenceParser()
        result = parser.normalize("Art. 156-A da Constituição Federal")
        assert result.normalized == "CF-art-156A"
        assert result.type == "CF"

    def test_normalize_decreto(self):
        parser = LegalReferenceParser()
        result = parser.normalize("Decreto 11.374/2023")
        assert result.normalized == "DEC-11374-2023"
        assert result.type == "DEC"
        assert result.number == "11374"
        assert result.year == "2023"

    def test_normalize_handles_variations(self):
        parser = LegalReferenceParser()
        variations = [
            "Lei Complementar nº 227/2026",
            "LC 227/2026",
            "LC 227, de 2026"
        ]
        for var in variations:
            result = parser.normalize(var)
            assert result.normalized == "LC-227-2026"

    def test_normalize_invalid_reference_returns_none(self):
        parser = LegalReferenceParser()
        result = parser.normalize("Invalid text without legal reference")
        assert result is None
