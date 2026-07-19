# tests/conftest.py
import pytest
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