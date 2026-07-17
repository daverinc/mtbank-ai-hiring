# core/llm/factory.py
import os
from core.llm.base import LLMClient
from core.llm.groq_client import GroqClient
from core.llm.ollama_client import OllamaClient


def get_llm_client() -> LLMClient:
    """
    Создаёт и возвращает LLM-клиент на основе переменной LLM_PROVIDER.
    Поддерживаемые значения: groq | ollama
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        if not api_key:
            raise ValueError("GROQ_API_KEY не задан в .env")

        return GroqClient(api_key=api_key, model=model)

    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:32b")

        return OllamaClient(base_url=base_url, model=model)

    else:
        raise ValueError(f"Неизвестный LLM_PROVIDER: {provider}. Используй 'groq' или 'ollama'.")
