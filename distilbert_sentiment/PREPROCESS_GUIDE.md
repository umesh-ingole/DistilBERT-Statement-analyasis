# IMDb Preprocessing Guide

## Overview

`preprocess.py` is a complete data preprocessing pipeline for sentiment analysis using the IMDb dataset. It handles data loading, validation, tokenization, and splitting with detailed error checking.

---

## What It Does

### Step-by-Step Process

```
1. LOAD IMDb Dataset
   Download 25,000 labeled reviews from HuggingFace

2. VALIDATE SAMPLES
   Check for quality issues:
   - Null/empty texts
   - Invalid labels
   - Suspicious patterns
   
3. TOKENIZE
   Convert text to token IDs:
   - DistilBERT wordpiece tokenization
   - Padding to max_length=128
   - Truncation for long texts
   
4. SPLIT DATA
   Train/Validation/Test split:
   - Training: 72% (18,000 samples)
   - Validation: 8% (2,000 samples)
   - Test: 20% (5,000 samples)
   
5. SAVE
   Store preprocessed data for training
```

---

## Quick Start

### Run Preprocessing

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate    # macOS/Linux

# Navigate to project root
cd distilbert_sentiment

# Run preprocessing
python preprocess.py
```

**Expected Output:**
```
======================================================================
IMDb SENTIMENT DATASET PREPROCESSING
======================================================================
This script will:
  1. Download IMDb dataset (25,000 training reviews)
  2. Validate samples (check for quality/format issues)
  3. Tokenize with DistilBERT (convert text to token IDs)
  4. Split into training (80%) and validation (10%) sets
  5. Save preprocessed data for training
======================================================================

STEP 1: Loading IMDb dataset...
2024-04-26 10:30:45,123 - INFO - Downloading IMDb dataset (split='train')...
2024-04-26 10:30:52,456 - INFO - Loaded IMDb dataset (train): 25000 examples

STEP 2: Validating samples...
2024-04-26 10:30:52,789 - INFO - Validating 25000 samples...
2024-04-26 10:30:54,012 - INFO - Validation complete: 25000 valid, 0 invalid
```

After completion:
- ✓ Preprocessing complete! Data saved to: data/
  - Train: 22500 samples
  - Validation: 2500 samples

---

## Key Components

### 1. IMDbPreprocessor Class

Main class handling all preprocessing operations.

**Initialization:**
```python
from preprocess import IMDbPreprocessor

preprocessor = IMDbPreprocessor(
    model_name="distilbert-base-uncased",
    seed=42
)
```

**Core Methods:**

#### load_imdb_dataset(split='train')
Load IMDb dataset from HuggingFace.

```python
# Load training examples
dataset = preprocessor.load_imdb_dataset('train')  # 25,000 examples
print(f"Loaded {len(dataset)} samples")

# Access a sample
sample = dataset[0]
print(f"Text: {sample['text'][:100]}...")
print(f"Label: {sample['label']} (0=negative, 1=positive)")
```

**Output Example:**
```
Text: I watched this movie hoping to see more of the recent Casey Affleck...
Label: 1 (positive)
```

---

#### validate_sample(text, label, sample_id)
Check if a single sample is valid.

```python
is_valid, msg = preprocessor.validate_sample(
    text="Great movie!",
    label=1,
    sample_id=0
)
print(f"Valid: {is_valid}, Message: {msg}")
# Output: Valid: True, Message: OK

# Invalid sample
is_valid, msg = preprocessor.validate_sample(
    text="",  # Empty text
    label=1,
    sample_id=1
)
print(f"Valid: {is_valid}, Message: {msg}")
# Output: Valid: False, Message: Sample 1: Text is empty
```

**Validation Checks:**
- Text is not None/empty
- Text is string type
- Text has minimum length (5+ characters)
- Label is 0 or 1 (binary)
- No suspicious patterns

---

#### validate_dataset(dataset, verbose=True)
Validate entire dataset and filter bad samples.

```python
dataset = preprocessor.load_imdb_dataset('train')
clean_dataset, num_errors = preprocessor.validate_dataset(
    dataset,
    verbose=True
)

