# Architecture Guide

## Overview

Backend structure for Voice-to-Text Processing

```
FastAPI Server (Port 9999)
    ↓
main.py (Request Handler)
    ├── Receives audio from Frontend
    ├── Routes to Whisper STT
    ├── Post-processing
    └── Returns response to Frontend
```

---

## Backend Modules

### 1. main.py (FastAPI Server)
**Purpose:** Main API server and request handler

**Key Components:**
- FastAPI app initialization
- CORS middleware (allow requests from React)
- Whisper model loading
- Route handlers:
  - `POST /transcribe/file` - Upload audio file
  - `POST /transcribe/base64` - Send audio as base64 (from browser recording)
  - `GET /health` - Health check
  - `GET /logs` - Retrieve transcription logs

**Data Flow:**
```
Client Request
    ↓
main.py validates input
    ↓
Routes to appropriate processor
    ↓
Returns JSON response
```

---

### 2. number_processor.py
**Purpose:** Fix Farsi number conversion issues

**Key Functions:**
- `convert_digit_chars()` - Convert ۰-۹ to 0-9
- `convert_spoken_numbers()` - Convert spoken Farsi to digits
  - Example: "شصت شصت دو" → "6062"
- `fix_account_patterns()` - Format account numbers
  - Example: "6060 7891 3115" → "6060-7891-3115"

**Input:** Raw Whisper text
**Output:** Cleaned text with proper numbers

---

### 3. confidence_scorer.py
**Purpose:** Calculate confidence level of transcription

**Key Functions:**
- `calculate_confidence()` - Return confidence 0-100%
  
**Algorithm:**
- Analyzes Whisper segment probabilities
- Checks text characteristics (length, number density, repetition)
- Adjusts confidence based on risks

**Output:** Confidence score + reliability level
- very_high (90-100%)
- high (75-89%)
- medium (60-74%)
- low (40-59%)
- very_low (0-39%)

---

### 4. keyword_extractor.py
**Purpose:** Extract banking keywords and entities

**Key Functions:**
- `extract_keywords()` - Find important entities

**Extracts:**
- Account numbers (4-4-4-4-4-4 format)
- Amounts (numerical values)
- Banking commands (transfer, balance, cancel, etc)
- Recipients

**Example Output:**
```json
{
  "accounts": ["6060-7891-3115"],
  "amounts": ["12850000"],
  "commands": ["transfer"],
  "transaction_detected": true
}
```

---

### 5. audio_validator.py
**Purpose:** Validate audio quality before processing

**Key Functions:**
- `validate_audio()` - Check audio file integrity

**Checks:**
- File exists and not empty
- File format supported (wav, mp3, ogg, webm, m4a, flac, opus)
- Reasonable duration (not too short/long)
- Estimated file quality

**Output:** Quality level + recommendations
- good: Process normally
- acceptable: Process with caution
- poor: May need retry
- very_poor: Do not process

---

## Data Models (Pydantic)

### TranscribeBase64Request
```python
{
  "audio_base64": "base64_encoded_audio",
  "language": "fa",  # fa, en, or empty for auto
  "audio_format": "webm",
  "user_id": "test"
}
```

### TranscribeResponse
```python
{
  "text": "Raw Whisper output",
  "text_processed": "Cleaned text with fixed numbers",
  "language_detected": "fa",
  "duration_seconds": 3.5,
  "processing_time_ms": 820,
  "log_id": "a1b2c3d4",
  "audio_filename": "20260611-140000-test.webm",
  "confidence": 92.5,
  "reliability": "high",
  "detected_keywords": {...},
  "quality_assessment": {...}
}
```

---

## Processing Pipeline

```
1. Receive Request (main.py)
   ↓
2. Validate Audio (audio_validator.py)
   ↓
3. Save Audio File (main.py)
   ↓
4. Run Whisper STT (main.py)
   ↓
5. Post-Process Numbers (number_processor.py)
   ↓
6. Calculate Confidence (confidence_scorer.py)
   ↓
7. Extract Keywords (keyword_extractor.py)
   ↓
8. Log Results (main.py)
   ↓
9. Return Response (main.py)
   ↓
10. Frontend displays result
```

---

## File Storage

**Audios folder:**
- Location: `Farsi to Text/Audios/`
- Contains: All recorded/uploaded audio files
- Naming: `YYYYMMDD-HHMMSS-userid.ext`
- Example: `20260611-140000-test.webm`

**CSV Log:**
- Location: `Farsi to Text/transcription_log.csv`
- Contains: Transcription history
- Columns: id, user_id, timestamp, audio_filename, language, confidence, text, etc

---

## Server Startup Sequence

```
1. start.bat runs
2. FastAPI backend starts (port 9999)
   - Loads Whisper model to GPU/CPU
   - Initializes database connection
   - Ready for requests
3. Frontend server starts (port 3000)
   - Serves index.html
4. Browser opens (http://localhost:3000)
5. User can record/upload audio
```

---

## Error Handling

**Audio Validation Errors:**
- Empty file → 400 Bad Request
- Invalid format → 400 Bad Request
- Very short/long audio → Warning badge in response

**Model Errors:**
- Model not loaded → 503 Service Unavailable
- CUDA error → Automatic CPU fallback

**Request Errors:**
- Invalid base64 → 400 Bad Request
- Missing file → 400 Bad Request

---

## Performance Metrics

- Whisper model load time: ~5 seconds
- Audio processing: 1-3 seconds per minute (on GPU)
- Response time (total): 2-5 seconds
- CSV write time: ~10ms

---

## Scalability

**Current Setup:**
- Single FastAPI worker
- Single Whisper model instance
- CSV logging

**For Production:**
- Multiple workers: `--workers 4`
- Database instead of CSV
- Redis caching
- Load balancer
- Multiple GPU servers for horizontal scaling

