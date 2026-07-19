# tests/test_quality.py
import pytest
from agents.quality import QualityAgent


@pytest.mark.asyncio
async def test_quality_agent_returns_valid_structure(mock_llm_client):
    mock_llm_client.chat_completion.return_value = '{"total": 85, "checklist": {"greeting": true}}'
    agent = QualityAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert "total" in result
    assert "checklist" in result


@pytest.mark.asyncio
async def test_quality_agent_returns_default_on_error(mock_llm_client):
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")
    agent = QualityAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["total"] == 60
    assert result["checklist"] == {}


@pytest.mark.asyncio
async def test_quality_agent_handles_llm_error(mock_llm_client):
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")
    agent = QualityAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["total"] == 60
