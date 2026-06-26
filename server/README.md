# Farsi Voice to Text

Advanced offline speech-to-text for Persian language using Whisper large-v3 model on CUDA GPU.

## Features

- Full offline transcription (no internet after model download)
- Persian (Farsi) language support
- English and multi-language support
- Real-time waveform visualization
- Confidence scoring
- Number processing (Farsi digits to English)
- Account/card number detection
- Audio quality validation
- CSV logging

## Model

Uses Whisper large-v3 from Systran:
- Accuracy: 95%+ for clear speech
- Speed: 2-3s per minute on RTX 4060
- Size: 3GB (downloaded once, then offline)

## Files

backend/
  main.py - FastAPI server
  number_processor.py - Fix Farsi numbers
  confidence_scorer.py - Confidence calculation
  keyword_extractor.py - Banking keyword extraction
  audio_validator.py - Audio quality check
  requirements.txt - Python dependencies

frontend/
  index.html - Web interface

start.bat - Launch script

## Usage

1. Run start.bat
2. Browser opens automatically
3. Record or upload audio
4. Click "Transcribe to Text"
5. Get text with confidence score

## Output

- Raw text from Whisper
- Processed text (corrected numbers)
- Confidence score (0-100%)
- Reliability level
- Audio quality assessment
- All results logged to CSV

## System Requirements

- Windows/Linux/Mac
- Python 3.9+
- 8GB+ RAM
- GPU recommended (NVIDIA CUDA)

