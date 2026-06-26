# Installation Guide

## Prerequisites
- Python 3.9+
- CUDA 11.8+ (for GPU acceleration - recommended)
- FFmpeg

## Step 1: Install Python dependencies

```bash
cd Farsi_to_Text
pip install -r backend/requirements.txt
```

## Step 2: Download Whisper model

First run will auto-download (3GB):
```bash
python -m uvicorn backend.main:app --port 9999
```

Wait for "Application startup complete" message, then stop (Ctrl+C).

## Step 3: Run the app

Double-click `start.bat` (Windows) or run:

```bash
python -m uvicorn backend.main:app --port 9999
```

In another terminal:
```bash
python -m http.server 3000 --directory frontend
```

Then open: http://localhost:3000

## Troubleshooting

**Port already in use:**
```bash
netstat -ano | findstr :9999
taskkill /PID <PID> /F
```

**CUDA errors:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Model download fails:**
Download manually from: https://huggingface.co/Systran/faster-whisper-large-v3

