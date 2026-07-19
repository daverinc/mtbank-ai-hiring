# tests/test_pipeline.py
import os
import asyncio
import warnings
import sys
from dotenv import load_dotenv

# Добавляем корень проекта в sys.path, чтобы можно было импортировать pipeline.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Подавляем предупреждения
warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")

load_dotenv()

# Устанавливаем HF_HOME
hf_home = os.getenv("HF_HOME")
if hf_home:
    os.environ["HF_HOME"] = hf_home

# Импортируем Pipeline из файла pipeline.py в корне
from pipeline import Pipeline


async def main():
    print("=== Тестирование Pipeline ===\n")

    pipeline = Pipeline()

    print("[Test] Выполняем on_startup()...")
    await pipeline.on_startup()
    print("[Test] on_startup() завершён.\n")

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