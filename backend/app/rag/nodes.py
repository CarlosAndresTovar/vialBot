import re

from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.rag.prompts import (
    CHAT_PROMPT,
    CLARIFICATION_PROMPT,
    GREETING_PROMPT,
    INTENT_CLASSIFICATION_PROMPT,
    OUT_OF_CONTEXT_PROMPT,
)
from app.rag.retriever import get_vector_store
from app.rag.state import RAGState

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.google_api_key,
    temperature=0.2,
)

RELEVANCE_THRESHOLD = 0.5
VALID_INTENTS = {"transito", "saludo", "vaga", "fuera_contexto"}


def _clean_answer(text: str) -> str:
    text = text.strip()
    # Elimina bold/italic markdown sin romper palabras
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    # Normaliza asteriscos sueltos al inicio de línea o después de salto a viñetas
    text = re.sub(r"\n\s*\*\s*", "\n- ", text)
    text = re.sub(r"^\s*\*\s*", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"\*\s*\*\s*", " ", text)
    text = re.sub(r"\*{2,}", "", text)
    # Elimina espacios múltiples
    text = re.sub(r"[ \t]+", " ", text)
    # Normaliza saltos de línea excesivos
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_greeting(question: str) -> bool:
    greetings = {
        "hola",
        "buenos dias",
        "buenas tardes",
        "buenas noches",
        "buenas",
        "hey",
        "saludos",
        "que mas",
        "como estas",
        "qué tal",
        "todo bien",
    }
    normalized = re.sub(r"[^\w\s]", "", question.lower().strip())
    return normalized in greetings or any(normalized.startswith(g) for g in greetings)


def _get_history(state: RAGState) -> list:
    return state.get("messages", [])


async def classify_intent_node(state: RAGState) -> dict:
    question = state["question"]

    if _is_greeting(question):
        return {"intent": "saludo"}

    response = await llm.ainvoke(
        INTENT_CLASSIFICATION_PROMPT.format_messages(question=question)
    )
    intent = response.content.strip().lower().split()[0] if response.content else "vaga"
    if intent not in VALID_INTENTS:
        intent = "vaga"
    return {"intent": intent}


async def clarify_node(state: RAGState) -> dict:
    question = state["question"]
    history = _get_history(state) + [HumanMessage(content=question)]
    response = await llm.ainvoke(
        CLARIFICATION_PROMPT.format_messages(question=question, history=history)
    )
    answer = _clean_answer(str(response.content))
    return {
        "answer": answer,
        "messages": history + [AIMessage(content=answer)],
        "fallback": False,
    }


async def retrieve_node(state: RAGState) -> dict:
    question = state["question"]
    messages = _get_history(state) + [HumanMessage(content=question)]

    if state.get("intent") == "saludo":
        return {"context": [], "is_greeting": True, "messages": messages}

    store = get_vector_store()
    results = await store.search(question, k=4)
    return {"context": results, "is_greeting": False, "messages": messages}


async def grade_documents_node(state: RAGState) -> dict:
    if state.get("is_greeting"):
        return {"fallback": False}

    context = state["context"]
    relevant = [doc for doc in context if doc["score"] >= RELEVANCE_THRESHOLD]
    return {"context": relevant, "fallback": len(relevant) == 0}


async def generate_node(state: RAGState) -> dict:
    question = state["question"]
    history = _get_history(state)

    if state.get("is_greeting"):
        response = await llm.ainvoke(
            GREETING_PROMPT.format_messages(question=question, history=history)
        )
        answer = _clean_answer(str(response.content))
        return {
            "answer": answer,
            "messages": history + [AIMessage(content=answer)],
        }

    context = state["context"]
    context_text = "\n\n---\n\n".join(
        f"Fuente: {doc['metadata']}\n{doc['content']}" for doc in context
    )
    response = await llm.ainvoke(
        CHAT_PROMPT.format_messages(
            question=question,
            context=context_text,
            history=history,
        )
    )
    answer = _clean_answer(str(response.content))
    return {
        "answer": answer,
        "messages": history + [AIMessage(content=answer)],
    }


async def fallback_node(state: RAGState) -> dict:
    question = state["question"]
    history = _get_history(state)
    response = await llm.ainvoke(
        OUT_OF_CONTEXT_PROMPT.format_messages(question=question, history=history)
    )
    answer = _clean_answer(str(response.content))
    return {
        "answer": answer,
        "messages": history + [AIMessage(content=answer)],
    }
