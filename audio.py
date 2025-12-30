"""Audio capture and transcription module."""

import whisper
import sounddevice as sd
import numpy as np
from typing import Dict
from models import AudioData, TranscriptionResult, AudioProcessingConfig
from logger import get_logger

logger = get_logger(__name__)


class AudioProcessor:
    """Handle audio capture and processing with Whisper transcription."""
    
    def __init__(self, config: AudioProcessingConfig = None):
        """
        Initialize audio processor.
        
        Args:
            config: AudioProcessingConfig instance. If None, uses defaults.
        """
        self.config = config or AudioProcessingConfig()
        self.whisper_model = None
        self.load_whisper_model(self.config.model_size)
    
    def load_whisper_model(self, model_size: str = "small"):
        """
        Load OpenAI Whisper model.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        try:
            logger.info(f"Loading Whisper model: {model_size}")
            self.whisper_model = whisper.load_model(model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def record_audio(self, duration: int = None) -> AudioData:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds. If None, uses config value.
            
        Returns:
            AudioData instance
        """
        if duration is None:
            duration = self.config.chunk_duration
        
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            audio_data = sd.rec(
                int(duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            logger.info("Audio recording completed")
            
            return AudioData(
                data=audio_data.flatten().tolist(),
                sample_rate=self.config.sample_rate,
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            raise
    
    def transcribe_audio(self, audio: AudioData) -> TranscriptionResult:
        """
        Transcribe audio using Whisper.
        
        Args:
            audio: AudioData instance
            
        Returns:
            TranscriptionResult instance
        """
        if self.whisper_model is None:
            self.load_whisper_model(self.config.model_size)
        
        try:
            logger.info("Transcribing audio with Whisper...")
            
            # Convert list back to numpy array
            audio_array = np.array(audio.data, dtype=np.float32)
            
            # checking the language set in config
            print(self.config.language, "language given to whisper")
            
            result = self.whisper_model.transcribe(
                audio_array,
                language=self.config.language,
                fp16=True  # Set to False for CPU
            )
            
            text = result['text'].strip()
            logger.info(f"Transcription completed: {text}")
            
            return TranscriptionResult(
                text=text,
                language=self.config.language,
                confidence=result.get('confidence', 0.0),
                duration=audio.duration_seconds
            )
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
