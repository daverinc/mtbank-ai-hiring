# tests/test_classifier.py
import pytest
from agents.classifier import ClassifierAgent


@pytest.mark.asyncio
async def test_classifier_agent_returns_valid_structure(mock_llm_client):
    """Проверяем, что ClassifierAgent возвращает корректную структуру ответа."""
    agent = ClassifierAgent(llm_client=mock_llm_client)

    transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк."},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Хочу узнать про кредит."},
    ]

    result = await agent.run(transcript)

    assert isinstance(result, dict)
    assert "topic" in result
    assert "priority" in result
    assert result["topic"] == "кредиты"
    assert result["priority"] == "medium"


@pytest.mark.asyncio
async def test_classifier_agent_handles_empty_transcript(mock_llm_client):
    """Проверяем поведение при пустом транскрипте."""
    agent = ClassifierAgent(llm_client=mock_llm_client)

    result = await agent.run([])

    assert "topic" in result
    assert "priority" in result