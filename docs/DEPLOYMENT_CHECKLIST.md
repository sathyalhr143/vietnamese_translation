# ✅ Deployment Checklist

Complete this checklist before deploying to Render (or any production environment).

## 📋 Pre-Deployment

### Code Quality
- [ ] All code changes committed to GitHub
- [ ] No hardcoded API keys in code
- [ ] No sensitive information in .env file (it's in .gitignore)
- [ ] requirements.txt is up to date
- [ ] No unused imports or dead code

### Testing
- [ ] Ran `python test_api.py` and all tests passed
- [ ] Tested web UI locally at http://localhost:8000
- [ ] Tested text translation feature
- [ ] Tested audio file upload feature (if audio file available)
- [ ] Tested live recording feature (in web UI)
- [ ] Tested API endpoints with curl or Postman
- [ ] Tested translation history feature

### Documentation
- [ ] README.md is current and accurate
- [ ] API_GUIDE.md is complete
- [ ] RENDER_DEPLOYMENT.md is reviewed
- [ ] All new files have docstrings
- [ ] REFACTOR_SUMMARY.md documents changes

### Environment Setup
- [ ] .env.example has all required variables
- [ ] .gitignore includes .env (checked with git ls-files)
- [ ] No .env file committed to Git
- [ ] OPENAI_API_KEY is valid and works locally

### Configuration Files
- [ ] render.yaml exists and is valid YAML
- [ ] render.yaml has correct start command
- [ ] Dockerfile exists and builds successfully
- [ ] docker-compose.yml is functional (optional)

---

## 🚀 Render Deployment

### Before Connecting to Render
- [ ] Repository pushed to GitHub
- [ ] All commits are clean (no work-in-progress files)
- [ ] Branch is `main` or your deployment branch

### Render Dashboard Setup
1. [ ] Created Render account (https://render.com)
2. [ ] Connected GitHub account to Render
3. [ ] Created new Web Service from GitHub

### Environment Variables in Render
- [ ] Set `OPENAI_API_KEY` (mark as secret!)
- [ ] Verify all other env vars have defaults (or set them)
- [ ] Checked for typos in variable names

### Deployment Verification
- [ ] Deployment completed successfully
- [ ] Service shows "Live" status in Render Dashboard
- [ ] No errors in deployment logs
- [ ] Health check passes: `GET /api/health`
- [ ] Web interface loads at service URL
- [ ] Can translate text via API
- [ ] Can upload audio file
- [ ] Translation history works

---

## 🧪 Post-Deployment Testing

### Web Interface
- [ ] Visit https://your-app.onrender.com
- [ ] Text translation works
- [ ] Audio file upload works
- [ ] Live recording works (requires microphone)
- [ ] History page loads
- [ ] All buttons respond correctly

### REST API
```bash
# Health check
curl https://your-app.onrender.com/api/health

# Text translation
curl -X POST https://your-app.onrender.com/api/translate/text \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào"}'

# Get history
curl https://your-app.onrender.com/api/history?limit=5
```

### Performance
- [ ] Web UI loads in < 5 seconds
- [ ] API responds in < 10 seconds
- [ ] No timeout errors
- [ ] Database queries complete reasonably fast

### Error Handling
- [ ] Invalid requests return proper error messages
- [ ] Missing OPENAI_API_KEY shows error (not crash)
- [ ] Large files are rejected gracefully
- [ ] Unsupported audio formats are rejected

---

## 🔒 Security Checklist

### Secrets & Keys
- [ ] OPENAI_API_KEY is set as secret in Render (not visible)
- [ ] No API key in code or logs
- [ ] No credentials in git history
- [ ] No test accounts with real data

### Data Protection
- [ ] Database file path is correct
- [ ] Database permissions are set properly (if self-hosted)
- [ ] HTTPS is enabled (Render provides this automatically)
- [ ] No sensitive data in logs

### Access Control (Optional)
- [ ] Public API access is intentional
- [ ] No authentication bypass vulnerabilities
- [ ] Rate limiting considered (if public API)
- [ ] CORS settings are appropriate

---

## 📊 Production Setup (Optional)

### Database
- [ ] SQLite is working locally
- [ ] Consider upgrading to PostgreSQL for production
- [ ] Backup strategy planned (if important data)
- [ ] Database schema documented

### Monitoring
- [ ] Render logs are accessible
- [ ] Error alerts configured (optional)
- [ ] Health check endpoint is monitored
- [ ] Uptime tracking set up (optional)

### Scaling
- [ ] Service is set to restart on failure (Render default)
- [ ] Consider if free tier is sufficient
- [ ] Plan for upgrade timeline if needed
- [ ] Understand free tier limitations

---

## 📚 Documentation Completed

- [ ] README.md updated with current info
- [ ] API_GUIDE.md has working examples
- [ ] RENDER_DEPLOYMENT.md covers your setup
- [ ] DOCKER_GUIDE.md available for reference
- [ ] REFACTOR_SUMMARY.md explains changes
- [ ] Code comments are clear

---

## 🎯 Launch Checklist

### Final Verification
- [ ] All tests pass locally
- [ ] Deployment logs show no errors
- [ ] Service is marked as "Live"
- [ ] Can access web UI at deployment URL
- [ ] API health check succeeds
- [ ] At least one translation works

### Communication
- [ ] Team notified of deployment (if applicable)
- [ ] Documentation is accessible
- [ ] Support process defined (for issues)
- [ ] Feedback mechanism set up

### Post-Launch
- [ ] Monitor logs for errors for first 24 hours
- [ ] Check API error rate
- [ ] Verify database integrity
- [ ] Plan next improvements

---

## 🆘 Troubleshooting During Deployment

### Build Fails
- [ ] Check render.yaml syntax
- [ ] Verify Python version (3.11+)
- [ ] Check requirements.txt for conflicts
- [ ] View build logs in Render Dashboard

### Application Won't Start
- [ ] Check OPENAI_API_KEY is set
- [ ] Verify environment variable names
- [ ] Check startup command in render.yaml
- [ ] View application logs

### API Returns Errors
- [ ] Check OPENAI_API_KEY validity
- [ ] Verify input format matches API spec
- [ ] Check file size limits
- [ ] View application logs for details

### Performance Issues
- [ ] Reduce WHISPER_MODEL_SIZE to 'tiny'
- [ ] Check OpenAI rate limits
- [ ] Monitor Render resource usage
- [ ] Consider upgrading from free tier

---

## 📝 Notes for Future Reference

```
Service URL: https://your-app.onrender.com
Repository: https://github.com/username/repo
Database: /tmp/translations.db (ephemeral on free tier)
Support Docs: See README.md and API_GUIDE.md
```

---

## ✨ Success Criteria

### Deployment is Successful When:
✅ Service shows "Live" in Render Dashboard  
✅ Health check endpoint returns 200 OK  
✅ Web UI loads and displays correctly  
✅ Can translate text and get results  
✅ No errors in application logs  
✅ Performance is acceptable  
✅ All team members notified  

---

## 🎉 Ready to Launch!

When all checkboxes are checked:
1. **You're ready to deploy!**
2. **The application is production-ready**
3. **Users can start using it immediately**
4. **You can monitor and maintain it**

---

## 📞 Need Help?

- **Deployment Issues**: Check RENDER_DEPLOYMENT.md
- **API Questions**: See API_GUIDE.md
- **Docker Issues**: See DOCKER_GUIDE.md
- **Code Questions**: Check REFACTOR_SUMMARY.md

**Good luck with your deployment! 🚀**
