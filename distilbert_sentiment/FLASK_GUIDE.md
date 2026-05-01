# 🚀 Flask Web Application - Sentiment Analysis

## Overview

This Flask application connects the DistilBERT sentiment analysis model to a modern web interface. The model is loaded **once at startup** and reused for all predictions, avoiding the overhead of reloading on every request.

---

## 📋 Quick Start

### 1. **Install Flask Dependency**

```bash
pip install flask>=2.3.0,<4.0.0
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### 2. **Ensure You Have a Trained Model**

The Flask app expects a trained model at: `models/best_model/`

If you haven't trained yet:
```bash
python train.py
```

### 3. **Start the Flask Server**

```bash
python app.py
```

Expected output:
```
🚀 Starting Flask Sentiment Analysis Application
Python version: 3.10.x
PyTorch version: 2.x.x
Device: cuda  (or cpu)
✓ Model loaded successfully at startup
✓ Application ready
Opening browser at: http://localhost:5000
```

### 4. **Open in Browser**

Automatically opens: **http://localhost:5000**

Or manually visit it in your browser

---

## 🎨 Web Interface Features

### Single Text Prediction
- Enter text (3-512 characters)
- Click "Analyze Sentiment" or press Ctrl+Enter
- Get instant sentiment prediction with confidence score
- See probability distribution for both labels

### Visual Feedback
- 🟢 **Green highlight**: POSITIVE sentiment
- 🔴 **Red highlight**: NEGATIVE sentiment
- Confidence percentage and probability bars
- Real-time character counter

### Error Handling
- Clear error messages if model fails to load
- Input validation (length, content)
- Connection error handling

---

## 🔌 REST API Endpoints

### Single Prediction
**POST** `/api/predict`

Request:
```json
{
    "text": "This movie was amazing!"
}
```

Response:
```json
{
    "success": true,
    "text": "This movie was amazing!",
    "label": "POSITIVE",
    "confidence": 0.95,
    "probabilities": {
        "NEGATIVE": 0.05,
        "POSITIVE": 0.95
    },
    "prediction_id": 1
}
```

### Batch Prediction
**POST** `/api/predict_batch`

Request:
```json
{
    "texts": [
        "Great movie!",
        "Terrible experience",
        "Not bad"
    ]
}
```

Response:
```json
{
    "success": true,
    "count": 3,
    "results": [
        {"text": "Great movie!", "label": "POSITIVE", ...},
        {"text": "Terrible experience", "label": "NEGATIVE", ...},
        {"text": "Not bad", "label": "POSITIVE", ...}
    ]
}
```

### Status Check
**GET** `/api/status`

Response:
```json
{
    "status": "ready",
    "model_loaded": true,
    "device": "cuda",
    "model_path": "models/best_model"
}
```

### Health Check
**GET** `/api/health`

Response:
```json
{
    "health": "ok"
}
```

---

## 📊 Performance Characteristics

### Model Loading
- ⏱️ **Startup time**: ~5-10 seconds (one-time)
- 💾 **Memory**: ~300MB (DistilBERT)
- ⚡ **Inference time**: ~100-200ms per text
- 🔄 **Reloading**: **Never** (loaded once, reused)

### Throughput
- **Single prediction**: ~5-10 requests/second (CPU)
- **Single prediction**: ~50-100 requests/second (GPU)

---

## 🛠️ Development vs Production

### Development Mode (Current)
```python
app.run(
    host="127.0.0.1",  # localhost only
    port=5000,
    debug=False,
    use_reloader=False  # Prevents model reloading
)
```

### Production Deployment

For production, use a WSGI server:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

With NVIDIA GPU:
```bash
CUDA_VISIBLE_DEVICES=0 gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🐛 Troubleshooting

### Model Not Found Error
```
✗ Failed to load model
Ensure training is complete: python train.py
```

**Solution**: Train the model first
```bash
python train.py
```

### Import Error: "No module named 'flask'"
```bash
pip install flask
```

### Port Already in Use
```bash
# Use a different port
python -c "from app import app; app.run(port=5001)"
```

Or find and kill the process:
```bash
# Windows
netstat -ano | findstr :5000

# Mac/Linux
lsof -i :5000
kill -9 <PID>
```

### GPU Out of Memory
Models runs on CPU automatically if CUDA fails. Or force CPU:
```python
# Edit app.py, change DEVICE
from src.config import DEVICE  # automatically detects
# Or force it:
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

### Model Reloads on Every Request
✓ **This is prevented** by:
- Loading model at startup
- Using `use_reloader=False`
- Storing predictor as global variable

---

## 📝 API Usage Examples

### Python Requests
```python
import requests

url = "http://localhost:5000/api/predict"
data = {"text": "This is amazing!"}

response = requests.post(url, json=data)
result = response.json()

print(f"Sentiment: {result['label']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### cURL
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This is great!"}'
```

### JavaScript Fetch
```javascript
fetch('/api/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: 'Awesome!'})
})
.then(r => r.json())
.then(data => console.log(data.label))
```

---

## 🔒 Security Notes

1. **Input Validation**: 3-512 character limit
2. **Batch Limit**: Max 100 texts per request
3. **Rate Limiting**: Consider adding for production
4. **CORS**: Not enabled by default (safe for localhost)

To enable CORS for external APIs:
```bash
pip install flask-cors
```

Then in app.py:
```python
from flask_cors import CORS
CORS(app)
```

---

## 📈 Monitoring & Logging

All requests and model operations are logged to console:

```
2025-04-28 10:30:15,123 - INFO - ✓ Model loaded successfully at startup
2025-04-28 10:30:20,456 - INFO - Processing batch of 3 samples
2025-04-28 10:30:22,789 - INFO - Batch processing complete
```

For file logging, modify `app.py`:
```python
import logging

# Add file handler
file_handler = logging.FileHandler('app.log')
logger.addHandler(file_handler)
```

---

## 🚀 Next Steps

- ✅ Model connected to web UI
- ✅ Single & batch API endpoints
- ✅ Model loaded once (efficient)
- 🔄 Consider: Docker containerization
- 🔄 Consider: Database for storing predictions
- 🔄 Consider: Authentication/API keys for production

---

## 📄 Files Overview

| File | Purpose |
|------|---------|
| `app.py` | Flask application with API endpoints |
| `templates/index.html` | Modern web UI |
| `static/` | CSS, JS, images (if needed) |
| `predict.py` | Sentiment prediction logic (imported) |
| `src/config.py` | Configuration & paths |
| `requirements.txt` | Dependencies |

---

## 🎯 Key Design Decisions

1. **Model Loaded Once**: Global `predictor` instance initialized at startup
2. **No Reloader**: Flask reloader disabled to prevent model reloading
3. **Threaded**: Multiple requests can be handled concurrently
4. **Stateless API**: Each request is independent
5. **Clean Error Handling**: Meaningful error messages returned as JSON

---

## ✅ Checklist Before Going Live

- [ ] Train and save model with `python train.py`
- [ ] Verify model exists at `models/best_model/`
- [ ] Install Flask: `pip install -r requirements.txt`
- [ ] Test locally: `python app.py`
- [ ] Test API endpoints with curl/Postman
- [ ] Check performance with batch requests
- [ ] Review security for production deployment
- [ ] Set up monitoring/logging
- [ ] Document for team

---

**Enjoy your sentiment analysis web app! 🚀**