print(f"Removed {num_errors} invalid samples")
print(f"Kept {len(clean_dataset)} valid samples")
```

**Output:**
```
INFO - Validating 25000 samples...
INFO - Validation complete: 25000 valid, 0 invalid
INFO - Filtered dataset: 25000 -> 25000 samples
```

---

#### tokenize_batch(examples, max_length=128)
Tokenize a batch of texts using DistilBERT.

```python
# Batch of texts
batch = {
    'text': [
        "Amazing movie!",
        "Terrible film."
    ],
    'label': [1, 0]
}

# Tokenize
tokenized = preprocessor.tokenize_batch(batch, max_length=128)

print(tokenized.keys())
# Output: dict_keys(['input_ids', 'attention_mask', 'labels'])

print(tokenized['input_ids'])
# Output: [[2572, 3185, 999, 0, ...], [14225, 3185, 1012, 0, ...]]

print(tokenized['attention_mask'])
# Output: [[1, 1, 1, 0, ...], [1, 1, 1, 0, ...]]
```

**What Happens:**
1. Text is split into tokens: "Amazing" → "amaz" + "ing"
2. Tokens converted to IDs: "amaz"→2572, "ing"→3185
3. Padded with [PAD] tokens (ID=0) to length 128
4. Attention mask created: 1 for real tokens, 0 for padding

---

#### preprocess_dataset(dataset, batch_size=16)
Tokenize entire dataset efficiently.

```python
dataset = preprocessor.load_imdb_dataset('train')
processed = preprocessor.preprocess_dataset(
    dataset,
    batch_size=16
)

print(processed.features)
# Output: {'input_ids': Sequence(feature=Value(dtype='int64')),
#          'attention_mask': Sequence(feature=Value(dtype='int64')),
#          'labels': ClassLabel(names=['0', '1'])}

# Check a sample
sample = processed[0]
print(f"Input IDs shape: {sample['input_ids'].shape}")  # (128,)
print(f"Attention mask shape: {sample['attention_mask'].shape}")  # (128,)
print(f"Label: {sample['labels']}")  # 0 or 1
```

---

#### split_dataset(dataset, train_size=0.8, val_size=0.1)
Split dataset into train/validation/test.

```python
train_data, val_data, test_data = preprocessor.split_dataset(
    processed_dataset,
    train_size=0.8,  # 80% for training
    val_size=0.1     # 10% of train for validation
)

print(f"Train: {len(train_data)}")      # ~18,000
print(f"Validation: {len(val_data)}")   # ~2,000
print(f"Test: {len(test_data)}")        # ~5,000
```

**Split Strategy:**
```
Original Dataset (25,000)
    ↓
Step 1: 80% train (20,000), 20% test (5,000)
    ↓
Step 2: 90% train (18,000), 10% validation (2,000)
    ↓
Final: Train (18,000), Validation (2,000), Test (5,000)
```

---

#### save_datasets(train, val, test, output_dir)
Save preprocessed datasets to disk.

```python
preprocessor.save_datasets(
    train_data,
    val_data,
    test_data,
    output_dir=DATA_DIR
)

# Creates:
# data/train/
# data/validation/
# data/test/
```

**Format:** HuggingFace Dataset Arrow format (binary, efficient)

---

### 2. Preprocessing Function

`preprocess_imdb()` - Complete pipeline in one function.

```python
from preprocess import preprocess_imdb

train_data, val_data = preprocess_imdb(
    output_dir="data/",
    batch_size=16,
    remove_test_set=True
)

print(f"Train: {len(train_data)}")
print(f"Validation: {len(val_data)}")
```

---

## Usage Examples

### Example 1: Full Pipeline

```python
from preprocess import preprocess_imdb
from config import DATA_DIR

# Run full preprocessing
train_data, val_data = preprocess_imdb(
    output_dir=DATA_DIR,
    batch_size=16
)

# Check dataset structure
print(f"Train dataset: {train_data}")
print(f"Val dataset: {val_data}")

# Get a sample
sample = train_data[0]
print(f"Sample keys: {sample.keys()}")
# Output: ['input_ids', 'attention_mask', 'labels']

print(f"Input shape: {sample['input_ids'].shape}")   # (128,)
print(f"Label: {sample['labels']}")                   # 0 or 1
```

---

### Example 2: Custom Preprocessing

```python
from preprocess import IMDbPreprocessor
from config import DATA_DIR, MAX_LENGTH

# Initialize
preprocessor = IMDbPreprocessor()

