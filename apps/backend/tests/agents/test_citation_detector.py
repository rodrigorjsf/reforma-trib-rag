# apps/backend/tests/agents/test_citation_detector.py
import pytest
from src.agents.citation_detector import CitationDetector
from src.utils.legal_reference_parser import LegalReference


class TestCitationDetector:
    @pytest.fixture
    def detector(self):
        return CitationDetector()

    def test_extract_from_text_lei_complementar(self, detector):
        text = "Conforme LC 227/2026, art. 5º, o contribuinte..."
        refs = detector._extract_from_text(text)
        assert len(refs) >= 1
        assert any("227" in ref and "2026" in ref for ref in refs)

    def test_extract_from_text_multiple_references(self, detector):
        text = """
        A LC 227/2026 modifica o Art. 156-A da Constituição Federal,
        conforme estabelecido pelo Decreto 11.374/2023.
        """
        refs = detector._extract_from_text(text)
        assert len(refs) >= 3

    def test_extract_from_text_no_references(self, detector):
        text = "Este texto não contém referências legais válidas."
        refs = detector._extract_from_text(text)
        assert len(refs) == 0

    def test_normalize_extracts_legal_references(self, detector):
        raw_refs = [
            "Lei Complementar nº 227/2026",
            "Art. 156-A da Constituição Federal",
            "Decreto 11.374/2023"
        ]
        normalized = detector._normalize(raw_refs)

        assert len(normalized) == 3
        assert any(ref.normalized == "LC-227-2026" for ref in normalized)
        assert any(ref.normalized == "CF-art-156A" for ref in normalized)
        assert any(ref.normalized == "DEC-11374-2023" for ref in normalized)

    def test_detect_deduplicates_references(self, detector):
        text = "LC 227/2026 e LC 227/2026 são mencionados duas vezes."
        chunks = []  # No chunks for this test

        refs = detector.detect(text, chunks)
        # Should only have one unique reference
        assert len(refs) == 1
        assert refs[0].normalized == "LC-227-2026"

    def test_detect_combines_text_and_chunks(self, detector):
        text = "Conforme LC 227/2026..."
        chunks = [
            {"metadata": {"legal_references": ["Decreto 11.374/2023"]}}
        ]

        refs = detector.detect(text, chunks)
        assert len(refs) == 2
        normalized_refs = {ref.normalized for ref in refs}
        assert "LC-227-2026" in normalized_refs
        assert "DEC-11374-2023" in normalized_refs
