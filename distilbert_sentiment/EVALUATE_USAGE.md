# evaluate.py - Comprehensive Model Evaluation

## Overview

`evaluate.py` is a dedicated evaluation script that runs after model training to assess performance on the test dataset. It provides:

- ✅ **Metrics**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- ✅ **Confusion Matrix**: TP, FP, TN, FN with derived metrics
- ✅ **Sample Predictions**: 10 diverse examples (correct & incorrect)
- ✅ **Classification Report**: Per-class breakdown
- ✅ **JSON Export**: Results saved for reporting

---

## Prerequisites

1. **Training must be complete**: `models/best_model/` directory exists
2. **Data preprocessed**: `data/test_dataset/` exists
3. **Dependencies installed**: `pip install -r requirements.txt`
4. **Virtual environment activated**: `venv\Scripts\activate`

---

## Usage

### Basic Usage
```bash
python evaluate.py
```

### With Custom Model Path
```bash
python evaluate.py --model_path models/best_model
```

### With Custom Batch Size (for faster inference)
```bash
python evaluate.py --batch_size 64
```

### With Custom Output Directory
```bash
python evaluate.py --output_dir results/
```

### Full Example with All Options
```bash
python evaluate.py \
  --model_path models/best_model \
  --batch_size 64 \
  --data_dir data \
  --output_dir outputs \
  --seed 42 \
  --device cpu
```

### View All Options
```bash
python evaluate.py --help
```

---

## Expected Output

### 1. Initial Logs
```
2026-04-26 14:35:22,123 - INFO - ================================================================================
2026-04-26 14:35:22,124 - INFO - DISTILBERT SENTIMENT CLASSIFICATION - EVALUATION
2026-04-26 14:35:22,125 - INFO - ================================================================================
2026-04-26 14:35:22,126 - INFO - Model path: models/best_model
2026-04-26 14:35:22,127 - INFO - Batch size: 32
2026-04-26 14:35:22,128 - INFO - Data directory: data
2026-04-26 14:35:22,129 - INFO - Device: cpu
2026-04-26 14:35:22,130 - INFO - ================================================================================
2026-04-26 14:35:22,456 - INFO - Initializing evaluator with device: cpu
2026-04-26 14:35:22,789 - INFO - Loading model from: models/best_model
2026-04-26 14:35:25,123 - INFO - Model loaded successfully
2026-04-26 14:35:25,456 - INFO - Loading tokenizer
2026-04-26 14:35:25,789 - INFO - Tokenizer loaded successfully
2026-04-26 14:35:25,912 - INFO - Loading test dataset from: data/test_dataset
2026-04-26 14:35:26,145 - INFO - Test dataset loaded: 5000 samples
```

### 2. Evaluation Metrics
```
================================================================================
EVALUATION METRICS
================================================================================
Accuracy:  0.8923 (89.23%)
Precision: 0.8934 (89.34%)
Recall:    0.8910 (89.10%)
F1-Score:  0.8922 (89.22%)
ROC-AUC:   0.9450
================================================================================
```

**What Each Metric Means:**
- **Accuracy**: % of all predictions that were correct
- **Precision**: % of positive predictions that were actually positive
- **Recall**: % of actual positives that were correctly identified
- **F1-Score**: Balanced harmonic mean of precision & recall (best overall metric)
- **ROC-AUC**: Area under receiver operating characteristic curve (0-1, higher is better)

### 3. Confusion Matrix
```
================================================================================
CONFUSION MATRIX
================================================================================

True Positives (TP):   2230  (predicted POSITIVE, actually POSITIVE)
False Positives (FP):  285   (predicted POSITIVE, actually NEGATIVE)
True Negatives (TN):   2215  (predicted NEGATIVE, actually NEGATIVE)
False Negatives (FN):  270   (predicted NEGATIVE, actually POSITIVE)

Total samples: 5000
Sensitivity (True Positive Rate): 0.8920
Specificity (True Negative Rate): 0.8858
================================================================================
```

**What This Means:**
- **TP (2230)**: Model correctly predicted POSITIVE reviews (true positives)
- **FP (285)**: Model predicted POSITIVE but were actually NEGATIVE (false alarms)
- **TN (2215)**: Model correctly predicted NEGATIVE reviews (true negatives)
- **FN (270)**: Model predicted NEGATIVE but were actually POSITIVE (misses)
- **Sensitivity**: How many actual positives did we catch? 89.20%
- **Specificity**: How many actual negatives did we correctly identify? 88.58%

