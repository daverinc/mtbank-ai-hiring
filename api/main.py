# api/main.py
import os
import time
import json
import logging
import warnings
import tempfile
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

from asr.transcriber import Transcriber
from multiagent.orchestrator import AgentOrchestrator
from core.llm.factory import get_llm_client

warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")
load_dotenv()

# === Логирование ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")


def log_json(message: str, extra: dict = None):
    """Вывод логов в JSON-формате"""
    log_data = {"message": message, "timestamp": time.time()}
    if extra:
        log_data.update(extra)
    logger.info(json.dumps(log_data, ensure_ascii=False))


# === Модели ===
class AnalyzeByUrl(BaseModel):
    url: HttpUrl


app = FastAPI(
    title="MTBank Call Analytics API",
    description="API для автоматического анализа звонков контакт-центра",
    version="1.0.0"
)

transcriber = None
orchestrator = None
MAX_FILE_SIZE_MB = 50


@app.on_event("startup")
async def startup_event():
    global transcriber, orchestrator
    log_json("API starting up...")

    huggingface_token = os.getenv("HF_TOKEN")
    whisper_model = os.getenv("WHISPER_MODEL", "medium")

    transcriber = Transcriber(model_size=whisper_model, huggingface_token=huggingface_token)
    llm_client = get_llm_client()
    orchestrator = AgentOrchestrator(llm_client)

    log_json("API startup complete")


def _validate_file_size(file: UploadFile):
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell() / (1024 * 1024)
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB"
        )


def _download_from_url(url: str) -> str:
    try:
        response = requests.get(str(url), timeout=30, stream=True)
        response.raise_for_status()

        suffix = os.path.splitext(str(url))[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
            return tmp.name
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download audio: {str(e)}")


@app.post("/analyze")
async def analyze_call(
    file: UploadFile = File(None),
    body: AnalyzeByUrl = Body(None)
):
    start_time = time.time()
    temp_path = None
    request_type = None

    try:
        # === Определяем тип запроса ===
        if file:
            request_type = "file"
            if not file.filename.lower().endswith((".wav", ".mp3", ".ogg")):
                raise HTTPException(status_code=400, detail="Unsupported file format")

            _validate_file_size(file)
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(await file.read())

        elif body and body.url:
            request_type = "url"
            temp_path = _download_from_url(body.url)
        else:
            raise HTTPException(status_code=400, detail="Either 'file' or 'url' must be provided")

        log_json("Analysis started", {"type": request_type, "file": str(temp_path)})

        # === ASR + Анализ ===
        transcript = await transcriber.run(temp_path)
        analysis = await orchestrator.run(transcript)

        response = {
            "transcript": transcript,
            "classification": analysis.get("classification", {}),
            "quality_score": analysis.get("quality_score", {}),
            "compliance": analysis.get("compliance", {}),
            "summary": analysis.get("summary", ""),
            "action_items": analysis.get("action_items", []),
        }

        duration = round(time.time() - start_time, 2)
        log_json("Analysis completed", {
            "type": request_type,
            "duration_sec": duration,
            "segments": len(transcript)
        })

        return JSONResponse(content=response)

    except HTTPException as e:
        log_json("HTTP error", {"status_code": e.status_code, "detail": e.detail})
        raise
    except Exception as e:
        log_json("Internal error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/health")
async def health_check():
    return {"status": "ok"}