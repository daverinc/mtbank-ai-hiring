# generate_dialog.py
import asyncio
import os
import shutil
from typing import List, Tuple
from pydub import AudioSegment
import edge_tts

# === Конфигурация ===
OUTPUT_DIR = "test_data"
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp_tts")
DIALOG_FILE = "docs/sample-dialog.md"   # Можно вынести диалог сюда

OPERATOR_VOICE = "ru-RU-SvetlanaNeural"
CLIENT_VOICE = "ru-RU-DmitryNeural"
PAUSE_MS = 650                          # пауза между репликами
OUTPUT_FILENAME = "call_01_dialog.wav"
TARGET_SAMPLE_RATE = 16000              # 16kHz — оптимально для Whisper


# === Диалог (можно вынести в отдельный файл) ===
DIALOG: List[Tuple[str, str]] = [
    ("operator", "Добрый день, МТБанк, меня зовут Анна, чем могу помочь?"),
    ("client", "Здравствуйте. Хочу узнать про условия по кредиту наличными."),
    ("operator", "Конечно, подскажите, пожалуйста, какая сумма вас интересует и на какой срок?"),
    ("client", "Примерно десять тысяч рублей, на год."),
    ("operator", "Отлично. На данный момент ставка от четырнадцати и девяти процентов годовых, решение за пятнадцать минут. Вы уже являетесь клиентом МТБанка?"),
    ("client", "Да, у меня есть карточка ваша."),
    ("operator", "Прекрасно, тогда для вас действуют специальные условия. Ежемесячный платёж составит около девятисот рублей. Вам удобно подать заявку онлайн через приложение или предпочитаете приехать в отделение?"),
    ("client", "Лучше онлайн. Но у меня вопрос — если я захочу досрочно погасить, есть штрафы?"),
    ("operator", "Нет, досрочное погашение без штрафов и комиссий, в любое время и в любом объёме."),
    ("client", "Хорошо, а страховка обязательна?"),
    ("operator", "Страхование жизни подключается по вашему желанию, это не обязательное условие получения кредита. Однако при подключении страховки ставка может быть немного снижена."),
    ("client", "Понятно. Тогда я попробую подать через приложение."),
    ("operator", "Отлично. Если возникнут вопросы в процессе заполнения — звоните, мы поможем. Также могу отправить вам краткую инструкцию на email, если хотите."),
    ("client", "Да, пожалуйста, отправьте."),
    ("operator", "Хорошо, подскажите ваш email."),
    ("client", "Михаил-собака-пример-точка-бай."),
    ("operator", "Записала. В течение нескольких минут получите письмо с инструкцией и ссылкой на заявку. Есть ещё вопросы?"),
    ("client", "Нет, всё понятно, спасибо."),
    ("operator", "Спасибо за обращение в МТБанк, хорошего дня!"),
    ("client", "И вам, до свидания."),
]


def ensure_directories():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)


async def generate_speech(text: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def generate_all_audio(dialog: List[Tuple[str, str]]) -> List[str]:
    """Генерирует все аудиофайлы и возвращает пути к ним."""
    file_paths = []
    for i, (role, text) in enumerate(dialog):
        voice = OPERATOR_VOICE if role == "operator" else CLIENT_VOICE
        filename = f"{role}_{i:02d}.mp3"
        filepath = os.path.join(TEMP_DIR, filename)

        await generate_speech(text, voice, filepath)
        file_paths.append(filepath)
        print(f"  [{i+1}/{len(dialog)}] {role}: {text[:60]}...")

    return file_paths


def merge_audio(files: List[str], output_path: str):
    """Склеивает аудио с паузами."""
    print("\nСклейка аудио с паузами...")
    pause = AudioSegment.silent(duration=PAUSE_MS)
    final_audio = AudioSegment.empty()

    for filepath in files:
        segment = AudioSegment.from_mp3(filepath)
        final_audio += segment + pause

    # Приводим к 16kHz mono (лучше для Whisper)
    final_audio = final_audio.set_frame_rate(TARGET_SAMPLE_RATE).set_channels(1)
    final_audio.export(output_path, format="wav")

    return len(final_audio) / 1000


def cleanup_temp_files():
    """Удаляет временные MP3 файлы."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        print(f"Временные файлы удалены: {TEMP_DIR}")


async def main():
    ensure_directories()

    print("=== Генерация тестового диалога ===\n")
    print(f"Голос оператора: {OPERATOR_VOICE}")
    print(f"Голос клиента:   {CLIENT_VOICE}")
    print(f"Пауза между репликами: {PAUSE_MS} мс\n")

    # 1. Генерация аудио
    print("Генерация речи...")
    audio_files = await generate_all_audio(DIALOG)

    # 2. Склейка
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    duration = merge_audio(audio_files, output_path)

    # 3. Очистка
    cleanup_temp_files()

    print(f"\n✅ Готово!")
    print(f"   Файл: {output_path}")
    print(f"   Длительность: {duration:.1f} секунд")
    print(f"   Реплик: {len(DIALOG)}")


if __name__ == "__main__":
    asyncio.run(main())
