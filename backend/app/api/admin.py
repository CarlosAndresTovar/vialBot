from fastapi import APIRouter, Header, HTTPException, status

from app.config import settings
from app.ingestion.index import index_pdf

router = APIRouter(prefix="/admin", tags=["admin"])


def _verify_admin_key(admin_key: str | None) -> None:
    expected = getattr(settings, "admin_api_key", None)
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ADMIN_API_KEY no configurada",
        )
    if admin_key != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado",
        )


@router.post("/ingest", status_code=202)
async def ingest_pdf(admin_key: str | None = Header(None, alias="X-Admin-Key")) -> dict:
    _verify_admin_key(admin_key)
    count = await index_pdf("data/codigo_nacional_transito.pdf")
    return {"message": f"Indexados {count} chunks"}
