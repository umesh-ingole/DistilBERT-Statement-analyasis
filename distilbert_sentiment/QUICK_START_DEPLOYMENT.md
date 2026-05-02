# 🚀 QUICK START - Deploy Flask + DistilBERT in 10 Minutes

## TL;DR - Super Fast Version

### What Changed?
✅ Fixed circular imports  
✅ Fixed dependency conflicts  
✅ Added lazy model loading  
✅ Added environment variable support  
✅ Created Procfile for Render  

### Local Testing (2 minutes)
```bash
# 1. Activate environment
cd c:\Users\Admin\OneDrive\Desktop\Umesh\distilbert_sentiment
venv_310\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run app
python app.py

# 4. In another terminal, test
curl http://localhost:5000/health
python test_deployment_local.py
```

### Deploy to Render (5 minutes)
```bash
# 1. Push to GitHub
git add .
git commit -m "Production deployment fixes"
git push

# 2. Go to https://render.com
# 3. New Web Service → Connect GitHub → Select repo
# 4. Settings:
#    Build Command: pip install -r requirements.txt
#    Start Command: gunicorn app:app
# 5. Deploy

# 6. Test
curl https://YOUR-APP.onrender.com/health
```

---

## Files Modified

| File | What's New |
|------|-----------|
| `app.py` | ✅ Fixed (lazy loading, env vars) |
| `requirements.txt` | ✅ Fixed (Render-compatible) |
| `Procfile` | ✨ Created |
| `runtime.txt` | ✨ Created |
| `RENDER_DEPLOYMENT_GUIDE.md` | 📖 Full guide |
| `DEPLOYMENT_FIXES_SUMMARY.md` | 📖 Detailed fixes |
| `test_deployment_local.py` | 🧪 Test script |

---

## What You Get

```
✅ Model loading: 5-10s first request (cached after)
✅ Inference: ~100-200ms per prediction
✅ Endpoints: /health, /predict, /api/predict
✅ Works locally & on Render (same code!)
✅ Production WSGI (gunicorn)
✅ Lazy loading (no startup crashes)
```

---

## Key Endpoints

### Health Check
```bash
curl https://YOUR-APP.onrender.com/health
# {"status": "healthy", "model_loaded": true}
```

### Make Prediction
```bash
curl -X POST https://YOUR-APP.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing movie!"}'

# {
#   "success": true,
#   "label": "POSITIVE",
#   "confidence": 0.99,
#   ...
# }
```

### Web UI
```
https://YOUR-APP.onrender.com/
```

---

## Verification Checklist

Before pushing to GitHub:
```bash
✓ app.py has NO "from .predict" or "from .src"
✓ app.py has "get_predictor()" function
✓ app.py has "os.environ.get("PORT")"
✓ requirements.txt has "gunicorn==21.2.0"
✓ requirements.txt has "numpy==1.24.3"
✓ Procfile exists with "web: gunicorn app:app"
✓ runtime.txt exists with "python-3.10.13"
✓ models/best_model/config.json exists
```

Check:
```bash
grep "from .predict" app.py        # Should be EMPTY
grep "get_predictor" app.py        # Should exist
grep "gunicorn" requirements.txt    # Should exist
cat Procfile                        # Should show gunicorn command
```

---

## Render Setup in 3 Steps

### Step 1: Push Code
```bash
git add .
git commit -m "Production fixes"
git push
```

### Step 2: Create Service
1. https://render.com → Dashboard
2. New + → Web Service
3. Connect GitHub → Select repo
4. Fill in:
   - Name: `distilbert-sentiment-api`
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
5. Deploy

### Step 3: Test
```bash
curl https://YOUR-APP.onrender.com/health
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Check app.py has `sys.path.insert()` |
| `Model not found` | `git add models/best_model/` and push |
| First request slow | Normal (cold start, 5-10s) |
| 503 error | Check Render logs, model may not be loading |
| Import circular error | Remove `from .` imports from app.py |

---

## For Details, See:

- **Full Guide:** `RENDER_DEPLOYMENT_GUIDE.md`
- **All Fixes:** `DEPLOYMENT_FIXES_SUMMARY.md`
- **Test Locally:** `python test_deployment_local.py`

---

## Success!

When deployed:
```
✅ https://YOUR-APP.onrender.com/        (Web UI)
✅ https://YOUR-APP.onrender.com/health  (Health check)
✅ POST to /api/predict                  (Predictions)
```

🎉 **Done!**
