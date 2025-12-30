"""Main entry point for the live translation application."""

import os
from dotenv import load_dotenv
from live_translator import LiveTranslator
from models import TranslationConfig
from config import settings
from logger import get_logger

# Load environment variables
load_dotenv()

# Get logger
logger = get_logger(__name__)


def main():
    """Main entry point for the translator."""
    try:
        # Initialize translator with configuration from .env
        config = TranslationConfig(
            source_language=settings.source_language,
            target_language=settings.target_language,
            whisper_model_size=settings.whisper_model_size
        )
        
        translator = LiveTranslator(config=config)
        
        # Option 1: Single translation
        # result = translator.translate_stream(duration=5)
        # if result:
        #     print("\n" + "="*70)
        #     print("Single Translation Result:")
        #     print(json.dumps(result.model_dump(), indent=2, default=str))
        #     print("="*70)
        
        # Option 2: Continuous translation (uncomment to run)
        # Force 10s chunk duration for translations
        translator.continuous_translation(chunk_duration=10)
        
        # Option 3: View translation history (uncomment to run)
        # history = translator.get_translation_history()
        # print("\n" + "="*70)
        # print("Translation History:")
        # for entry in history:
        #     print(json.dumps(entry.model_dump(), indent=2, default=str))
        # print("="*70)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure OPENAI_API_KEY is set in your .env file")
        exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
