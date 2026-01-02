"""Configuration management using environment variables."""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Translation Configuration
        self.source_language = os.getenv("SOURCE_LANGUAGE", "vi")
        self.target_language = os.getenv("TARGET_LANGUAGE", "en")
        
        # Audio Configuration
        self.audio_sample_rate = int(os.getenv("AUDIO_SAMPLE_RATE", 16000))
        self.audio_chunk_duration = int(os.getenv("AUDIO_CHUNK_DURATION", 10))
        self.whisper_model_size = os.getenv("WHISPER_MODEL_SIZE", "small")
        
        # Database Configuration
        self.db_path = os.getenv("DB_PATH", "translations.db")
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


# Load settings
settings = Settings()

