from pathlib import Path

import fitz  # pymupdf


def load_pdf_text(pdf_path: str | Path) -> list[dict]:
    """Extrae texto de un PDF manteniendo metadatos de página."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            pages.append(
                {
                    "page_number": page_num + 1,
                    "text": text.strip(),
                }
            )
    return pages


def load_pdf_text_from_bytes(pdf_bytes: bytes) -> list[dict]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            pages.append(
                {
                    "page_number": page_num + 1,
                    "text": text.strip(),
                }
            )
    return pages
