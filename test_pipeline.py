# test_pipeline.py
import os
import asyncio
import warnings
from dotenv import load_dotenv

# Подавляем предупреждения
warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")

load_dotenv()

# Устанавливаем HF_HOME
hf_home = os.getenv("HF_HOME")
if hf_home:
    os.environ["HF_HOME"] = hf_home

from pipeline.pipeline import Pipeline


async def main():
    print("=== Тестирование Pipeline ===\n")

    # Создаём экземпляр Pipeline
    pipeline = Pipeline()

    # Вызываем on_startup (инициализация ASR и Orchestrator)
    print("[Test] Выполняем on_startup()...")
    await pipeline.on_startup()
    print("[Test] on_startup() завершён.\n")

    # Формируем тестовое тело сообщения (как от OpenWebUI)
    test_body = {
        "messages": [
            {
                "role": "user",
                "content": "Проанализируй звонок"
            }
        ]
    }

    print("[Test] Вызываем pipe()...")
    result = await pipeline.pipe(test_body)
    print("\n=== Результат Pipeline ===\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
