# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import tempfile
import requests

from core.llm.factory import get_llm_client
from asr.transcriber import Transcriber
from pipeline.orchestrator import AgentOrchestrator


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
        print("[Pipeline] Initializing components...")

        # ASR
        self.transcriber = Transcriber(
            model_size=self.valves.WHISPER_MODEL,
            huggingface_token=self.valves.HF_TOKEN
        )

        # Multi-Agent Orchestrator
        llm_client = get_llm_client()
        self.orchestrator = AgentOrchestrator(llm_client)

        print("[Pipeline] Initialization complete.")

    async def pipe(self, body: dict, __user__: Optional[dict] = None) -> str:
        """
        Основная точка входа Pipeline.
        """
        # 1. Извлечение аудио
        audio_input = self._extract_audio(body)
        if not audio_input:
            return "Ошибка: не удалось получить аудиофайл."

        print(f"[Pipeline] Processing audio: {audio_input}")

        # 2. ASR + Диаризация
        transcript: List[Dict[str, Any]] = await self.transcriber.run(audio_input)
        print(f"[Pipeline] Transcription done. Segments: {len(transcript)}")

        # 3. Запуск Multi-Agent системы
        analysis: Dict[str, Any] = await self.orchestrator.run(transcript)
        print("[Pipeline] Agent analysis complete.")

        # 4. Формирование ответа
        return self._format_response(transcript, analysis)

    def _extract_audio(self, body: dict) -> Optional[str]:
        """
        Извлечение аудиофайла из сообщения пользователя.
        Поддерживает:
        - Загруженные файлы (body["files"])
        - URL в тексте сообщения
        """
        messages = body.get("messages", [])
        if not messages:
            return None

        last_message = messages[-1]
        content = last_message.get("content", "")

        # 1. Проверка на наличие загруженных файлов
        files = body.get("files", [])
        if files:
            file_info = files[0]
            file_path = file_info.get("path") or file_info.get("url")

            if file_path and os.path.exists(file_path):
                return file_path

        # 2. Проверка на URL в сообщении
        if isinstance(content, str) and content.startswith(("http://", "https://")):
            try:
                response = requests.get(content, timeout=30)
                if response.status_code == 200:
                    suffix = os.path.splitext(content)[1] or ".wav"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(response.content)
                        return tmp.name
            except Exception as e:
                print(f"[Pipeline] Failed to download audio from URL: {e}")

        return None

    def _format_response(self, transcript: List[Dict], analysis: Dict) -> str:
        """
        Форматирование результата анализа звонка в красивый markdown.
        """
        classification = analysis.get("classification", {})
        quality = analysis.get("quality_score", {})
        compliance = analysis.get("compliance", {})
        summary = analysis.get("summary", "")
        action_items = analysis.get("action_items", [])

        # === Заголовок ===
        output = "# 📞 Результат анализа звонка\n\n"

        # === Классификация ===
        output += "## 🏷️ Классификация\n"
        output += f"- **Тема:** `{classification.get('topic', '—')}`\n"
        output += f"- **Приоритет:** `{classification.get('priority', '—')}`\n\n"

        # === Оценка качества ===
        output += "## ⭐️ Оценка качества обслуживания\n"
        output += f"**Общий балл:** `{quality.get('total', 0)}/100`\n\n"

        checklist = quality.get("checklist", {})
        if checklist:
            output += "### Чек-лист:\n"
            for key, value in checklist.items():
                emoji = "✅" if value else "❌"
                output += f"- {emoji} {key.replace('_', ' ').title()}\n"
            output += "\n"

        # === Compliance ===
        output += "## 🛡️ Compliance\n"
        passed = compliance.get("passed", True)
        output += f"**Статус:** {'✅ Пройден' if passed else '❌ Есть нарушения'}\n"

        issues = compliance.get("issues", [])
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

        # === Транскрипт (сокращённый) ===
        output += "## 📜 Транскрипт (первые 15 реплик)\n"
        for seg in transcript[:15]:
            output += f"- **{seg['speaker']}** ({seg['start']}s): {seg['text']}\n"

        if len(transcript) > 15:
            output += f"\n_... и ещё {len(transcript) - 15} реплик_\n"

        output += "\n---\n"
        output += "*Анализ выполнен автоматически с помощью Multi-Agent системы.*"

        return output