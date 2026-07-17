# test_api.py
import requests
import json
import os
from datetime import datetime

API_URL = "http://localhost:8000"
RESULTS_DIR = "test_results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def save_result(filename: str, data: dict):
    """Сохраняет результат анализа в JSON-файл."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(filename))[0]
    output_path = os.path.join(RESULTS_DIR, f"{base_name}_{timestamp}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Результат сохранён: {output_path}\n")
    return output_path


def test_health():
    print("=== Тест Health Check ===")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Ошибка: {e}\n")


def test_analyze_file(file_path: str):
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

            # Сохраняем результат
            save_result(file_path, result)

        else:
            print(f"Ошибка: {response.text}")

    except Exception as e:
        print(f"Ошибка запроса: {e}")

    print()


if __name__ == "__main__":
    test_health()
    test_analyze_file("test_data/call_01_dialog.wav")