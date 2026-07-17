# test_classifier.py
import asyncio
import os
from dotenv import load_dotenv
from agents.classifier import ClassifierAgent

load_dotenv()

async def main():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")  # значение по умолчанию

    if not api_key:
        print("Ошибка: GROQ_API_KEY не найден в .env")
        return

    print(f"Используется модель: {model}")

    agent = ClassifierAgent(groq_api_key=api_key, model=model)

    # Тестовый транскрипт
    test_transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк, меня зовут Анна, чем могу помочь?"},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Здравствуйте. Хочу узнать про условия по кредиту наличными."},
        {"speaker": "Оператор", "start": 8.5, "end": 15.0, "text": "Конечно, подскажите, пожалуйста, какая сумма вас интересует и на какой срок?"},
        {"speaker": "Клиент", "start": 15.3, "end": 18.0, "text": "Примерно десять тысяч рублей, на год."},
    ]

    result = await agent.run(test_transcript)
    print("\nРезультат классификации:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
