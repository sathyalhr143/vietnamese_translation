"""FastAPI application for Vietnamese translation with file upload and live recording."""

import os
import io
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the web interface."""
    return get_html_interface()


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
        from models import TranslationRecord
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
        
        # Load and transcribe audio
        import librosa
        audio_data, sr = librosa.load(temp_path, sr=translator.config.audio_sample_rate)
        
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
        from models import TranslationRecord
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
                        from models import TranslationRecord
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


# ==================== HTML Interface ====================

def get_html_interface() -> str:
    """Generate HTML interface for the translation service."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vietnamese Translation Service</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
                padding-top: 20px;
            }
            
            h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .subtitle {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            
            .tab-btn {
                padding: 12px 24px;
                border: none;
                border-radius: 8px 8px 0 0;
                background: rgba(255, 255, 255, 0.3);
                color: white;
                cursor: pointer;
                font-size: 1em;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            
            .tab-btn.active {
                background: white;
                color: #667eea;
            }
            
            .tab-btn:hover {
                background: rgba(255, 255, 255, 0.5);
            }
            
            .tab-content {
                display: none;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            .tab-content.active {
                display: block;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            
            textarea, input[type="text"], input[type="file"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s ease;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            textarea:focus, input[type="text"]:focus, input[type="file"]:focus {
                outline: none;
                border-color: #667eea;
            }
            
            textarea {
                resize: vertical;
                min-height: 120px;
            }
            
            button {
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            button:hover {
                background: #764ba2;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            
            .result-box {
                background: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                display: none;
            }
            
            .result-box.show {
                display: block;
                animation: slideIn 0.3s ease;
            }
            
            .result-item {
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 1px solid #ddd;
            }
            
            .result-item:last-child {
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }
            
            .result-label {
                font-weight: 600;
                color: #667eea;
                margin-bottom: 5px;
                font-size: 0.9em;
                text-transform: uppercase;
            }
            
            .result-text {
                color: #333;
                line-height: 1.6;
            }
            
            .status {
                padding: 10px 15px;
                border-radius: 8px;
                margin-top: 15px;
                text-align: center;
            }
            
            .status.loading {
                background: #fff3cd;
                color: #856404;
            }
            
            .status.success {
                background: #d4edda;
                color: #155724;
            }
            
            .status.error {
                background: #f8d7da;
                color: #721c24;
            }
            
            .recording-controls {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            
            .record-btn {
                padding: 12px 24px;
                background: #e74c3c;
                color: white;
            }
            
            .record-btn:hover {
                background: #c0392b;
            }
            
            .record-btn.recording {
                animation: pulse 1s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            .stop-btn {
                padding: 12px 24px;
                background: #95a5a6;
                color: white;
            }
            
            .stop-btn:hover {
                background: #7f8c8d;
            }
            
            .history-list {
                margin-top: 20px;
            }
            
            .history-item {
                background: #f9f9f9;
                padding: 15px;
                border-left: 4px solid #667eea;
                margin-bottom: 10px;
                border-radius: 4px;
            }
            
            .history-time {
                font-size: 0.9em;
                color: #999;
                margin-bottom: 8px;
            }
            
            .history-source {
                margin-bottom: 10px;
            }
            
            .history-translation {
                color: #667eea;
                font-weight: 500;
            }
            
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .file-input-wrapper {
                position: relative;
                overflow: hidden;
                display: inline-block;
                width: 100%;
            }
            
            .file-input-label {
                display: block;
                padding: 12px;
                background: #f5f5f5;
                border: 2px dashed #667eea;
                border-radius: 8px;
                cursor: pointer;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .file-input-label:hover {
                background: #ede7f6;
            }
            
            input[type="file"] {
                display: none;
            }
            
            @media (max-width: 768px) {
                h1 { font-size: 1.8em; }
                .tabs { flex-direction: column; }
                .tab-btn { width: 100%; border-radius: 8px; }
                .tab-content { padding: 20px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🌐 Vietnamese Translation</h1>
                <p class="subtitle">Real-time Vietnamese ↔ English Translation Service</p>
            </header>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('text')">📝 Text Translation</button>
                <button class="tab-btn" onclick="switchTab('audio')">🎤 Upload Audio</button>
                <button class="tab-btn" onclick="switchTab('live')">🔴 Live Recording</button>
                <button class="tab-btn" onclick="switchTab('history')">📚 History</button>
            </div>
            
            <!-- Text Translation Tab -->
            <div id="text" class="tab-content active">
                <h2>Text Translation</h2>
                <div class="form-group">
                    <label for="text-input">Vietnamese Text</label>
                    <textarea id="text-input" placeholder="Enter Vietnamese text here..."></textarea>
                </div>
                <button onclick="translateText()">Translate</button>
                <div id="text-result" class="result-box">
                    <div class="result-item">
                        <div class="result-label">Source (Vietnamese)</div>
                        <div class="result-text" id="text-source"></div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Translation (English)</div>
                        <div class="result-text" id="text-translation"></div>
                    </div>
                </div>
                <div id="text-status"></div>
            </div>
            
            <!-- Audio Upload Tab -->
            <div id="audio" class="tab-content">
                <h2>Audio File Translation</h2>
                <div class="form-group">
                    <label for="audio-file">Select Audio File (WAV, MP3, OGG, FLAC)</label>
                    <div class="file-input-wrapper">
                        <label class="file-input-label" for="audio-file">
                            Click to upload or drag & drop
                        </label>
                        <input type="file" id="audio-file" accept="audio/*">
                    </div>
                </div>
                <button onclick="translateAudio()">Translate Audio</button>
                <div id="audio-result" class="result-box">
                    <div class="result-item">
                        <div class="result-label">Transcription (Vietnamese)</div>
                        <div class="result-text" id="audio-source"></div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Translation (English)</div>
                        <div class="result-text" id="audio-translation"></div>
                    </div>
                    <div class="result-item">
                        <div class="result-label">Duration</div>
                        <div class="result-text" id="audio-duration"></div>
                    </div>
                </div>
                <div id="audio-status"></div>
            </div>
            
            <!-- Live Recording Tab -->
            <div id="live" class="tab-content">
                <h2>Live Audio Recording</h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Record audio directly from your microphone and get real-time translations.
                </p>
                <div class="recording-controls">
                    <button class="record-btn" id="record-btn" onclick="startRecording()">🔴 Start Recording</button>
                    <button class="stop-btn" id="stop-btn" onclick="stopRecording()" disabled>Stop Recording</button>
                </div>
                <div id="live-result" class="result-box">
                    <div id="live-translations"></div>
                </div>
                <div id="live-status"></div>
            </div>
            
            <!-- History Tab -->
            <div id="history" class="tab-content">
                <h2>Translation History</h2>
                <button onclick="loadHistory()" style="margin-bottom: 20px;">Load History</button>
                <div id="history-list" class="history-list"></div>
                <div id="history-status"></div>
            </div>
        </div>
        
        <script>
            let mediaRecorder = null;
            let audioChunks = [];
            let websocket = null;
            
            // Tab switching
            function switchTab(tabName) {
                // Hide all tabs
                const tabs = document.querySelectorAll('.tab-content');
                tabs.forEach(tab => tab.classList.remove('active'));
                
                // Remove active class from buttons
                const buttons = document.querySelectorAll('.tab-btn');
                buttons.forEach(btn => btn.classList.remove('active'));
                
                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }
            
            // Text Translation
            async function translateText() {
                const text = document.getElementById('text-input').value.trim();
                if (!text) {
                    showStatus('text-status', 'Please enter text to translate', 'error');
                    return;
                }
                
                showStatus('text-status', 'Translating...', 'loading');
                
                try {
                    const response = await fetch('/api/translate/text', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text, source_language: 'vi', target_language: 'en' })
                    });
                    
                    if (!response.ok) throw new Error('Translation failed');
                    
                    const data = await response.json();
                    document.getElementById('text-source').textContent = data.source_text;
                    document.getElementById('text-translation').textContent = data.translated_text;
                    document.getElementById('text-result').classList.add('show');
                    showStatus('text-status', 'Translation complete!', 'success');
                } catch (error) {
                    showStatus('text-status', 'Error: ' + error.message, 'error');
                }
            }
            
            // Audio Upload
            async function translateAudio() {
                const fileInput = document.getElementById('audio-file');
                if (!fileInput.files.length) {
                    showStatus('audio-status', 'Please select an audio file', 'error');
                    return;
                }
                
                showStatus('audio-status', 'Processing audio...', 'loading');
                
                try {
                    const formData = new FormData();
                    formData.append('file', fileInput.files[0]);
                    
                    const response = await fetch('/api/translate/audio', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) throw new Error('Audio translation failed');
                    
                    const data = await response.json();
                    document.getElementById('audio-source').textContent = data.source_text;
                    document.getElementById('audio-translation').textContent = data.translated_text;
                    document.getElementById('audio-duration').textContent = data.duration_seconds.toFixed(2) + ' seconds';
                    document.getElementById('audio-result').classList.add('show');
                    showStatus('audio-status', 'Translation complete!', 'success');
                } catch (error) {
                    showStatus('audio-status', 'Error: ' + error.message, 'error');
                }
            }
            
            // Live Recording
            async function startRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.start(2000); // Send chunks every 2 seconds
                    
                    document.getElementById('record-btn').disabled = true;
                    document.getElementById('record-btn').classList.add('recording');
                    document.getElementById('stop-btn').disabled = false;
                    
                    // Connect WebSocket
                    connectWebSocket();
                    showStatus('live-status', 'Recording... Speak into your microphone', 'success');
                } catch (error) {
                    showStatus('live-status', 'Microphone access denied: ' + error.message, 'error');
                }
            }
            
            function stopRecording() {
                if (mediaRecorder) {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    
                    document.getElementById('record-btn').disabled = false;
                    document.getElementById('record-btn').classList.remove('recording');
                    document.getElementById('stop-btn').disabled = true;
                    
                    if (websocket) websocket.close();
                    
                    showStatus('live-status', 'Recording stopped', 'success');
                }
            }
            
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                websocket = new WebSocket(protocol + '//' + window.location.host + '/ws/live-translate');
                
                websocket.onopen = () => {
                    showStatus('live-status', 'Connected to live translation server', 'success');
                };
                
                websocket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.error) {
                        showStatus('live-status', 'Error: ' + data.error, 'error');
                    } else {
                        addLiveTranslation(data);
                    }
                };
                
                websocket.onerror = () => {
                    showStatus('live-status', 'WebSocket connection error', 'error');
                };
                
                mediaRecorder.ondataavailable = (event) => {
                    if (websocket && websocket.readyState === WebSocket.OPEN) {
                        websocket.send(event.data);
                    }
                };
            }
            
            function addLiveTranslation(data) {
                const container = document.getElementById('live-translations');
                const item = document.createElement('div');
                item.className = 'history-item';
                item.innerHTML = `
                    <div class="history-source"><strong>Vietnamese:</strong> ${escapeHtml(data.source_text)}</div>
                    <div class="history-translation"><strong>English:</strong> ${escapeHtml(data.translated_text)}</div>
                `;
                container.insertBefore(item, container.firstChild);
                document.getElementById('live-result').classList.add('show');
            }
            
            // Translation History
            async function loadHistory() {
                showStatus('history-status', 'Loading history...', 'loading');
                
                try {
                    const response = await fetch('/api/history?limit=20');
                    if (!response.ok) throw new Error('Failed to load history');
                    
                    const data = await response.json();
                    const container = document.getElementById('history-list');
                    container.innerHTML = '';
                    
                    if (data.translations.length === 0) {
                        container.innerHTML = '<p style="color: #999; text-align: center;">No translations yet</p>';
                    } else {
                        data.translations.forEach(t => {
                            const item = document.createElement('div');
                            item.className = 'history-item';
                            item.innerHTML = `
                                <div class="history-time">${new Date(t.timestamp).toLocaleString()}</div>
                                <div><strong>Vietnamese:</strong> ${escapeHtml(t.source_text)}</div>
                                <div class="history-translation"><strong>English:</strong> ${escapeHtml(t.translated_text)}</div>
                            `;
                            container.appendChild(item);
                        });
                    }
                    
                    showStatus('history-status', `Showing ${data.returned} of ${data.total_translations} translations`, 'success');
                } catch (error) {
                    showStatus('history-status', 'Error: ' + error.message, 'error');
                }
            }
            
            // Utility Functions
            function showStatus(elementId, message, type) {
                const element = document.getElementById(elementId);
                element.innerHTML = `<div class="status ${type}">${message}</div>`;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            // Drag and drop for file input
            const fileInput = document.getElementById('audio-file');
            const fileLabel = document.querySelector('.file-input-label');
            
            fileLabel.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileLabel.style.background = '#ede7f6';
            });
            
            fileLabel.addEventListener('dragleave', () => {
                fileLabel.style.background = '';
            });
            
            fileLabel.addEventListener('drop', (e) => {
                e.preventDefault();
                fileLabel.style.background = '';
                fileInput.files = e.dataTransfer.files;
            });
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
