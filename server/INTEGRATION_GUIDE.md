# Integration Guide - How to Use with React

## GitHub Repository Structure

```
my-repo/
├── server/                (Python Backend - This project)
│   ├── backend/
│   │   ├── main.py
│   │   ├── number_processor.py
│   │   ├── confidence_scorer.py
│   │   ├── keyword_extractor.py
│   │   ├── audio_validator.py
│   │   ├── requirements.txt
│   │   └── __init__.py
│   ├── frontend/
│   │   └── index.html    (Can be replaced with React)
│   ├── start.bat
│   ├── README.md
│   ├── ARCHITECTURE.md
│   └── DEPLOY_SERVER.md
│
└── client/               (React Frontend - Your project)
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── services/
    │       └── voiceApi.js   (← API calls to backend)
    ├── package.json
    └── ...
```

---

## How Backend Works

### Backend URL
```
Local:  http://localhost:9999
Server: https://your-domain.com/api
```

### Available Endpoints

#### 1. Transcribe Audio File
```
POST /transcribe/file

Query Parameters:
  - language (optional): "fa", "en", or empty for auto
  - user_id (optional): User identifier for logging

Request Body: multipart/form-data
  - file: Audio file (wav, mp3, ogg, webm, m4a, flac, opus)

Response:
{
  "text": "Raw transcription",
  "text_processed": "Cleaned text",
  "language_detected": "fa",
  "confidence": 92.5,
  "reliability": "high",
  "detected_keywords": {
    "accounts": ["6060-7891-3115"],
    "commands": ["transfer"],
    "transaction_detected": true
  },
  "quality_assessment": {
    "quality_level": "good",
    "file_size_mb": 0.45,
    "estimated_duration": 3.5
  }
}
```

#### 2. Transcribe Base64 Audio (From Browser Recording)
```
POST /transcribe/base64

Request Body (JSON):
{
  "audio_base64": "base64_encoded_audio_data",
  "language": "fa",
  "audio_format": "webm",
  "user_id": "john_doe"
}

Response: Same as endpoint #1
```

#### 3. Get Transcription Logs
```
GET /logs

Query Parameters:
  - limit (default: 50): Number of recent logs
  - user_id (optional): Filter by user
  - min_confidence (optional): Filter by minimum confidence

Response:
{
  "total": 150,
  "logs": [
    {
      "id": "a1b2c3d4",
      "user_id": "john_doe",
      "timestamp": "2026-06-11 14:00:00",
      "audio_filename": "20260611-140000-test.webm",
      "text": "سلام",
      "confidence": 92.5,
      "reliability": "high"
    }
  ]
}
```

#### 4. Health Check
```
GET /health

Response:
{
  "status": "ok",
  "model": "large-v3",
  "device": "cuda"
}
```

---

## React Integration Example

### API Service (voiceApi.js)

```javascript
// services/voiceApi.js

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:9999';

export const voiceApi = {
  
  // Send file
  transcribeFile: async (file, language = 'fa', userId = 'test') => {
    const formData = new FormData();
    formData.append('file', file);
    
    const params = new URLSearchParams({
      language,
      user_id: userId
    });
    
    const response = await fetch(`${API_BASE}/transcribe/file?${params}`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) throw new Error('API Error');
    return response.json();
  },
  
  // Send base64
  transcribeBase64: async (audioBase64, format = 'webm', language = 'fa', userId = 'test') => {
    const response = await fetch(`${API_BASE}/transcribe/base64`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_base64: audioBase64,
        language,
        audio_format: format,
        user_id: userId
      })
    });
    
    if (!response.ok) throw new Error('API Error');
    return response.json();
  },
  
  // Get logs
  getLogs: async (limit = 50, userId = null) => {
    const params = new URLSearchParams({ limit });
    if (userId) params.append('user_id', userId);
    
    const response = await fetch(`${API_BASE}/logs?${params}`);
    return response.json();
  },
  
  // Health check
  healthCheck: async () => {
    const response = await fetch(`${API_BASE}/health`);
    return response.json();
  }
};
```

### React Component Example

```javascript
// components/VoiceInput.jsx

import { useState } from 'react';
import { voiceApi } from '../services/voiceApi';

export const VoiceInput = ({ onTranscribe }) => {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  let mediaRecorder;
  let chunks = [];
  
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    chunks = [];
    
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'audio/webm' });
      setRecordedBlob(blob);
    };
    
    mediaRecorder.start();
    setRecording(true);
  };
  
  const stopRecording = () => {
    mediaRecorder.stop();
    setRecording(false);
  };
  
  const handleTranscribe = async () => {
    if (!recordedBlob) return;
    
    setLoading(true);
    try {
      const result = await voiceApi.transcribeFile(
        recordedBlob,
        'fa',
        'user123'
      );
      
      onTranscribe({
        text: result.text_processed,
        confidence: result.confidence,
        keywords: result.detected_keywords
      });
      
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to transcribe');
    }
    setLoading(false);
  };
  
  return (
    <div>
      <button onClick={recording ? stopRecording : startRecording}>
        {recording ? 'Stop Recording' : 'Start Recording'}
      </button>
      
      {recordedBlob && (
        <button onClick={handleTranscribe} disabled={loading}>
          {loading ? 'Processing...' : 'Transcribe'}
        </button>
      )}
    </div>
  );
};
```

---

## Environment Variables

### React (.env)
```
REACT_APP_API_URL=http://localhost:9999
REACT_APP_API_URL=https://your-domain.com/api  (Production)
```

### Backend (Windows: start.bat)
```
set KMP_DUPLICATE_LIB_OK=TRUE
```

### Backend (Linux: systemd)
```
Environment="KMP_DUPLICATE_LIB_OK=TRUE"
```

---

## Development Workflow

### 1. Start Backend
```bash
cd server/backend
pip install -r requirements.txt
python -m uvicorn main:app --port 9999
```

### 2. Start Frontend (React)
```bash
cd client
npm install
npm start  (starts on http://localhost:3000)
```

### 3. Test Integration
- Open http://localhost:3000 in browser
- Record audio
- Click Transcribe
- Check if backend responds

### 4. Debug
- Check console (Ctrl+Shift+I)
- Check backend logs in terminal
- Use browser DevTools Network tab

---

## CORS Configuration

Backend allows cross-origin requests:

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, restrict to:
```python
allow_origins=["https://your-domain.com"]
```

---

## Production Deployment

### Backend (Python)
```bash
# On server
cd server
pip install -r backend/requirements.txt
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
```

### Frontend (React)
```bash
# Build
npm run build

# Deploy to your hosting (Vercel, Netlify, etc)
```

### Connect Them
```javascript
// .env (Production)
REACT_APP_API_URL=https://your-backend-domain.com/api
```

---

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] Can record audio
- [ ] Audio sends to backend
- [ ] Response returns correctly
- [ ] Confidence score displays
- [ ] Keywords extract properly
- [ ] Logs are saved
- [ ] Mobile responsive
- [ ] Works with different languages

---

## Troubleshooting

### CORS Error
**Problem:** "Access to XMLHttpRequest blocked by CORS policy"
**Solution:** Check API_URL in .env, ensure backend allows origin

### 404 Not Found
**Problem:** "POST /transcribe/file 404"
**Solution:** Check backend is running, verify port number

### Model Not Loaded
**Problem:** "Whisper model not loaded"
**Solution:** Check backend logs, ensure GPU memory sufficient

### Slow Response
**Problem:** Takes >10 seconds to transcribe
**Solution:** Use GPU, reduce model size to `medium` or `small`

