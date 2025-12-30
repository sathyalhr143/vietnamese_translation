# Render Deployment Guide

This document explains how to deploy the Vietnamese Translation **FastAPI** application to Render.

## What Changed

The application is now a **FastAPI web service** instead of a command-line tool:

✅ **Before**: CLI tool that only worked with live microphone input  
✅ **Now**: Web application with:
- Web UI for easy interaction
- REST API for programmatic access
- File upload support
- Live audio recording (via browser)
- Translation history tracking

## Prerequisites

- A [Render.com](https://render.com) account
- Your project pushed to GitHub/GitLab
- OpenAI API key

## Deployment Steps

### 1. Connect Your Repository to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub/GitLab repository
4. Select this repository

### 2. Configure the Service

The `render.yaml` file contains all configuration. Render will automatically read it.

**Key Settings:**
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m uvicorn app:app --host 0.0.0.0 --port 8000`
- **Region**: Oregon (free tier available)
- **Plan**: Free (or upgrade as needed)

### 3. Set Environment Variables

Before deploying, set these in Render Dashboard:

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key (mark as secret!)

**Optional (defaults provided):**
- `SOURCE_LANGUAGE` (default: `vi`)
- `TARGET_LANGUAGE` (default: `en`)
- `WHISPER_MODEL_SIZE` (default: `small`)
- `AUDIO_SAMPLE_RATE` (default: `16000`)
- `AUDIO_CHUNK_DURATION` (default: `10`)
- `DB_PATH` (default: `translations.db`)
- `LOG_LEVEL` (default: `INFO`)

### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Build your project (install dependencies)
   - Start the FastAPI server
   - Deploy to production

Your app will be available at:
```
https://your-service-name.onrender.com
```

### 5. Access Your Application

Visit your deployed URL to:
- Use the web UI immediately
- Access REST API endpoints
- Upload audio files
- Record live audio

## Using the Application

### Web Interface
Open `https://your-service-name.onrender.com` in your browser.

Four main tabs:
1. **📝 Text Translation**: Paste Vietnamese text
2. **🎤 Upload Audio**: Upload WAV, MP3, OGG, FLAC files
3. **🔴 Live Recording**: Record directly from microphone
4. **📚 History**: View past translations

### REST API
See [API_GUIDE.md](API_GUIDE.md) for full documentation.

Example:
```bash
curl -X POST https://your-service-name.onrender.com/api/translate/text \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào"}'
```

### Health Check
```bash
curl https://your-service-name.onrender.com/api/health
```

## Important Notes

### Audio Input

**Live Recording** (WebSocket):
- ✅ Works great in web browsers
- ✅ Records user's microphone
- ✅ Real-time transcription
- Uses browser's MediaRecorder API

**File Upload**:
- ✅ Supports WAV, MP3, OGG, FLAC
- ✅ No server-side audio hardware needed
- ✅ Best for batch processing

### Database

SQLite database is created at: `/tmp/translations.db`

⚠️ **Important for Production**:
- On Render free tier, `/tmp` is ephemeral (resets when service restarts)
- For persistent data, upgrade to **Render PostgreSQL**
- See [Render PostgreSQL Docs](https://render.com/docs/databases)

### Free Tier Limitations

- Service spins down after 15 minutes of inactivity
- Limited to 750 compute hours/month
- Shared CPU resources
- `/tmp` storage not persistent

### Performance

- **Whisper Model**: `small` (default) balances accuracy and speed
  - `tiny`/`base`: Faster, less accurate
  - `medium`/`large`: Slower, more accurate
- **API Rate Limits**: Check your OpenAI account for rate limits

## Production Setup Checklist

For production deployment, consider:

- [ ] **Database**: Upgrade to Render PostgreSQL for data persistence
- [ ] **API Key Security**: Ensure `OPENAI_API_KEY` is marked as secret in Render
- [ ] **Monitoring**: Set up error tracking (Sentry, etc.)
- [ ] **Rate Limiting**: Add rate limiting for public API endpoints
- [ ] **Authentication**: Add user authentication if needed
- [ ] **CORS**: Configure for your frontend domain
- [ ] **Logging**: Set `LOG_LEVEL=WARNING` in production
- [ ] **Model Size**: Choose appropriate Whisper model size

## Troubleshooting

### Build Fails
- Check requirements.txt for all dependencies
- View build logs in Render Dashboard
- Ensure Python version is 3.11+

### Application Won't Start
- Check `OPENAI_API_KEY` is set in environment variables
- View logs in Render Dashboard
- Verify render.yaml syntax is correct

### Slow Performance
- Reduce `WHISPER_MODEL_SIZE` to `tiny` or `base`
- Check OpenAI API rate limits
- Upgrade from free tier for better resources

### Audio Processing Fails
- Ensure audio format is supported
- Check file size (free tier has limits)
- Verify audio codec is compatible

### "No speech detected" Error
- Ensure audio quality is good
- Try a different audio file
- Check source language setting

### WebSocket Issues
- Live recording requires HTTPS on production (Render provides this)
- Browser must support WebSockets
- Check browser console for errors

## Monitoring

### View Logs
1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. Filter by timestamp or error level

### Common Log Entries
```
Translator initialized successfully     → App started OK
Translation error                       → API request failed
Transcription completed                 → Audio processed
WebSocket connection established        → Live recording started
```

## Updating Your Application

1. Make changes locally
2. Push to GitHub
3. Render automatically redeploys

To force redeploy:
1. Go to Render Dashboard
2. Select service
3. Click "Manual Deploy"

## Rolling Back

If deployment breaks:
1. Go to Render Dashboard
2. Click "Deployments"
3. Select a previous deployment
4. Click "Deploy"

## Cost Estimate

**Render Costs:**
- Free tier: $0 (with limitations)
- Standard tier: ~$7/month
- PostgreSQL: +$7/month

**OpenAI Costs:**
- Whisper API: $0.02 per minute of audio
- GPT-4o mini: $0.15 per 1M input tokens

## Support & Documentation

- [Render Docs](https://render.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [OpenAI Docs](https://platform.openai.com/docs)
- [Project API Guide](./API_GUIDE.md)

## Next Steps

1. ✅ Deploy to Render
2. Test all features via web UI
3. Integrate REST API into your application
4. Set up monitoring/alerts
5. Plan upgrade to paid tier if needed

Enjoy your deployed translation service! 🚀
