"""Live Translation Application.

A modular, AI-powered real-time language translator using OpenAI Whisper and GPT-4o mini.
"""

__version__ = "1.0.0"
__author__ = "Translation Team"

# Lazy import to avoid issues with heavy dependencies like whisper
def __getattr__(name):
    if name == "LiveTranslator":
        from .live_translator import LiveTranslator
        return LiveTranslator
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

from .models import (
    TranslationConfig,
    TranslationResponse,
    TranslationRecord,
    AudioData,
    TranscriptionResult
)
from .config import settings

__all__ = [
    "LiveTranslator",
    "TranslationConfig",
    "TranslationResponse",
    "TranslationRecord",
    "AudioData",
    "TranscriptionResult",
    "settings"
]
