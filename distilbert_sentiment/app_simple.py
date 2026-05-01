#!/usr/bin/env python3
"""
Flask web application for DistilBERT Sentiment Analysis
Simplified version that works without PyTorch initially
"""

import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False

# Global model instance - loaded once at startup
predictor = None
model_loaded = False


def load_model_once():
    """Load model and tokenizer once at application startup"""
    global predictor, model_loaded
    
    if model_loaded:
        return True
    
    try:
        import torch
        from src.config import DEVICE, SEED, BEST_MODEL_DIR
        from src.utils import set_seed
        from predict import SentimentPredictor
        
        logger.info("=" * 80)
        logger.info("LOADING SENTIMENT PREDICTION MODEL")
        logger.info("=" * 80)
        
        # Initialize predictor
        model_path = str(BEST_MODEL_DIR)
        logger.info(f"Model path: {model_path}")
        logger.info(f"Device: {DEVICE}")
        
        # Check if model exists
        if not Path(model_path).exists():
            logger.warning(f"⚠ Model directory not found: {model_path}")
            logger.warning("Train model with: python train.py")
            return False
        
        set_seed(SEED)
        predictor = SentimentPredictor(
            model_path=model_path,
            device=DEVICE,
            seed=SEED
        )
        
        # Load model and tokenizer
        success = predictor.load_model_and_tokenizer()
        
        if success:
            model_loaded = True
            logger.info("✓ Model loaded successfully")
            logger.info("=" * 80)
            return True
        else:
            logger.error("✗ Failed to load model")
            return False
            
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        logger.warning("Running in demo mode")
        logger.info("=" * 80)
        return False


@app.route("/", methods=["GET"])
def index():
    """Serve the main web interface"""
    return render_template("index.html", model_loaded=model_loaded)


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """REST API endpoint for sentiment prediction"""
    if not model_loaded:
        return jsonify({
            "success": False,
            "error": "Model not loaded. Train with: python train.py"
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or "text" not in data:
            return jsonify({"success": False, "error": "Missing 'text' field"}), 400
        
        text = data.get("text", "").strip()
        
        # Validate input
        is_valid, error_msg = predictor.validate_input(text)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg}), 400
        
        # Make prediction
        result = predictor.predict(text)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"success": False, "error": f"Error: {str(e)}"}), 500


@app.route("/api/predict_batch", methods=["POST"])
def api_predict_batch():
    """REST API endpoint for batch sentiment prediction"""
    if not model_loaded:
        return jsonify({"success": False, "error": "Model not loaded"}), 503
    
    try:
        data = request.get_json()
        if not data or "texts" not in data:
            return jsonify({"success": False, "error": "Missing 'texts' field"}), 400
        
        texts = data.get("texts", [])
        if not isinstance(texts, list) or len(texts) == 0 or len(texts) > 100:
            return jsonify({"success": False, "error": "Invalid texts (1-100)"}), 400
        
        results = predictor.predict_batch(texts)
        return jsonify({"success": True, "count": len(results), "results": results}), 200
        
    except Exception as e:
        logger.error(f"Batch error: {e}")
        return jsonify({"success": False, "error": f"Error: {str(e)}"}), 500


@app.route("/api/status", methods=["GET"])
def api_status():
    """Check application status"""
    try:
        from src.config import DEVICE, BEST_MODEL_DIR
        device = DEVICE
        model_path = str(BEST_MODEL_DIR)
    except:
        device = "unknown"
        model_path = "unknown"
    
    return jsonify({
        "status": "ready" if model_loaded else "setup_needed",
        "model_loaded": model_loaded,
        "device": device,
        "model_path": model_path
    }), 200


@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint"""
    return jsonify({"health": "ok"}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    logger.info("🚀 Starting Sentiment Analysis Flask App")
    logger.info(f"Python: {__import__('sys').version.split()[0]}")
    
    # Try loading model
    model_status = load_model_once()
    
    if model_status:
        logger.info("✓ Ready with model")
    else:
        logger.warning("⚠ Running in setup mode - to train model: python train.py")
    
    logger.info("Starting server at http://localhost:5000")
    
    try:
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("\n✓ App stopped")
