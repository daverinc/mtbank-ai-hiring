import os
import logging
from dotenv import load_dotenv

from core.llm.base import LLMClient
from core.llm.groq_client import GroqClient
from core.llm.ollama_client import OllamaClient

load_dotenv()

logger = logging.getLogger("llm.factory")


def get_llm_client() -> LLMClient:
    """
    Создаёт и возвращает LLM-клиент на основе переменной LLM_PROVIDER.
    Поддерживаемые значения: groq | ollama
    """
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    logger.info(f"Initializing LLM client with provider: {provider}")

    # === Универсальное чтение модели ===
    model = os.getenv("LLM_MODEL") or os.getenv("GROQ_MODEL")

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY не задан в .env")

        if not model:
            model = "llama-3.3-70b-versatile"

        logger.info(f"Using Groq model: {model}")
        return GroqClient(api_key=api_key, model=model)

    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

        logger.info(f"Using Ollama model: {ollama_model} at {base_url}")
        return OllamaClient(base_url=base_url, model=ollama_model)

    else:
        raise ValueError(f"Неизвестный LLM_PROVIDER: {provider}. Используй 'groq' или 'ollama'.")