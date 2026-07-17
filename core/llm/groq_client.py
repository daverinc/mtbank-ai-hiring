# core/llm/groq_client.py
from typing import Dict, Any
from groq import AsyncGroq

from core.llm.base import LLMClient


class GroqClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.client = AsyncGroq(api_key=api_key)
        self.model = model

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 500,
        response_format: Dict[str, Any] = None,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )
        return response.choices[0].message.content
