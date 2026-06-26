import re
from typing import Dict

def calculate_confidence(segments, text: str) -> Dict:
    if not text:
        return {
            "confidence": 0,
            "reliability": "very_low",
        }
    
    segment_count = 0
    total_probability = 0
    
    for segment in segments:
        segment_count += 1
        prob = getattr(segment, "probability", 0.95)
        total_probability += prob
    
    avg_confidence = (total_probability / max(segment_count, 1)) * 100
    confidence_adjustments = 0
    
    if len(text) < 10:
        confidence_adjustments -= 15
    
    number_ratio = len(re.findall(r'\d', text)) / max(len(text), 1)
    if number_ratio > 0.15:
        confidence_adjustments -= 10
    
    words = text.split()
    if len(words) > 5:
        unique_words = len(set(words))
        word_repeat_ratio = 1 - (unique_words / len(words))
        if word_repeat_ratio > 0.3:
            confidence_adjustments -= 10
    
    final_confidence = max(0, min(100, avg_confidence + confidence_adjustments))
    
    if final_confidence >= 90:
        reliability = "very_high"
    elif final_confidence >= 75:
        reliability = "high"
    elif final_confidence >= 60:
        reliability = "medium"
    elif final_confidence >= 40:
        reliability = "low"
    else:
        reliability = "very_low"
    
    return {
        "confidence": round(final_confidence, 1),
        "reliability": reliability,
        "segment_count": segment_count,
    }
