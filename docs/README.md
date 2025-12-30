# Vietnamese Translation Service

A modern, production-ready AI-powered translation platform with **web UI**, **REST API**, and **WebSocket support**. Powered by OpenAI Whisper for speech-to-text and GPT-4o mini for high-quality translation.

## Features

- 🌐 **Web Interface**: User-friendly UI for all features
- 📝 **Text Translation**: Vietnamese to English translation
- 🎤 **Audio Upload**: Process WAV, MP3, OGG, FLAC files
- 🔴 **Live Recording**: Record audio directly from browser microphone
- 📚 **History Tracking**: View all past translations
- 🔌 **REST API**: Full API for programmatic access
- 🔗 **WebSocket**: Real-time audio streaming support
- 💾 **Persistent Storage**: SQLite database for translation history
- 🚀 **Cloud-Ready**: Optimized for Render deployment
- ✅ **Type-Safe**: Full Pydantic validation for all data

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone <repo-url>
cd vienamese_translation
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (use `.env.example` as template):
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

5. Run the server:
```bash
python -m uvicorn app:app --reload
```

6. Open browser to `http://localhost:8000`

## Project Structure

```
vienamese_translation/
├── app.py                   # FastAPI application (NEW!)
├── main.py                  # CLI entry point (original)
├── live_translator.py       # Translation orchestration
├── audio.py                 # Audio capture & transcription
├── translator.py            # Translation operations
├── database.py              # Database operations
├── models.py                # Pydantic models
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── render.yaml             # Render deployment config
├── API_GUIDE.md            # REST API documentation
├── RENDER_DEPLOYMENT.md    # Deployment guide
├── test_api.py             # API test suite
└── README.md               # This file
```

## Usage

### Web Interface

Simply open `http://localhost:8000` in your browser:

1. **Text Translation Tab**: Paste Vietnamese text, get English translation
2. **Audio Upload Tab**: Upload audio files (WAV, MP3, OGG, FLAC)
3. **Live Recording Tab**: Record directly from microphone
4. **History Tab**: View all past translations

### REST API

See [API_GUIDE.md](API_GUIDE.md) for complete documentation.

Quick examples:

**Text Translation**:
```bash
curl -X POST http://localhost:8000/api/translate/text \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào"}'
```

**Audio Upload**:
```bash
curl -X POST http://localhost:8000/api/translate/audio \
  -F "file=@audio.wav"
```

**Get History**:
```bash
curl http://localhost:8000/api/history?limit=10
```

### Python

```python
import requests

# Text translation
response = requests.post(
    'http://localhost:8000/api/translate/text',
    json={'text': 'Xin chào'}
)
print(response.json()['translated_text'])

# Audio file
with open('audio.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/translate/audio',
        files={'file': f}
    )
print(response.json()['translated_text'])
```

## Testing

Run the test suite to verify everything works:

```bash
python test_api.py
```

This will:
- Check server health
- Test text translation
- Retrieve translation history
- Test audio upload (if test file exists)

## Deployment to Render

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions.

Quick summary:
1. Push code to GitHub
2. Connect repository to Render
3. Set `OPENAI_API_KEY` environment variable
4. Render automatically deploys using `render.yaml`

Your app will be live at: `https://your-app-name.onrender.com`

## Configuration

Edit `.env` or set environment variables:

| Variable | Default | Notes |
|----------|---------|-------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `SOURCE_LANGUAGE` | `vi` | Vietnamese |
| `TARGET_LANGUAGE` | `en` | English |
| `WHISPER_MODEL_SIZE` | `small` | tiny/base/small/medium/large |
| `AUDIO_SAMPLE_RATE` | `16000` | Hz |
| `AUDIO_CHUNK_DURATION` | `10` | Seconds |
| `DB_PATH` | `translations.db` | Database file |
| `LOG_LEVEL` | `INFO` | DEBUG/INFO/WARNING/ERROR |
| `PORT` | `8000` | Server port |

## Architecture

```
┌──────────────────┐
│   Web Browser    │
└────────┬─────────┘
         │ HTTP/WebSocket
         ▼
    ┌─────────────┐
    │  FastAPI    │
    │  (uvicorn)  │
    └─────┬───────┘
          │
    ┌─────┴──────────────────┬──────────┐
    ▼                        ▼          ▼
┌─────────┐          ┌──────────────┐  ┌──────────┐
│Whisper  │          │   OpenAI     │  │ SQLite   │
│(Audio)  │          │   (GPT-4o)   │  │Database  │
└─────────┘          └──────────────┘  └──────────┘
```

## Performance

- **Whisper Model Performance**:
  - `tiny`: Fastest, ~0.5s for 10s audio
  - `base`: Fast, ~1s for 10s audio
  - `small`: Balanced (default), ~2s for 10s audio
  - `medium`/`large`: Most accurate, slower

- **API Latency**: ~2-5s for full pipeline (transcription + translation)

## Troubleshooting

### "OPENAI_API_KEY not provided"
- Make sure `.env` file exists
- Or set environment variable: `export OPENAI_API_KEY=your_key`

### Slow performance
- Reduce `WHISPER_MODEL_SIZE` to `tiny` or `base`
- Check OpenAI API rate limits

### No speech detected
- Ensure audio quality is good
- Check microphone is working
- Try a different audio file

### Server won't start
- Check if port 8000 is already in use
- Try different port: `uvicorn app:app --port 8001`

## API Endpoints

### HTTP Endpoints
- `GET /` - Web interface
- `GET /api/health` - Health check
- `POST /api/translate/text` - Translate text
- `POST /api/translate/audio` - Translate audio file
- `GET /api/history` - Get translation history
- `GET /api/translation/{id}` - Get specific translation

### WebSocket
- `WS /ws/live-translate` - Live audio streaming

See [API_GUIDE.md](API_GUIDE.md) for detailed documentation.

## Requirements

- Python 3.11+
- 2GB RAM minimum
- 5GB disk space (for Whisper models)
- OpenAI API key

## Dependencies

Core dependencies:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai-whisper` - Speech-to-text
- `openai` - Translation API
- `pydantic` - Data validation
- `librosa` - Audio processing

See `requirements.txt` for complete list.

## License

MIT License - Feel free to use this project for any purpose.

## Support

- 📖 [API Documentation](API_GUIDE.md)
- 🚀 [Deployment Guide](RENDER_DEPLOYMENT.md)
- 🐛 [Report Issues](https://github.com/your-repo/issues)

## Next Steps

1. ✅ Run locally and test all features
2. ✅ Deploy to Render (see RENDER_DEPLOYMENT.md)
3. ✅ Integrate API into your application
4. ✅ Set up monitoring and alerts
5. ✅ Upgrade to paid tier if needed

Enjoy your Vietnamese translation service! 🎉

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