### 4. Sample Predictions
```
================================================================================
SAMPLE PREDICTIONS
================================================================================

Showing 10 samples (8 correct, 2 incorrect)

1. [✓ CORRECT]
   Text: This movie is absolutely fantastic! The acting is superb and the plot...
   True Label:      POSITIVE
   Predicted Label: POSITIVE (confidence: 8.3421)

2. [✓ CORRECT]
   Text: Terrible waste of time. Poor acting and boring story. Not recommend...
   True Label:      NEGATIVE
   Predicted Label: NEGATIVE (confidence: -7.8956)

3. [✓ CORRECT]
   Text: One of the best films I've ever seen! Highly entertaining from start...
   True Label:      POSITIVE
   Predicted Label: POSITIVE (confidence: 7.9234)

4. [✗ WRONG]
   Text: The movie had some good moments but overall it was quite boring...
   True Label:      NEGATIVE
   Predicted Label: POSITIVE (confidence: 2.1456)

5. [✓ CORRECT]
   Text: Don't bother watching this. Absolutely horrible. Worst movie ever...
   True Label:      NEGATIVE
   Predicted Label: NEGATIVE (confidence: -8.5234)

6. [✓ CORRECT]
   Text: Amazing! Perfect in every way. I loved every second of it...
   True Label:      POSITIVE
   Predicted Label: POSITIVE (confidence: 8.7123)

7. [✗ WRONG]
   Text: It's okay. Some parts were good, some parts were bad. Average...
   True Label:      POSITIVE
   Predicted Label: NEGATIVE (confidence: -1.2345)

8. [✓ CORRECT]
   Text: This film exceeded all my expectations. Brilliant and captivating...
   True Label:      POSITIVE
   Predicted Label: POSITIVE (confidence: 8.1567)

9. [✓ CORRECT]
   Text: Complete disaster. I couldn't even finish watching it...
   True Label:      NEGATIVE
   Predicted Label: NEGATIVE (confidence: -7.6234)

10. [✓ CORRECT]
    Text: Absolutely wonderful! A masterpiece of cinema. Highly recommend...
    True Label:      POSITIVE
    Predicted Label: POSITIVE (confidence: 8.9456)

================================================================================
```

**Understanding Confidence:**
- **Positive confidence** (e.g., +8.34): Model is confident it's POSITIVE
- **Negative confidence** (e.g., -7.89): Model is confident it's NEGATIVE
- **Near zero** (e.g., ±0.5): Model is uncertain
- **Larger magnitude** (|8.0+|): Model is very confident

### 5. Classification Report
```
================================================================================
CLASSIFICATION REPORT
================================================================================

              precision    recall  f1-score   support

    NEGATIVE       0.89      0.89      0.89      2500
    POSITIVE       0.89      0.89      0.89      2500

    accuracy                           0.89      5000
   macro avg       0.89      0.89      0.89      5000
weighted avg       0.89      0.89      0.89      5000

================================================================================
```

**Reading the Classification Report:**
- **NEGATIVE metrics**: How well the model performs on negative reviews
  - Precision: 89% of predicted NEGATIVE were actually NEGATIVE
  - Recall: 89% of actual NEGATIVE were correctly identified
  - F1-Score: Balanced metric (89%)

- **POSITIVE metrics**: How well the model performs on positive reviews
  - Precision: 89% of predicted POSITIVE were actually POSITIVE
  - Recall: 89% of actual POSITIVE were correctly identified
  - F1-Score: Balanced metric (89%)

- **Support**: Number of samples in each class (2,500 NEGATIVE, 2,500 POSITIVE)

### 6. Final Status
```
================================================================================
EVALUATION COMPLETE
================================================================================
Results saved to: outputs/evaluation_results.json
================================================================================

2026-04-26 14:37:45,789 - INFO - Evaluation completed successfully!
```

---

## Output Files

### JSON Results File: `outputs/evaluation_results.json`

