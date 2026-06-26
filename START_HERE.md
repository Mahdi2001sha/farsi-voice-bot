# Voice to Text - Complete Setup

## Quick Start

### 1. Server Setup (Python)

```bash
cd server/backend
pip install -r requirements.txt

# Run with environment variable
set KMP_DUPLICATE_LIB_OK=TRUE
python -m uvicorn main:app --host 0.0.0.0 --port 9999
```

**Expected output:**
```
SUCCESS: Whisper 'large-v3' loaded
Application startup complete.
Uvicorn running on http://0.0.0.0:9999
```

### 2. Client Setup (React)

In a NEW terminal:

```bash
cd client
npm install
npm start
```

**Expected output:**
```
You can now view voice-to-text-client in the browser.
Local: http://localhost:3000
```

Browser opens automatically. If not, go to http://localhost:3000

---

## Important

- Server MUST run before client
- Both must run simultaneously
- Keep both terminals open
- Don't close either terminal

---

## Usage

1. Click **Start Recording**
2. Speak in Farsi or English
3. Click **Stop Recording**
4. Click **Send**
5. Wait for transcription

---

## Troubleshooting

### "Failed to fetch" error
- Check if server is running (http://localhost:9999/health)
- Check .env file: `REACT_APP_API_URL=http://localhost:9999`
- Refresh browser (Ctrl+R)

### Server won't start
- Add environment variable: `set KMP_DUPLICATE_LIB_OK=TRUE`
- Make sure port 9999 is free
- Check Python 3.9+ installed

### npm install fails
- Delete node_modules folder
- Delete package-lock.json
- Run `npm install` again

---

## File Structure

```
Your-Project/
├── server/
│   ├── backend/
│   │   ├── main.py
│   │   ├── number_processor.py
│   │   ├── confidence_scorer.py
│   │   ├── keyword_extractor.py
│   │   ├── audio_validator.py
│   │   ├── requirements.txt
│   │   └── __init__.py
│   │
│   ├── frontend/
│   │   └── index.html
│   │
│   ├── start.bat
│   ├── README.md
│   └── ... (other docs)
│
└── client/
    ├── src/
    │   ├── services/
    │   │   └── voiceApi.js
    │   ├── components/
    │   │   ├── VoiceComponent.jsx
    │   │   └── VoiceComponent.css
    │   ├── App.js
    │   ├── App.css
    │   ├── index.js
    │   └── index.css
    ├── public/
    │   └── index.html
    ├── .env
    ├── package.json
    └── README.md
```

---

## How It Works

1. **Voice Recording**: Click mic → record → stop
2. **Send to Server**: Click Send button
3. **Backend Processing**:
   - Audio validation
   - Whisper STT (speech-to-text)
   - Number processing
   - Confidence scoring
   - Keyword extraction
4. **Display Results**: Show transcription + confidence

---

## Ports

- **Server**: http://localhost:9999
- **Client**: http://localhost:3000

---

## Environment Variables

### Server (.env in server/)
```
KMP_DUPLICATE_LIB_OK=TRUE
```

### Client (.env in client/)
```
REACT_APP_API_URL=http://localhost:9999
```

---

## API Endpoints

- `POST /transcribe/file` - Upload audio file
- `POST /transcribe/base64` - Send base64 audio
- `GET /health` - Server health check
- `GET /logs` - Get transcription logs

---

## Features

- Farsi & English support
- Real-time transcription
- Confidence scoring
- Account number detection
- Banking command recognition
- Audio quality validation
- Full transcription history

---

## Support

Check these files for more info:
- `server/README.md` - Backend details
- `server/ARCHITECTURE.md` - System design
- `server/INTEGRATION_GUIDE.md` - API docs
- `client/README.md` - Frontend details
