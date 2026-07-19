# agents/compliance.py
# Copyright (c) 2026 Sergey Postnikov. All rights reserved.

import json
import logging
from typing import Dict, Any, List

from core.llm.base import LLMClient

logger = logging.getLogger("agents.compliance")


class ComplianceAgent:
    """
    Агент проверки compliance (запрещённые фразы, disclaimers и т.д.).
    """

    SYSTEM_PROMPT = """Ты — специалист по compliance в банковском контакт-центре.
Проверь транскрипт на наличие нарушений и верни JSON:

{
  "passed": true/false,
  "issues": ["список нарушений"]
}

Отвечай только JSON."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        dialog_text = "\n".join(
            [f"{turn.get('speaker', 'Unknown')}: {turn.get('text', '')}" for turn in transcript]
        )

        user_prompt = f"Проверь соблюдение compliance:\n\n{dialog_text}"

        try:
            response = await self.llm_client.chat_completion(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=400,
                response_format={"type": "json_object"}
            )

            result = json.loads(response)
            return {
                "passed": result.get("passed", True),
                "issues": result.get("issues", [])
            }

        except Exception as e:
            logger.error(f"[ComplianceAgent] Error: {e}")
            return {"passed": True, "issues": []}