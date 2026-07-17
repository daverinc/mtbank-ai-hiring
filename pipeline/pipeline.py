# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

from core.llm.factory import get_llm_client
from asr.transcriber import Transcriber
from pipeline.orchestrator import AgentOrchestrator


class Pipeline:
    """
    OpenWebUI Pipeline для анализа звонков контакт-центра.
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
        Извлечение пути к аудиофайлу из сообщения пользователя.
        """
        # TODO: Реализовать извлечение файла из OpenWebUI
        # Пока заглушка
        messages = body.get("messages", [])
        if not messages:
            return None

        # В реальной реализации здесь будет логика получения файла
        # Пока возвращаем тестовый файл
        return "test_data/call_01_dialog.wav"

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

    
    def _format_response(self, transcript: List[Dict], analysis: Dict) -> str:
        """
        Форматирование результата в markdown для чата OpenWebUI.
        """
        output = "### Результат анализа звонка\n\n"

        # Транскрипт
        output += "#### Транскрипт\n"
        for seg in transcript[:10]:  # первые 10 сегментов
            output += f"- **{seg['speaker']}** ({seg['start']}s): {seg['text']}\n"
        if len(transcript) > 10:
            output += f"... и ещё {len(transcript) - 10} сегментов\n"

        output += "\n"

        # Анализ
        output += "#### Классификация\n"
        output += f"- **Тема:** {analysis.get('classification', {}).get('topic')}\n"
        output += f"- **Приоритет:** {analysis.get('classification', {}).get('priority')}\n\n"

        output += "#### Оценка качества\n"
        output += f"- **Общий балл:** {analysis.get('quality_score', {}).get('total')}\n\n"

        output += "#### Compliance\n"
        output += f"- **Пройден:** {analysis.get('compliance', {}).get('passed')}\n"
        if analysis.get('compliance', {}).get('issues'):
            output += f"- **Нарушения:** {analysis['compliance']['issues']}\n"

        output += "\n#### Резюме\n"
        output += analysis.get('summary', '') + "\n\n"

        output += "#### Action Items\n"
        for item in analysis.get('action_items', []):
            output += f"- {item}\n"

        return output
