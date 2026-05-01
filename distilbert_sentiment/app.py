from flask import Flask, render_template, request, jsonify
import logging
from pathlib import Path
from typing import Optional

from predict import SentimentPredictor
from src.config import DEVICE, SEED, BEST_MODEL_DIR  


from .predict import SentimentPredictor
from .src.config import DEVICE, SEED, BEST_MODEL_DIR
from .src.utils import set_seed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Load once globally
predictor: Optional[SentimentPredictor] = None


def load_model():
    global predictor

    try:
        model_path = str(BEST_MODEL_DIR)

        if not Path(model_path).exists():
            logger.error(f"Model folder not found: {model_path}")
            return False

        predictor = SentimentPredictor(
            model_path=model_path,
            device=DEVICE,
            seed=SEED
        )

        if predictor.load_model_and_tokenizer():
            logger.info("[OK] Model loaded successfully")
            return True

        return False

    except Exception as e:
        logger.error(f"Startup model load failed: {e}")
        return False


@app.route("/")
def home():
    return render_template("index.html")


def predict_handler():
    global predictor

    if predictor is None:
        return jsonify({
            "success": False,
            "error": "Model not loaded"
        }), 500

    try:
        text = request.form.get("text") or request.json.get("text")

        if not text:
            return jsonify({
                "success": False,
                "error": "No text provided"
            }), 400

        result = predictor.predict(text)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Prediction error: {e}")

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/predict", methods=["POST"])
def predict():
    return predict_handler()


@app.route("/api/predict", methods=["POST"])
def api_predict():
    return predict_handler()


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": predictor is not None
    })


@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "ok",
        "model_loaded": predictor is not None
    })


if __name__ == "__main__":
    print("Loading model...")

    if not load_model():
        print("Model failed to load.")
        exit(1)

    print("Starting Flask app at http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )