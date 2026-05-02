# 🚀 Render Deployment Guide - DistilBERT Sentiment Analysis API

## Overview

This guide provides step-by-step instructions to deploy the Flask + DistilBERT sentiment analysis API to [Render](https://render.com).

**What's Included:**
- Production-ready Flask app (lazy model loading, error handling)
- Render-compatible dependencies (CPU-only, NumPy 1.x)
- Procfile + runtime.txt for deployment
- Health checks and API endpoints

---

## Prerequisites

### Local Machine
- ✅ Python 3.10+
- ✅ Git installed
- ✅ GitHub account (to push code)
- ✅ Render account (free tier available)

### Project Files (Already Provided)
```
distilbert_sentiment/
├── app.py                      # Fixed: Lazy loading, env vars, no circular imports
├── predict.py                  # Unchanged: Your predictor class
├── requirements.txt            # Fixed: Render-compatible, CPU-only
├── Procfile                    # NEW: Gunicorn startup command
├── runtime.txt                 # NEW: Python 3.10.13
├── models/best_model/          # Must exist locally (copied to Render)
├── src/
│   ├── config.py
│   ├── utils.py
│   └── ...
├── templates/
│   └── index.html
└── static/
    └── ...
```

---

## Step 1: Prepare Local Code for Deployment

### 1.1 Verify File Changes

Confirm these files have been updated:

```bash
# app.py should have:
# - NO circular imports (from .predict or .src)
# - get_predictor() function (lazy loading)
# - Environment variables: PORT, HOST
# - Error handlers
```

Check:
```bash
grep -n "from .predict" app.py        # Should be EMPTY
grep -n "get_predictor()" app.py      # Should exist
grep -n "os.environ.get" app.py       # Should show PORT, HOST
```

### 1.2 Verify Model Exists

```bash
ls -la models/best_model/config.json   # Must exist
ls -la models/best_model/model.safetensors  # Must exist
```

### 1.3 Verify Requirements

```bash
# requirements.txt must include:
grep gunicorn requirements.txt         # Should show: gunicorn==21.2.0
grep "torch==" requirements.txt        # Should show: torch==2.1.2
grep "numpy==" requirements.txt        # Should show: numpy==1.24.3
```

### 1.4 Verify Deployment Files

```bash
cat Procfile                           # Should show: web: gunicorn app:app
cat runtime.txt                        # Should show: python-3.10.13
```

---

## Step 2: Push Code to GitHub

### 2.1 Initialize Git Repo (if not already done)

```bash
cd c:\Users\Admin\OneDrive\Desktop\Umesh\distilbert_sentiment

git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"

git init
```

### 2.2 Add Files

```bash
# Add all files
git add .

# Verify what's staged
git status
```

### 2.3 Create .gitignore (Recommended)

```bash
# Create .gitignore
echo "venv/" > .gitignore
echo "venv_310/" >> .gitignore
echo "venv_313/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".DS_Store" >> .gitignore
echo ".env" >> .gitignore
echo "*.egg-info/" >> .gitignore

git add .gitignore
```

### 2.4 Initial Commit

```bash
git commit -m "Initial commit: Flask + DistilBERT API (production ready)"
```

### 2.5 Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click **New** → create repository
3. Name: `distilbert-sentiment-api`
4. Description: "Production Flask API for DistilBERT sentiment analysis"
5. Choose Public or Private
6. Click **Create repository**

### 2.6 Push to GitHub

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/distilbert-sentiment-api.git
git push -u origin main

# Verify
git remote -v
```

---

## Step 3: Deploy to Render

### 3.1 Connect GitHub to Render

1. Go to [https://render.com](https://render.com)
2. Sign up or log in
3. Go to Dashboard
4. Click **New +** → **Web Service**
5. Select **Build and deploy from a Git repository**
6. Click **Connect Account** (GitHub) and authorize Render

### 3.2 Create Web Service

1. Find your repository: `distilbert-sentiment-api`
2. Click **Connect**
3. Fill in the deployment details:

```
Name:                          distilbert-sentiment-api
Region:                        (Choose closest to your location)
Branch:                        main
Runtime:                       Python 3
Build Command:                 pip install -r requirements.txt
Start Command:                 gunicorn app:app
```

4. **Important - Set Environment Variables:**

   In the "Environment" section, add:
   ```
   PYTHONUNBUFFERED=1
   ```
   
   (Optional) To enable debug logs:
   ```
   FLASK_DEBUG=False
   ```

5. **Instance Type:**
   - Select **Free** (if available) or **Starter**
   - Note: Free tier has limited resources and sleeps after 15 min inactivity

6. Click **Create Web Service**

### 3.3 Monitor Deployment

The build will start automatically:

```
Cloning repository...
Installing dependencies...
Building...
Deploying...
```

**Check the Live Log tab** for any errors:
- Look for: `"Sentiment model loaded successfully"`
- If you see errors, scroll to find the issue

---

## Step 4: Test the Deployment

Once deployment is complete, you'll get a URL like:
```
https://distilbert-sentiment-api.onrender.com
```

### 4.1 Health Check

```bash
# Test health endpoint
curl https://distilbert-sentiment-api.onrender.com/health

# Expected response:
# {
#   "status": "healthy",
#   "model_loaded": true
# }
```

### 4.2 Make a Prediction

**Option A: Using curl**
```bash
curl -X POST https://distilbert-sentiment-api.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This movie was absolutely amazing!"}'

# Expected response:
# {
#   "success": true,
#   "text": "This movie was absolutely amazing!",
#   "label": "POSITIVE",
#   "confidence": 0.9940,
#   "probabilities": {
#     "NEGATIVE": 0.0060,
#     "POSITIVE": 0.9940
#   }
# }
```

**Option B: Using Python**
```python
import requests
import json

url = "https://distilbert-sentiment-api.onrender.com/api/predict"
data = {"text": "This movie was absolutely amazing!"}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

**Option C: Using the Web UI**
1. Open: `https://distilbert-sentiment-api.onrender.com/`
2. Type your review
3. Click predict

---

## Step 5: Troubleshooting

### Issue: Model Takes Too Long to Load

**Symptom:** First request times out, subsequent requests work

**Cause:** Cold start - model loads on first request (lazy loading)

**Solution:** This is normal for the first request. Consider:
- Use health check to warm up: `curl /health`
- Keep-alive option on Render (paid tier)

### Issue: ModuleNotFoundError: No module named 'predict'

**Cause:** Circular imports or path issues in app.py

**Fix:** Verify app.py has:
```python
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
```

### Issue: Model Not Found

**Symptom:** `"error": "Model directory not found: /opt/render/project/src/../models/best_model"`

**Cause:** Model files not uploaded to Render

**Fix:**
1. Verify locally: `ls models/best_model/config.json`
2. Check git: `git ls-files models/best_model/`
3. If missing, add to git: `git add models/best_model/`
4. Commit and push
5. Redeploy on Render

### Issue: ImportError: cannot import name 'BEST_MODEL_DIR'

**Cause:** src/config.py not found or misconfigured

**Fix:** Verify config.py exists and contains:
```python
BEST_MODEL_DIR = MODELS_DIR / "best_model"
```

### Issue: 503 Service Unavailable

**Cause:** Model failed to load, app is down

**Check Render logs:**
1. Render Dashboard → Web Service
2. Click **Logs** tab
3. Look for error messages starting with `ERROR`

---

## Step 6: API Endpoints

### Prediction Endpoint

**POST** `/predict` or `/api/predict`

**Request (JSON):**
```json
{
  "text": "Your review text here"
}
```

**Response (Success):**
```json
{
  "success": true,
  "text": "Your review text here",
  "label": "POSITIVE",
  "confidence": 0.95,
  "probabilities": {
    "NEGATIVE": 0.05,
    "POSITIVE": 0.95
  },
  "prediction_id": 1
}
```

**Response (Error - No Text):**
```json
{
  "success": false,
  "error": "No text provided. Please include 'text' in your request."
}
```

**Response (Error - Model Loading):**
```json
{
  "success": false,
  "error": "Model not available. Please try again later."
}
```

### Health Check Endpoint

**GET** `/health` or `/api/status`

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

## Step 7: Monitoring & Maintenance

### Check Deployment Status

1. Render Dashboard → Web Service
2. See **Deploys** tab for history
3. Current status shows: ✅ Live, 🔄 Building, ❌ Failed

### View Logs

**Real-time logs:**
```
Dashboard → Web Service → Logs tab
```

**Look for:**
- ✅ `"Sentiment model loaded successfully"` = Model working
- ❌ `"Model directory not found"` = Files missing
- ❌ `ImportError` = Code issues

### Auto-Redeploy

To automatically redeploy when you push to GitHub:
1. Render Dashboard → Web Service
2. Settings → Auto-Deploy
3. Toggle ON for "Auto-deploy commit"

---

## Step 8: Local Testing (Before Render)

**Test locally to ensure everything works:**

```bash
# 1. Activate venv_310
cd c:\Users\Admin\OneDrive\Desktop\Umesh\distilbert_sentiment
venv_310\Scripts\activate

# 2. Install production requirements
pip install -r requirements.txt

# 3. Test with environment variables
set PORT=5000
set HOST=0.0.0.0
python app.py

# 4. In another terminal, test endpoints
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/predict -H "Content-Type: application/json" -d "{\"text\": \"Great movie!\"}"
```

---

## Step 9: Advanced Configuration (Optional)

### Enable Debug Logging

Set environment variable on Render:
```
FLASK_DEBUG=True
```

### Custom Domain

1. Render Dashboard → Web Service → Custom Domain
2. Add your domain (e.g., `sentiment.yourdomain.com`)
3. Follow DNS configuration steps

### Performance Tuning

For paid Render instance:
```
set GUNICORN_WORKERS=4
set GUNICORN_THREADS=2
```

Then modify Procfile:
```
web: gunicorn --workers 4 --threads 2 app:app
```

---

## Step 10: Production Checklist

Before going live, verify:

- ✅ `app.py` has no circular imports
- ✅ `requirements.txt` has `gunicorn==21.2.0`
- ✅ `requirements.txt` has `numpy==1.24.3` (not 2.x)
- ✅ `Procfile` exists with correct command
- ✅ `runtime.txt` has `python-3.10.13`
- ✅ `models/best_model/` exists locally and pushed to git
- ✅ All files committed to GitHub
- ✅ Health endpoint returns `"model_loaded": true`
- ✅ Prediction endpoint works with sample text
- ✅ Environment variables set (PORT, HOST, etc.)

---

## Quick Reference Commands

```bash
# Push code after updates
git add .
git commit -m "Update: deployment fixes"
git push

# Test locally
python app.py

# View Render logs
# Dashboard → Web Service → Logs

# Test production API
curl https://distilbert-sentiment-api.onrender.com/health

# Make prediction
curl -X POST https://distilbert-sentiment-api.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing movie!"}'
```

---

## Support & Debugging

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **First request is slow** | Normal (cold start, model loads on first request) |
| **503 Service Unavailable** | Check Render logs for model loading errors |
| **ImportError** | Verify `sys.path.insert()` in app.py exists |
| **Model not found** | Commit model files to git: `git add models/best_model/` |
| **NumPy version conflict** | Ensure `numpy==1.24.3` in requirements.txt |

### Getting Help

1. **Render Docs:** [https://render.com/docs](https://render.com/docs)
2. **Flask Docs:** [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
3. **Check Logs:** Render Dashboard → Logs tab

---

## Summary

You now have:
- ✅ Production-ready Flask app (local + Render compatible)
- ✅ Fixed dependencies (NumPy 1.x, torch 2.1.2, gunicorn)
- ✅ Deployment files (Procfile, runtime.txt)
- ✅ Lazy model loading (no startup crashes)
- ✅ Environment variable support
- ✅ Health check and API endpoints
- ✅ Comprehensive deployment guide

**Next Step:** Push to GitHub and deploy on Render!

