from pathlib import Path
from typing import Dict

def validate_audio(audio_path: str) -> Dict:
    path = Path(audio_path)
    validation = {
        "valid": True,
        "issues": [],
        "file_size_mb": 0,
        "estimated_duration": 0,
        "quality_level": "acceptable",
    }
    
    if not path.exists():
        validation["valid"] = False
        validation["issues"].append("file_not_found")
        return validation
    
    file_size_bytes = path.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)
    validation["file_size_mb"] = round(file_size_mb, 2)
    
    if file_size_bytes == 0:
        validation["valid"] = False
        validation["issues"].append("empty_file")
        validation["quality_level"] = "very_poor"
        return validation
    
    estimated_duration = file_size_mb / 1.0
    validation["estimated_duration"] = round(estimated_duration, 1)
    
    if estimated_duration < 0.5:
        validation["issues"].append("very_short_audio")
        validation["quality_level"] = "poor"
    
    ext = path.suffix.lower()
    supported_formats = ['.wav', '.mp3', '.ogg', '.webm', '.m4a', '.flac', '.opus']
    
    if ext not in supported_formats:
        validation["issues"].append(f"unusual_format_{ext}")
    
    if not validation["issues"]:
        validation["quality_level"] = "good"
    
    validation["recommendation"] = "do_not_process" if validation["issues"] else "process_normally"
    
    return validation
