"""Translation operations module."""

from openai import OpenAI
import os
from typing import Optional
from src.logger import get_logger
from dotenv import load_dotenv

logger = get_logger(__name__)
load_dotenv()

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
        self.chunk_size = 2000  # Characters per chunk (roughly 500 tokens)
        logger.info("Translation service initialized (OpenAI 4o mini)")
    
    def _split_text_into_chunks(self, text: str) -> list:
        """
        Split text into chunks by sentence boundaries to avoid breaking meaning.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        # Split by sentences (., !, ?)
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Split text into {len(chunks)} chunks for translation")
        return chunks
    
    def translate_text(
        self,
        text: str,
        source_lang: str = "vi",
        target_lang: str = "en"
    ) -> str:
        """
        Translate text from source to target language using OpenAI 4o mini.
        Handles large texts by splitting into chunks.
        
        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'vi')
            
        Returns:
            Translated text
        """
        if not text.strip():
            logger.warning("Received empty text for translation")
            return ""
        
        try:
            # Enforce Vietnamese -> English translations only
            source_lang = "vi"
            target_lang = "en"
            logger.info(f"Translation request received")
            logger.info(f"Text to translate (length: {len(text)}): '{text[:200]}'{'...' if len(text) > 200 else ''}")
            logger.info(f"From {source_lang} to {target_lang}")
            
            # Split text into chunks if needed
            chunks = self._split_text_into_chunks(text)
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Translating chunk {i + 1}/{len(chunks)} ({len(chunk)} chars)")
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional translator. Translate Vietnamese text to English accurately and naturally. Respond only with the translation."
                        },
                        {
                            "role": "user",
                            "content": f"Translate this Vietnamese text to English:\n\n{chunk}"
                        }
                    ],
                    temperature=0.3
                )
                
                translated = response.choices[0].message.content.strip()
                logger.info(f"Chunk {i + 1} translation: '{translated[:100]}'{'...' if len(translated) > 100 else ''}")
                translated_chunks.append(translated)
            
            # Combine all translated chunks
            final_translation = " ".join(translated_chunks)
            logger.info(f"Final translation (length: {len(final_translation)}): '{final_translation[:200]}'{'...' if len(final_translation) > 200 else ''}")
            return final_translation
            
        except Exception as e:
            logger.error(f"Error translating text: {e}", exc_info=True)
            return text  # Return original text on error
