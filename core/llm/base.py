# core/llm/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMClient(ABC):
    """
    Абстрактный базовый класс для LLM-клиентов.
    Все провайдеры (Groq, Ollama, OpenAI и т.д.) должны реализовывать этот интерфейс.
    """

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 500,
        response_format: Dict[str, Any] = None,
    ) -> str:
        """
        Выполняет запрос к LLM и возвращает текст ответа.
        """
        pass
