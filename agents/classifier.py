# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

import json
from typing import Dict, Any, List
from groq import AsyncGroq


class ClassifierAgent:
    """
    Агент классификации обращений.
    Определяет тематику и приоритет обращения.
    """

    SYSTEM_PROMPT = """Ты — опытный аналитик контакт-центра МТБанка.
Твоя задача — классифицировать обращение клиента по транскрипту разговора.

Ты должен вернуть JSON-объект строго в следующем формате:
{
  "topic": "кредиты | карты | переводы | жалобы | другое",
  "priority": "low | medium | high"
}

Правила:
- topic должен быть на русском языке и соответствовать одному из предложенных вариантов.
- priority определяется по срочности и эмоциональному состоянию клиента.
- Отвечай только JSON, без лишнего текста."""

    def __init__(self, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Классифицирует обращение на основе транскрипта.
        """
        # Преобразуем транскрипт в текст
        dialog_text = "\n".join(
            [f"{turn.get('speaker', 'Unknown')}: {turn.get('text', '')}" for turn in transcript]
        )

        user_prompt = f"Проанализируй следующий диалог и верни JSON:\n\n{dialog_text}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return {
                "topic": result.get("topic", "другое"),
                "priority": result.get("priority", "medium")
            }

        except Exception as e:
            print(f"[ClassifierAgent] Error: {e}")
            return {"topic": "другое", "priority": "medium"}
