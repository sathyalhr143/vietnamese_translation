"""FastAPI application for Vietnamese translation with file upload and live recording."""

import os
import io
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, WebSocket, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import asyncio
import json

from src.live_translator import LiveTranslator
from src.models import TranslationConfig, TranslationResponse
from src.logger import get_logger

logger = get_logger(__name__)

# Hard-coded configuration
SOURCE_LANGUAGE = "vi"  # Vietnamese
TARGET_LANGUAGE = "en"  # English
WHISPER_MODEL_SIZE = "small"  # Model size: tiny, base, small, medium, large

# Global translator instance
translator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global translator
    
    # Startup
    try:
        config = TranslationConfig(
            source_language=SOURCE_LANGUAGE,
            target_language=TARGET_LANGUAGE,
            whisper_model_size=WHISPER_MODEL_SIZE
        )
        translator = LiveTranslator(config=config)
        logger.info("Translator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize translator: {e}")
        raise
    
    yield
    
    # Shutdown
    translator = None
    logger.info("Translator shutdown")


# Initialize FastAPI app
app = FastAPI(
    title="Vietnamese Translation API",
    description="Real-time Vietnamese to English translation service",
    version="1.0.0",
    lifespan=lifespan
)


# ==================== Pydantic Models ====================

class TranslationRequest(BaseModel):
    """Request model for text translation."""
    text: str
    source_language: Optional[str] = "vi"
    target_language: Optional[str] = "en"


class TranslationHistoryResponse(BaseModel):
    """Response model for translation history."""
    total_translations: int
    translations: List[dict]


