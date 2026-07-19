# core/llm/groq_client.py
import logging
from typing import Dict, Any, Optional
from groq import AsyncGroq

from core.llm.base import LLMClient

logger = logging.getLogger("llm.groq")


class GroqClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        logger.info(f"GroqClient initialized with model: {model}")

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 500,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        try:
            logger.debug(f"Sending request to Groq | model={self.model}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
            )
            content = response.choices[0].message.content
            logger.debug(f"Groq response received | length={len(content)}")
            return content

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise