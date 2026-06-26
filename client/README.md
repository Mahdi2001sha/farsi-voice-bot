# Voice to Text Client (React)

Frontend application for Farsi Voice-to-Text transcription.

## Setup

### Install Dependencies
```bash
npm install
```

### Environment Variables
Create `.env` file:
```
REACT_APP_API_URL=http://localhost:9999
```

### Start Development Server
```bash
npm start
```

Opens [http://localhost:3000](http://localhost:3000) in browser.

## Build for Production
```bash
npm run build
```

## Features

- Record audio from microphone
- Upload audio files
- Real-time transcription
- Confidence scoring
- Keyword extraction
- Transcription history

## API Integration

Uses `src/services/voiceApi.js` to communicate with backend.

```javascript
import { voiceApi } from './services/voiceApi';

// Transcribe file
const result = await voiceApi.transcribeFile(file, 'fa', 'user123');

// Transcribe base64
const result = await voiceApi.transcribeBase64(base64Audio, 'webm', 'fa', 'user123');

// Get logs
const logs = await voiceApi.getLogs(50);

// Health check
const health = await voiceApi.healthCheck();
```

## Components

- `VoiceComponent` - Main recording and transcription interface
- `App` - Main application wrapper with history

## File Structure

```
client/
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

## Deployment

### Build
```bash
npm run build
```

### Deploy to Vercel
```bash
npm i -g vercel
vercel
```

### Deploy to Netlify
```bash
npm run build
# Drag 'build' folder to Netlify
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| REACT_APP_API_URL | Backend API URL |

## Support

For issues or questions, check backend documentation in server folder.
