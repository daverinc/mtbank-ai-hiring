# test_classifier.py
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

hf_home = os.getenv("HF_HOME")
if hf_home:
    os.environ["HF_HOME"] = hf_home

from core.llm.factory import get_llm_client
from agents.classifier import ClassifierAgent


async def main():
    llm_client = get_llm_client()
    agent = ClassifierAgent(llm_client)

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
