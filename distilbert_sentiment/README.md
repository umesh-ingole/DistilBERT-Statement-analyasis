# DistilBERT Sentiment Analysis

Fine-tuned DistilBERT model for sentiment classification (positive/negative).

## Project Structure

```
distilbert_sentiment/
├── data/              # Dataset storage
├── models/            # Trained models and checkpoints
│   ├── checkpoints/   # Training checkpoints
│   └── best_model/    # Best model weights
├── outputs/           # Results, metrics, visualizations
├── notebooks/         # Jupyter notebooks for exploration
├── src/              # Source code
│   ├── __init__.py
│   ├── config.py     # Configuration settings
│   ├── utils.py      # Utility functions
│   ├── data_handler.py # Data processing
│   ├── model.py      # Model definition
│   ├── trainer.py    # Training logic (Phase 1)
│   └── evaluator.py  # Evaluation metrics (Phase 1)
├── requirements.txt  # Project dependencies
└── README.md        # This file
```

## Environment Setup

### Prerequisites
- Python 3.10
- Virtual environment (venv or conda)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Unix
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify GPU (optional):
```bash
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"
```

## Phases

### Phase 1 (Current)
- [x] Environment setup
- [x] Project structure
- [ ] Train sentiment model
- [ ] Test sentiment model

### Phase 2 (Future)
- [ ] Flask API deployment
- [ ] Model serving

## Usage

Training script will be available in Phase 1.

## Requirements

All dependencies are pinned to stable versions to prevent conflicts:
- torch==2.0.1
- transformers==4.33.0
- datasets==2.14.0
- scikit-learn==1.3.0
- pandas==2.0.3
- numpy==1.24.3

## Notes

- Using DistilBERT for lighter model size while maintaining performance
- Binary classification (positive/negative sentiment)
- Max sequence length: 128 tokens
- Batch size: 16
- Learning rate: 2e-5
