import re

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.config import settings

_STOPWORDS = {
    "el", "la", "los", "las", "de", "del", "a", "al", "en", "que", "y", "o",
    "un", "una", "unos", "unas", "con", "por", "para", "es", "son", "se", "lo",
    "como", "más", "sin", "sobre", "entre", "su", "sus", "le", "les", "me", "mi",
    "tu", "te", "este", "esta", "esto", "estos", "estas", "ese", "esa", "eso",
    "esos", "esas", "cual", "cuales", "quien", "quienes", "cuando", "donde",
}


def _normalize(text: str) -> set[str]:
    text = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = text.split()
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 2}


class VectorStore:
    def __init__(self) -> None:
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key,
        )
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.store = QdrantVectorStore(
            client=self.client,
            collection_name=settings.qdrant_collection_name,
            embedding=self.embeddings,
        )

    async def search(
        self, query: str, k: int = 8, top_n: int = 4
    ) -> list[dict]:
        docs = await self.store.asimilarity_search_with_score(query, k=k)
        query_terms = _normalize(query)
        scored: list[tuple[float, object, float]] = []
        for doc, similarity in docs:
            doc_terms = _normalize(doc.page_content)
            overlap = (
                len(query_terms & doc_terms) / max(len(query_terms), 1)
                if query_terms
                else 0.0
            )
            combined = 0.7 * float(similarity) + 0.3 * overlap
            scored.append((combined, doc, float(similarity)))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            }
            for _combined, doc, score in scored[:top_n]
        ]


_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
