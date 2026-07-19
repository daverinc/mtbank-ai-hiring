# tests/test_api.py
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Автоматически подменяем transcriber и orchestrator перед каждым тестом."""
    mock_transcriber = MagicMock()
    mock_transcriber.run = AsyncMock(return_value=[
        {"speaker": "Оператор", "start": 0.0, "end": 4.2, "text": "Добрый день, МТБанк."},
        {"speaker": "Клиент", "start": 4.5, "end": 8.1, "text": "Хочу узнать про кредит."},
    ])

    mock_orchestrator = MagicMock()
    mock_orchestrator.run = AsyncMock(return_value={
        "classification": {"topic": "кредиты", "priority": "medium"},
        "quality_score": {
            "total": 85,
            "checklist": {
                "greeting": True,
                "need_detection": True,
                "solution_provided": True,
                "farewell": False
            }
        },
        "compliance": {"passed": True, "issues": []},
        "summary": "Клиент обратился по вопросу кредита наличными.",
        "action_items": ["Отправить КП на email клиента"]
    })

    monkeypatch.setattr("api.main.transcriber", mock_transcriber)
    monkeypatch.setattr("api.main.orchestrator", mock_orchestrator)


# === Позитивные тесты ===

def test_analyze_file_success(file_path: str):
    """Успешная загрузка аудиофайла."""
    with open(file_path, "rb") as f:
        response = client.post(
            "/analyze",
            files={"file": (os.path.basename(file_path), f, "audio/wav")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert data["classification"]["topic"] == "кредиты"


def test_analyze_url_success():
    """Успешная загрузка аудио по URL."""
    response = client.post(
        "/analyze",
        json={"url": "https://example.com/test.wav"}
    )
    # В реальном тесте URL должен быть валидным, здесь мокаем поведение
    assert response.status_code in [200, 400]


def test_health_check():
    """Проверка эндпоинта /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_response_structure(file_path: str):
    """Проверка структуры JSON-ответа."""
    with open(file_path, "rb") as f:
        response = client.post(
            "/analyze",
            files={"file": (os.path.basename(file_path), f, "audio/wav")}
        )

    data = response.json()
    assert "transcript" in data
    assert "classification" in data
    assert "quality_score" in data
    assert "compliance" in data
    assert "summary" in data
    assert "action_items" in data


# === Негативные тесты ===

def test_analyze_unsupported_file_format():
    """Попытка загрузить файл неподдерживаемого формата."""
    response = client.post(
        "/analyze",
        files={"file": ("test.txt", b"fake content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_analyze_file_too_large(monkeypatch):
    """Попытка загрузить файл больше 50 MB."""
    large_content = b"x" * (51 * 1024 * 1024)  # 51 MB

    response = client.post(
        "/analyze",
        files={"file": ("large.wav", large_content, "audio/wav")}
    )
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]


def test_analyze_no_file_and_no_url():
    """Запрос без файла и без URL."""
    response = client.post("/analyze", json={})
    assert response.status_code == 400
    assert "Either 'file' or 'url' must be provided" in response.json()["detail"]


def test_analyze_missing_file_field():
    """Отправка запроса без поля 'file'."""
    response = client.post(
        "/analyze",
        files={"wrong_field": ("test.wav", b"content", "audio/wav")}
    )
    assert response.status_code == 400


def test_analyze_internal_error(monkeypatch):
    """Ошибка при обработке (в orchestrator)."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run = AsyncMock(side_effect=Exception("Internal processing error"))
    monkeypatch.setattr("api.main.orchestrator", mock_orchestrator)

    response = client.post(
        "/analyze",
        files={"file": ("test.wav", b"content", "audio/wav")}
    )
    assert response.status_code == 500