from typing import TypedDict

from langchain_core.messages import BaseMessage


class RAGInput(TypedDict):
    question: str


class RAGState(TypedDict):
    question: str
    context: list[dict]
    answer: str
    fallback: bool
    is_greeting: bool
    intent: str | None
    clarification: str | None
    messages: list[BaseMessage]
