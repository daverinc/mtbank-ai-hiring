# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.
# test_orchestrator.py
import asyncio
import os
from dotenv import load_dotenv
from pipeline.orchestrator import AgentOrchestrator

load_dotenv()

async def main():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        print("Ошибка: GROQ_API_KEY не найден в .env")
        return

    print(f"Используется модель: {model}")
    print("Запуск оркестратора с 4 агентами...\n")

    orchestrator = AgentOrchestrator(groq_api_key=api_key, llm_model=model)

    # Тестовый транскрипт
    test_transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк, меня зовут Анна, чем могу помочь?"},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Здравствуйте. Хочу узнать про условия по кредиту наличными."},
        {"speaker": "Оператор", "start": 8.5, "end": 15.0, "text": "Конечно, подскажите, пожалуйста, какая сумма вас интересует и на какой срок?"},
        {"speaker": "Клиент", "start": 15.3, "end": 18.0, "text": "Примерно десять тысяч рублей, на год."},
        {"speaker": "Оператор", "start": 18.5, "end": 25.0, "text": "Отлично. На данный момент ставка от 14.9% годовых, решение за 15 минут."},
        {"speaker": "Клиент", "start": 25.5, "end": 28.0, "text": "Хорошо, тогда я попробую подать через приложение."},
        {"speaker": "Оператор", "start": 28.5, "end": 33.0, "text": "Спасибо за обращение в МТБанк, хорошего дня!"},
    ]

    result = await orchestrator.run(test_transcript)

    print("=== Результат работы оркестратора ===\n")
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
