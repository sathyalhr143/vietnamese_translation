# FastAPI Application Guide

## Overview

The Vietnamese Translation application is now a **FastAPI web service** that provides:
- **Web UI** for easy interaction
- **REST API** endpoints for integration
- **WebSocket** support for live streaming
- **File uploads** for batch processing
- **Translation history** tracking

## Features

### 1. Web Interface
- **Text Translation**: Paste Vietnamese text and get English translation
- **Audio Upload**: Upload WAV, MP3, OGG, or FLAC files for transcription and translation
- **Live Recording**: Record audio directly from your microphone (browser-based)
- **History**: View past translations with timestamps

### 2. REST API Endpoints

#### Health Check
```http
GET /api/health
```
Returns service status.

#### Text Translation
```http
POST /api/translate/text
Content-Type: application/json

{
  "text": "Xin chào",
  "source_language": "vi",
  "target_language": "en"
}
```
Response:
```json
{
  "translation_id": 1,
  "source_language": "vi",
  "target_language": "en",
  "source_text": "Xin chào",
  "translated_text": "Hello",
  "timestamp": "2025-01-01T12:00:00"
}
```

#### Audio File Translation
```http
POST /api/translate/audio
Content-Type: multipart/form-data

file: <audio-file>
```

Supported formats: WAV, MP3, OGG, FLAC

Response:
```json
{
  "translation_id": 2,
  "source_language": "vi",
  "target_language": "en",
  "source_text": "Transcribed Vietnamese text",
  "translated_text": "Translated English text",
  "duration_seconds": 5.2,
  "confidence": 0.95,
  "timestamp": "2025-01-01T12:00:00"
}
```

#### Get Translation History
```http
GET /api/history?limit=50
```
Returns recent translations.

Response:
```json
{
  "total_translations": 100,
  "returned": 50,
  "translations": [...]
}
```

#### Get Specific Translation
```http
GET /api/translation/{translation_id}
```
Returns details of a single translation.

### 3. WebSocket Endpoint

For live audio streaming:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live-translate');

ws.onmessage = (event) => {
  const translation = JSON.parse(event.data);
  console.log(translation.translated_text);
};

// Send audio chunks as binary data
ws.send(audioBuffer);
```

## Running Locally

### Prerequisites
```bash
pip install -r requirements.txt
```

### Development
```bash
python -m uvicorn app:app --reload
```

Access at: http://localhost:8000

### Production
```bash
python app.py
```

Or with gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `SOURCE_LANGUAGE` | `vi` | Source language code |
| `TARGET_LANGUAGE` | `en` | Target language code |
| `WHISPER_MODEL_SIZE` | `small` | Whisper model size |
| `AUDIO_SAMPLE_RATE` | `16000` | Audio sample rate in Hz |
| `AUDIO_CHUNK_DURATION` | `10` | Chunk duration in seconds |
| `DB_PATH` | `translations.db` | SQLite database path |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PORT` | `8000` | Server port |

## Deployment

### Render

1. Push code to GitHub
2. Connect repository to Render
3. Render will automatically:
   - Read `render.yaml`
   - Install dependencies
   - Start FastAPI server

The app will be available at:
```
https://your-app-name.onrender.com
```

### Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t vietnamese-translation .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  vietnamese-translation
```

## Database

The app uses SQLite for translation history. Database file location:
- Development: `translations.db` (in project directory)
- Render: `/tmp/translations.db` (ephemeral storage)

**Note**: For production, upgrade to Render PostgreSQL for persistent data.

## Performance Tips

1. **Audio Processing**: Larger Whisper models are more accurate but slower
   - `tiny` / `base`: Fast, suitable for real-time
   - `small` / `medium`: Balanced
   - `large`: Most accurate, slower

2. **Batch Processing**: For large files, use `/api/translate/audio` endpoint

3. **Caching**: Consider caching frequent translations in your frontend

## Troubleshooting

### "Translator not initialized" Error
- Check `OPENAI_API_KEY` is set
- Check logs in Render Dashboard
- Try restarting the service

### Audio Upload Fails
- Ensure audio format is supported (WAV, MP3, OGG, FLAC)
- Check file size (Render free tier has limits)
- Check audio codec compatibility

### WebSocket Connection Fails
- Ensure browser supports WebSockets
- Check if CORS is properly configured
- Verify WebSocket URL protocol (ws:// or wss://)

### Slow Translation
- Model size is too large for your resources
- Reduce `WHISPER_MODEL_SIZE` to `tiny` or `base`
- Check API rate limits with OpenAI

## API Examples

### Python
```python
import requests

# Text translation
response = requests.post(
    'http://localhost:8000/api/translate/text',
    json={'text': 'Xin chào', 'source_language': 'vi'}
)
print(response.json()['translated_text'])

# Audio upload
with open('audio.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/translate/audio',
        files={'file': f}
    )
print(response.json()['translated_text'])
```

### JavaScript/Fetch
```javascript
// Text translation
const response = await fetch('/api/translate/text', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'Xin chào'})
});
const data = await response.json();
console.log(data.translated_text);
```

### cURL
```bash
# Text translation
curl -X POST http://localhost:8000/api/translate/text \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào"}'

# Audio upload
curl -X POST http://localhost:8000/api/translate/audio \
  -F "file=@audio.wav"

# History
curl http://localhost:8000/api/history?limit=10
```

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (Web UI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│    FastAPI Server       │
│  (uvicorn on port 8000) │
└──┬──────────────┬────────┘
   │              │
   ▼              ▼
┌──────────┐  ┌──────────────┐
│ Translator  │ Database     │
│ (OpenAI)  │ (SQLite)      │
└──────────┘  └──────────────┘
```

## Security Considerations

- **API Key**: Never expose `OPENAI_API_KEY` in logs or frontend
- **Rate Limiting**: Consider adding rate limiting for production
- **Authentication**: Add user authentication for production use
- **CORS**: Configure CORS properly if using from different domains
- **File Upload**: Validate file types and sizes to prevent abuse

## Future Enhancements

- [ ] Add user authentication
- [ ] Implement rate limiting
- [ ] Support more language pairs
- [ ] Add batch processing API
- [ ] WebSocket audio streaming improvements
- [ ] Database schema for persistence
- [ ] Caching layer for frequent translations
