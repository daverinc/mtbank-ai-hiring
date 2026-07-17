"""
Убедись, что API запущен:
uvicorn api.main:app --reload --port 8000
Запусти тест:
python3 test_api.py

Проверяет /health
Тестирует загрузку файла
Тестирует загрузку по URL (закомментировано)
Красиво выводит результаты
"""
# test_api.py
import requests
import json
import os

API_URL = "http://localhost:8000"


def test_health():
    """Проверка работоспособности API"""
    print("=== Тест Health Check ===")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Ошибка: {e}\n")


def test_analyze_file(file_path: str):
    """Тест анализа аудиофайла"""
    print(f"=== Тест анализа файла: {file_path} ===")

    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}\n")
        return

    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "audio/wav")}
            response = requests.post(f"{API_URL}/analyze", files=files)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("Анализ успешно выполнен!")
            print(f"Транскрипт: {len(result.get('transcript', []))} сегментов")
            print(f"Тема: {result.get('classification', {}).get('topic')}")
            print(f"Приоритет: {result.get('classification', {}).get('priority')}")
            print(f"Качество: {result.get('quality_score', {}).get('total')}")
            print(f"Compliance: {result.get('compliance', {}).get('passed')}")
            print(f"Summary: {result.get('summary', '')[:100]}...")
        else:
            print(f"Ошибка: {response.text}")

    except Exception as e:
        print(f"Ошибка запроса: {e}")

    print()


def test_analyze_url(url: str):
    """Тест анализа по URL"""
    print(f"=== Тест анализа по URL: {url} ===")
    try:
        payload = {"url": url}
        response = requests.post(f"{API_URL}/analyze", json=payload)

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Анализ по URL успешно выполнен!")
            print(f"Транскрипт: {len(result.get('transcript', []))} сегментов")
        else:
            print(f"Ошибка: {response.text}")

    except Exception as e:
        print(f"Ошибка запроса: {e}")

    print()


if __name__ == "__main__":
    # 1. Проверка здоровья
    test_health()

    # 2. Анализ файла
    test_analyze_file("test_data/call_01_dialog.wav")

    # 3. Анализ по URL (раскомментируй, если нужен)
    # test_analyze_url("https://example.com/audio.wav")