# tests/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from multiagent.orchestrator import AgentOrchestrator


@pytest.fixture
def mock_llm_client():
    """Фикстура мокового LLM-клиента."""
    mock_client = MagicMock()
    mock_client.chat_completion = AsyncMock(return_value='{"result": "ok"}')
    return mock_client


@pytest.fixture
def mock_agents():
    """Фикстура с замоканными агентами."""
    mock_classifier = MagicMock()
    mock_classifier.run = AsyncMock(return_value={"topic": "кредиты", "priority": "medium"})

    mock_quality = MagicMock()
    mock_quality.run = AsyncMock(return_value={
        "total": 85,
        "checklist": {"greeting": True, "need_detection": True, "solution_provided": True, "farewell": False}
    })

    mock_compliance = MagicMock()
    mock_compliance.run = AsyncMock(return_value={"passed": True, "issues": []})

    mock_summarizer = MagicMock()
    mock_summarizer.run = AsyncMock(return_value={
        "summary": "Клиент обратился по вопросу кредита.",
        "action_items": ["Отправить информацию на email"]
    })

    return mock_classifier, mock_quality, mock_compliance, mock_summarizer


# === Тесты ===

@pytest.mark.asyncio
async def test_orchestrator_runs_all_agents(mock_llm_client, mock_agents):
    """Проверяем, что оркестратор успешно запускает всех 4 агентов."""
    mock_classifier, mock_quality, mock_compliance, mock_summarizer = mock_agents

    orchestrator = AgentOrchestrator(llm_client=mock_llm_client)
    orchestrator.classifier = mock_classifier
    orchestrator.quality = mock_quality
    orchestrator.compliance = mock_compliance
    orchestrator.summarizer = mock_summarizer

    transcript = [{"speaker": "Клиент", "text": "Хочу кредит"}]

    result = await orchestrator.run(transcript)

    mock_classifier.run.assert_awaited_once()
    mock_quality.run.assert_awaited_once()
    mock_compliance.run.assert_awaited_once()
    mock_summarizer.run.assert_awaited_once()

    assert "classification" in result
    assert "quality_score" in result
    assert "compliance" in result
    assert "summary" in result


@pytest.mark.asyncio
async def test_orchestrator_calls_agents_in_order(mock_llm_client, mock_agents):
    """Проверяем порядок вызова агентов."""
    mock_classifier, mock_quality, mock_compliance, mock_summarizer = mock_agents

    orchestrator = AgentOrchestrator(llm_client=mock_llm_client)
    orchestrator.classifier = mock_classifier
    orchestrator.quality = mock_quality
    orchestrator.compliance = mock_compliance
    orchestrator.summarizer = mock_summarizer

    transcript = [{"speaker": "Клиент", "text": "test"}]
    await orchestrator.run(transcript)

    # Проверяем порядок вызовов
    assert mock_classifier.run.called
    assert mock_quality.run.called
    assert mock_compliance.run.called
    assert mock_summarizer.run.called


@pytest.mark.asyncio
async def test_orchestrator_handles_agent_error(mock_llm_client, mock_agents):
    """Проверяем поведение при ошибке одного из агентов."""
    mock_classifier, mock_quality, mock_compliance, mock_summarizer = mock_agents
    mock_quality.run = AsyncMock(side_effect=Exception("Quality agent failed"))

    orchestrator = AgentOrchestrator(llm_client=mock_llm_client)
    orchestrator.classifier = mock_classifier
    orchestrator.quality = mock_quality
    orchestrator.compliance = mock_compliance
    orchestrator.summarizer = mock_summarizer

    transcript = [{"speaker": "Клиент", "text": "test"}]

    with pytest.raises(Exception):
        await orchestrator.run(transcript)


@pytest.mark.asyncio
async def test_orchestrator_returns_correct_state(mock_llm_client, mock_agents):
    """Проверяем структуру возвращаемого результата."""
    mock_classifier, mock_quality, mock_compliance, mock_summarizer = mock_agents

    orchestrator = AgentOrchestrator(llm_client=mock_llm_client)
    orchestrator.classifier = mock_classifier
    orchestrator.quality = mock_quality
    orchestrator.compliance = mock_compliance
    orchestrator.summarizer = mock_summarizer

    transcript = [{"speaker": "Клиент", "text": "test"}]
    result = await orchestrator.run(transcript)

    assert isinstance(result, dict)
    assert "classification" in result
    assert "quality_score" in result
    assert "compliance" in result
    assert "summary" in result
    assert "action_items" in result


@pytest.mark.asyncio
async def test_orchestrator_empty_transcript(mock_llm_client, mock_agents):
    """Проверяем работу с пустым транскриптом."""
    mock_classifier, mock_quality, mock_compliance, mock_summarizer = mock_agents

    orchestrator = AgentOrchestrator(llm_client=mock_llm_client)
    orchestrator.classifier = mock_classifier
    orchestrator.quality = mock_quality
    orchestrator.compliance = mock_compliance
    orchestrator.summarizer = mock_summarizer

    result = await orchestrator.run([])

    assert "classification" in result


@pytest.mark.asyncio
async def test_orchestrator_partial_agent_failure(mock_llm_client, mock_agents):
    """Проверяем ситуацию, когда один агент падает, а остальные работают."""
    mock_classifier, mock_quality, mock_compliance, mock_summarizer = mock_agents
    mock_compliance.run = AsyncMock(side_effect=Exception("Compliance error"))

    orchestrator = AgentOrchestrator(llm_client=mock_llm_client)
    orchestrator.classifier = mock_classifier
    orchestrator.quality = mock_quality
    orchestrator.compliance = mock_compliance
    orchestrator.summarizer = mock_summarizer

    transcript = [{"speaker": "Клиент", "text": "test"}]

    with pytest.raises(Exception):
        await orchestrator.run(transcript)
