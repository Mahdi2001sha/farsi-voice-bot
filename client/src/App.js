import { useState } from 'react';
import { VoiceComponent } from './components/VoiceComponent';
import './App.css';

function App() {
  const [transcriptions, setTranscriptions] = useState([]);

  const handleTranscribe = (result) => {
    setTranscriptions([
      {
        text: result.text,
        confidence: result.confidence,
        timestamp: new Date().toLocaleTimeString(),
        keywords: result.keywords
      },
      ...transcriptions
    ]);
  };

  return (
    <div className="App">
      <VoiceComponent onTranscribe={handleTranscribe} />
      
      {transcriptions.length > 0 && (
        <div className="history-section">
          <h3>Transcription History</h3>
          <div className="history-list">
            {transcriptions.map((item, index) => (
              <div key={index} className="history-item">
                <div className="history-header">
                  <span className="timestamp">{item.timestamp}</span>
                  <span className="confidence">{item.confidence}%</span>
                </div>
                <p className="history-text">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
