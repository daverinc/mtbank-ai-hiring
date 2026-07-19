# pipeline.py
# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from dotenv import load_dotenv

load_dotenv() 

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import tempfile
import requests
import logging

from core.llm.factory import get_llm_client
from asr.transcriber import Transcriber
from multiagent.orchestrator import AgentOrchestrator

logger = logging.getLogger("pipeline")


class Pipeline:
    """
    OpenWebUI Pipeline для анализа звонков контакт-центра МТБанка.
    """

    class Valves(BaseModel):
        WHISPER_MODEL: str = "medium"
        HF_TOKEN: str = ""
        ENABLE_DIARIZATION: bool = True

    def __init__(self):
        self.valves = self.Valves()
        self.transcriber = None
        self.orchestrator = None

    async def on_startup(self):
        """Инициализация компонентов при старте Pipeline."""
        logger.info("[Pipeline] Initializing components...")

        self.transcriber = Transcriber(
            model_size=self.valves.WHISPER_MODEL,
            huggingface_token=self.valves.HF_TOKEN
        )

        llm_client = get_llm_client()
        self.orchestrator = AgentOrchestrator(llm_client)

        logger.info("[Pipeline] Initialization complete.")

    async def pipe(self, body: dict, __user__: Optional[dict] = None) -> str:
        """
        Основная точка входа Pipeline.
        """
        if self.transcriber is None or self.orchestrator is None:
            logger.error("[Pipeline] Pipeline components are not initialized")
            return "Ошибка: Pipeline не инициализирован."

        audio_input = self._extract_audio(body)
        if not audio_input:
            return "Ошибка: не удалось получить аудиофайл."

        logger.info(f"[Pipeline] Processing audio: {audio_input}")

        try:
            transcript: List[Dict[str, Any]] = await self.transcriber.run(audio_input)
            logger.info(f"[Pipeline] Transcription done. Segments: {len(transcript)}")

            analysis: Dict[str, Any] = await self.orchestrator.run(transcript)
            logger.info("[Pipeline] Agent analysis complete.")

            return self._format_response(transcript, analysis)

        except Exception as e:
            logger.exception(f"[Pipeline] Error during processing: {e}")
            return "Ошибка при обработке аудиофайла."

    def _extract_audio(self, body: dict) -> Optional[str]:
        """
        Извлечение аудиофайла из сообщения пользователя.
        Поддерживает:
        - Загруженные файлы (body["files"])
        - URL в тексте сообщения
        """
        messages = body.get("messages", [])
        if not messages:
            logger.warning("[Pipeline] No messages found in request body")
            return None

        last_message = messages[-1]
        content = last_message.get("content", "")

        # 1. Проверка на наличие загруженных файлов
        files = body.get("files", [])
        if files:
            file_info = files[0]
            file_path = file_info.get("path") or file_info.get("url")

            if file_path and os.path.exists(file_path):
                logger.info(f"[Pipeline] Audio file received from upload: {file_path}")
                return file_path
            else:
                logger.warning(f"[Pipeline] File path does not exist: {file_path}")

        # 2. Проверка на URL в сообщении
        if isinstance(content, str) and content.startswith(("http://", "https://")):
            try:
                logger.info(f"[Pipeline] Attempting to download audio from URL: {content}")
                response = requests.get(content, timeout=30)
                response.raise_for_status()

                suffix = os.path.splitext(content)[1] or ".wav"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(response.content)
                    logger.info(f"[Pipeline] Audio downloaded successfully to: {tmp.name}")
                    return tmp.name

            except requests.exceptions.RequestException as e:
                logger.error(f"[Pipeline] Failed to download audio from URL: {e}")
            except Exception as e:
                logger.error(f"[Pipeline] Unexpected error while downloading audio: {e}")

        logger.warning("[Pipeline] No valid audio source found in the request")
        return None

    def _format_response(self, transcript: List[Dict], analysis: Dict) -> str:
        """
        Форматирование результата анализа звонка в красивый markdown.
        Устойчив к неполным данным от агентов.
        """
        if not analysis:
            return "Ошибка: не удалось получить результаты анализа."

        classification = analysis.get("classification", {}) or {}
        quality = analysis.get("quality_score", {}) or {}
        compliance = analysis.get("compliance", {}) or {}
        summary = analysis.get("summary", "Резюме недоступно.")
        action_items = analysis.get("action_items", []) or []

        output = "# 📞 Результат анализа звонка\n\n"

        # === Классификация ===
        output += "## 🏷 Классификация\n"
        output += f"- **Тема:** `{classification.get('topic', '—')}`\n"
        output += f"- **Приоритет:** `{classification.get('priority', '—')}`\n\n"

        # === Оценка качества ===
        output += "## ⭐️ Оценка качества обслуживания\n"
        output += f"**Общий балл:** `{quality.get('total', 0)}/100`\n\n"

        checklist = quality.get("checklist") or {}
        if checklist:
            output += "### Чек-лист:\n"
            for key, value in checklist.items():
                emoji = "✅" if value else "❌"
                output += f"- {emoji} {key.replace('_', ' ').title()}\n"
            output += "\n"

        # === Compliance ===
        output += "## 🛡 Compliance\n"
        passed = compliance.get("passed", True)
        output += f"**Статус:** {'✅ Пройден' if passed else '❌ Есть нарушения'}\n"

        issues = compliance.get("issues") or []
        if issues:
            output += "\n**Выявленные нарушения:**\n"
            for issue in issues:
                output += f"- ⚠️ {issue}\n"
        output += "\n"

        # === Резюме ===
        output += "## 📝 Резюме разговора\n"
        output += f"{summary}\n\n"

        # === Action Items ===
        output += "## ✅ Рекомендации (Action Items)\n"
        if action_items:
            for item in action_items:
                output += f"- {item}\n"
        else:
            output += "- Нет рекомендаций\n"
        output += "\n"

        # === Транскрипт ===
        output += "## 📜 Транскрипт (первые 15 реплик)\n"
        for seg in transcript[:15]:
            speaker = seg.get("speaker", "Unknown")
            start = seg.get("start", 0)
            text = seg.get("text", "")
            output += f"- **{speaker}** ({start}s): {text}\n"

        if len(transcript) > 15:
            output += f"\n_... и ещё {len(transcript) - 15} реплик_\n"

        output += "\n---\n"
        output += "*Анализ выполнен автоматически с помощью Multi-Agent системы.*"

        return output
    
pipeline = Pipeline()
