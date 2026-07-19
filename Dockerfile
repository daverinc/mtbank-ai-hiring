# Dockerfile
FROM python:3.13-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements-api.txt .

# Устанавливаем Python-зависимости
RUN pip install -r requirements-api.txt

# Копируем весь проект
COPY . .

# Порт FastAPI
EXPOSE 8000

# Переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/models

# Запуск FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]