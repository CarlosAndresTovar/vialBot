import asyncio
from pathlib import Path

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import settings
from app.ingestion.chunk import chunk_pages
from app.ingestion.load_pdf import load_pdf_text


def ensure_collection(client: QdrantClient, collection_name: str, size: int) -> None:
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)
    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE),
        )
        print(f"Colección '{collection_name}' creada con vector size={size}")
    else:
        print(f"Colección '{collection_name}' ya existe")


async def index_pdf(pdf_path: str | Path) -> int:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")

    pages = load_pdf_text(pdf_path)
    chunks = chunk_pages(pages)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    ensure_collection(client, settings.qdrant_collection_name, settings.embedding_dimensions)

    store = QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection_name,
        embedding=embeddings,
    )

    texts = [c["content"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    await store.aadd_texts(texts=texts, metadatas=metadatas)
    print(f"Indexados {len(chunks)} chunks en '{settings.qdrant_collection_name}'")
    return len(chunks)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m app.ingestion.index <ruta_al_pdf>")
        sys.exit(1)

    asyncio.run(index_pdf(sys.argv[1]))
