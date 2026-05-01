"""
Configuration settings for the sentiment analysis project
"""
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Model Configuration
MODEL_NAME = "distilbert-base-uncased"
NUM_CLASSES = 2  # Binary sentiment (positive/negative)
MAX_LENGTH = 128
BATCH_SIZE = 16
LEARNING_RATE = 2e-5
NUM_EPOCHS = 3
WARMUP_STEPS = 500
SEED = 42

# Training Configuration
DEVICE = "cuda" if __import__("torch").cuda.is_available() else "cpu"
USE_MIXED_PRECISION = False

# Data Configuration
TRAIN_TEST_SPLIT = 0.2
VALIDATION_SPLIT = 0.1

# Paths for saved models
CHECKPOINT_DIR = MODELS_DIR / "checkpoints"
BEST_MODEL_DIR = MODELS_DIR / "best_model"

# Create directories if they don't exist
for dir_path in [DATA_DIR, MODELS_DIR, OUTPUTS_DIR, CHECKPOINT_DIR, BEST_MODEL_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
