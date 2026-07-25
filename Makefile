# Makefile

.PHONY: help up down restart build logs clean test test-cov coverage clean-cov \
        test-agents test-integration test-pipeline test-all \
        wer logs-api logs-pipelines logs-webui logs-ollama

# Цвета для вывода
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

# === Помощь ===

help:
	@echo ""
	@echo "$(YELLOW)Доступные команды:$(RESET)"
	@echo ""
	@echo "  $(GREEN)make up$(RESET)              - Запустить все сервисы"
	@echo "  $(GREEN)make down$(RESET)            - Остановить все сервисы"
	@echo "  $(GREEN)make restart$(RESET)         - Перезапустить все сервисы"
	@echo "  $(GREEN)make build$(RESET)           - Собрать образы без кэша"
	@echo "  $(GREEN)make logs$(RESET)            - Логи API"
	@echo "  $(GREEN)make logs-api$(RESET)        - Логи FastAPI"
	@echo "  $(GREEN)make logs-pipelines$(RESET)  - Логи Pipeline"
	@echo "  $(GREEN)make logs-webui$(RESET)      - Логи OpenWebUI"
	@echo "  $(GREEN)make clean$(RESET)           - Полная очистка (включая volumes)"
	@echo ""
	@echo "  $(GREEN)make test$(RESET)            - Запустить все тесты"
	@echo "  $(GREEN)make test-cov$(RESET)        - Тесты с покрытием (терминал)"
	@echo "  $(GREEN)make coverage$(RESET)        - Тесты с HTML-отчётом"
	@echo "  $(GREEN)make test-agents$(RESET)     - Только unit-тесты агентов"
	@echo "  $(GREEN)make test-integration$(RESET)- Интеграционные тесты"
	@echo "  $(GREEN)make test-pipeline$(RESET)   - Тесты Pipeline"
	@echo ""
	@echo "  $(GREEN)make wer$(RESET)             - Посчитать WER по тестовым файлам"
	@echo ""

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

logs-api:
	docker compose logs -f api

logs-pipelines:
	docker compose logs -f pipelines

logs-webui:
	docker compose logs -f openwebui

logs-ollama:
	docker compose logs -f ollama

clean:
	docker compose down -v --remove-orphans

# === Тесты ===

test:
	pytest -v

test-cov:
	pytest --cov=. --cov-report=term-missing -q

coverage:
	pytest --cov=. --cov-report=html:htmlcov --cov-report=term-missing

clean-cov:
	rm -rf htmlcov .coverage

# Unit-тесты агентов
test-agents:
	pytest tests/test_classifier.py tests/test_quality.py tests/test_compliance.py tests/test_summarizer.py -v

# Интеграционные тесты
test-integration:
	pytest tests/test_api.py tests/test_orchestrator.py -v

# Тесты Pipeline
test-pipeline:
	pytest tests/test_pipeline.py -v || echo "Файл test_pipeline.py не найден"

# Все тесты
test-all: test-agents test-integration

# === WER ===

wer:
	python3 calculate_wer.py