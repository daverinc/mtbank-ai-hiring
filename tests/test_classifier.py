# tests/test_classifier.py
import pytest
from agents.classifier import ClassifierAgent


@pytest.mark.asyncio
async def test_classifier_agent_returns_valid_structure(mock_llm_client):
    agent = ClassifierAgent(llm_client=mock_llm_client)
    transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк."},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Хочу узнать про кредит."},
    ]
    result = await agent.run(transcript)

    assert "topic" in result
    assert "priority" in result
    assert result["topic"] == "кредиты"


@pytest.mark.asyncio
async def test_classifier_agent_handles_empty_transcript(mock_llm_client):
    agent = ClassifierAgent(llm_client=mock_llm_client)
    result = await agent.run([])
    assert "topic" in result
    assert "priority" in result


@pytest.mark.asyncio
async def test_classifier_agent_handles_llm_error(mock_llm_client):
    """Негативный тест: ошибка LLM."""
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")
    agent = ClassifierAgent(llm_client=mock_llm_client)
    result = await agent.run([{"speaker": "Клиент", "text": "Привет"}])

    assert result["topic"] == "другое"
    assert result["priority"] == "medium"
