# tests/test_summarizer.py
import pytest
from agents.summarizer import SummarizerAgent


@pytest.mark.asyncio
async def test_summarizer_agent_returns_valid_structure(mock_llm_client):
    mock_llm_client.chat_completion.return_value = '''
    {
        "summary": "Клиент обратился по вопросу кредита.",
        "action_items": ["Отправить КП на email"]
    }
    '''
    agent = SummarizerAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert "summary" in result
    assert "action_items" in result
    assert isinstance(result["action_items"], list)


@pytest.mark.asyncio
async def test_summarizer_agent_returns_empty_on_error(mock_llm_client):
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")
    agent = SummarizerAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["summary"] == ""
    assert result["action_items"] == []


@pytest.mark.asyncio
async def test_summarizer_agent_handles_llm_error(mock_llm_client):
    """Негативный тест: обработка ошибки LLM."""
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")
    agent = SummarizerAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["summary"] == ""
    assert result["action_items"] == []