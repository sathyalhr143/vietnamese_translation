"""Configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    
    # Translation Configuration
    source_language: str = Field(default="vi", description="Source language code")
    target_language: str = Field(default="en", description="Target language code")
    
    # Audio Configuration
    audio_sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    audio_chunk_duration: int = Field(default=10, description="Audio chunk duration in seconds")
    whisper_model_size: str = Field(default="small", description="Whisper model size")
    
    # Database Configuration
    db_path: str = Field(default="translations.db", description="Path to SQLite database")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Load settings
settings = Settings()
