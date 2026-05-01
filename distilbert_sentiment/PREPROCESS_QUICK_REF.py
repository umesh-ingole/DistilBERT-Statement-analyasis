#!/usr/bin/env python3
"""
PREPROCESS.PY - QUICK REFERENCE

IMDb Sentiment Dataset Preprocessing with DistilBERT

For full documentation, see: PREPROCESS_GUIDE.md
"""

# ============================================================================
# QUICK START
# ============================================================================

# 1. RUN FULL PREPROCESSING
# $ python preprocess.py
# 
# Output:
#   ✓ Downloads IMDb dataset (25,000 reviews)
#   ✓ Validates samples (removes bad data)
#   ✓ Tokenizes with DistilBERT
#   ✓ Splits into train/validation
#   ✓ Saves to data/ directory
#
# Time: ~3-4 minutes (first run includes download)
# Output: data/train/, data/validation/


# ============================================================================
# USAGE IN CODE
# ============================================================================

# OPTION 1: Use preprocessing function
from preprocess import preprocess_imdb

train_data, val_data = preprocess_imdb()
print(f"Train: {len(train_data)} samples")
print(f"Validation: {len(val_data)} samples")


# OPTION 2: Use class for custom preprocessing
from preprocess import IMDbPreprocessor
from config import DATA_DIR

preprocessor = IMDbPreprocessor()

# Load
dataset = preprocessor.load_imdb_dataset('train')
print(f"Loaded {len(dataset)} samples")

# Validate
dataset, errors = preprocessor.validate_dataset(dataset)
print(f"Validation errors: {errors}")

# Preprocess (tokenize)
processed = preprocessor.preprocess_dataset(dataset)

# Split
train, val, test = preprocessor.split_dataset(processed)

# Save
preprocessor.save_datasets(train, val, test)

# Load later
train, val, test = preprocessor.load_preprocessed_datasets(DATA_DIR)


# ============================================================================
# SAMPLE INSPECTION
# ============================================================================

# Get one sample
sample = train_data[0]

# What's inside
print(sample.keys())
# Output: dict_keys(['input_ids', 'attention_mask', 'labels'])

print(sample['input_ids'].shape)     # Shape: (128,) - token IDs
print(sample['attention_mask'])      # [1, 1, 1, ..., 0, 0] - mask
print(sample['labels'])              # 0 (negative) or 1 (positive)

# Get batch
batch = train_data[:4]

print(batch['input_ids'].shape)      # (4, 128) - 4 samples of 128 tokens
print(batch['labels'])               # tensor([1, 0, 1, 1])


# ============================================================================
# UNDERSTANDING TOKENIZATION
# ============================================================================

# What tokenization does:
#
# Original:     "This movie is amazing!"
#       ↓
# Tokens:       ["this", "movie", "is", "amazing", "!"]
#       ↓
# Token IDs:    [2023, 3185, 2003, 6571, 999]
#       ↓
# Padded:       [2023, 3185, 2003, 6571, 999, 0, 0, ..., 0]  (to length=128)
#       ↓
# Attention:    [1, 1, 1, 1, 1, 0, 0, ..., 0]  (1=real token, 0=padding)


# ============================================================================
# VALIDATION EXAMPLES
# ============================================================================

from preprocess import IMDbPreprocessor

preprocessor = IMDbPreprocessor()

# Good samples (will pass validation)
is_valid, msg = preprocessor.validate_sample("Great movie!", 1, 0)
# Output: (True, 'OK')

is_valid, msg = preprocessor.validate_sample("Terrible film.", 0, 1)
# Output: (True, 'OK')

# Bad samples (will be filtered)
is_valid, msg = preprocessor.validate_sample("", 1, 2)
# Output: (False, 'Sample 2: Text is empty')

is_valid, msg = preprocessor.validate_sample(None, 1, 3)
# Output: (False, 'Sample 3: Text is None')

is_valid, msg = preprocessor.validate_sample("Good!", 2, 4)
# Output: (False, 'Sample 4: Invalid label 2 (must be 0 or 1)')


# ============================================================================
# DATASET STRUCTURE
# ============================================================================

# After preprocessing, you have:
# 
# data/
#   train/          - 22,500 training samples
#     dataset.arrow
#     dataset_dict.json
#     state.json
#   validation/     - 2,500 validation samples
#     dataset.arrow
#     dataset_dict.json
#     state.json
#   test/           - 5,000 test samples (optional)
#     dataset.arrow
#     dataset_dict.json
#     state.json


# ============================================================================
# BATCH PROCESSING
# ============================================================================

# Get batches for training
batch_size = 16

for i in range(0, len(train_data), batch_size):
    batch = train_data[i:i+batch_size]
    
    # Each batch contains:
    # batch['input_ids']       - Token IDs (batch_size, 128)
    # batch['attention_mask']  - Masks (batch_size, 128)
    # batch['labels']          - Labels (batch_size,)
    
    # Batch size can be different for last batch
    print(f"Batch {i//batch_size}: {batch['input_ids'].shape[0]} samples")


# ============================================================================
# CONFIGURATION
# ============================================================================

# Modify in src/config.py:
#
# MODEL_NAME = "distilbert-base-uncased"  # Tokenizer model
# MAX_LENGTH = 128                        # Max sequence length
# BATCH_SIZE = 16                         # Processing batch size
# TRAIN_TEST_SPLIT = 0.2                  # Test set fraction
# VALIDATION_SPLIT = 0.1                  # Validation fraction of train
# SEED = 42                               # For reproducibility
#
# To customize:
#   MAX_LENGTH = 256      # Longer sequences
#   BATCH_SIZE = 32       # Larger batches (uses more GPU memory)


