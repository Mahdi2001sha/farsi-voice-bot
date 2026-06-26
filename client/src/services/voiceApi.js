// services/voiceApi.js
// API service for Voice-to-Text backend

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:9999';

export const voiceApi = {
  
  transcribeFile: async (file, language = 'fa', userId = 'test') => {
    try {
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
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to transcribe');
      }
      
      return await response.json();
    } catch (error) {
      console.error('voiceApi.transcribeFile error:', error);
      throw error;
    }
  },

  transcribeBase64: async (audioBase64, format = 'webm', language = 'fa', userId = 'test') => {
    try {
      const response = await fetch(`${API_BASE}/transcribe/base64`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          audio_base64: audioBase64,
          language,
          audio_format: format,
          user_id: userId
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to transcribe');
      }
      
      return await response.json();
    } catch (error) {
      console.error('voiceApi.transcribeBase64 error:', error);
      throw error;
    }
  },

  getLogs: async (limit = 50, userId = null, minConfidence = 0) => {
    try {
      const params = new URLSearchParams({ limit });
      if (userId) params.append('user_id', userId);
      if (minConfidence > 0) params.append('min_confidence', minConfidence);
      
      const response = await fetch(`${API_BASE}/logs?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }
      
      return await response.json();
    } catch (error) {
      console.error('voiceApi.getLogs error:', error);
      throw error;
    }
  },

  healthCheck: async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      
      if (!response.ok) {
        throw new Error('Server not responding');
      }
      
      return await response.json();
    } catch (error) {
      console.error('voiceApi.healthCheck error:', error);
      throw error;
    }
  }
};
