# tests/test_summarizer.py
import pytest
from agents.summarizer import SummarizerAgent


@pytest.mark.asyncio
async def test_summarizer_agent_returns_valid_structure(mock_llm_client):
    """Проверяем, что SummarizerAgent возвращает корректную структуру ответа."""
    mock_llm_client.chat_completion.return_value = '''
    {
        "summary": "Клиент обратился по вопросу кредита. Оператор предоставил информацию о ставке.",
        "action_items": ["Отправить КП на email клиента"]
    }
    '''

    agent = SummarizerAgent(llm_client=mock_llm_client)

    transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк."},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Хочу узнать про кредит."},
    ]

    result = await agent.run(transcript)

    assert isinstance(result, dict)
    assert "summary" in result
    assert "action_items" in result
    assert isinstance(result["action_items"], list)
    assert len(result["summary"]) > 0


@pytest.mark.asyncio
async def test_summarizer_agent_returns_empty_on_error(mock_llm_client):
    """Проверяем поведение при ошибке."""
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")

    agent = SummarizerAgent(llm_client=mock_llm_client)

    result = await agent.run([])

    assert result["summary"] == ""
    assert result["action_items"] == []