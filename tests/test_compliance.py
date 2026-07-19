# tests/test_compliance.py
import pytest
from agents.compliance import ComplianceAgent


@pytest.mark.asyncio
async def test_compliance_agent_returns_valid_structure(mock_llm_client):
    mock_llm_client.chat_completion.return_value = '{"passed": true, "issues": []}'
    agent = ComplianceAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert "passed" in result
    assert "issues" in result


@pytest.mark.asyncio
async def test_compliance_agent_detects_issues(mock_llm_client):
    mock_llm_client.chat_completion.return_value = '{"passed": false, "issues": ["Нет disclaimer"]}'
    agent = ComplianceAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["passed"] is False


# === Негативные тесты ===

@pytest.mark.asyncio
async def test_compliance_handles_llm_error(mock_llm_client):
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")
    agent = ComplianceAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["passed"] is True
    assert result["issues"] == []


@pytest.mark.asyncio
async def test_compliance_handles_invalid_json(mock_llm_client):
    mock_llm_client.chat_completion.return_value = "bad json"
    agent = ComplianceAgent(llm_client=mock_llm_client)
    result = await agent.run([])

    assert result["passed"] is True
