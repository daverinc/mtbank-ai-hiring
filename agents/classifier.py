# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

import json
from typing import Dict, Any, List

from core.llm.base import LLMClient


class ClassifierAgent:
    """
    Агент классификации обращений.
    """

    SYSTEM_PROMPT = """Ты — опытный аналитик контакт-центра МТБанка.
Твоя задача — классифицировать обращение клиента по транскрипту разговора.

Верни JSON строго в формате:
{
  "topic": "кредиты | карты | переводы | жалобы | другое",
  "priority": "low | medium | high"
}

Отвечай только JSON."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        dialog_text = "\n".join(
            [f"{turn.get('speaker', 'Unknown')}: {turn.get('text', '')}" for turn in transcript]
        )

        user_prompt = f"Проанализируй следующий диалог и верни JSON:\n\n{dialog_text}"

        try:
            response = await self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            result = json.loads(response)
            return {
                "topic": result.get("topic", "другое"),
                "priority": result.get("priority", "medium")
            }

        except Exception as e:
            print(f"[ClassifierAgent] Error: {e}")
            return {"topic": "другое", "priority": "medium"}
