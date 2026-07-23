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

    sent = dict()

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

        # Защита от повторного вызова
        if Pipeline.sent.get(str(body)):
            logger.info("[INLET] Файл уже был обработан. Пропускаем повторный вызов.")
            return body

        try:
            files = []
            if "metadata" in body:
                user_msg = body["metadata"].get("user_message", {})
                files = user_msg.get("files", [])

            if not files:
                files = body.get("files", [])

            logger.info(f"[INLET] Найдено файлов: {len(files)}")

            if not files:
                logger.warning("[INLET] Файлы не найдены")
                return body

            file = files[0]
            self.file_name = file.get("name", "audio.wav")

            # Пробуем прочитать напрямую по пути
            file_path = file.get("path")
            if file_path and os.path.exists(file_path):
                logger.info(f"[INLET] Читаем файл напрямую: {file_path}")
                with open(file_path, "rb") as src:
                    content = src.read()
            else:
                # Fallback — скачиваем через HTTP
                logger.warning("[INLET] Поле 'path' недоступно, скачиваем через HTTP")
                file_id = file.get("id")
                if not file_id:
                    logger.error("[INLET] У файла отсутствует 'id'")
                    return body

                auth_token = self.valves.openwebui_api_key or user.get("token", "")
                headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

                content_url = f"{self.valves.openwebui_url}/api/v1/files/{file_id}/content"
                logger.info(f"[INLET] Скачиваем файл: {content_url}")

                response = requests.get(content_url, headers=headers, timeout=60)
                if response.status_code != 200:
                    logger.error(f"[INLET] Ошибка скачивания: {response.status_code}")
                    return body

                content = response.content

            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(content)
                self.temp_file_path = tmp.name


            # Помечаем, что файл уже обработан
            Pipeline.sent[str(body)] = True

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
            # Защита от повторной отправки
            if Pipeline.sent.get(str(body)):
                logger.info("[PIPE] Файл уже был отправлен. Пропускаем повторный вызов.")
                return None

            if not self.temp_file_path or not os.path.exists(self.temp_file_path):
                return "Ошибка: аудиофайл не был обработан в inlet."

            with open(self.temp_file_path, "rb") as f:
                response = requests.post(
                    self.valves.api_url,
                    files={"file": (self.file_name, f, "audio/wav")}
                )

            # Помечаем, что файл отправлен
            Pipeline.sent[str(body)] = True
      
            # Удаляем временный файл
            if os.path.exists(self.temp_file_path):
                os.remove(self.temp_file_path)
                self.temp_file_path = None

            if response.status_code != 200:
                return f"Ошибка API: {response.status_code}"

            return self._format_response(response.json())

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
