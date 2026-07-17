# api/main.py
import os
import warnings
import tempfile
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from asr.transcriber import Transcriber
from pipeline.orchestrator import AgentOrchestrator
from core.llm.factory import get_llm_client

warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")

load_dotenv()


# === Модели ===
class AnalyzeByUrl(BaseModel):
    url: str


app = FastAPI(
    title="MTBank Call Analytics API",
    description="API для автоматического анализа звонков контакт-центра",
    version="1.0.0"
)

transcriber = None
orchestrator = None


@app.on_event("startup")
async def startup_event():
    global transcriber, orchestrator
    print("[API] Initializing components...")

    huggingface_token = os.getenv("HF_TOKEN")
    whisper_model = os.getenv("WHISPER_MODEL", "medium")

    transcriber = Transcriber(
        model_size=whisper_model,
        huggingface_token=huggingface_token
    )

    llm_client = get_llm_client()
    orchestrator = AgentOrchestrator(llm_client)

    print("[API] Initialization complete.")


def _download_from_url(url: str) -> str:
    """Скачивает аудио по URL и сохраняет во временный файл."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        suffix = os.path.splitext(url)[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(response.content)
            return tmp.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download audio: {str(e)}")


@app.post("/analyze")
async def analyze_call(
    file: UploadFile = File(None),
    url: str = None,
    body: AnalyzeByUrl = Body(None)
):
    """
    Анализ звонка.
    Поддерживает:
    - Загрузку файла (multipart/form-data)
    - Передачу URL (JSON: {"url": "..."})
    """
    temp_path = None

    # === Вариант 1: Загрузка файла ===
    if file:
        if not file.filename.endswith((".wav", ".mp3", ".ogg")):
            raise HTTPException(status_code=400, detail="Unsupported file format")

        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

    # === Вариант 2: Загрузка по URL ===
    elif url or (body and body.url):
        audio_url = url or body.url
        temp_path = _download_from_url(audio_url)

    else:
        raise HTTPException(status_code=400, detail="Either 'file' or 'url' must be provided")

    try:
        # ASR
        transcript = await transcriber.run(temp_path)

        # Анализ агентами
        analysis = await orchestrator.run(transcript)

        response = {
            "transcript": transcript,
            "classification": analysis.get("classification", {}),
            "quality_score": analysis.get("quality_score", {}),
            "compliance": analysis.get("compliance", {}),
            "summary": analysis.get("summary", ""),
            "action_items": analysis.get("action_items", []),
        }

        return JSONResponse(content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
