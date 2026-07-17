
# api/main.py
import os
import warnings
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from asr.transcriber import Transcriber
from pipeline.orchestrator import AgentOrchestrator
from core.llm.factory import get_llm_client

warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")

load_dotenv()

# === Инициализация ===
app = FastAPI(
    title="MTBank Call Analytics API",
    description="API для автоматического анализа звонков контакт-центра",
    version="1.0.0"
)

# Глобальные объекты
transcriber = None
orchestrator = None


@app.on_event("startup")
async def startup_event():
    global transcriber, orchestrator

    print("[API] Initializing components...")

    # ASR
    huggingface_token = os.getenv("HF_TOKEN")
    whisper_model = os.getenv("WHISPER_MODEL", "medium")
    transcriber = Transcriber(
        model_size=whisper_model,
        huggingface_token=huggingface_token
    )

    # Multi-Agent
    llm_client = get_llm_client()
    orchestrator = AgentOrchestrator(llm_client)

    print("[API] Initialization complete.")


@app.post("/analyze")
async def analyze_call(file: UploadFile = File(...)):
    """
    Принимает аудиофайл и возвращает полный анализ звонка.
    """
    if not file.filename.endswith((".wav", ".mp3", ".ogg")):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Сохраняем временный файл
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        # 1. ASR + Диаризация
        transcript = await transcriber.run(temp_path)

        # 2. Анализ агентами
        analysis = await orchestrator.run(transcript)

        # 3. Формирование ответа
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
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/health")
async def health_check():
    return {"status": "ok"