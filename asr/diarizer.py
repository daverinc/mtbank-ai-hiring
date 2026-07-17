# Copyright (c) 2026 Sergey Postnikov. All rights reserved.
# Данное решение выполнено исключительно для рассмотрения кандидатуры на вакансию.

import os
from typing import List, Dict, Any
from pyannote.audio import Pipeline
import torch


class Diarizer:
    """
    Диаризация спикеров с использованием pyannote.audio.
    Разделяет аудио на сегменты по говорящим.
    """

    def __init__(self, huggingface_token: str):
        self.token = huggingface_token
        self.pipeline = None

    def load(self):
        """Загружает модель диаризации."""
        if self.pipeline is None:
            print("[Diarizer] Loading pyannote/speaker-diarization-3.1 ...")
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=self.token          # ← было: use_auth_token
            )
            if torch.cuda.is_available():
                self.pipeline.to(torch.device("cuda"))
            print("[Diarizer] Model loaded successfully.")

    def diarize(self, audio_path: str) -> List[Dict[str, Any]]:
        if self.pipeline is None:
            self.load()

        diarization = self.pipeline(audio_path)

        segments = []

        # Новый способ итерации для pyannote 3.1+
        for segment, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):
            segments.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "speaker": speaker
            })

        return segments

