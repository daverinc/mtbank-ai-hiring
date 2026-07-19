# tests/test_quality.py
import pytest
from agents.quality import QualityAgent


@pytest.mark.asyncio
async def test_quality_agent_returns_valid_structure(mock_llm_client):
    """Проверяем, что QualityAgent возвращает корректную структуру ответа."""
    # Переопределяем возвращаемое значение мока под QualityAgent
    mock_llm_client.chat_completion.return_value = '''
    {
        "total": 85,
        "checklist": {
            "greeting": true,
            "need_detection": true,
            "solution_provided": true,
            "farewell": false
        }
    }
    '''

    agent = QualityAgent(llm_client=mock_llm_client)

    transcript = [
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк."},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Хочу узнать про кредит."},
    ]

    result = await agent.run(transcript)

    assert isinstance(result, dict)
    assert "total" in result
    assert "checklist" in result
    assert isinstance(result["checklist"], dict)
    assert result["total"] == 85


@pytest.mark.asyncio
async def test_quality_agent_returns_default_on_error(mock_llm_client):
    """Проверяем, что при ошибке возвращаются дефолтные значения."""
    mock_llm_client.chat_completion.side_effect = Exception("LLM error")

    agent = QualityAgent(llm_client=mock_llm_client)

    result = await agent.run([])

    assert result["total"] == 60
    assert result["checklist"] == {}