# calculate_wer.py
import os
import warnings
from dotenv import load_dotenv
from jiwer import wer
from faster_whisper import WhisperModel

warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")

load_dotenv()

# === Конфигурация ===
TEST_DATA_DIR = "test_data"
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")
HF_HOME = os.getenv("HF_HOME")

if HF_HOME:
    os.environ["HF_HOME"] = HF_HOME


def load_ground_truth(filepath: str) -> str:
    """Читает эталонный транскрипт и убирает префиксы спикеров."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    text = " ".join(line.split(": ", 1)[-1].strip() for line in lines if ": " in line)
    return text.strip()


def transcribe_audio(audio_path: str, model) -> str:
    """Транскрибирует аудио и возвращает текст."""
    segments, _ = model.transcribe(audio_path, language="ru", vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments)


def main():
    print("=== Подсчёт WER для тестовых файлов ===\n")

    # === Определяем устройство и compute_type ===
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    print(f"Загрузка модели faster-whisper ({WHISPER_MODEL}) на {device} ({compute_type})...")

    model = WhisperModel(
        WHISPER_MODEL,
        device=device,
        compute_type=compute_type
    )
    print("Модель загружена.\n")

    results = []

    # Ищем все wav-файлы
    for filename in sorted(os.listdir(TEST_DATA_DIR)):
        if not filename.endswith(".wav"):
            continue

        audio_path = os.path.join(TEST_DATA_DIR, filename)
        transcript_path = os.path.join(TEST_DATA_DIR, filename.replace(".wav", ".txt"))

        if not os.path.exists(transcript_path):
            print(f"⚠️  Пропущен {filename}: нет эталонного транскрипта")
            continue

        print(f"Обработка: {filename}...")

        # Эталонный текст
        ground_truth = load_ground_truth(transcript_path)

        # Распознанный текст
        hypothesis = transcribe_audio(audio_path, model)

        # Считаем WER
        error_rate = wer(ground_truth, hypothesis) * 100

        results.append({
            "file": filename,
            "wer": round(error_rate, 2),
        })

        print(f"  → WER: {error_rate:.2f}%\n")

    # Вывод таблицы
    print("\n" + "=" * 60)
    print(f"{'Файл':<30} {'WER (%)':<10}")
    print("=" * 60)

    for r in results:
        print(f"{r['file']:<30} {r['wer']:<10}")

    print("=" * 60)

    if results:
        avg_wer = sum(r["wer"] for r in results) / len(results)
        print(f"\nСредний WER: {avg_wer:.2f}%")

if __name__ == "__main__":
    main()
