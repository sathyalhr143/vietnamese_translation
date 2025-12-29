# Live Real-Time Language Translator

A modular, production-ready AI-powered live translation system using OpenAI Whisper for accurate speech recognition and GPT-4o mini for superior translation quality. Built with Pydantic for robust data validation and SQLite for persistent transcript storage.

## Features

- 🎤 **Real-time Audio Capture**: Records live audio from microphone
- 🤖 **OpenAI Whisper**: Accurate speech-to-text transcription (local)
- 🌐 **GPT-4o mini**: Advanced translation with superior context awareness
- 💾 **Automatic Storage**: Saves all transcripts and translations to SQLite database
- 📊 **History Tracking**: Query and review translation history anytime
- 🏗️ **Modular Architecture**: Clean separation of concerns with Pydantic models
- ✅ **Type-Safe**: Full Pydantic validation for all data structures

## Project Structure

```
vienamese_translation/
├── main.py                  # Entry point
├── live_translator.py       # Main orchestration
├── audio.py                # Audio capture and transcription
├── translator.py           # Translation operations
├── database.py             # Database operations
├── models.py               # Pydantic data models
├── config.py               # Configuration management
├── __init__.py             # Package initialization
├── requirements.txt        # Dependencies
├── .env.example            # Environment variables template
├── translations.db         # SQLite database (auto-created)
└── README.md              # Documentation
```

## Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd vienamese_translation
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up OpenAI API key:
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage

### Option 1: Single Translation
```python
from live_translator import LiveTranslator
from models import TranslationConfig

config = TranslationConfig(source_language="en", target_language="vi")
translator = LiveTranslator(config=config)

result = translator.translate_stream(duration=5)
print(f"Source: {result.source_text}")
print(f"Translation: {result.translated_text}")
```

### Option 2: Continuous Live Translation
```bash
python main.py
```

Records and translates audio in real-time. Press `Ctrl+C` to stop.

### Option 3: View Translation History
```python
from live_translator import LiveTranslator
from models import TranslationConfig

config = TranslationConfig(source_language="en", target_language="vi")
translator = LiveTranslator(config=config)

history = translator.get_translation_history()
for entry in history:
    print(f"{entry.source_text} → {entry.translated_text}")
```

### Option 4: Query by Language Pair
```python
translator = LiveTranslator()
en_vi_translations = translator.get_translations_by_language_pair("en", "vi")
```

## Modules

### `live_translator.py`
Main orchestration class that coordinates the translation pipeline.

### `audio.py`
Handles audio capture from microphone and Whisper transcription.

### `translator.py`
Manages translation using OpenAI GPT-4o mini.

### `database.py`
Handles all SQLite database operations.

### `models.py`
Pydantic data models for validation and serialization.

### `config.py`
Environment-based configuration using Pydantic Settings.

## Configuration

Edit `.env` to customize:
```env
OPENAI_API_KEY=your_key_here
SOURCE_LANGUAGE=en
TARGET_LANGUAGE=vi
AUDIO_SAMPLE_RATE=16000
AUDIO_CHUNK_DURATION=5
WHISPER_MODEL_SIZE=base
DB_PATH=./translations.db
LOG_LEVEL=INFO
```

## Supported Languages

Supports any language pair that OpenAI Whisper and GPT-4o mini support, including:
- English, Spanish, French, German, Chinese, Japanese, Korean, Portuguese, Russian, Vietnamese, and many more

## Database Schema

### translations table
- `id`: Unique identifier
- `timestamp`: When translation occurred
- `source_language`: Source language code
- `target_language`: Target language code
- `source_text`: Original transcribed text
- `translated_text`: Translated text
- `duration_seconds`: Audio duration
- `confidence`: Transcription confidence score
- `status`: Translation status

## Notes

- First run downloads the Whisper model (~140MB for 'base' model)
- Requires microphone access
- Requires OpenAI API key (set in `.env` file)
- Uses OpenAI's GPT-4o mini for translations (~$0.15 per 1M input tokens)
- Models are cached locally for fast subsequent transcriptions
- All data is stored locally in SQLite database

## Future Enhancements

- [ ] Web UI for visualization
- [ ] Real-time dashboard
- [ ] Audio file input
- [ ] Batch processing
- [ ] API server (FastAPI)
- [ ] Performance metrics and analytics
