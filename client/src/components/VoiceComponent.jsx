import { useState, useRef } from 'react';
import { voiceApi } from '../services/voiceApi';
import './VoiceComponent.css';

export const VoiceComponent = ({ onTranscribe }) => {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [language, setLanguage] = useState('fa');
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setRecordedBlob(blob);
      };

      mediaRecorder.start();
      setRecording(true);
      setError(null);
    } catch (err) {
      setError('Microphone access denied: ' + err.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setRecording(false);
    }
  };

  const handleTranscribe = async () => {
    if (!recordedBlob) return;

    setLoading(true);
    setError(null);

    try {
      const result = await voiceApi.transcribeFile(
        recordedBlob,
        language,
        'user123'
      );

      setResult(result);
      
      if (onTranscribe) {
        onTranscribe({
          text: result.text_processed,
          confidence: result.confidence,
          keywords: result.detected_keywords
        });
      }

      setRecordedBlob(null);
    } catch (err) {
      setError('Error: ' + err.message);
    }

    setLoading(false);
  };

  const handleUploadFile = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const result = await voiceApi.transcribeFile(file, language, 'user123');
      setResult(result);
      
      if (onTranscribe) {
        onTranscribe({
          text: result.text_processed,
          confidence: result.confidence,
          keywords: result.detected_keywords
        });
      }
    } catch (err) {
      setError('Error: ' + err.message);
    }

    setLoading(false);
  };

  return (
    <div className="voice-container">
      <div className="voice-card">
        <h2>Voice to Text</h2>

        <div className="language-selector">
          <label>Language:</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="fa">Farsi (FA)</option>
            <option value="en">English (EN)</option>
            <option value="">Auto-detect</option>
          </select>
        </div>

        <div className="controls">
          <button
            onClick={recording ? stopRecording : startRecording}
            disabled={loading}
            className={`btn ${recording ? 'btn-danger' : 'btn-primary'}`}
          >
            {recording ? 'Stop Recording' : 'Start Recording'}
          </button>

          <label className="file-input-label">
            Upload Audio
            <input
              type="file"
              accept="audio/*"
              onChange={handleUploadFile}
              disabled={loading}
            />
          </label>

          {recordedBlob && (
            <button
              onClick={handleTranscribe}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Processing...' : 'Transcribe'}
            </button>
          )}
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {result && (
          <div className="result-container">
            <h3>Results</h3>
            
            <div className="result-item">
              <strong>Raw Text:</strong>
              <p>{result.text}</p>
            </div>

            <div className="result-item">
              <strong>Processed Text:</strong>
              <p>{result.text_processed}</p>
            </div>

            <div className="result-item">
              <strong>Confidence:</strong>
              <p>
                <span className="confidence-badge">
                  {result.confidence}% ({result.reliability})
                </span>
              </p>
            </div>

            <div className="result-item">
              <strong>Duration:</strong>
              <p>{result.duration_seconds.toFixed(2)}s</p>
            </div>

            {result.detected_keywords?.accounts?.length > 0 && (
              <div className="result-item">
                <strong>Accounts:</strong>
                <p>{result.detected_keywords.accounts.join(', ')}</p>
              </div>
            )}

            {result.detected_keywords?.commands?.length > 0 && (
              <div className="result-item">
                <strong>Commands:</strong>
                <p>{result.detected_keywords.commands.join(', ')}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
