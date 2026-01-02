# Vietnamese Translation Service

A modern, production-ready AI-powered translation platform with **web UI**, **REST API**, and **WebSocket support**. Powered by OpenAI Whisper for speech-to-text and GPT-4o mini for high-quality translation.

## Features

- 🌐 **Web Interface**: Streamlit-based UI for intuitive translation experience
- 📝 **Text Translation**: Vietnamese to English translation with chunked processing for long texts
- 🎤 **Audio Upload**: Process WAV, MP3, OGG, FLAC files up to 36+ MB with automatic chunking
- 📊 **Large File Support**: Automatic audio file chunking for files exceeding 25 MB Whisper API limit
- 📚 **History Tracking**: View all past translations with metadata (duration, confidence)
- 🔌 **REST API**: Full API for programmatic access
- 💾 **Persistent Storage**: SQLite database for translation history
- 🚀 **Cloud-Ready**: Optimized for Render deployment
- ✅ **Type-Safe**: Full Pydantic validation for all data
- 🧠 **Intelligent Chunking**: Sentence-aware text chunking for optimal translation quality

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

5. Start the FastAPI backend:
```bash
source .venv/bin/activate
python -m uvicorn src.app:app --reload --port 8000
```

6. In a new terminal, start the Streamlit frontend:
```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

7. Open browser to `http://localhost:8501` for the Streamlit interface

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

### Web Interface (Streamlit)

Open `http://localhost:8501` in your browser with 3 main tabs:

1. **Text Translation Tab**: 
   - Paste Vietnamese text
   - Get instant English translation
   - View translation metadata (ID, timestamp)

2. **Audio Translation Tab**: 
   - Upload audio files (WAV, MP3, OGG, FLAC)
   - Files up to 36+ MB supported (automatically chunked)
   - Displays:
     - Vietnamese transcription (from Whisper)
     - English translation
     - Duration, confidence score, translation ID

3. **History Tab**: 
   - View all past translations
   - Sort by timestamp
   - See metadata for each translation

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

## Development Roadblocks & Solutions

### 1. **Dependency Management Issues**
**Problem**: Pydantic version compatibility conflict between FastAPI and direct pydantic-settings imports.

**Solution**: Standardized imports to use `from pydantic_settings import BaseSettings` and removed redundant dependencies. Used `uv pip` for faster, more reliable dependency resolution.

---

### 2. **HTTP Exception Handling**
**Problem**: Confusion between `HTTP` and `HTTPException` in FastAPI, causing import errors.

**Solution**: Clarified that `HTTPException` from `fastapi` is the correct exception type for REST API error responses. Updated all error handling accordingly.

---

### 3. **Whisper Confidence Calculation**
**Problem**: Whisper's `avg_logprob` values are in log scale (-1 to 0), not directly interpretable as confidence (0-1 scale).

**Solution**: Implemented exponential conversion: `confidence = exp(avg_logprob)` to transform log probabilities to interpretable confidence scores between 0 and 1.

---

### 4. **Frontend Migration from HTML/CSS to Streamlit**
**Problem**: Initial HTML/CSS frontend was complex and difficult to maintain. Required switching to a more user-friendly framework.

**Solution**: Migrated to Streamlit, which provides:
- Clean, component-based UI
- Easy state management
- Built-in file upload handling
- Minimal code (~300 lines for full interface)

---

### 5. **Live Translation with WebRTC (Abandoned Feature)**
**Problem**: Attempted to implement live audio streaming using `streamlit-webrtc`, but encountered multiple issues:
- ScriptRunContext warnings from async threads
- Audio buffer resetting on every Streamlit rerun
- Audio chunks not being reliably sent to backend
- Complex state management across reruns

**Solution**: **Removed** live translation feature in favor of file upload approach. This provides:
- Better reliability
- Simpler implementation
- Similar user experience
- Easier maintenance

---

### 6. **Audio Buffer Memory Issues**
**Problem**: Using `uploaded_file.getbuffer()` created numpy array references that couldn't be resized during garbage collection, causing `BufferError: Existing exports of data: object cannot be re-sized`.

**Solution**: Changed to `uploaded_file.read()` which returns a clean copy of bytes instead of a buffer view. Wrapped in `io.BytesIO()` for file-like object compatibility.

---

### 7. **Large File Processing Limitations**
**Problem**: OpenAI Whisper API has a 25 MB file size limit. Uploading files >25 MB directly would fail.

**Solution**: Implemented intelligent audio chunking:
- Split large files into ~20 MB chunks
- Process each chunk independently with Whisper
- Combine transcriptions with proper spacing
- Seamlessly handles files up to 36+ MB in practice

---

### 8. **Translation API Failure with Long Text**
**Problem**: OpenAI GPT-4o mini was returning error response `"I'm sorry, but I can't assist with that."` when given the full 33,000+ character transcription.

**Root Cause**: Long transcriptions exceeded optimal token limits or triggered model behavior issues.

**Solution**: Implemented intelligent text chunking:
- Split transcriptions into ~2000 character chunks
- Respects sentence boundaries to maintain meaning
- Translates each chunk independently
- Combines translations with space preservation
- Maintains context and narrative flow

---

### 9. **Empty Transcription Results**
**Problem**: Initial chunked audio processing returned empty transcription text, causing downstream translation to fail.

**Solution**: Added verbose logging throughout the pipeline to identify at which stage text was being lost. Improved chunk size calculations and error handling for edge cases.

---

### 10. **Accidental File Deletion**
**Problem**: User accidentally deleted the main `streamlit_app.py` file during development.

**Solution**: Restored file from working state and implemented proper version control practices with Git commits.

---

## Lessons Learned

1. **Chunking is Essential**: Both audio and text processing benefit from intelligent chunking to work within API limits.
2. **Buffer Management**: Be careful with numpy/memory buffer references in web frameworks like Streamlit.
3. **Verbose Logging**: Detailed logging at each pipeline stage makes debugging much easier.
4. **Feature Prioritization**: Sometimes simpler features (file upload vs live streaming) provide better user experience.
5. **Token Awareness**: Always consider token limits when working with language models.
6. **Sentence Boundaries**: Respecting sentence structure when chunking preserves translation quality.

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
