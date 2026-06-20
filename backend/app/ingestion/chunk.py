from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[dict]:
    """Divide las páginas en chunks con metadatos."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = []
    for page in pages:
        splits = text_splitter.split_text(page["text"])
        for i, split in enumerate(splits):
            chunks.append(
                {
                    "content": split.strip(),
                    "metadata": {
                        "page": page["page_number"],
                        "chunk_index": i,
                        "source": "codigo_nacional_transito",
                    },
                }
            )
    return chunks
