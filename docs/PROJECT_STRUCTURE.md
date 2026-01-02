# Project Structure

This is the **Streamlit Branch** of the Vietnamese Translation Service, optimized for web UI deployment.

## Directory Layout

```
vienamese_translation/
├── streamlit_app.py              # Main Streamlit web interface
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (DO NOT COMMIT)
├── .env.example                  # Template for .env
├── .gitignore                    # Git ignore rules
├── Dockerfile                    # Docker container configuration
├── docker-compose.yml            # Docker Compose setup
├── render.yaml                   # Render deployment config
├── start.sh                      # Quick start script
├── pyproject.toml                # Project metadata
│
├── src/                          # Core application modules
│   ├── __init__.py
│   ├── app.py                    # FastAPI backend server
│   ├── audio.py                  # Audio processing & Whisper transcription
│   ├── translator.py             # OpenAI GPT-4o translation (chunked)
│   ├── database.py               # SQLite database operations
│   ├── models.py                 # Pydantic data models
│   ├── config.py                 # Configuration management
│   ├── logger.py                 # Logging setup
│   └── live_translator.py        # Translation orchestrator
│
├── docs/                         # Documentation
│   ├── README.md                 # Main documentation
│   ├── API_GUIDE.md              # REST API reference
│   ├── COMPLETION_STATUS.md      # Project status
│   ├── START_HERE.md             # Getting started guide
│   └── ...other guides
│
├── logs/                         # Application logs (created at runtime)
└── .streamlit/                   # Streamlit configuration (created at runtime)
```

## Core Files

### `streamlit_app.py` (Frontend)
- Main Streamlit web interface
- 3 tabs: Text Translation, Audio Translation, History
- File upload handling with size validation
- Displays results with confidence scores and metadata

### `src/app.py` (Backend)
- FastAPI REST API server
- Endpoints: `/api/translate/text`, `/api/translate/audio`, `/api/history`
- Handles file uploads and processing
- Returns JSON responses

### `src/audio.py` (Audio Processing)
- Whisper transcription with confidence calculation
- Audio file chunking for large files (>25 MB)
- Supports WAV, MP3, OGG, FLAC formats
- Calculates confidence from log probabilities: `exp(avg_logprob)`

### `src/translator.py` (Translation)
- OpenAI GPT-4o mini translation
- **Text chunking** for long transcriptions (>2000 chars)
- Processes chunks independently
- Combines results preserving context

### `src/database.py` (Persistence)
- SQLite database for translation history
- Stores: source text, translation, metadata, timestamp
- Query by language pair, limit results

### `src/models.py` (Data Validation)
- Pydantic models for request/response validation
- Type safety across application

## Configuration

All settings in `.env`:
- `OPENAI_API_KEY` - Required for translations
- `WHISPER_MODEL_SIZE` - tiny/base/small/medium/large
- `SOURCE_LANGUAGE` - vi (Vietnamese)
- `TARGET_LANGUAGE` - en (English)
- `DB_PATH` - Database file location
- `LOG_LEVEL` - DEBUG/INFO/WARNING/ERROR

## Deployment

### Local Development
```bash
./start.sh
```

### Docker
```bash
docker-compose up
```

### Render (Cloud)
- Push to GitHub
- Connect to Render
- Set `OPENAI_API_KEY` environment variable
- Auto-deploys from render.yaml

## Removed Files (from original project)

This branch removed:
- ❌ `main.py` - Old CLI interface
- ❌ `test_api.py` - Test utilities
- ❌ `pipeline_monolith.py` - Monolithic pipeline
- ❌ `setup.sh` - Old setup script
- ❌ `server/` - Old server code

These are not needed for Streamlit-focused deployment.

## Dependencies

Key packages:
- `streamlit` - Web UI
- `fastapi` + `uvicorn` - REST API backend
- `openai-whisper` - Speech-to-text
- `openai` - Translation API
- `pydub` - Audio chunking
- `pydantic` - Data validation
- `librosa` - Audio analysis

See `requirements.txt` for full list.

## Development

Run backend and frontend simultaneously:

**Terminal 1** (Backend):
```bash
source .venv/bin/activate
python -m uvicorn src.app:app --reload --port 8000
```

**Terminal 2** (Frontend):
```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

Access:
- Frontend: http://localhost:8501
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## Branch Purpose

This is the **streamlit_vi_trans** branch:
- ✅ Optimized for Streamlit UI deployment
- ✅ Cleaned up unnecessary files
- ✅ Simplified Docker configuration
- ✅ Ready for Render cloud deployment
- ✅ Focus on web interface + REST API backend

For live recording/WebRTC features, use a different branch (deferred due to complexity).
