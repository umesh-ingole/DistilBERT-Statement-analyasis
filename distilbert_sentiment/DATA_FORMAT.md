# Sample Data Format

Your sentiment analysis model expects CSV files with the following format:

## Required CSV Structure

**File:** `data/sentiment_data.csv`

```csv
text,label
"This movie was absolutely amazing!",1
"I loved the acting and storytelling.",1
"Best film I've seen all year.",1
"Terrible waste of time.",0
"The plot was confusing and boring.",0
"I couldn't stand watching this.",0
```

### Column Definitions

| Column | Type | Description |
|--------|------|-------------|
| `text` | string | Review or sentiment text (required) |
| `label` | int | 0 = negative, 1 = positive (required) |

### Example Datasets

You can use:
1. **Movie Reviews** (IMDB format)
2. **Product Reviews** (Amazon format)
3. **Social Media** (Twitter, Reddit sentiment)
4. **Custom Reviews**

### Sample CSV with 20 rows

```csv
text,label
"Absolutely fantastic experience!",1
"Best purchase I've ever made.",1
"Love it! Highly recommend!",1
"Amazing quality and service.",1
"This is wonderful!",1
"Terrible quality.",0
"Waste of money.",0
"Very disappointed.",0
"Horrible experience.",0
"Would not recommend.",0
"Great value for money!",1
"Perfect! Five stars!",1
"Not worth it at all.",0
"Decent but not great.",0
"Could be better.",0
"Really enjoyed this.",1
"Outstanding work!",1
"Poor quality.",0
"Exceeded expectations!",1
"Not satisfied.",0
```

## How to Use with the Training Code

Once you create `data/sentiment_data.csv`, the training script will:

```python
from src.data_handler import SentimentDataHandler
from pathlib import Path

handler = SentimentDataHandler()
df = handler.load_csv(Path("data/sentiment_data.csv"))

# Automatically splits into 80% train, 10% val, 10% test
train_ds, val_ds, test_ds = handler.train_test_split_data(
    df['text'].tolist(),
    df['label'].tolist()
)

print(f"Train: {len(train_ds)} samples")
print(f"Val: {len(val_ds)} samples")  
print(f"Test: {len(test_ds)} samples")
```

## Data Considerations

✓ **Minimum samples:** 200+ for reasonable training  
✓ **Balanced classes:** Similar number of positive/negative examples  
✓ **Text preprocessing:** Handled automatically by tokenizer  
✓ **Length:** Max 128 tokens (very long texts truncated)  

---

## Quick Start Dataset

To get started immediately, use the sample data above. Save it as `data/sentiment_data.csv` and you're ready for training!
