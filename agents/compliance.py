# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

import json
from typing import Dict, Any, List
from groq import AsyncGroq


class ComplianceAgent:
    """
    Агент проверки compliance.
    Проверяет запрещённые фразы и обязательные disclaimers.
    """

    SYSTEM_PROMPT = """Ты — специалист по compliance в банковском контакт-центре.
Проверь транскрипт на наличие нарушений.

Верни JSON:
{
  "passed": true/false,
  "issues": ["список нарушений"]
}

Проверяй:
- Запрещённые фразы
- Отсутствие обязательных disclaimers
- Некорректные обещания или гарантии

Отвечай только JSON."""

    def __init__(self, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        dialog_text = "\n".join(
            [f"{turn.get('speaker', 'Unknown')}: {turn.get('text', '')}" for turn in transcript]
        )

        user_prompt = f"Проверь соблюдение compliance:\n\n{dialog_text}"

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
                "passed": result.get("passed", True),
                "issues": result.get("issues", [])
            }

        except Exception as e:
            print(f"[ComplianceAgent] Error: {e}")
            return {"passed": True, "issues": []}
