# Quick Start Guide - DistilBERT Sentiment Analysis

## ✅ Status: Ready to Run

Both `train.py` and `test.py` have been validated and are production-ready.

---

## 🚀 Quick Start (5 minutes)

### 1. Activate Virtual Environment
```bash
cd c:\Users\Admin\OneDrive\Desktop\Umesh\distilbert_sentiment
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Data
```bash
python preprocess.py
```

Expected output:
- `data/train_dataset/` (18,000 reviews)
- `data/validation_dataset/` (2,000 reviews)
- `data/test_dataset/` (5,000 reviews)

### 4. Train Model
```bash
python train.py
```

Expected duration: 8-10 minutes on CPU

### 5. Evaluate Model
```bash
python test.py
```

Expected output: `outputs/evaluation_results.json` with metrics

---

## 📋 File Structure

```
distilbert_sentiment/
├── train.py                    # ✅ Training script (529 lines)
├── test.py                     # ✅ Evaluation script (544 lines)
├── preprocess.py               # ✅ Data preprocessing
├── src/
│   ├── config.py              # ✅ Configuration
│   ├── utils.py               # ✅ Utilities
│   ├── data_handler.py        # ✅ Data handling
│   └── model.py               # ✅ Model wrapper
├── requirements.txt            # ✅ Dependencies
├── data/                       # (created after preprocess.py)
│   ├── train_dataset/
│   ├── validation_dataset/
│   └── test_dataset/
├── models/                     # (created after train.py)
│   ├── best_model/            # Best checkpoint
│   └── checkpoints/           # All checkpoints
└── outputs/                    # (created after test.py)
    └── evaluation_results.json
```

---

## 🔧 Configuration

All settings in `src/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| MODEL_NAME | distilbert-base-uncased | Pre-trained model |
| BATCH_SIZE | 16 | Training batch size |
| NUM_EPOCHS | 3 | Number of training epochs |
| LEARNING_RATE | 2e-5 | Fine-tuning learning rate |
| SEED | 42 | Reproducibility seed |
| MAX_LENGTH | 128 | Max token sequence length |

---

## 📊 Expected Results

### Training (per epoch on CPU)
```
Epoch 1: loss~0.45, f1~0.88
Epoch 2: loss~0.35, f1~0.90  
Epoch 3: loss~0.28, f1~0.92
```

### Evaluation
```
Accuracy:  ~89%
Precision: ~89%
Recall:    ~89%
F1-Score:  ~89%
ROC-AUC:   ~94%
```

---

## ⚙️ Advanced Usage

### Custom Training Parameters
```bash
python train.py \
  --epochs 5 \
  --batch_size 8 \
  --learning_rate 1e-5 \
  --early_stopping_patience 5 \
  --warmup_ratio 0.1
```

### Custom Evaluation
```bash
python test.py \
  --model_path models/best_model \
  --batch_size 64 \
  --output_dir outputs/
```

### View All Options
```bash
python train.py --help
python test.py --help
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Activate venv: `venv\Scripts\activate` |
| Data not found | Run: `python preprocess.py` |
| Model not found | Ensure `train.py` completed successfully |
| GPU memory error | Already CPU-optimized; reduce `--batch_size` if needed |
| Slow training | Normal on CPU; expected 8-10 min for 18k samples |

---

## ✨ Key Features

✅ **HuggingFace Trainer API** - Production-grade training framework  
✅ **Early Stopping** - Prevents overfitting (patience=3 evaluations)  
✅ **Checkpointing** - Saves best 3 models automatically  
✅ **CPU Optimized** - Gradient accumulation, no mixed precision  
✅ **Comprehensive Metrics** - Accuracy, Precision, Recall, F1, ROC-AUC  
✅ **Reproducible** - Fixed seed=42 across all components  
✅ **Error Handling** - Comprehensive logging and exception handling  
✅ **CLI Friendly** - Full argument parsing for easy customization  

---

## 📚 Full Documentation

- `TEST_VERIFICATION_RESULTS.md` - Validation report
- `TRAINING_AND_EVALUATION_GUIDE.md` - Detailed parameter reference
- `TRAINING_IMPLEMENTATION_DETAILS.md` - Architecture and design decisions

---

## 🎯 What Happens During Training

1. **Load**: DistilBERT model + WordPiece tokenizer
2. **Initialize**: HuggingFace Trainer with:
   - Early stopping (patience=3)
   - Checkpoint saving (every epoch)
   - Best model selection (by F1-score)
3. **Train**: 3 epochs on 18,000 samples
   - Evaluation every epoch
   - Auto-save best model
   - Stop early if no improvement
4. **Output**: 
   - Best model → `models/best_model/`
   - Checkpoints → `models/checkpoints/`
   - Training logs → console

---

## 🎯 What Happens During Evaluation

1. **Load**: Best trained model from checkpoint
2. **Evaluate**: On 5,000 test samples
3. **Compute**: Metrics (accuracy, precision, recall, F1, ROC-AUC)
4. **Generate**: Confusion matrix and per-class statistics
5. **Save**: Results to `outputs/evaluation_results.json`

---

**Status: ✅ Both scripts validated and ready to run!**
