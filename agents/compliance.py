# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from typing import Dict, Any, List


class ComplianceAgent:
    """
    Агент проверки compliance.
    Проверяет запрещённые фразы, disclaimers и корректность.
    """

    def __init__(self, groq_api_key: str, model: str):
        self.groq_api_key = groq_api_key
        self.model = model

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Проверяет соблюдение compliance-требований.
        """
        # TODO: Реализовать промпт и вызов LLM
        return {
            "passed": True,
            "issues": []
        }