# ==================== REST API Endpoints ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Vietnamese Translation API",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/translate/text")
async def translate_text(request: TranslationRequest):
    """
    Translate text from Vietnamese to English.
    
    Args:
        request: TranslationRequest with text to translate
        
    Returns:
        Translation result
    """
    if not translator:
        raise HTTPException(status_code=500, detail="Translator not initialized")
    
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        translated_text = translator.translator.translate_text(
            request.text,
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        # Create translation record
        from src.models import TranslationRecord
        record = TranslationRecord(
            source_language=request.source_language,
            target_language=request.target_language,
            source_text=request.text,
            translated_text=translated_text
        )
        
        # Store in database
        translation_id = translator.database.insert_translation(record)
        
        return {
            "translation_id": translation_id,
            "source_language": request.source_language,
            "target_language": request.target_language,
            "source_text": request.text,
            "translated_text": translated_text,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/translate/audio")
async def translate_audio(file: UploadFile = File(...)):
    """
    Upload and translate audio file.
    
    Supports: WAV, MP3, OGG, FLAC, etc.
    
    Args:
        file: Audio file to translate
        
    Returns:
        Translation result with transcription and translation
    """
    if not translator:
        raise HTTPException(status_code=500, detail="Translator not initialized")
    
    # Check file type
    allowed_types = {"audio/wav", "audio/mpeg", "audio/ogg", "audio/flac", "audio/x-wav"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format. Allowed: WAV, MP3, OGG, FLAC")
    
    try:
        # Read file content
        content = await file.read()
        
        # Save temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Process audio
        logger.info(f"Processing audio file: {file.filename}")
        
        # Transcribe with Whisper
        transcription = translator.audio_processor.transcribe_audio_from_file(temp_path)
        
        if not transcription.text:
            raise HTTPException(status_code=400, detail="No speech detected in audio file")
        
        # Translate
        translated_text = translator.translator.translate_text(
            transcription.text,
            source_lang=translator.config.source_language,
            target_lang=translator.config.target_language
        )
        
        # Store in database
        from src.models import TranslationRecord
        record = TranslationRecord(
            source_language=translator.config.source_language,
            target_language=translator.config.target_language,
            source_text=transcription.text,
            translated_text=translated_text,
            duration_seconds=transcription.duration,
            confidence=transcription.confidence
        )
        
        translation_id = translator.database.insert_translation(record)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            "translation_id": translation_id,
            "source_language": translator.config.source_language,
            "target_language": translator.config.target_language,
            "source_text": transcription.text,
            "translated_text": translated_text,
            "duration_seconds": transcription.duration,
            "confidence": transcription.confidence,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def get_history(limit: int = 50):
    """
    Get translation history.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        List of recent translations
    """
    if not translator:
        raise HTTPException(status_code=500, detail="Translator not initialized")
    
    try:
        history = translator.get_translation_history()
        
        # Return last 'limit' records
        records = history[-limit:] if history else []
        
        return {
            "total_translations": len(history),
            "returned": len(records),
            "translations": [
                {
                    "id": r.id,
                    "timestamp": r.timestamp.isoformat(),
                    "source_language": r.source_language,
                    "target_language": r.target_language,
                    "source_text": r.source_text,
                    "translated_text": r.translated_text,
                    "duration_seconds": r.duration_seconds,
                    "confidence": r.confidence
                }
                for r in records
            ]
        }
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/translation/{translation_id}")
async def get_translation(translation_id: int):
    """
    Get a specific translation by ID.
    
    Args:
        translation_id: Translation ID
        
    Returns:
        Translation record
    """
    if not translator:
        raise HTTPException(status_code=500, detail="Translator not initialized")
    
    try:
        record = translator.get_translation_by_id(translation_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Translation not found")
        
        return {
            "id": record.id,
            "timestamp": record.timestamp.isoformat(),
            "source_language": record.source_language,
            "target_language": record.target_language,
            "source_text": record.source_text,
            "translated_text": record.translated_text,
            "duration_seconds": record.duration_seconds,
            "confidence": record.confidence,
            "status": record.status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WebSocket for Live Recording ====================

@app.websocket("/ws/live-translate")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for live audio streaming and translation.
    
    Protocol:
    1. Client sends audio chunks as binary data
    2. Server transcribes and translates
    3. Server sends translation results back as JSON
    """
    await websocket.accept()
    
    if not translator:
        await websocket.send_json({"error": "Translator not initialized"})
        await websocket.close()
        return
    
    try:
        logger.info("WebSocket connection established for live translation")
        
        audio_buffer = io.BytesIO()
        sample_count = 0
        
        while True:
            # Receive audio chunk from client
            data = await websocket.receive_bytes()
            audio_buffer.write(data)
            sample_count += len(data) // 2  # Assuming 16-bit audio
            
            # Process when buffer reaches ~10 seconds of audio (16000 Hz * 10 sec * 2 bytes)
            bytes_per_second = translator.config.audio_sample_rate * 2
            target_bytes = bytes_per_second * translator.config.audio_chunk_duration
            
            if audio_buffer.tell() >= target_bytes:
                try:
                    # Transcribe audio buffer
                    audio_buffer.seek(0)
                    import numpy as np
                    audio_data = np.frombuffer(audio_buffer.getvalue(), dtype=np.int16)
                    audio_data = audio_data.astype(np.float32) / 32768.0
                    
                    # Transcribe with Whisper
                    result = translator.audio_processor.whisper_model.transcribe(
                        audio_data,
                        language=translator.config.source_language,
                        task="transcribe"
                    )
                    
                    source_text = result.get("text", "").strip()
                    
                    if source_text:
                        # Translate
                        translated_text = translator.translator.translate_text(
                            source_text,
                            source_lang=translator.config.source_language,
                            target_lang=translator.config.target_language
                        )
                        
                        # Store in database
                        from src.models import TranslationRecord
                        record = TranslationRecord(
                            source_language=translator.config.source_language,
                            target_language=translator.config.target_language,
                            source_text=source_text,
                            translated_text=translated_text,
                            duration_seconds=audio_buffer.tell() / bytes_per_second
                        )
                        
                        translation_id = translator.database.insert_translation(record)
                        
                        # Send response
                        await websocket.send_json({
                            "translation_id": translation_id,
                            "source_text": source_text,
                            "translated_text": translated_text,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Reset buffer
                    audio_buffer = io.BytesIO()
                
                except Exception as e:
                    logger.error(f"WebSocket translation error: {e}")
                    await websocket.send_json({"error": str(e)})
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection closed")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
