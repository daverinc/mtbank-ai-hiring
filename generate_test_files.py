# generate_test_files.py
import os
from pydub import AudioSegment
import edge_tts
import asyncio

OUTPUT_DIR = "test_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def generate_speech(text: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def main():
    print("=== Генерация дополнительных тестовых файлов ===\n")

    # 1. call_02_8khz.wav (из call_01_dialog.wav)
    print("[1/4] Создаём call_02_8khz.wav (8kHz)...")
    audio = AudioSegment.from_wav(f"{OUTPUT_DIR}/call_01_dialog.wav")
    audio_8khz = audio.set_frame_rate(8000).set_channels(1)
    audio_8khz.export(f"{OUTPUT_DIR}/call_02_8khz.wav", format="wav")
    print("      Готово.\n")

    # 2–4. Короткие монологи
    monologues = [
        ("call_03_mono.wav", "ru-RU-SvetlanaNeural", "Здравствуйте, я хотела бы уточнить информацию по моей карте. У меня возникли вопросы по комиссии за обслуживание."),
        ("call_04_mono.wav", "ru-RU-DmitryNeural", "Добрый день. Я перевёл деньги, но они до сих пор не дошли до получателя. Можете проверить статус перевода?"),
        ("call_05_mono.wav", "ru-RU-SvetlanaNeural", "Алло, добрый день. У меня проблема с приложением, не могу зайти в личный кабинет. Пишет ошибку авторизации."),
    ]

    for i, (filename, voice, text) in enumerate(monologues, start=3):
        print(f"[{i}/4] Создаём {filename}...")
        filepath = os.path.join(OUTPUT_DIR, filename)
        await generate_speech(text, voice, filepath.replace(".wav", ".mp3"))

        # Конвертируем в wav
        mp3_audio = AudioSegment.from_mp3(filepath.replace(".wav", ".mp3"))
        mp3_audio = mp3_audio.set_frame_rate(16000).set_channels(1)
        mp3_audio.export(filepath, format="wav")

        # Удаляем временный mp3
        os.remove(filepath.replace(".wav", ".mp3"))
        print(f"      Готово: {filename}\n")

    print("=== Все файлы успешно созданы ===")
    print(f"Файлы находятся в папке: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
