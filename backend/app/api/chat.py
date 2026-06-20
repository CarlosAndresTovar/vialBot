from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api.rate_limit import limiter
from app.auth.cognito import get_current_user
from app.rag.state import RAGInput

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    thread_id: str | None = Field(
        None,
        description="ID de conversación; si no se envía se crea uno nuevo",
    )


class ChatResponse(BaseModel):
    answer: str
    thread_id: str


def _get_thread_id(body: ChatRequest, user: dict) -> str:
    thread_id = body.thread_id or f"{user['sub']}-default"
    if not thread_id.startswith(user["sub"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes acceder a conversaciones de otro usuario",
        )
    return thread_id


async def _stream_answer(graph, state: RAGInput, thread_id: str):
    async for update in graph.astream(
        state,
        config={"configurable": {"thread_id": thread_id}},
        stream_mode="updates",
    ):
        if not isinstance(update, dict):
            continue
        answer = None
        for node_name in ("generate", "clarify", "fallback"):
            node_update = update.get(node_name)
            if isinstance(node_update, dict) and node_update.get("answer"):
                answer = node_update["answer"]
                break
        if answer:
            yield f"data: {answer}\n\n"
            yield f"event: done\ndata: {thread_id}\n\n"
            return
    yield f"event: done\ndata: {thread_id}\n\n"


@router.post("", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    user: Annotated[dict, Depends(get_current_user)],
) -> ChatResponse:
    thread_id = _get_thread_id(body, user)
    graph = request.app.state.rag_graph
    result = await graph.ainvoke(
        RAGInput(question=body.message),
        config={"configurable": {"thread_id": thread_id}},
    )
    return ChatResponse(answer=result["answer"], thread_id=thread_id)


@router.post("/stream")
@limiter.limit("10/minute")
async def chat_stream(
    request: Request,
    body: ChatRequest,
    user: Annotated[dict, Depends(get_current_user)],
):
    thread_id = _get_thread_id(body, user)
    graph = request.app.state.rag_graph
    return StreamingResponse(
        _stream_answer(graph, RAGInput(question=body.message), thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
