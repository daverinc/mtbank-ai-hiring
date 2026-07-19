# tests/test_classifier.py
import pytest
from agents.classifier import ClassifierAgent


@pytest.mark.asyncio
async def test_classifier_agent_returns_valid_structure(mock_llm_client):
    agent = ClassifierAgent(llm_client=mock_llm_client)
    transcript = [{"speaker": "Клиент", "text": "Хочу кредит"}]
    result = await agent.run(transcript)

    assert "topic" in result
    assert "priority" in result


@pytest.mark.asyncio
async def test_classifier_agent_handles_empty_transcript(mock_llm_client):
    agent = ClassifierAgent(llm_client=mock_llm_client)
    result = await agent.run([])
    assert "topic" in result
    assert "priority" in result


# === Негативные тесты ===

@pytest.mark.asyncio
async def test_classifier_handles_llm_error(mock_llm_client):
    """Ошибка при обращении к LLM."""
    mock_llm_client.chat_completion.side_effect = Exception("LLM connection error")
    agent = ClassifierAgent(llm_client=mock_llm_client)
    result = await agent.run([{"speaker": "Клиент", "text": "Привет"}])

    assert result["topic"] == "другое"
    assert result["priority"] == "medium"


@pytest.mark.asyncio
async def test_classifier_handles_invalid_json(mock_llm_client):
    """LLM вернул невалидный JSON."""
    mock_llm_client.chat_completion.return_value = "not a json"
    agent = ClassifierAgent(llm_client=mock_llm_client)
    result = await agent.run([{"speaker": "Клиент", "text": "test"}])

    assert result["topic"] == "другое"
    assert result["priority"] == "medium"
