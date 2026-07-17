# test_asr.py
import os
import asyncio
import time
from dotenv import load_dotenv

# === Загружаем .env в самом начале ===
load_dotenv()

# === Устанавливаем HF_HOME до импорта моделей ===
hf_home = os.getenv("HF_HOME")
if hf_home:
    os.environ["HF_HOME"] = hf_home
    print(f"[Config] HF_HOME установлен: {hf_home}")

from asr.transcriber import Transcriber


async def main():
    huggingface_token = os.getenv("HF_TOKEN")
    whisper_model = os.getenv("WHISPER_MODEL", "medium")

    if not huggingface_token:
        print("Ошибка: HF_TOKEN не найден в .env")
        return

    audio_path = "test_data/call_01_dialog.wav"

    if not os.path.exists(audio_path):
        print(f"Ошибка: Файл не найден: {audio_path}")
        return

    print(f"Модель Whisper: {whisper_model}")
    print(f"Аудиофайл: {audio_path}")
    print("Запуск транскрибации и диаризации...\n")

    start_time = time.time()

    transcriber = Transcriber(
        model_size=whisper_model,
        huggingface_token=huggingface_token
    )

    result = await transcriber.run(audio_path)
    elapsed = time.time() - start_time

    print(f"\n=== Результат ASR ({len(result)} сегментов) ===\n")
    for seg in result:
        print(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['speaker']}: {seg['text']}")

    print(f"\nВремя выполнения: {elapsed:.1f} секунд")


if __name__ == "__main__":
    asyncio.run(main())
