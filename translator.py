"""Translation operations module."""

from openai import OpenAI
import os
from typing import Optional
from logger import get_logger

logger = get_logger(__name__)


class Translator:
    """Handle translation operations using OpenAI 4o mini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client for translations.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY environment variable.
        """
        key = api_key or os.getenv('OPENAI_API_KEY')
        if not key:
            raise ValueError("OPENAI_API_KEY not provided. Set it as an environment variable or pass it as an argument.")
        
        self.client = OpenAI(api_key=key)
        logger.info("Translation service initialized (OpenAI 4o mini)")
    
    def translate_text(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "vi"
    ) -> str:
        """
        Translate text from source to target language using OpenAI 4o mini.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'vi')
            
        Returns:
            Translated text
        """
        if not text.strip():
            return ""
        
        try:
            logger.info(f"Translating '{text}' from {source_lang} to {target_lang}")
            
            # Language names for the prompt
            lang_names = {
                "en": "English",
                "vi": "Vietnamese",
                "es": "Spanish",
                "fr": "French",
                "de": "German",
                "zh": "Chinese",
                "ja": "Japanese",
                "ko": "Korean",
                "pt": "Portuguese",
                "ru": "Russian"
            }
            
            source_lang_name = lang_names.get(source_lang, source_lang)
            target_lang_name = lang_names.get(target_lang, target_lang)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the user's text from {source_lang_name} to {target_lang_name}. Respond with only the translated text, no explanations."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3
            )
            
            translated = response.choices[0].message.content.strip()
            logger.info(f"Translation successful: {translated}")
            return translated
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text  # Return original text on error
