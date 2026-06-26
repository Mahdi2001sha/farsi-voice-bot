# API Documentation

## Base URL
```
Development:  http://localhost:3000
Production:   https://your-domain.com/api
```

---

## Endpoints

### POST /transcribe/file

Upload audio file for transcription.

**URL:** `/transcribe/file`
**Method:** `POST`
**Content-Type:** `multipart/form-data`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| language | string | "fa" | Language code: "fa" (Farsi), "en" (English), "" (auto-detect) |
| user_id | string | "test" | User identifier for logging |

**Request Body:**

```
file: Binary audio file
  Supported formats: wav, mp3, ogg, webm, m4a, flac, opus
  Max size: 100MB (soft limit)
```

**Example cURL:**
```bash
curl -X POST "http://localhost:9999/transcribe/file?language=fa&user_id=user123" \
  -F "file=@recording.webm"
```

**Response (200 OK):**
```json
{
  "text": "سلام چطور می‌تونم شنبه با شما صحبت کنم",
  "text_processed": "سلام چطور می‌تونم شنبه با شما صحبت کنم",
  "language_detected": "fa",
  "duration_seconds": 3.45,
  "processing_time_ms": 1250,
  "log_id": "a1b2c3d4",
  "audio_filename": "20260611-140000-user123.webm",
  "confidence": 94.2,
  "reliability": "very_high",
  "detected_keywords": {
    "accounts": [],
    "amounts": [],
    "commands": [],
    "transaction_detected": false
  },
  "quality_assessment": {
    "valid": true,
    "file_size_mb": 0.45,
    "quality_level": "good",
    "estimated_duration": 3.5,
    "issues": [],
    "recommendation": "process_normally"
  }
}
```

**Error Responses:**

```json
// 400 Bad Request - Empty file
{
  "detail": "Audio validation failed: ['empty_file']"
}

// 503 Service Unavailable - Model not loaded
{
  "detail": "Whisper model not loaded."
}
```

---

### POST /transcribe/base64

Send audio as base64 string (from browser recording).

**URL:** `/transcribe/base64`
**Method:** `POST`
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "audio_base64": "UklGRiYAAA...",
  "language": "fa",
  "audio_format": "webm",
  "user_id": "user123"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| audio_base64 | string | Yes | Base64-encoded audio data |
| language | string | No | "fa", "en", or empty for auto |
| audio_format | string | No | Audio format (webm, wav, mp3, etc) |
| user_id | string | No | User identifier |

**Example JavaScript:**
```javascript
const audioBlob = new Blob([audioData], { type: 'audio/webm' });
const reader = new FileReader();

reader.onloadend = async () => {
  const base64 = reader.result.split(',')[1];
  
  const response = await fetch('http://localhost:3000/transcribe/base64', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audio_base64: base64,
      language: 'fa',
      audio_format: 'webm',
      user_id: 'user123'
    })
  });
  
  const result = await response.json();
  console.log(result.text_processed);
};

reader.readAsDataURL(audioBlob);
```

**Response:** Same as `/transcribe/file`

---

### GET /logs

Retrieve transcription logs.

**URL:** `/logs`
**Method:** `GET`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 50 | Number of recent records |
| user_id | string | null | Filter by user ID |
| min_confidence | float | 0 | Minimum confidence threshold (0-100) |

**Example:**
```bash
# Get latest 100 logs
GET /logs?limit=100

# Get logs for specific user
GET /logs?user_id=user123

# Get logs with confidence > 80%
GET /logs?min_confidence=80
```

**Response (200 OK):**
```json
{
  "total": 245,
  "logs": [
    {
      "id": "a1b2c3d4",
      "user_id": "user123",
      "timestamp": "2026-06-11 14:00:38",
      "audio_filename": "20260611-140000-user123.webm",
      "language_requested": "fa",
      "language_detected": "fa",
      "duration_seconds": 3.45,
      "processing_time_ms": 1250,
      "text": "سلام",
      "text_processed": "سلام",
      "confidence": 94.2,
      "reliability": "very_high",
      "detected_commands": "transfer"
    }
  ]
}
```

---

### GET /health

Health check endpoint.

**URL:** `/health`
**Method:** `GET`

**Response (200 OK):**
```json
{
  "status": "ok",
  "model": "large-v3",
  "device": "cuda"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "model_not_loaded",
  "model": "large-v3",
  "device": "cuda"
}
```

---

### GET /

Root endpoint.

**URL:** `/`
**Method:** `GET`

**Response (200 OK):**
```json
{
  "status": "running",
  "model": "large-v3",
  "device": "cuda",
  "model_loaded": true
}
```

---

## Response Models

### TranscribeResponse
```typescript
{
  text: string;                    // Raw Whisper output
  text_processed: string;          // Cleaned text with fixed numbers
  language_detected: string;       // Detected language code
  duration_seconds: number;        // Audio duration in seconds
  processing_time_ms: number;      // Processing time in milliseconds
  log_id: string;                  // Unique log identifier
  audio_filename: string;          // Saved audio filename
  confidence: number;              // Confidence score (0-100)
  reliability: string;             // "very_high" | "high" | "medium" | "low" | "very_low"
  detected_keywords: {
    accounts: string[];            // Account numbers found
    amounts: string[];             // Amounts found
    commands: string[];            // Banking commands found
    transaction_detected: boolean;  // If transaction was detected
  };
  quality_assessment: {
    valid: boolean;                // Is audio valid
    file_size_mb: number;          // File size in MB
    quality_level: string;         // "good" | "acceptable" | "poor" | "very_poor"
    estimated_duration: number;    // Estimated duration in seconds
    issues: string[];              // List of issues
    recommendation: string;        // "process_normally" | "process_with_caution" | "do_not_process"
  };
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Cause |
|------|---------|-------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input or empty file |
| 503 | Service Unavailable | Model not loaded |

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

**Invalid base64:**
```json
{ "detail": "Invalid base64 audio data" }
```

**File too large:**
```json
{ "detail": "Audio validation failed: ['large_file']" }
```

**Unsupported format:**
```json
{ "detail": "Audio validation failed: ['unusual_format_.xyz']" }
```

---

## Rate Limiting

Currently no rate limiting. For production, add:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/transcribe/file")
@limiter.limit("10/minute")
async def transcribe_file(...):
    ...
```

---

## Authentication

Currently no authentication. For production, add JWT or API keys.

---

## CORS Policy

Allows all origins in development:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

For production, restrict to specific domain.

---

## Versioning

Current API version: `v1` (implied)

Future versions could use:
```
/api/v2/transcribe/file
/api/v2/transcribe/base64
```

---

## WebSocket Support (Future)

For real-time streaming transcription:
```
WebSocket: ws://localhost:9999/ws/transcribe
Message: { "audio_chunk": "base64_data", "language": "fa" }
```

