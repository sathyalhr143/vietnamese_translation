"""Pydantic models for data validation and serialization."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import numpy as np


class AudioData(BaseModel):
    """Audio data model."""
    data: list = Field(..., description="Audio samples")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    duration_seconds: float = Field(..., description="Duration of audio in seconds")
    
    class Config:
        arbitrary_types_allowed = True


class TranscriptionResult(BaseModel):
    """Whisper transcription result model."""
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language code")
    confidence: float = Field(default=0.0, description="Transcription confidence score")
    duration: float = Field(..., description="Audio duration in seconds")


class TranslationRecord(BaseModel):
    """Translation record model."""
    id: Optional[int] = Field(None, description="Database record ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="When translation occurred")
    source_language: str = Field(..., description="Source language code (e.g., 'en')")
    target_language: str = Field(..., description="Target language code (e.g., 'vi')")
    source_text: str = Field(..., description="Original transcribed text")
    translated_text: str = Field(..., description="Translated text")
    duration_seconds: float = Field(default=0.0, description="Audio duration in seconds")
    confidence: float = Field(default=0.0, description="Transcription confidence score")
    status: str = Field(default="completed", description="Translation status")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class TranslationResponse(BaseModel):
    """API response model for a single translation."""
    translation_id: int = Field(..., description="Unique translation ID")
    source_language: str = Field(..., description="Source language")
    target_language: str = Field(..., description="Target language")
    source_text: str = Field(..., description="Original text")
    translated_text: str = Field(..., description="Translated text")
    duration: float = Field(..., description="Audio duration")
    timestamp: datetime = Field(..., description="Timestamp")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class TranslationConfig(BaseModel):
    """Configuration model for translation parameters."""
    source_language: str = Field(default="en", description="Source language code")
    target_language: str = Field(default="vi", description="Target language code")
    audio_sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    audio_chunk_duration: int = Field(default=5, description="Audio chunk duration in seconds")
    whisper_model_size: str = Field(default="base", description="Whisper model size")
    db_path: str = Field(default="translations.db", description="Path to SQLite database")
    
    class Config:
        validate_assignment = True


class AudioProcessingConfig(BaseModel):
    """Configuration for audio processing."""
    sample_rate: int = Field(default=16000, description="Sample rate in Hz")
    chunk_duration: int = Field(default=5, description="Duration per chunk in seconds")
    model_size: str = Field(default="base", description="Whisper model size")
    language: str = Field(default="en", description="Language code")


class DatabaseConfig(BaseModel):
    """Configuration for database operations."""
    db_path: str = Field(default="translations.db", description="Database file path")
    timeout: int = Field(default=5, description="Database connection timeout in seconds")
