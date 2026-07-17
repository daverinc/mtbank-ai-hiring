# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

from typing import List, Dict, Any
from faster_whisper import WhisperModel

from asr.diarizer import Diarizer


class Transcriber:
    """
    Транскрибация аудио с использованием faster-whisper + pyannote диаризация.
    Выполняет объединение транскрипта со спикерами.
    """

    def __init__(self, model_size: str = "medium", huggingface_token: str = None):
        self.model_size = model_size
        self.model = None
        self.diarizer = Diarizer(huggingface_token) if huggingface_token else None

    def load_model(self):
        """Загружает модель Whisper."""
        if self.model is None:
            print(f"[Transcriber] Loading faster-whisper model: {self.model_size}")
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"

            self.model = WhisperModel(self.model_size, device=device, compute_type=compute_type)
            print("[Transcriber] Model loaded.")

    async def run(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Выполняет транскрибацию и диаризацию.
        Возвращает список сегментов со спикерами.
        """
        self.load_model()

        # 1. Транскрибация
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            language="ru",
            vad_filter=True
        )

        transcript_segments = []
        for segment in segments:
            transcript_segments.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            })

        # 2. Диаризация
        if self.diarizer:
            try:
                speaker_segments = self.diarizer.diarize(audio_path)
                # Объединяем транскрипт со спикерами
                result = self._merge_transcript_with_speakers(transcript_segments, speaker_segments)
                return result
            except Exception as e:
                print(f"[Transcriber] Diarization failed: {e}")
                return transcript_segments

        return transcript_segments

    def _merge_transcript_with_speakers(
        self,
        transcript: List[Dict[str, Any]],
        speakers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Объединяет транскрипт со спикерами по максимальному пересечению времени.
        """
        result = []

        for t_seg in transcript:
            t_start, t_end = t_seg["start"], t_seg["end"]
            best_speaker = "Unknown"
            max_overlap = 0.0

            for s_seg in speakers:
                s_start, s_end = s_seg["start"], s_seg["end"]

                # Вычисляем пересечение интервалов
                overlap_start = max(t_start, s_start)
                overlap_end = min(t_end, s_end)
                overlap = max(0.0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = s_seg["speaker"]

            result.append({
                "speaker": best_speaker,
                "start": t_start,
                "end": t_end,
                "text": t_seg["text"]
            })

        return result
