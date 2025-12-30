"""Main orchestration module for live translation pipeline."""

from typing import Optional, List
from src.models import TranslationConfig, TranslationResponse, TranslationRecord, AudioProcessingConfig, DatabaseConfig
from src.database import TranslationDatabase
from src.audio import AudioProcessor
from src.translator import Translator
from datetime import datetime
from src.logger import get_logger

logger = get_logger(__name__)


class LiveTranslator:
    """Main class orchestrating the live translation pipeline."""
    
    def __init__(
        self,
        config: Optional[TranslationConfig] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize LiveTranslator with configuration.
        
        Args:
            config: TranslationConfig instance. If None, uses defaults.
            api_key: OpenAI API key. If None, reads from environment.
        """
        self.config = config or TranslationConfig()
        
        # Initialize components with their configs
        audio_config = AudioProcessingConfig(
            sample_rate=self.config.audio_sample_rate,
            chunk_duration=self.config.audio_chunk_duration,
            model_size=self.config.whisper_model_size,
            language=self.config.source_language
        )
        
        db_config = DatabaseConfig(db_path=self.config.db_path)
        
        self.audio_processor = AudioProcessor(audio_config)
        self.database = TranslationDatabase(db_config)
        self.translator = Translator(api_key)
        
        logger.info(f"LiveTranslator initialized: {self.config.source_language} → {self.config.target_language}")
    
    def translate_stream(self, duration: Optional[int] = None) -> TranslationResponse:
        """
        Capture, transcribe, and translate audio in real-time.
        
        Args:
            duration: Duration of audio to capture in seconds. If None, uses config value.
            
        Returns:
            TranslationResponse instance
        """
        if duration is None:
            duration = self.config.audio_chunk_duration
        
        try:
            # Step 1: Record audio
            audio_data = self.audio_processor.record_audio(duration)
            
            # Step 2: Transcribe with Whisper
            transcription = self.audio_processor.transcribe_audio(audio_data)
            source_text = transcription.text
            
            if not source_text:
                logger.warning("No speech detected in audio")
                return None
            
            # Step 3: Translate text
            translated_text = self.translator.translate_text(
                source_text,
                source_lang=self.config.source_language,
                target_lang=self.config.target_language
            )
            
            # Step 4: Create translation record
            record = TranslationRecord(
                source_language=self.config.source_language,
                target_language=self.config.target_language,
                source_text=source_text,
                translated_text=translated_text,
                duration_seconds=audio_data.duration_seconds,
                confidence=transcription.confidence
            )
            
            # Step 5: Store in database
            translation_id = self.database.insert_translation(record)
            
            # Step 6: Return response
            response = TranslationResponse(
                translation_id=translation_id,
                source_language=self.config.source_language,
                target_language=self.config.target_language,
                source_text=source_text,
                translated_text=translated_text,
                duration=audio_data.duration_seconds,
                timestamp=datetime.now()
            )
            
            return response
        except Exception as e:
            logger.error(f"Error in translation pipeline: {e}")
            raise
    
    def continuous_translation(self, chunk_duration: Optional[int] = None):
        """
        Run continuous live translation (infinite loop).
        
        Args:
            chunk_duration: Duration of each audio chunk in seconds. If None, uses config value.
        """
        if chunk_duration is None:
            chunk_duration = self.config.audio_chunk_duration
        
        logger.info("Starting continuous translation. Press Ctrl+C to stop.")
        try:
            while True:
                result = self.translate_stream(duration=chunk_duration)
                if result:
                    print("\n" + "="*70)
                    print(f"[{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]")
                    print(f"Source ({result.source_language}): {result.source_text}")
                    print(f"Translation ({result.target_language}): {result.translated_text}")
                    print(f"Translation ID: {result.translation_id}")
                    print("="*70 + "\n")
        except KeyboardInterrupt:
            logger.info("Translation stopped by user")
    
    def get_translation_history(self) -> List[TranslationRecord]:
        """Retrieve all translation history from database."""
        return self.database.get_all_translations()
    
    def get_translation_by_id(self, translation_id: int) -> Optional[TranslationRecord]:
        """Retrieve a specific translation by ID."""
        return self.database.get_translation_by_id(translation_id)
    
    def get_translations_by_language_pair(
        self,
        source_lang: str,
        target_lang: str
    ) -> List[TranslationRecord]:
        """Retrieve translations for a specific language pair."""
        return self.database.get_translations_by_language_pair(source_lang, target_lang)
