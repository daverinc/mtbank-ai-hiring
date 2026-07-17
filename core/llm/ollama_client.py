# core/llm/ollama_client.py
from typing import Dict, Any
from openai import AsyncOpenAI

from core.llm.base import LLMClient


class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key="ollama")
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
