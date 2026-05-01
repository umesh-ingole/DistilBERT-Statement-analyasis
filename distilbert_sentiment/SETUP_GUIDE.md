# DistilBERT Sentiment Analysis - Environment Setup Guide

## ✓ Setup Complete

Your project structure and environment have been configured for Phase 1: Training and Testing.

### Project Structure

```
distilbert_sentiment/
├── data/                    # Training/test data goes here
├── models/
│   ├── checkpoints/        # Training checkpoints
│   └── best_model/         # Best trained model
├── notebooks/              # Jupyter exploration notebooks
├── outputs/                # Results, metrics, visualizations
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration (model name, batch size, learning rate, etc.)
│   ├── utils.py           # Utility functions (seed, device, directories)
│   ├── data_handler.py    # Data loading and preprocessing
│   ├── model.py           # Model definition and management
│   ├── trainer.py         # [Ready for Phase 1 - Training logic]
│   └── evaluator.py       # [Ready for Phase 1 - Evaluation metrics]
├── requirements.txt       # Python dependencies
├── README.md
└── .gitignore
```

### Core Files Created

1. **src/config.py** - Centralized configuration
   - Model: DistilBERT (distilbert-base-uncased)
   - Task: Binary sentiment classification
   - Max length: 128 tokens
   - Batch size: 16
   - Learning rate: 2e-5
   - Epochs: 3

2. **src/utils.py** - Utilities
   - `set_seed()` - Reproducibility
   - `get_device()` - CPU/GPU detection
   - `print_gpu_info()` - GPU details
   - JSON save/load helpers

3. **src/data_handler.py** - Data management
   - `SentimentDataHandler` class with methods:
     - `load_csv()` - Load CSV datasets
     - `preprocess_texts()` - Tokenization
     - `create_dataset()` - HuggingFace Dataset creation
     - `train_test_split_data()` - Split into train/val/test

4. **src/model.py** - Model wrapper
   - `SentimentModel` class
   - Model loading/saving
   - Forward pass with tokenization

### Dependencies Installed

**Core Libraries:**
- `torch` - Deep learning framework (CPU version)
- `transformers` - Pre-trained models
- `datasets` - Data loading utilities
- `scikit-learn` - Metrics and utilities
- `numpy`, `pandas` - Data manipulation
- `accelerate` - Training acceleration

**Development:**
- `jupyter`, `ipykernel` - Notebooks
- `matplotlib`, `seaborn` - Visualization
- `python-dotenv` - Environment variables
- `tqdm` - Progress bars

### Environment Setup

**Activate virtual environment:**
```bash
cd c:\Users\Admin\OneDrive\Desktop\Umesh\distilbert_sentiment
.\.venv\Scripts\activate
```

**Verify installation (when ready):**
```bash
python -m pip show torch transformers datasets
```

## Known Issues & Solutions

### Windows DLL Error
If you encounter: `OSError: [WinError 1114] A dynamic link library (DLL) initialization routine failed`

**Solutions:**
1. **Reinstall Visual C++ Redistributable** (recommended)
   - Download from: https://support.microsoft.com/en-us/help/2977003
   - Install the latest x64 version

2. **Try older PyTorch version:**
   ```bash
   pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Use conda instead of venv:**
   ```bash
   conda create -n distilbert python=3.10
   conda install pytorch torchvision torchaudio cpuonly -c pytorch
   conda install -c conda-forge transformers datasets
   ```

## Next Steps for Phase 1

Ready to proceed with:
1. ✓ Data preparation module
2. ✓ Training loop implementation
3. ✓ Evaluation metrics
4. ✓ Model checkpointing
5. ✓ Results visualization

**Confirm you're ready to proceed to Phase 1 development!**

---

### Configuration Reference

All settings in `src/config.py`:

| Setting | Value | Description |
|---------|-------|-------------|
| MODEL_NAME | distilbert-base-uncased | Pre-trained model |
| NUM_CLASSES | 2 | Binary classification |
| MAX_LENGTH | 128 | Token sequence length |
| BATCH_SIZE | 16 | Training batch size |
| LEARNING_RATE | 2e-5 | Adam optimizer LR |
| NUM_EPOCHS | 3 | Training epochs |
| WARMUP_STEPS | 500 | LR warmup steps |
| DEVICE | cpu/cuda | Auto-detected |
| SEED | 42 | Reproducibility |

### How to Use the Modular Structure

**Example - Loading and preprocessing data:**
```python
from src.config import DATA_DIR, MAX_LENGTH
from src.data_handler import SentimentDataHandler
from src.utils import set_seed

# Set reproducibility
set_seed(42)

# Initialize handler
handler = SentimentDataHandler()

# Load data
df = handler.load_csv(DATA_DIR / "sentiment_data.csv")
texts = df['text'].tolist()
labels = df['label'].tolist()

# Split data
train_ds, val_ds, test_ds = handler.train_test_split_data(texts, labels)
```

**Example - Model initialization:**
```python
from src.model import SentimentModel
from src.utils import get_device

device = get_device()
model = SentimentModel(device=device)
```

---

## Status Summary

✅ Project structure created  
✅ Core modules configured  
✅ Dependencies resolved  
✅ Configuration centralized  
⏳ **Ready for Phase 1 development**

**What happens next?**
You confirm readiness → I create trainer.py and evaluator.py → Implement training loop → Build evaluation metrics → Create visualization utilities
