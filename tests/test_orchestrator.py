# tests/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from multiagent.orchestrator import AgentOrchestrator

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


@pytest.mark.asyncio
async def test_orchestrator_runs_all_agents(mock_llm_client, mock_agents):
    """Проверяем, что AgentOrchestrator последовательно вызывает всех 4 агентов."""
    mock_classifier, mock_quality, mock_compliance, mock_summarizer = mock_agents

    orchestrator = AgentOrchestrator(llm_client=mock_llm_client)

    # Подменяем реальные агенты на моки
    orchestrator.classifier = mock_classifier
    orchestrator.quality = mock_quality
    orchestrator.compliance = mock_compliance
    orchestrator.summarizer = mock_summarizer

    transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк."},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Хочу узнать про кредит."},
    ]

    result = await orchestrator.run(transcript)

    # Проверяем, что все агенты были вызваны
    mock_classifier.run.assert_awaited_once()
    mock_quality.run.assert_awaited_once()
    mock_compliance.run.assert_awaited_once()
    mock_summarizer.run.assert_awaited_once()

    # Проверяем структуру итогового результата
    assert "classification" in result
    assert "quality_score" in result
    assert "compliance" in result
    assert "summary" in result
    assert "action_items" in result

    assert result["classification"]["topic"] == "кредиты"
    assert result["quality_score"]["total"] == 85
    assert result["compliance"]["passed"] is True