# ============================================================================
# COMMON TASKS
# ============================================================================

# TASK 1: Preprocess with custom settings
from preprocess import preprocess_imdb
from config import DATA_DIR

train, val = preprocess_imdb(
    output_dir=DATA_DIR,
    batch_size=32,          # Larger batch
    remove_test_set=True    # Only train/val
)


# TASK 2: Validate custom data
from preprocess import IMDbPreprocessor

preprocessor = IMDbPreprocessor()

# Check a single sample
is_valid, msg = preprocessor.validate_sample(
    text="My custom review",
    label=1,
    sample_id=0
)

print(f"Valid: {is_valid}")
if not is_valid:
    print(f"Reason: {msg}")


# TASK 3: Preprocess with different max_length
from preprocess import IMDbPreprocessor
from config import DATA_DIR

preprocessor = IMDbPreprocessor()
dataset = preprocessor.load_imdb_dataset('train')
dataset, _ = preprocessor.validate_dataset(dataset)

# Tokenize with custom max_length
processed = preprocessor.preprocess_dataset(
    dataset,
    batch_size=16
)

# (max_length is controlled by modifying tokenize_batch)


# TASK 4: Load previously saved data
from preprocess import IMDbPreprocessor
from config import DATA_DIR

preprocessor = IMDbPreprocessor()
train, val, test = preprocessor.load_preprocessed_datasets(DATA_DIR)

print(f"Loaded {len(train)} training samples")
print(f"Loaded {len(val)} validation samples")


# TASK 5: Create custom validation
from preprocess import IMDbPreprocessor

preprocessor = IMDbPreprocessor()
dataset = preprocessor.load_imdb_dataset('train')

# Validate with error tracking
clean_dataset, num_errors = preprocessor.validate_dataset(
    dataset,
    verbose=True
)

if num_errors > 0:
    print(f"Found {num_errors} errors:")
    for error in preprocessor.validation_errors[:5]:
        print(f"  - {error}")


# ============================================================================
# ERROR HANDLING
# ============================================================================

try:
    # Try to load and preprocess
    train_data, val_data = preprocess_imdb()
    
except FileNotFoundError as e:
    print(f"File not found: {e}")
    
except RuntimeError as e:
    print(f"Runtime error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")


# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

# 1. First run is slower (downloads dataset)
#    - First run: ~3-4 minutes
#    - Subsequent runs: ~1 minute (uses cache)
#
# 2. Increase batch_size for speed (if memory allows)
#    - Default: 16
#    - Options: 32, 64 (faster but needs more GPU memory)
#
# 3. Reduce max_length for memory savings
#    - Default: 128
#    - Options: 64, 96 (faster but loses some text)
#
# 4. Use GPU for faster tokenization
#    - Tokenizer can run on GPU
#    - Check DEVICE in config.py


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

# Problem: "Module not found: config"
# Solution: Run from project root directory
#   $ cd distilbert_sentiment
#   $ python preprocess.py

# Problem: "Network error downloading dataset"
# Solution: Check internet, try again
#   Datasets are cached after first download

# Problem: "Out of memory" error
# Solution: Reduce batch_size
#   preprocess_imdb(batch_size=8)  # Instead of 16

# Problem: "Tokenizer not found"
# Solution: Install/update transformers
#   $ pip install transformers --upgrade


# ============================================================================
# NEXT STEPS
# ============================================================================

# After preprocessing:
#
# 1. TRAIN THE MODEL
#    $ python train.py
#    - Uses preprocessed data in data/train/
#    - Saves model to models/best_model/
#
# 2. EVALUATE THE MODEL
#    $ python test.py
#    - Tests on data/validation/
#    - Prints metrics (accuracy, precision, recall, F1)
#
# 3. ANALYZE RESULTS
#    - View metrics in outputs/
#    - Plot loss curves
#    - Analyze predictions


# ============================================================================
# FILE REFERENCE
# ============================================================================

# preprocess.py
#   Main preprocessing script
#   - IMDbPreprocessor class
#   - preprocess_imdb() function
#   - main() entry point
#
# PREPROCESS_GUIDE.md
#   Full documentation with examples
#   - Detailed API reference
#   - Usage examples
#   - Troubleshooting
#
# src/config.py
#   Configuration constants
#   - MAX_LENGTH, BATCH_SIZE, etc.
#
# src/utils.py
#   Utility functions
#   - set_seed(), create_directory(), etc.


# ============================================================================
# SUMMARY
# ============================================================================

"""
preprocess.py provides complete IMDb dataset preprocessing:

✓ Automatic download from HuggingFace
✓ Quality validation with error checking
✓ DistilBERT tokenization with padding/truncation
✓ Train/validation/test splitting
✓ Efficient binary format saving
✓ Comprehensive error handling
✓ Detailed logging and progress tracking

Three ways to use:

1. Command line (easiest):
   $ python preprocess.py

2. In code (simple):
   from preprocess import preprocess_imdb
   train, val = preprocess_imdb()

3. Custom (flexible):
   preprocessor = IMDbPreprocessor()
   dataset = preprocessor.load_imdb_dataset('train')
   ... (custom processing steps)

Ready for Phase 1 training!
"""
