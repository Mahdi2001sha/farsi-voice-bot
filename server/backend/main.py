from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile, os, base64, time, csv, uuid
from datetime import datetime
from pathlib import Path
from confidence_scorer import calculate_confidence
from keyword_extractor import extract_keywords
from audio_validator import validate_audio

app = FastAPI(title="Voice-to-Text API", version="7.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONFIG - Using small model fine-tuned on Persian
MODEL_PATH   = os.getenv("WHISPER_MODEL_PATH", "large-v3")
DEVICE       = os.getenv("WHISPER_DEVICE", "cuda")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE", "float16")

# PATHS
PARENT_DIR = Path(__file__).parent.parent
LOG_FILE = PARENT_DIR / "transcription_log.csv"
AUDIO_DIR = PARENT_DIR / "Audios"
AUDIO_DIR.mkdir(exist_ok=True)

LOG_HEADERS = ["id", "user_id", "timestamp", "audio_filename", "language_requested",
               "language_detected", "duration_seconds", "processing_time_ms", "text", 
               "confidence", "reliability", "detected_commands"]

# LOAD MODEL
print(f"Loading Whisper model: {MODEL_PATH} on {DEVICE.upper()}...")

try:
    from faster_whisper import WhisperModel
    whisper_model = WhisperModel(
        MODEL_PATH,
        device=DEVICE,
        compute_type=COMPUTE_TYPE,
        num_workers=2,
        cpu_threads=4,
    )
    print(f"SUCCESS: Whisper '{MODEL_PATH}' loaded")
except ImportError:
    print("ERROR: faster-whisper not installed")
    whisper_model = None
except Exception as e:
    print(f"ERROR: {e}")
    whisper_model = None

def init_csv():
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="", encoding="utf-8-sig") as f:
            csv.DictWriter(f, fieldnames=LOG_HEADERS).writeheader()

init_csv()
print(f"Audio folder: {AUDIO_DIR}")

# SCHEMAS
class TranscribeResponse(BaseModel):
    text: str
    language_detected: str
    duration_seconds: float
    processing_time_ms: int
    log_id: str
    audio_filename: str
    confidence: float
    reliability: str
    detected_keywords: dict
    quality_assessment: dict

# ENDPOINTS
@app.get("/")
def root():
    return {"status": "running", "model": MODEL_PATH, "device": DEVICE}

@app.get("/health")
def health():
    return {"status": "ok" if whisper_model else "model_not_loaded"}

@app.post("/transcribe/file", response_model=TranscribeResponse)
async def transcribe_file(
    file: UploadFile = File(...),
    language: str = Query(default="fa"),
    user_id: str = Query(default="test"),
):
    if not whisper_model:
        raise HTTPException(503, "Model not loaded")

    start = time.time()
    suffix = os.path.splitext(file.filename or "audio")[-1] or ".webm"
    
    timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    audio_filename = f"{timestamp_str}-{user_id}{suffix}"
    saved_audio_path = AUDIO_DIR / audio_filename
    
    content = await file.read()
    saved_audio_path.write_bytes(content)

    quality_assessment = validate_audio(str(saved_audio_path))
    
    if not quality_assessment["valid"]:
        raise HTTPException(400, f"Audio validation failed")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        text, detected_lang, duration, segments = _run_whisper(tmp_path, language or None)
    finally:
        os.unlink(tmp_path)

    confidence_data = calculate_confidence(segments, text)
    keywords = extract_keywords(text)

    processing_ms = int((time.time() - start) * 1000)
    log_id = _write_log(
        user_id, audio_filename, language, detected_lang, duration, processing_ms,
        text, confidence_data, keywords
    )

    print(f"[{log_id}] Done - Confidence: {confidence_data['confidence']}%")

    return TranscribeResponse(
        text=text,
        language_detected=detected_lang,
        duration_seconds=duration,
        processing_time_ms=processing_ms,
        log_id=log_id,
        audio_filename=audio_filename,
        confidence=confidence_data["confidence"],
        reliability=confidence_data["reliability"],
        detected_keywords=keywords,
        quality_assessment=quality_assessment,
    )

@app.post("/transcribe/base64", response_model=TranscribeResponse)
async def transcribe_base64(
    audio_base64: str,
    language: str = "fa",
    user_id: str = "test",
):
    if not whisper_model:
        raise HTTPException(503, "Model not loaded")

    start = time.time()

    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception:
        raise HTTPException(400, "Invalid base64")

    timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    audio_filename = f"{timestamp_str}-{user_id}.webm"
    saved_audio_path = AUDIO_DIR / audio_filename
    saved_audio_path.write_bytes(audio_bytes)

    quality_assessment = validate_audio(str(saved_audio_path))
    
    if not quality_assessment["valid"]:
        raise HTTPException(400, "Audio validation failed")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        text, detected_lang, duration, segments = _run_whisper(tmp_path, language)
    finally:
        os.unlink(tmp_path)

    confidence_data = calculate_confidence(segments, text)
    keywords = extract_keywords(text)

    processing_ms = int((time.time() - start) * 1000)
    log_id = _write_log(
        user_id, audio_filename, language, detected_lang, duration, processing_ms,
        text, confidence_data, keywords
    )

    return TranscribeResponse(
        text=text,
        language_detected=detected_lang,
        duration_seconds=duration,
        processing_time_ms=processing_ms,
        log_id=log_id,
        audio_filename=audio_filename,
        confidence=confidence_data["confidence"],
        reliability=confidence_data["reliability"],
        detected_keywords=keywords,
        quality_assessment=quality_assessment,
    )

@app.get("/logs")
def get_logs(limit: int = 50, user_id: str = None):
    if not LOG_FILE.exists():
        return {"logs": []}

    with open(LOG_FILE, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    if user_id:
        rows = [r for r in rows if r["user_id"] == user_id]

    return {"total": len(rows), "logs": rows[-limit:]}

# CORE
def _run_whisper(audio_path: str, language: str | None) -> tuple[str, str, float, list]:
    segments, info = whisper_model.transcribe(
        audio_path,
        language=language,
        beam_size=5,
        best_of=5,
        patience=2,
        condition_on_previous_text=False,
        temperature=0.0,
        vad_filter=False,
        word_timestamps=False,
        max_new_tokens=None,
        chunk_length=30,
        clip_timestamps="0",
    )

    segments_list = list(segments)
    full_text = ""
    last_end = 0.0
    
    for segment in segments_list:
        full_text += segment.text
        last_end = segment.end

    duration = getattr(info, "duration", last_end) or last_end
    return full_text.strip(), info.language, duration, segments_list

def _write_log(
    user_id: str,
    audio_filename: str,
    language_requested: str,
    language_detected: str,
    duration: float,
    processing_ms: int,
    text: str,
    confidence_data: dict,
    keywords: dict,
) -> str:
    log_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = {
        "id": log_id,
        "user_id": user_id,
        "timestamp": timestamp,
        "audio_filename": audio_filename,
        "language_requested": language_requested or "auto",
        "language_detected": language_detected,
        "duration_seconds": round(duration, 2),
        "processing_time_ms": processing_ms,
        "text": text,
        "confidence": confidence_data.get("confidence", 0),
        "reliability": confidence_data.get("reliability", "unknown"),
        "detected_commands": ",".join(keywords.get("commands", [])),
    }

    with open(LOG_FILE, "a", newline="", encoding="utf-8-sig") as f:
        csv.DictWriter(f, fieldnames=LOG_HEADERS).writerow(row)

    return log_id