# Load and validate
dataset = preprocessor.load_imdb_dataset('train')
dataset, errors = preprocessor.validate_dataset(dataset)
print(f"Validation errors: {errors}")

# Custom tokenization with different max_length
processed = preprocessor.preprocess_dataset(
    dataset,
    batch_size=32  # Larger batch
)

# Custom split
train_data, val_data, test_data = preprocessor.split_dataset(
    processed,
    train_size=0.85,  # 85% train
    val_size=0.05     # 5% validation
)

# Save
preprocessor.save_datasets(train_data, val_data, test_data)
```

---

### Example 3: Load Preprocessed Data

```python
from preprocess import IMDbPreprocessor
from config import DATA_DIR

preprocessor = IMDbPreprocessor()

# Load saved datasets
train_data, val_data, test_data = preprocessor.load_preprocessed_datasets(
    input_dir=DATA_DIR
)

print(f"Loaded train: {len(train_data)} samples")
print(f"Loaded validation: {len(val_data)} samples")

# Use for training
for sample in train_data.take(1):
    print(f"Sample input_ids: {sample['input_ids']}")
    print(f"Sample label: {sample['labels']}")
```

---

### Example 4: Error Handling

```python
from preprocess import IMDbPreprocessor

preprocessor = IMDbPreprocessor()

try:
    # Load dataset
    dataset = preprocessor.load_imdb_dataset('train')
    
    # Validate
    dataset, errors = preprocessor.validate_dataset(dataset)
    
    if errors > 100:
        print(f"Warning: Found {errors} validation errors!")
        print(f"First errors:")
        for err in preprocessor.validation_errors[:5]:
            print(f"  - {err}")
    
    # Proceed with processing
    processed = preprocessor.preprocess_dataset(dataset)
    
except Exception as e:
    print(f"Error during preprocessing: {str(e)}")
```

---

## Understanding Tokenization

### How It Works

**Original Text:**
```
"This movie was absolutely amazing! ★★★★★"
```

**Step 1: Tokenization (Split into tokens)**
```
['this', 'movie', 'was', 'absolutely', 'amazing', '!', '★', '★', '★', '★', '★']
```

**Step 2: Vocabulary Lookup (Convert to IDs)**
```
[2023, 3185, 2001, 3360, 6571, 999, 100, 100, 100, 100, 100]
```

**Step 3: Padding (Add padding to reach max_length=128)**
```
[2023, 3185, 2001, 3360, 6571, 999, 100, 100, 100, 100, 100, 0, 0, 0, ..., 0]
Length: 128
```

**Step 4: Attention Mask (Mark which tokens are real)**
```
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, ..., 0]
     ↑ Real tokens                   ↑ Padding
```

### Why Padding?

DistilBERT requires fixed-size inputs. Without padding:
- Different samples have different lengths
- Cannot batch together in neural networks

With padding to max_length=128:
- All samples are same size
- Can batch together efficiently
- Attention mask tells model which parts to ignore

### Why Attention Mask?

Without attention mask, model would treat [PAD] as real tokens:
```
Input:     [2023, 3185, 2001, 0, 0, 0]
Attention: [1, 1, 1, 0, 0, 0]
                         ↑
Model ignores these [PAD] tokens in computation
```

---

## Validation Examples

### Good Samples (Will Pass)

```
Text: "This movie was incredible!"
Label: 1
Status: ✓ VALID
Reason: Non-empty string, valid label

Text: "Worst film I've ever seen."
Label: 0
Status: ✓ VALID
Reason: Non-empty string, valid label

Text: "It was okay."
Label: 0
Status: ✓ VALID
Reason: Valid format
```

### Bad Samples (Will Be Filtered)

```
Text: None
Label: 1
Status: ✗ INVALID
Reason: Text is None

Text: ""
Label: 0
Status: ✗ INVALID
Reason: Text is empty

Text: "Hi"
Label: 1
Status: ✓ VALID (2 words is minimum)

Text: "x"
Label: 0
Status: ✗ INVALID
Reason: Too short

Text: "Great movie!"
Label: 2
Status: ✗ INVALID
Reason: Invalid label (must be 0 or 1)