```json
{
  "metrics": {
    "accuracy": 0.8923,
    "precision": 0.8934,
    "recall": 0.8910,
    "f1": 0.8922,
    "roc_auc": 0.9450
  },
  "confusion_matrix": {
    "TP": 2230,
    "FP": 285,
    "TN": 2215,
    "FN": 270
  },
  "samples": [
    {
      "index": 156,
      "text": "This movie is absolutely fantastic! The acting is super...",
      "true_label": "POSITIVE",
      "predicted_label": "POSITIVE",
      "confidence": 8.3421,
      "correct": true
    },
    ...
  ],
  "num_samples": 5000
}
```

---

## Interpreting Results

### ✅ Good Results
- Accuracy, Precision, Recall, F1 all > 85%
- ROC-AUC > 0.90
- Confusion matrix: Mostly TP and TN (diagonal heavy)
- Sample predictions mostly correct

### ⚠️ Warning Signs
- Any metric < 70%
- ROC-AUC < 0.75
- FP or FN significantly higher than expected
- Sample predictions showing systematic errors

### 📊 Typical Results for Sentiment Analysis
- **Accuracy**: 85-92% (challenging task)
- **Precision**: 85-92% (depends on class balance)
- **Recall**: 85-92% (depends on class balance)
- **F1-Score**: 85-92% (balanced metric)
- **ROC-AUC**: 0.93-0.97 (very good separation)

---

## Common Issues & Solutions

### Issue: `FileNotFoundError: Model not found`
**Solution:** Run training first
```bash
python train.py
```

### Issue: `FileNotFoundError: Test dataset not found`
**Solution:** Run preprocessing first
```bash
python preprocess.py
```

### Issue: Evaluation is very slow
**Solution:** Increase batch size
```bash
python evaluate.py --batch_size 128
```

### Issue: `CUDA out of memory`
**Solution:** Already CPU-optimized; reduce batch size if needed
```bash
python evaluate.py --batch_size 16
```

---

## Parameter Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--model_path` | `models/best_model` | Path to trained model checkpoint |
| `--batch_size` | 32 | Batch size for inference (higher = faster, more memory) |
| `--data_dir` | `data` | Directory containing test dataset |
| `--output_dir` | `outputs` | Directory to save evaluation results |
| `--seed` | 42 | Random seed for reproducibility |
| `--device` | `cpu` | Device to use (cpu or cuda) |

---

## Workflow

### Complete Sentiment Analysis Pipeline

```bash
# 1. Preprocess data (one-time)
python preprocess.py

# 2. Train model
python train.py

# 3. Evaluate on test set
python evaluate.py

# 4. View results
cat outputs/evaluation_results.json
```

---

## Key Features

✅ **Comprehensive Metrics**  
All standard ML metrics in one place

✅ **Confusion Matrix**  
Visual representation of prediction performance

✅ **Sample Predictions**  
See real examples of correct and incorrect predictions

✅ **Detailed Classification Report**  
Per-class performance breakdown

✅ **JSON Export**  
Easy integration with reporting tools

✅ **Well-Documented Terminal Output**  
Clear, human-readable results

✅ **Production Ready**  
Full error handling and logging

---

## Code Structure

```python
class SentimentEvaluator:
    - load_model_and_tokenizer()     # Load trained model
    - load_eval_dataset()             # Load test data
    - get_predictions()               # Run inference
    - compute_metrics()               # Calculate metrics
    - get_confusion_matrix()          # Build confusion matrix
    - get_sample_predictions()        # Extract diverse examples
    - print_metrics()                 # Display metrics
    - print_confusion_matrix()        # Display confusion matrix
    - print_sample_predictions()      # Display samples
    - print_classification_report()   # Display detailed report
    - evaluate()                      # Run complete evaluation

def main():                            # CLI entry point
```

---

## Technical Details

- **Framework**: HuggingFace Transformers + Trainer API
- **Model**: DistilBERT (distilbert-base-uncased)
- **Dataset**: IMDb sentiment (5,000 test samples)
- **Metrics**: scikit-learn for all calculations
- **Device**: Auto-detects CPU/GPU
- **Seed**: Fixed at 42 for reproducibility

---

**Created**: April 26, 2026  
**Status**: ✅ Production Ready  
**Lines of Code**: 500+  
**Dependencies**: transformers, torch, datasets, sklearn, numpy
