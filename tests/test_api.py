# tests/test_api.py
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Автоматически подменяем transcriber и orchestrator."""
    mock_transcriber = MagicMock()
    mock_transcriber.run = AsyncMock(return_value=[
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк."},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Хочу узнать про кредит."},
    ])

    mock_orchestrator = MagicMock()
    mock_orchestrator.run = AsyncMock(return_value={
        "classification": {"topic": "кредиты", "priority": "medium"},
        "quality_score": {"total": 85, "checklist": {}},
        "compliance": {"passed": True, "issues": []},
        "summary": "Клиент обратился по вопросу кредита.",
        "action_items": ["Отправить информацию на email"]
    })

    monkeypatch.setattr("api.main.transcriber", mock_transcriber)
    monkeypatch.setattr("api.main.orchestrator", mock_orchestrator)


# === Позитивные тесты ===

def test_analyze_file(file_path: str):
    """Тест отправки аудиофайла."""
    with open(file_path, "rb") as f:
        response = client.post(
            "/analyze",
            files={"file": (os.path.basename(file_path), f, "audio/wav")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert data["classification"]["topic"] == "кредиты"


def test_health_check():
    """Проверка эндпоинта /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# === Негативные тесты ===

def test_analyze_unsupported_file_format():
    """Тест: неподдерживаемый формат файла."""
    response = client.post(
        "/analyze",
        files={"file": ("test.txt", b"fake content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_analyze_file_too_large(monkeypatch):
    """Тест: файл больше 50 MB."""
    large_content = b"x" * (51 * 1024 * 1024)  # 51 MB

    response = client.post(
        "/analyze",
        files={"file": ("large.wav", large_content, "audio/wav")}
    )
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]


def test_analyze_no_file_and_no_url():
    """Тест: запрос без файла и без URL."""
    response = client.post("/analyze", json={})
    assert response.status_code == 400
    assert "Either 'file' or 'url' must be provided" in response.json()["detail"]
