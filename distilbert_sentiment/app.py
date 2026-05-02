"""
Flask REST API for DistilBERT Sentiment Analysis
Production-ready deployment (local + Render)

Handles:
- Model lazy loading on first request
- Graceful error handling
- Environment variable configuration
- Cold start optimization
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from flask import Flask, render_template, request, jsonify

# Add project root to path for absolute imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DEVICE, SEED, BEST_MODEL_DIR
from predict import SentimentPredictor

# ============================================================================
# CONFIGURATION
# ============================================================================

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Server Configuration
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

# Flask App
app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "templates"),
    static_folder=str(PROJECT_ROOT / "static")
)

# ============================================================================
# MODEL MANAGEMENT - LAZY LOADING
# ============================================================================

# Global predictor (None until first request)
predictor: Optional[SentimentPredictor] = None


def get_predictor() -> Optional[SentimentPredictor]:
    """
    Get or initialize the sentiment predictor (lazy loading).
    
    Returns:
        SentimentPredictor instance or None if load fails
    """
    global predictor
    
    # Already loaded
    if predictor is not None:
        return predictor
    
    # Attempt to load
    logger.info("Loading sentiment model...")
    
    try:
        model_path = str(BEST_MODEL_DIR)
        
        # Validate path
        if not Path(model_path).exists():
            logger.error(f"Model directory not found: {model_path}")
            logger.error("Expected structure: models/best_model/config.json")
            return None
        
        config_file = Path(model_path) / "config.json"
        if not config_file.exists():
            logger.error(f"Model config missing: {config_file}")
            logger.error("The model directory appears to be incomplete or corrupted")
            return None
        
        # Initialize and load
        predictor = SentimentPredictor(
            model_path=model_path,
            device=DEVICE,
            seed=SEED
        )
        
        if not predictor.load_model_and_tokenizer():
            logger.error("Failed to load model and tokenizer")
            predictor = None
            return None
        
        logger.info("✓ Sentiment model loaded successfully")
        return predictor
    
    except Exception as e:
        logger.error(f"Exception during model load: {e}", exc_info=True)
        predictor = None
        return None


# ============================================================================
# ROUTES
# ============================================================================

@app.route("/", methods=["GET"])
def home():
    """Serve the web UI."""
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering home: {e}")
        return jsonify({"error": "Failed to load UI"}), 500


@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict sentiment for provided text.
    
    Input (form or JSON):
        {
            "text": "Your review text here"
        }
    
    Response:
        {
            "success": true,
            "label": "POSITIVE",
            "confidence": 0.95,
            "probabilities": {"NEGATIVE": 0.05, "POSITIVE": 0.95}
        }
    """
    try:
        # Get model
        pred = get_predictor()
        if pred is None:
            return jsonify({
                "success": False,
                "error": "Model not available. Please try again later."
            }), 503
        
        # Extract text from form or JSON
        text = request.form.get("text") or (request.get_json() or {}).get("text")
        
        if not text:
            return jsonify({
                "success": False,
                "error": "No text provided. Please include 'text' in your request."
            }), 400
        
        # Predict
        result = pred.predict(text)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Prediction failed: {str(e)}"
        }), 500


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Alias for /predict (for API compatibility)."""
    return predict()


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    
    Response:
        {
            "status": "healthy",
            "model_loaded": true
        }
    """
    pred = get_predictor()
    return jsonify({
        "status": "healthy",
        "model_loaded": pred is not None
    }), 200 if pred is not None else 503


@app.route("/api/status", methods=["GET"])
def api_status():
    """Alias for /health (for API compatibility)."""
    return health()


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# STARTUP
# ============================================================================

def main():
    """Start the Flask application."""
    logger.info(f"Starting Flask app on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Device: {DEVICE}")
    
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        use_reloader=False  # Important for production/Render
    )


if __name__ == "__main__":
    main()