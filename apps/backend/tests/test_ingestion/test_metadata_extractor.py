import pytest
from src.ingestion.metadata_extractor import MetadataExtractor


@pytest.fixture
def extractor():
    return MetadataExtractor()


def test_extract_article_number(extractor):
    """Test extraction of article number"""
    text = "Art. 46. A alíquota do CBS será de 7%"
    result = extractor.extract_article(text)
    assert result == "Art. 46"


def test_extract_article_with_letter(extractor):
    """Test extraction of article with letter suffix"""
    text = "Art. 156-A. O imposto municipal..."
    result = extractor.extract_article(text)
    assert result == "Art. 156-A"


def test_extract_paragraph(extractor):
    """Test extraction of paragraph"""
    text = "§ 1º A alíquota referida no caput..."
    result = extractor.extract_paragraph(text)
    assert result == "§1º"


def test_extract_paragraph_with_unicode(extractor):
    """Test extraction with º symbol"""
    text = "§ 2º Outro parágrafo"
    result = extractor.extract_paragraph(text)
    assert result == "§2º"


def test_extract_inciso(extractor):
    """Test extraction of inciso (Roman numerals)"""
    text = "I - primeira alínea"
    result = extractor.extract_inciso(text)
    assert result == "I"

    text = "XII - décima segunda alínea"
    result = extractor.extract_inciso(text)
    assert result == "XII"


def test_extract_all_metadata(extractor):
    """Test extraction of all metadata from text"""
    text = """Art. 46. A alíquota do CBS será de 7%

§ 1º A alíquota referida no caput deste artigo poderá ser reduzida.

I - primeiro caso
II - segundo caso
"""

    metadata = extractor.extract_all(text)

    assert metadata["artigo"] == "Art. 46"
    assert metadata["paragrafos"] == ["§1º"]
    assert set(metadata["incisos"]) == {"I", "II"}
