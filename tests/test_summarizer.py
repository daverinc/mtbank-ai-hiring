# tests/test_summarizer.py
import pytest
from agents.summarizer import SummarizerAgent


@pytest.mark.asyncio
async def test_summarizer_agent_returns_valid_structure(mock_llm_client):
    mock_llm_client.chat_completion.return_value = '{"summary": "test", "action_items": []}'
    agent = SummarizerAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert "summary" in result
    assert "action_items" in result


@pytest.mark.asyncio
async def test_summarizer_agent_returns_empty_on_error(mock_llm_client):
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")
    agent = SummarizerAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["summary"] == ""
    assert result["action_items"] == []


# === Негативные тесты ===

@pytest.mark.asyncio
async def test_summarizer_handles_llm_error(mock_llm_client):
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")
    agent = SummarizerAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["summary"] == ""
    assert result["action_items"] == []


@pytest.mark.asyncio
async def test_summarizer_handles_invalid_json(mock_llm_client):
    mock_llm_client.chat_completion.return_value = "not json"
    agent = SummarizerAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["summary"] == ""
    assert result["action_items"] == []
