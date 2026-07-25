"""
title: MTBank API Bridge
author: Sergey Postnikov
author_url: https://github.com
version: 1.8.1
required_dependencies: requests
"""

from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import requests
import tempfile
import os
import logging

logger = logging.getLogger("MTBankPipeline")
logger.setLevel(logging.DEBUG)

file_handler = True


class Pipeline:

    done = {}       # файлы, которые уже прошли inlet
    sent = {}       # файлы, которые уже отправлены
    results = {}    # кэш результатов анализа

    class Valves(BaseModel):
        api_url: str = "http://api:8000/analyze"
        openwebui_url: str = "http://openwebui:8080"
        # Ключ берётся из переменной окружения OPENWEBUI_API_KEY (из .env)
        openwebui_api_key: str = os.getenv("OPENWEBUI_API_KEY", "")

    def __init__(self):
        self.name = "MTBank API Bridge"
        self.valves = self.Valves()
        self.temp_file_path = None
        self.file_name = "audio.wav"

    async def on_startup(self):
        logger.info(f"Starting pipeline: {self.name}")

    async def on_shutdown(self):
        logger.info(f"Stopping pipeline: {self.name}")
    
    async def inlet(self, body: dict, user: dict) -> dict:
        logger.info("=== [INLET] START ===")
    
        try:
            files = []
            if "metadata" in body:
                user_msg = body["metadata"].get("user_message", {})
                files = user_msg.get("files", [])
    
            if not files:
                files = body.get("files", [])
    
            if not files:
                logger.warning("[INLET] Файлы не найдены")
                return body
    
            file = files[0]
            self.file_name = file.get("name", "audio.wav")
            file_id = file.get("id")
    
            if not file_id:
                logger.error("[INLET] У файла отсутствует 'id'")
                return body
    
            # Защита от повторных вызовов
            if Pipeline.done.get(file_id):
                logger.info(f"[INLET] Файл {file_id} уже обработан. Пропускаем.")
                return body
    
            # === Поиск файла в volume ===
            uploads_path = "/app/openwebui_data/uploads"
            file_path = None
    
            if os.path.exists(uploads_path):
                for filename in os.listdir(uploads_path):
                    if filename.startswith(file_id) and filename.endswith(('.wav', '.mp3', '.ogg')):
                        file_path = os.path.join(uploads_path, filename)
                        break
    
            if file_path and os.path.exists(file_path):
                logger.info(f"[INLET] Файл найден в volume: {file_path}")
                with open(file_path, "rb") as src:
                    content = src.read()
            else:
                logger.warning(f"[INLET] Файл не найден в volume (file_id={file_id})")
                return body
    
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(content)
                self.temp_file_path = tmp.name
    
            Pipeline.done[file_id] = True
    
            logger.info(f"[INLET] Файл сохранён: {self.temp_file_path}")
            logger.info("=== [INLET] END (успех) ===")
    
        except Exception as e:
            logger.exception(f"[INLET] Ошибка: {e}")
            logger.info("=== [INLET] END (ошибка) ===")
    
        return body
         
    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        logger.info("=== [PIPE] START ===")
    
        try:
            # === Если результат уже есть — возвращаем его ===
            if Pipeline.results.get(self.file_name):
                logger.info(f"[PIPE] Возвращаем кэшированный результат для {self.file_name}")
                return Pipeline.results[self.file_name]
    
            if not self.temp_file_path or not os.path.exists(self.temp_file_path):
                return "Ошибка: аудиофайл не был обработан в inlet."
    
            with open(self.temp_file_path, "rb") as f:
                response = requests.post(
                    self.valves.api_url,
                    files={"file": (self.file_name, f, "audio/wav")}
                )
    
            if os.path.exists(self.temp_file_path):
                os.remove(self.temp_file_path)
                self.temp_file_path = None
    
            if response.status_code != 200:
                return f"Ошибка API: {response.status_code}"
    
            # Форматируем результат
            result = self._format_response(response.json())
    
            # === Сохраняем результат в кэш ===
            Pipeline.results[self.file_name] = result
    
            logger.info(f"[PIPE] Результат сохранён в кэш для {self.file_name}")
            return result
    
        except Exception as e:
            logger.exception(f"[PIPE] Ошибка: {e}")
            return f"Ошибка при обработке аудио: {str(e)}"
            
    def _format_response(self, data: dict) -> str:
        classification = data.get("classification", {})
        quality = data.get("quality_score", {})
        compliance = data.get("compliance", {})
        summary = data.get("summary", "")
        action_items = data.get("action_items", [])

        output = "# 📞 Результат анализа звонка\n\n"
        output += "## 🏷 Классификация\n"
        output += f"- **Тема:** `{classification.get('topic', '—')}`\n"
        output += f"- **Приоритет:** `{classification.get('priority', '—')}`\n\n"

        output += "## ⭐️ Оценка качества обслуживания\n"
        output += f"**Общий балл:** `{quality.get('total', 0)}/100`\n\n"

        checklist = quality.get("checklist", {})
        if checklist:
            output += "### Чек-лист:\n"
            for key, value in checklist.items():
                emoji = "✅" if value else "❌"
                output += f"- {emoji} {key.replace('_', ' ').title()}\n"
            output += "\n"

        output += "## 🛡 Compliance\n"
        passed = compliance.get("passed", True)
        output += f"**Статус:** {'✅ Пройден' if passed else '❌ Есть нарушения'}\n\n"

        output += "## 📝 Резюме разговора\n"
        output += f"{summary}\n\n"

        output += "## ✅ Рекомендации (Action Items)\n"
        if action_items:
            for item in action_items:
                output += f"- {item}\n"
        else:
            output += "- Нет рекомендаций\n"

        return output
