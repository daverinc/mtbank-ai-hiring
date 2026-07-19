# core/llm/ollama_client.py
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

from core.llm.base import LLMClient

logger = logging.getLogger("llm.ollama")


class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key="ollama")
        self.model = model
        logger.info(f"OllamaClient initialized | model={model}, url={base_url}")

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 500,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        try:
            logger.debug(f"Sending request to Ollama | model={self.model}")

            # Ollama иногда плохо поддерживает response_format,
            # поэтому передаём его только если он явно задан
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = await self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            logger.debug(f"Ollama response received | length={len(content)}")
            return content

        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise