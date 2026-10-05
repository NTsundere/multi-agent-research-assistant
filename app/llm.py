from typing import Optional
from langchain_openai import ChatOpenAI
from app.config import settings


def get_llm(temperature: float = 0.0, model: Optional[str] = None) -> ChatOpenAI:
    return ChatOpenAI(
        model=model or settings.ollama_model,
        temperature=temperature,
        base_url="http://localhost:11434/v1",  # OpenAI-совместимый эндпоинт Ollama
        api_key="ollama",  # Ollama не проверяет ключ, но поле обязательно
    )


def get_eval_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.ollama_model,
        temperature=0.0,
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )