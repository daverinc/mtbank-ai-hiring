# tests/conftest.py
import pytest
import os
from unittest.mock import AsyncMock, MagicMock

from core.llm.base import LLMClient


@pytest.fixture
def mock_llm_client():
    """
    Фикстура, возвращающая мок LLM-клиента.
    Все методы LLM-клиента (chat_completion) замоканы.
    """
    mock_client = MagicMock(spec=LLMClient)
    mock_client.chat_completion = AsyncMock(return_value='{"topic": "кредиты", "priority": "medium"}')
    return mock_client

@pytest.fixture
def file_path():
    """Возвращает путь к тестовому аудиофайлу."""
    path = "test_data/call_01_dialog.wav"
    
    if not os.path.exists(path):
        pytest.skip(f"Тестовый файл не найден: {path}")
    
    return path