# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class Pipeline:
    """
    OpenWebUI Pipeline для автоматического анализа звонков контакт-центра МТБанка.
    """

    class Valves(BaseModel):
        GROQ_API_KEY: str = ""
        LLM_MODEL: str = "qwen2.5:32b"
        WHISPER_MODEL: str = "medium"
        ENABLE_DIARIZATION: bool = True

    def __init__(self):
        self.transcriber = None
        self.orchestrator = None

    async def on_startup(self):
        """
        Инициализация компонентов при старте Pipeline.
        """
        from asr.transcriber import Transcriber
        from pipeline.orchestrator import AgentOrchestrator

        self.transcriber = Transcriber(model_size=self.valves.WHISPER_MODEL)
        self.orchestrator = AgentOrchestrator(
            groq_api_key=self.valves.GROQ_API_KEY,
            llm_model=self.valves.LLM_MODEL
        )

    async def pipe(self, body: dict, __user__: Optional[dict] = None) -> str:
        """
        Основная точка входа Pipeline.
        """
        # 1. Извлечение аудио
        audio_input = self._extract_audio(body)
        if not audio_input:
            return "Ошибка: не удалось получить аудиофайл."

        # 2. ASR + Диаризация
        transcript: List[Dict[str, Any]] = await self.transcriber.run(audio_input)

        # 3. Запуск Multi-Agent системы (4 агента)
        analysis: Dict[str, Any] = await self.orchestrator.run(transcript)

        # 4. Форматирование ответа
        return self._format_response(transcript, analysis)

    def _extract_audio(self, body: dict) -> Optional[str]:
        """Извлечение аудио из сообщения пользователя (файл или URL)"""
        # TODO: реализовать позже
        return None

    def _format_response(self, transcript: List[Dict], analysis: Dict) -> str:
        """Форматирование результата в markdown для чата"""
        # TODO: реализовать позже
        return "Анализ завершён (заглушка)"
