"""Monolithic pipeline demo

A single-file sequential pipeline to help debug flow:
- Records 10s of audio from the default microphone
- Uses Whisper to transcribe with language set to Vietnamese ("vi")
- Uses OpenAI to translate transcribed text to English ("en")
- Stores the translation in a local SQLite database `translations.db`
- Logs each step so you can inspect intermediate outputs

Usage:
    python pipeline_monolith.py

Requirements (same as project): sounddevice, numpy, whisper, openai, python-dotenv
"""

import os
import sqlite3
import logging
from datetime import datetime

import numpy as np
import sounddevice as sd
import whisper
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment (.env)")
openai.api_key = OPENAI_API_KEY

# Configuration (hard-coded to vi->en, 10s)
SOURCE_LANG = "vi"
TARGET_LANG = "en"
CHUNK_DURATION = int(os.getenv("AUDIO_CHUNK_DURATION", "10"))
SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")
DB_PATH = os.getenv("DB_PATH", "translations.db")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("pipeline_monolith")


def ensure_db(path: str):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source_language TEXT NOT NULL,
            target_language TEXT NOT NULL,
            source_text TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            duration_seconds REAL,
            confidence REAL,
            status TEXT DEFAULT 'completed'
        )
        """
    )
    conn.commit()
    return conn


def record_audio(duration: int, sample_rate: int) -> np.ndarray:
    """Record mono audio for `duration` seconds and return a numpy array."""
    logger.info(f"Recording audio for {duration} seconds...")
    frames = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait()
    audio = frames.flatten()
    logger.info("Audio recording completed")
    return audio


def transcribe_with_whisper(audio_array: np.ndarray, model_size: str, language: str) -> dict:
    """Transcribe audio using Whisper model. Returns dict with 'text' and optional 'confidence'."""
    logger.info(f"Loading Whisper model: {model_size}")
    model = whisper.load_model(model_size)
    logger.info(f"Transcribing audio with Whisper (language={language})...")
    # whisper expects either file path or numpy array
    result = model.transcribe(audio_array, language=language, fp16=False)
    text = result.get("text", "").strip()
    logger.info(f"Transcription completed: {text}")
    
    # Calculate average confidence from segments
    confidence = 0.0
    if 'segments' in result and result['segments']:
        confidences = [seg.get('avg_logprob', 0.0) for seg in result['segments']]
        # Convert log probabilities to confidence scores (0-1 range)
        # avg_logprob is typically between -1 and 0, with 0 being highest confidence
        confidence = np.mean([np.exp(c) for c in confidences]) if confidences else 0.0
    
    return {"text": text, "confidence": confidence}


def translate_with_openai(text: str, source: str, target: str) -> str:
    """Translate text using OpenAI chat completion.
    Returns translated text.
    """
    if not text.strip():
        return ""

    logger.info(f"Translating '{text}' from {source} to {target}")

    system_prompt = f"You are a professional translator. Translate the user's text from {source} to {target}. Respond with only the translated text, no explanations."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    try:
        # Use ChatCompletion API
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
        )
        translated = resp["choices"][0]["message"]["content"].strip()
        logger.info(f"Translation successful: {translated}")
        return translated
    except Exception as e:
        logger.error(f"OpenAI translation error: {e}")
        return text


def save_translation(conn: sqlite3.Connection, source, target, source_text, translated_text, duration, confidence):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO translations (source_language, target_language, source_text, translated_text, duration_seconds, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (source, target, source_text, translated_text, duration, confidence),
    )
    conn.commit()
    translation_id = cur.lastrowid
    logger.info(f"Translation {translation_id} inserted successfully")
    return translation_id


def main():
    conn = ensure_db(DB_PATH)

    try:
        # 1) Record
        audio = record_audio(CHUNK_DURATION, SAMPLE_RATE)

        # 2) Transcribe
        transcription = transcribe_with_whisper(audio, MODEL_SIZE, SOURCE_LANG)
        source_text = transcription.get("text", "")
        confidence = transcription.get("confidence", 0.0)

        if not source_text:
            logger.warning("No speech detected in this chunk.")
            return

        # 3) Translate
        translated_text = translate_with_openai(source_text, SOURCE_LANG, TARGET_LANG)

        # 4) Save
        translation_id = save_translation(conn, SOURCE_LANG, TARGET_LANG, source_text, translated_text, CHUNK_DURATION, confidence)

        # 5) Print summary
        print("\n" + "=" * 70)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
        print(f"Source ({SOURCE_LANG}): {source_text}")
        print(f"Translation ({TARGET_LANG}): {translated_text}")
        print(f"Translation ID: {translation_id}")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as exc:
        logger.error(f"Pipeline error: {exc}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
