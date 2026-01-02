# Streamlit Branch Deployment Guide

This guide covers deployment for the **streamlit_vi_trans** branch - the Streamlit-focused version.

## Quick Start (Local)

### Prerequisites
- Python 3.11+
- OpenAI API key

### Setup
```bash
# Clone and enter directory
git clone <repo-url>
cd vienamese_translation

# Use quick start script
./start.sh

# Or manual setup:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running Locally

**Option 1: Quick Start Script**
```bash
./start.sh
```

**Option 2: Manual (2 terminals needed)**

Terminal 1 - Start Backend:
```bash
source .venv/bin/activate
python -m uvicorn src.app:app --reload --port 8000
```

Terminal 2 - Start Frontend:
```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

Access at:
- 🎨 Frontend: http://localhost:8501
- 🔌 Backend: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

## Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

Access at:
- Frontend: http://localhost:8501
- Backend: http://localhost:8000

### Logs
```bash
docker-compose logs -f
```

## Render Cloud Deployment

### 1. Push to GitHub
```bash
git push origin streamlit_vi_trans
```

### 2. Connect to Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Select branch: `streamlit_vi_trans`
5. Root directory: leave empty
6. Build command: `pip install -r requirements.txt`
7. Start command: `streamlit run streamlit_app.py --server.port=8501 --server.headless=true`

### 3. Environment Variables
Add these in Render dashboard:
- `OPENAI_API_KEY` - Your OpenAI API key (secret)
- `SOURCE_LANGUAGE` - `vi`
- `TARGET_LANGUAGE` - `en`
- `WHISPER_MODEL_SIZE` - `small`
- `LOG_LEVEL` - `INFO`

### 4. Deploy
Click "Deploy" - takes 2-5 minutes

## Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `OPENAI_API_KEY` | `sk-...` | Required, keep secret |
| `SOURCE_LANGUAGE` | `vi` | Vietnamese |
| `TARGET_LANGUAGE` | `en` | English |
| `WHISPER_MODEL_SIZE` | `small` | tiny/base/small/medium/large |
| `AUDIO_SAMPLE_RATE` | `16000` | Hz |
| `AUDIO_CHUNK_DURATION` | `10` | Seconds |
| `DB_PATH` | `translations.db` | Database file |
| `LOG_LEVEL` | `INFO` | Logging level |

## Performance Tips

### Optimize for Cloud
1. **Whisper Model**: Use `tiny` or `base` for faster response
   ```
   WHISPER_MODEL_SIZE=base
   ```

2. **Database**: Keep `translations.db` local (not in version control)

3. **Caching**: Streamlit caches results automatically

### Cost Optimization
- GPT-4o mini: ~$0.15 per 1M input tokens
- Whisper: ~$0.02 per minute of audio
- Free tier includes $5 in credits

## Troubleshooting

### Port Already in Use
```bash
# Find process on port 8501
lsof -i :8501

# Kill it
kill -9 <PID>
```

### Streamlit Not Starting
```bash
# Clear cache
rm -rf ~/.streamlit
streamlit run streamlit_app.py --logger.level=debug
```

### Backend Not Responding
```bash
# Check if running
curl http://localhost:8000/api/health

# Restart
python -m uvicorn src.app:app --port 8000
```

### API Key Not Working
1. Verify it's set: `echo $OPENAI_API_KEY`
2. Check it's valid at openai.com/account/billing
3. Has available credits

### Large File Fails
- Check file size (<36 MB recommended)
- Audio should be Vietnamese
- Try with different audio format (MP3, WAV)

## Monitoring

### Logs
```bash
# Local
tail -f logs/app.log

# Docker
docker-compose logs -f streamlit

# Render
View in Render Dashboard > Logs
```

### Database
```bash
# Check translations count
sqlite3 translations.db "SELECT COUNT(*) FROM translations;"

# View recent translations
sqlite3 translations.db "SELECT * FROM translations ORDER BY timestamp DESC LIMIT 5;"
```

## Scaling

### For Higher Traffic
1. Upgrade Render plan (Standard or Pro)
2. Increase worker count if needed
3. Consider API caching layer

### Cost Considerations
- Whisper: Pay per minute
- GPT-4o mini: Pay per token
- Render: $7-12/month for standard tier

## Backup & Maintenance

### Database Backup
```bash
cp translations.db translations.db.backup
```

### Update Dependencies
```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```

## Security Notes

- ✅ Never commit `.env` file
- ✅ Use secrets for API keys in CI/CD
- ✅ Set HTTPS on production (Render does this)
- ✅ Validate file uploads (done automatically)
- ✅ Rate limit API if public-facing

## Support

- 📖 [Project README](docs/README.md)
- 📘 [API Guide](docs/API_GUIDE.md)
- 🐛 [Report Issues](https://github.com/...)
- 💬 [Discussions](https://github.com/...)

## Quick Links

- [Streamlit Docs](https://docs.streamlit.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [OpenAI Docs](https://platform.openai.com/docs)
- [Render Docs](https://render.com/docs)
