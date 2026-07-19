# Makefile

.PHONY: up down restart build logs clean test test-cov coverage clean-cov

# === Docker ===

up:
 docker compose up -d

down:
 docker compose down

restart: down up

build:
 docker compose build --no-cache

logs:
 docker compose logs -f api

logs-ollama:
 docker compose logs -f ollama

logs-webui:
 docker compose logs -f openwebui

clean:
 docker compose down -v

create-volume:
 docker volume create rag_ollama_data


# === Тесты ===

# Запуск всех тестов
test:
 pytest -v

# Запуск тестов с покрытием (терминальный отчёт)
test-cov:
 pytest --cov=. --cov-report=term-missing

# Запуск тестов с генерацией HTML-отчёта покрытия
coverage:
 pytest --cov=. --cov-report=html:htmlcov --cov-report=term-missing

# Очистка отчётов покрытия
clean-cov:
 rm -rf htmlcov .coverage


# === Полезные команды ===

# Запуск только unit-тестов на агентов
test-agents:
 pytest tests/test_classifier.py tests/test_quality.py tests/test_compliance.py tests/test_summarizer.py -v

# Запуск интеграционных тестов
test-integration:
 pytest tests/test_orchestrator.py tests/test_api.py -v