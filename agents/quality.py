# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

import json
from typing import Dict, Any, List
from groq import AsyncGroq


class QualityAgent:
    """
    Агент оценки качества обслуживания.
    Проверяет соблюдение чек-листа оператора.
    """

    SYSTEM_PROMPT = """Ты — эксперт по оценке качества обслуживания в контакт-центре МТБанка.
Твоя задача — оценить качество работы оператора по чек-листу.

Верни JSON строго в следующем формате:
{
  "total": 0-100,
  "checklist": {
    "greeting": true/false,
    "need_detection": true/false,
    "solution_provided": true/false,
    "farewell": true/false
  }
}

Оценивай только по предоставленному транскрипту. Отвечай только JSON."""

    def __init__(self, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        dialog_text = "\n".join(
            [f"{turn.get('speaker', 'Unknown')}: {turn.get('text', '')}" for turn in transcript]
        )

        user_prompt = f"Оцени качество обслуживания по чек-листу:\n\n{dialog_text}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=400,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return {
                "total": result.get("total", 70),
                "checklist": result.get("checklist", {})
            }

        except Exception as e:
            print(f"[QualityAgent] Error: {e}")
            return {"total": 60, "checklist": {}}
