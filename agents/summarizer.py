# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from typing import Dict, Any, List


class SummarizerAgent:
    """
    Агент суммаризации.
    Формирует краткое резюме и список action items.
    """

    def __init__(self, groq_api_key: str, model: str):
        self.groq_api_key = groq_api_key
        self.model = model

    async def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Создаёт саммари и action items.
        """
        # TODO: Реализовать промпт и вызов LLM
        return {
            "summary": "Клиент интересовался условиями кредита наличными.",
            "action_items": ["Отправить инструкцию на email"]
        }