Text: "Amazing!"
Label: "1"  (string, not int)
Status: ✗ INVALID
Reason: Label type is string, not integer
```

---

## Output Structure

After preprocessing, data directory looks like:

```
data/
├── train/
│   ├── dataset_dict.json
│   ├── dataset.arrow     (22,500 samples)
│   └── state.json
├── validation/
│   ├── dataset_dict.json
│   ├── dataset.arrow     (2,500 samples)
│   └── state.json
└── test/
    ├── dataset_dict.json
    ├── dataset.arrow     (5,000 samples)
    └── state.json
```

**File Sizes (Approximate):**
- Each file: ~100-200 MB (binary Arrow format)
- Total: ~400-600 MB for full dataset

---

## Configuration

Edit settings in `src/config.py`:

```python
MODEL_NAME = "distilbert-base-uncased"  # Tokenizer model
MAX_LENGTH = 128                        # Sequence length
BATCH_SIZE = 16                         # Processing batch size
TRAIN_TEST_SPLIT = 0.2                  # Test set fraction
VALIDATION_SPLIT = 0.1                  # Val set fraction of train
SEED = 42                               # Reproducibility
```

---

## Troubleshooting

### Issue: "Module not found: config"
**Solution:**
```bash
# Make sure you're in project root
cd distilbert_sentiment

# Check structure
ls src/config.py  # Should exist

# Run from root
python preprocess.py
```

### Issue: "Network error downloading dataset"
**Solution:**
```bash
# Check internet connection
ping huggingface.co

# Try again
python preprocess.py
```

First run downloads ~80 MB dataset, subsequent runs use cache.

### Issue: "CUDA out of memory"
**Solution:** Reduce batch size in code:
```python
train_data, val_data = preprocess_imdb(
    batch_size=8  # Instead of 16
)
```

### Issue: "Tokenizer not found"
**Solution:**
```bash
# Install transformers
pip install transformers --upgrade

# Clear cache
rm -rf ~/.cache/huggingface/transformers/
```

---

## Performance Notes

### Processing Speed

- Loading dataset: ~30 seconds (first time, downloads from internet)
- Validation: ~5 seconds (25,000 samples)
- Tokenization: ~2-3 minutes (25,000 samples, depends on batch size)
- Splitting: ~1 second
- Saving: ~10 seconds
- **Total: ~3-4 minutes**

### Memory Usage

- During processing: ~2-3 GB RAM
- Saved datasets: ~300-500 MB disk

---

## Next Steps

After preprocessing:

1. **Train Model**
   ```bash
   python train.py
   ```

2. **Evaluate Model**
   ```bash
   python test.py
   ```

3. **Analyze Results**
   ```bash
   python analyze_results.py
   ```

---

## Reference

### Dataset Info

**IMDb**
- Source: Andrew L. Maas et al., 2011
- Train samples: 25,000 labeled
- Labels: 0 (negative, ≤4/10), 1 (positive, ≥7/10)
- Average review length: 200-300 words
- Problem: Binary sentiment classification

---

## API Reference

### IMDbPreprocessor

```python
class IMDbPreprocessor:
    __init__(model_name: str, seed: int)
    load_imdb_dataset(split: str) -> Dataset
    validate_sample(text: str, label: int, sample_id: int) -> Tuple[bool, str]
    validate_dataset(dataset: Dataset, verbose: bool) -> Tuple[Dataset, int]
    tokenize_batch(examples: Dict, max_length: int) -> Dict[str, Tensor]
    preprocess_dataset(dataset: Dataset, batch_size: int) -> Dataset
    split_dataset(dataset: Dataset, train_size: float, val_size: float) -> Tuple[Dataset, Dataset, Dataset]
    save_datasets(train: Dataset, val: Dataset, test: Dataset, output_dir: Path)
    load_preprocessed_datasets(input_dir: Path) -> Tuple[Dataset, Dataset, Dataset]
```

### Functions

```python
def preprocess_imdb(
    output_dir: Path,
    batch_size: int,
    remove_test_set: bool
) -> Tuple[Dataset, Dataset]

def main()
```

---

## Summary

`preprocess.py` provides a complete, production-ready data preprocessing solution:

✓ Load IMDb dataset automatically  
✓ Validate samples with error handling  
✓ Tokenize with DistilBERT  
✓ Create train/validation/test splits  
✓ Save efficiently for training  
✓ Detailed logging and error messages  
✓ Reusable class-based API  

Ready for Phase 1 training!
