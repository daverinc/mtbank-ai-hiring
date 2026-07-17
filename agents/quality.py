# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from typing import Dict, Any, List


class QualityAgent:
    """
    Агент оценки качества обслуживания.
    Проверяет соблюдение чек-листа оператора.
    """

    def __init__(self, groq_api_key: str, model: str):
        self.groq_api_key = groq_api_key
        self.model = model

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Оценивает качество обслуживания по чек-листу.
        """
        # TODO: Реализовать промпт и вызов LLM
        return {
            "total": 78,
            "checklist": {
                "greeting": True,
                "need_detection": True,
                "solution_provided": True,
                "farewell": False
            }
        }

