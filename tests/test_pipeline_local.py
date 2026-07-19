# tests/test_pipeline_local.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pipeline import Pipeline


@pytest.mark.asyncio
async def test_pipeline_initialization():
    """Проверяем, что Pipeline корректно инициализируется."""
    pipeline = Pipeline()

    assert pipeline.transcriber is None
    assert pipeline.orchestrator is None
    assert pipeline.valves is not None


@pytest.mark.asyncio
async def test_pipeline_pipe_without_initialization():
    """Проверяем поведение, если on_startup не был вызван."""
    pipeline = Pipeline()

    body = {
        "messages": [
            {"role": "user", "content": "Проанализируй звонок"}
        ]
    }

    result = await pipeline.pipe(body)
    assert "Pipeline не инициализирован" in result


@pytest.mark.asyncio
@patch("pipeline.os.path.exists", return_value=True)
@patch("pipeline.Transcriber")
@patch("pipeline.AgentOrchestrator")
async def test_pipeline_pipe_success(mock_orchestrator, mock_transcriber, mock_exists):
    """Проверяем успешный запуск pipe() с моками."""
    pipeline = Pipeline()

    # Мокаем Transcriber
    mock_transcriber_instance = MagicMock()
    mock_transcriber_instance.run = AsyncMock(return_value=[
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк."},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Хочу узнать про кредит."},
    ])
    mock_transcriber.return_value = mock_transcriber_instance

    # Мокаем Orchestrator
    mock_orchestrator_instance = MagicMock()
    mock_orchestrator_instance.run = AsyncMock(return_value={
        "classification": {"topic": "кредиты", "priority": "medium"},
        "quality_score": {"total": 85, "checklist": {}},
        "compliance": {"passed": True, "issues": []},
        "summary": "Клиент обратился по вопросу кредита.",
        "action_items": ["Отправить КП на email"]
    })
    mock_orchestrator.return_value = mock_orchestrator_instance

    # Инициализируем Pipeline
    await pipeline.on_startup()

    body = {
        "messages": [
            {"role": "user", "content": "Проанализируй звонок"}
        ],
        "files": [
            {"path": "/tmp/test_audio.wav"}
        ]
    }

    result = await pipeline.pipe(body)

    assert "Результат анализа звонка" in result
    assert "кредиты" in result
    assert "Отправить КП на email" in result


@pytest.mark.asyncio
async def test_pipeline_pipe_no_audio_source():
    """Проверяем поведение, когда аудиофайл не найден."""
    pipeline = Pipeline()
    await pipeline.on_startup()

    body = {
        "messages": [
            {"role": "user", "content": "Проанализируй звонок"}
        ]
    }

    result = await pipeline.pipe(body)
    assert "не удалось получить аудиофайл" in result