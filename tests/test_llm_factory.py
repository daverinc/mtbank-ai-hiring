# tests/test_llm_factory.py
import pytest
from unittest.mock import patch

from core.llm.factory import get_llm_client
from core.llm.groq_client import GroqClient
from core.llm.ollama_client import OllamaClient


def test_factory_returns_groq_client(monkeypatch):
    """Проверяем создание GroqClient с кастомной моделью."""
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test_key_123")
    monkeypatch.setenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    client = get_llm_client()

    assert isinstance(client, GroqClient)
    assert client.model == "llama-3.3-70b-versatile"


def test_factory_returns_ollama_client(monkeypatch):
    """Проверяем создание OllamaClient с кастомной моделью и URL."""
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.1:8b")

    client = get_llm_client()

    assert isinstance(client, OllamaClient)
    assert client.model == "llama3.1:8b"


def test_factory_raises_on_missing_groq_key(monkeypatch):
    """Проверяем ошибку при отсутствии GROQ_API_KEY."""
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError) as exc_info:
        get_llm_client()

    assert "GROQ_API_KEY" in str(exc_info.value)


def test_factory_raises_on_unknown_provider(monkeypatch):
    """Проверяем ошибку при неизвестном провайдере."""
    monkeypatch.setenv("LLM_PROVIDER", "azure")

    with pytest.raises(ValueError) as exc_info:
        get_llm_client()

    assert "Неизвестный LLM_PROVIDER" in str(exc_info.value)


def test_factory_defaults_to_groq(monkeypatch):
    """Проверяем, что по умолчанию используется Groq."""
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "default_key")

    client = get_llm_client()

    assert isinstance(client, GroqClient)


def test_factory_ollama_without_model_uses_default(monkeypatch):
    """Проверяем, что для Ollama используется модель по умолчанию, если она не указана."""
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    client = get_llm_client()

    assert isinstance(client, OllamaClient)
    assert client.model == "qwen2.5:7b"


def test_factory_groq_without_model_uses_default(monkeypatch):
    """Проверяем, что для Groq используется модель по умолчанию, если она не указана."""
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test_key")
    monkeypatch.delenv("GROQ_MODEL", raising=False)

    client = get_llm_client()

    assert isinstance(client, GroqClient)
    assert client.model == "llama-3.3-70b-versatile"