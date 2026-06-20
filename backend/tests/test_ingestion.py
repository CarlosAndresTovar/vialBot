from pathlib import Path

import pytest

from app.ingestion.chunk import chunk_pages
from app.ingestion.load_pdf import load_pdf_text


@pytest.fixture
def sample_pdf() -> Path:
    path = Path(__file__).parent.parent.parent / "data" / "codigo_nacional_transito.pdf"
    if not path.exists():
        pytest.skip("PDF de prueba no encontrado")
    return path


def test_load_pdf(sample_pdf):
    pages = load_pdf_text(sample_pdf)
    assert len(pages) > 0
    assert "Código Nacional de Tránsito" in pages[0]["text"] or "LEY 769" in pages[0]["text"]


def test_chunk_pages(sample_pdf):
    pages = load_pdf_text(sample_pdf)
    chunks = chunk_pages(pages, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= len(pages)
    assert all("content" in c and "metadata" in c for c in chunks)
