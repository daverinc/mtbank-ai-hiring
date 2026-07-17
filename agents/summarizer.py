# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

import json
from typing import Dict, Any, List
from groq import AsyncGroq


class SummarizerAgent:
    """
    Агент суммаризации.
    Формирует краткое резюме и список action items.
    """

    SYSTEM_PROMPT = """Ты — аналитик контакт-центра.
Сделай краткое резюме разговора и выдели action items.

Верни JSON:
{
  "summary": "Краткое резюме в 3-5 предложениях",
  "action_items": ["список действий"]
}

Отвечай только JSON."""

    def __init__(self, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        dialog_text = "\n".join(
            [f"{turn.get('speaker', 'Unknown')}: {turn.get('text', '')}" for turn in transcript]
        )

        user_prompt = f"Сделай резюме и action items:\n\n{dialog_text}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return {
                "summary": result.get("summary", ""),
                "action_items": result.get("action_items", [])
            }

        except Exception as e:
            print(f"[SummarizerAgent] Error: {e}")
            return {"summary": "", "action_items": []}
