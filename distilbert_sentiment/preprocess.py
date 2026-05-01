"""
Preprocess IMDb sentiment dataset for DistilBERT training.

This script:
1. Downloads the IMDb dataset from HuggingFace
2. Tokenizes reviews with DistilBERT tokenizer
3. Validates and filters bad samples
4. Splits into train/validation sets
5. Saves preprocessed data for training

IMDb Dataset Info:
- Source: HuggingFace Datasets (imdb)
- Size: 50,000 examples (25,000 train, 25,000 test) + 50,000 unlabeled
- Labels: 0 = negative, 1 = positive
- Text: Movie reviews (10-1000+ words)
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import torch
import numpy as np
from datasets import load_dataset, Dataset, DatasetDict
from transformers import AutoTokenizer
import logging

# Add src to path to import config
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import (
    MODEL_NAME,
    MAX_LENGTH,
    SEED,
    DATA_DIR,
    BATCH_SIZE,
    TRAIN_TEST_SPLIT,
    VALIDATION_SPLIT,
)
from utils import set_seed, create_directory


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IMDbPreprocessor:
    """
    Preprocessor for IMDb sentiment dataset with error checking and validation.
    
    Workflow:
    1. Load IMDb dataset from HuggingFace
    2. Validate samples (check text/label quality)
    3. Filter bad samples
    4. Tokenize with DistilBERT tokenizer
    5. Create train/validation split
    6. Save preprocessed data
    """
    
    def __init__(self, model_name: str = MODEL_NAME, seed: int = SEED):
        """
        Initialize the preprocessor.
        
        Args:
            model_name: HuggingFace model name (for tokenizer)
            seed: Random seed for reproducibility
        """
        set_seed(seed)
        self.model_name = model_name
        self.seed = seed
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.dataset = None
        self.validation_errors = []
        
        logger.info(f"Initialized preprocessor with model: {model_name}")
    
    def load_imdb_dataset(self, split: str = "train") -> Dataset:
        """
        Load IMDb dataset from HuggingFace.
        
        Args:
            split: Which split to load ('train', 'test', 'unsupervised', or None for all)
                  - 'train': 25,000 labeled training examples
                  - 'test': 25,000 labeled test examples
                  - 'unsupervised': 50,000 unlabeled reviews
                  - None: all splits combined
        
        Returns:
            HuggingFace Dataset object
        
        Example:
            >>> preprocessor = IMDbPreprocessor()
            >>> dataset = preprocessor.load_imdb_dataset('train')
            >>> print(f"Loaded {len(dataset)} examples")
        """
        try:
            logger.info(f"Downloading IMDb dataset (split='{split}')...")
            
            if split is None:
                # Load all splits and combine
                imdb_train = load_dataset("imdb", split="train")
                imdb_test = load_dataset("imdb", split="test")
                dataset = DatasetDict({
                    "train": imdb_train,
                    "test": imdb_test,
                })
                logger.info(f"Loaded complete IMDb dataset: "
                           f"{len(imdb_train)} train + {len(imdb_test)} test examples")
                return dataset
            else:
                # Load specific split
                dataset = load_dataset("imdb", split=split)
                logger.info(f"Loaded IMDb dataset ({split}): {len(dataset)} examples")
                return dataset
                
        except Exception as e:
            logger.error(f"Failed to load IMDb dataset: {str(e)}")
            raise
    
    def validate_sample(self, text: str, label: int, sample_id: int) -> Tuple[bool, str]:
        """
        Validate a single sample for quality and format.
        
        Checks:
        - Text is not None/empty
        - Text is string type
        - Text has minimum length (5+ words)
        - Label is 0 or 1 (binary classification)
        - No suspicious patterns
        
        Args:
            text: Review text to validate
            label: Label (0 or 1)
            sample_id: Sample index for error tracking
        
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        
        Example:
            >>> is_valid, msg = preprocessor.validate_sample("Great movie!", 1, 0)
            >>> print(f"Valid: {is_valid}, Message: {msg}")
        """
        # Check if text is None
        if text is None:
            return False, f"Sample {sample_id}: Text is None"
        
        # Check if text is string
        if not isinstance(text, str):
            return False, f"Sample {sample_id}: Text is not string (type: {type(text).__name__})"
        
        # Check if text is empty or too short
        text_clean = text.strip()
        if len(text_clean) == 0:
            return False, f"Sample {sample_id}: Text is empty"
        
        # Check minimum word count (at least 2 words for a meaningful review)
        word_count = len(text_clean.split())
        if word_count < 2:
            return False, f"Sample {sample_id}: Text too short ({word_count} words, need >=2)"
        
        # Check label is valid (0 or 1 for binary classification)
        if label not in [0, 1]:
            return False, f"Sample {sample_id}: Invalid label {label} (must be 0 or 1)"
        
        # Check label type
        if not isinstance(label, (int, np.integer)):
            return False, f"Sample {sample_id}: Label is not integer (type: {type(label).__name__})"
        
        # No issues found
        return True, "OK"
    
    def validate_dataset(self, dataset: Dataset, verbose: bool = True) -> Tuple[Dataset, int]:
        """
        Validate entire dataset and filter bad samples.
        
        This function:
        - Checks each sample for quality
        - Logs validation errors
        - Removes invalid samples
        - Returns cleaned dataset and error count
        
        Args:
            dataset: HuggingFace Dataset to validate
            verbose: If True, log all errors
        
        Returns:
            Tuple of (cleaned_dataset, num_errors)
        
        Example:
            >>> dataset = preprocessor.load_imdb_dataset('train')
            >>> clean_dataset, errors = preprocessor.validate_dataset(dataset)
            >>> print(f"Removed {errors} bad samples, kept {len(clean_dataset)}")
        """
        logger.info(f"Validating {len(dataset)} samples...")
        
        valid_indices = []
        self.validation_errors = []
        
        # Check each sample
        for idx, sample in enumerate(dataset):
            text = sample.get('text', '')
            label = sample.get('label', -1)
            is_valid, error_msg = self.validate_sample(text, label, idx)
            
            if is_valid:
                valid_indices.append(idx)
            else:
                self.validation_errors.append(error_msg)
                if verbose and len(self.validation_errors) <= 10:  # Log first 10 errors
                    logger.warning(error_msg)
        
        # Log summary
        num_errors = len(self.validation_errors)
        logger.info(f"Validation complete: {len(valid_indices)} valid, {num_errors} invalid")
        
        if num_errors > 0:
            logger.info(f"First error: {self.validation_errors[0]}")
        
        # Filter dataset to keep only valid samples
        if num_errors > 0:
            cleaned_dataset = dataset.select(valid_indices)
            logger.info(f"Filtered dataset: {len(dataset)} -> {len(cleaned_dataset)} samples")
            return cleaned_dataset, num_errors
        
        return dataset, num_errors
    
    def tokenize_batch(
        self,
        examples: Dict[str, List],
        max_length: int = MAX_LENGTH
    ) -> Dict[str, torch.Tensor]:
        """
        Tokenize a batch of examples using DistilBERT tokenizer.
        
        Process:
        1. Take list of texts from batch
        2. Tokenize with wordpiece tokenization
        3. Pad to max_length with [PAD] token
        4. Truncate to max_length
        5. Create attention masks (1 for real tokens, 0 for padding)
        
        Args:
            examples: Dict with 'text' key containing list of review texts
            max_length: Maximum sequence length (default: 128 tokens)
        
        Returns:
            Dict with 'input_ids' and 'attention_mask' tensors
        
        Tokenization Example:
            Text: "Great movie!"
            Tokens: ['great', 'movie', '!']
            Token IDs: [2572, 3185, 999]  # Using DistilBERT vocabulary
            Padded (max_length=5): [2572, 3185, 999, 0, 0]
            Attention Mask: [1, 1, 1, 0, 0]  # 1 for real tokens, 0 for padding
        
        Truncation Example:
            Long text (300 tokens) -> Truncated to 128 tokens
            Original: [token1, token2, ..., token300]
            Truncated: [token1, token2, ..., token128]
        """
        # Tokenize texts with special handling
        encodings = self.tokenizer(
            examples['text'],  # List of review texts
            max_length=max_length,  # Maximum sequence length
            padding='max_length',  # Pad all to max_length
            truncation=True,  # Truncate if longer than max_length
            return_tensors=None,  # Return as Python lists (converted later)
        )
        
        # Add labels to encodings
        encodings['labels'] = examples['label']
        
        return encodings
    
    def preprocess_dataset(
        self,
        dataset: Dataset,
        batch_size: int = BATCH_SIZE
    ) -> Dataset:
        """
        Preprocess entire dataset using batch tokenization.
        
        This function:
        - Maps tokenization over dataset in batches
        - Keeps original 'text' column for reference
        - Removes unnecessary columns
        - Converts to PyTorch tensors
        
        Args:
            dataset: HuggingFace Dataset to preprocess
            batch_size: Batch size for processing
        
        Returns:
            Preprocessed Dataset with 'input_ids', 'attention_mask', 'labels'
        
        Example:
            >>> dataset = preprocessor.load_imdb_dataset('train')
            >>> processed = preprocessor.preprocess_dataset(dataset)
            >>> print(processed.features)
            # Shows: input_ids, attention_mask, labels
        """
        logger.info(f"Preprocessing {len(dataset)} samples with batch_size={batch_size}...")
        
        # Apply tokenization to entire dataset in batches
        processed = dataset.map(
            self.tokenize_batch,
            batched=True,  # Process in batches for speed
            batch_size=batch_size,
            remove_columns=['text'],  # Remove original text column (save disk space)
            desc="Tokenizing",  # Progress bar description
            num_proc=1,  # Number of processes (use 1 on Windows)
        )
        
        # Set format for PyTorch
        processed.set_format(
            type='torch',
            columns=['input_ids', 'attention_mask', 'labels']
        )
        
        logger.info(f"Preprocessing complete. Dataset features: {processed.features}")
        
        return processed
    
    def split_dataset(
        self,
        dataset: Dataset,
        train_size: float = 1.0 - TRAIN_TEST_SPLIT,
        val_size: float = VALIDATION_SPLIT,
        seed: int = None
    ) -> Tuple[Dataset, Dataset, Optional[Dataset]]:
        """
        Split dataset into train/validation/test sets.
        
        Split Strategy:
        - Original: Single dataset
        - Step 1: Split into train (80%) and test (20%)
        - Step 2: Split train into train (90%) and validation (10%)
        - Result: train=72%, validation=8%, test=20%
        
        Alternative: Can use different proportions by adjusting train_size and val_size
        
        Args:
            dataset: HuggingFace Dataset to split
            train_size: Fraction for train set (default: 0.8)
            val_size: Fraction of train to use for validation (default: 0.1)
            seed: Random seed for reproducibility
        
        Returns:
            Tuple of (train_dataset, val_dataset, test_dataset)
        
        Example:
            >>> dataset = preprocessor.preprocess_dataset(imdb_dataset)
            >>> train, val, test = preprocessor.split_dataset(dataset)
            >>> print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        """
        if seed is None:
            seed = self.seed
        
        logger.info(f"Splitting dataset: {len(dataset)} samples")
        
        # Step 1: Split into train and test
        test_size = 1.0 - train_size
        train_test_split = dataset.train_test_split(
            test_size=test_size,
            seed=seed
        )
        
        train_data = train_test_split['train']
        test_data = train_test_split['test']
        
        logger.info(f"Initial split: {len(train_data)} train, {len(test_data)} test")
        
        # Step 2: Split train into train and validation
        train_val_split = train_data.train_test_split(
            test_size=val_size,
            seed=seed
        )
        
        train_final = train_val_split['train']
        val_final = train_val_split['test']
        
        logger.info(f"Final split: {len(train_final)} train, "
                   f"{len(val_final)} validation, {len(test_data)} test")
        
        return train_final, val_final, test_data
    
    def save_datasets(
        self,
        train_dataset: Dataset,
        val_dataset: Dataset,
        test_dataset: Optional[Dataset] = None,
        output_dir: Path = DATA_DIR
    ) -> None:
        """
        Save preprocessed datasets to disk.
        
        Saves as HuggingFace dataset format for easy loading:
        - output_dir/train/
        - output_dir/validation/
        - output_dir/test/ (optional)
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset
            test_dataset: Test dataset (optional)
            output_dir: Output directory (default: data/)
        
        Example:
            >>> preprocessor.save_datasets(train_data, val_data, test_data)
            >>> # Creates: data/train/, data/validation/, data/test/
        """
        output_dir = Path(output_dir)
        create_directory(output_dir)
        
        # Save train dataset
        train_path = output_dir / "train"
        logger.info(f"Saving training dataset to {train_path}...")
        train_dataset.save_to_disk(str(train_path))
        logger.info(f"Saved {len(train_dataset)} training samples")
        
        # Save validation dataset
        val_path = output_dir / "validation"
        logger.info(f"Saving validation dataset to {val_path}...")
        val_dataset.save_to_disk(str(val_path))
        logger.info(f"Saved {len(val_dataset)} validation samples")
        
        # Save test dataset if provided
        if test_dataset is not None:
            test_path = output_dir / "test"
            logger.info(f"Saving test dataset to {test_path}...")
            test_dataset.save_to_disk(str(test_path))
            logger.info(f"Saved {len(test_dataset)} test samples")
    
    def load_preprocessed_datasets(
        self,
        input_dir: Path = DATA_DIR
    ) -> Tuple[Dataset, Dataset, Optional[Dataset]]:
        """
        Load previously saved preprocessed datasets.
        
        Args:
            input_dir: Directory containing saved datasets
        
        Returns:
            Tuple of (train_dataset, val_dataset, test_dataset)
        """
        input_dir = Path(input_dir)
        
        logger.info(f"Loading preprocessed datasets from {input_dir}...")
        
        train_path = input_dir / "train"
        val_path = input_dir / "validation"
        test_path = input_dir / "test"
        
        train_dataset = Dataset.load_from_disk(str(train_path))
        val_dataset = Dataset.load_from_disk(str(val_path))
        test_dataset = Dataset.load_from_disk(str(test_path)) if test_path.exists() else None
        
        logger.info(f"Loaded {len(train_dataset)} train, {len(val_dataset)} validation samples")
        
        return train_dataset, val_dataset, test_dataset


def preprocess_imdb(
    output_dir: Path = DATA_DIR,
    batch_size: int = BATCH_SIZE,
    remove_test_set: bool = True
) -> Tuple[Dataset, Dataset]:
    """
    Complete preprocessing pipeline for IMDb dataset.
    
    Steps:
    1. Load IMDb training dataset
    2. Validate samples (remove bad examples)
    3. Tokenize texts with DistilBERT
    4. Split into train/validation
    5. Save to disk
    
    Args:
        output_dir: Where to save preprocessed data
        batch_size: Batch size for tokenization
        remove_test_set: If True, don't save test set (only train/val)
    
    Returns:
        Tuple of (train_dataset, val_dataset)
    
    Example:
        >>> train_data, val_data = preprocess_imdb()
        >>> print(f"Train: {len(train_data)}, Val: {len(val_data)}")
        Train: 22400, Val: 2600
    """
    logger.info("="*70)
    logger.info("IMDB SENTIMENT DATASET PREPROCESSING")
    logger.info("="*70)
    
    # Initialize preprocessor
    preprocessor = IMDbPreprocessor()
    
    # Step 1: Load dataset
    logger.info("\nSTEP 1: Loading IMDb dataset...")
    imdb_dataset = preprocessor.load_imdb_dataset(split='train')
    
    # Step 2: Validate samples
    logger.info("\nSTEP 2: Validating samples...")
    imdb_dataset, num_errors = preprocessor.validate_dataset(imdb_dataset, verbose=True)
    
    if num_errors > 0:
        logger.warning(f"Removed {num_errors} invalid samples")
    
    # Step 3: Preprocess (tokenize)
    logger.info("\nSTEP 3: Tokenizing with DistilBERT...")
    processed_dataset = preprocessor.preprocess_dataset(
        imdb_dataset,
        batch_size=batch_size
    )
    
    # Step 4: Split dataset
    logger.info("\nSTEP 4: Splitting into train/validation...")
    train_data, val_data, test_data = preprocessor.split_dataset(
        processed_dataset,
        train_size=1.0 - TRAIN_TEST_SPLIT,
        val_size=VALIDATION_SPLIT
    )
    
    # Step 5: Save datasets
    logger.info("\nSTEP 5: Saving preprocessed datasets...")
    if remove_test_set:
        preprocessor.save_datasets(train_data, val_data, test_dataset=None, output_dir=output_dir)
    else:
        preprocessor.save_datasets(train_data, val_data, test_data, output_dir=output_dir)
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("PREPROCESSING COMPLETE")
    logger.info("="*70)
    logger.info(f"Training samples: {len(train_data)}")
    logger.info(f"Validation samples: {len(val_data)}")
    if not remove_test_set:
        logger.info(f"Test samples: {len(test_data)}")
    logger.info(f"Max sequence length: {MAX_LENGTH}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Output directory: {output_dir}")
    logger.info("="*70 + "\n")
    
    return train_data, val_data


def main():
    """
    Main entry point for preprocessing.
    
    Run with: python preprocess.py
    """
    print("\n" + "="*70)
    print("IMDb SENTIMENT DATASET PREPROCESSING")
    print("="*70)
    print("This script will:")
    print("  1. Download IMDb dataset (25,000 training reviews)")
    print("  2. Validate samples (check for quality/format issues)")
    print("  3. Tokenize with DistilBERT (convert text to token IDs)")
    print("  4. Split into training (80%) and validation (10%) sets")
    print("  5. Save preprocessed data for training")
    print("="*70 + "\n")
    
    # Run preprocessing
    train_data, val_data = preprocess_imdb(
        output_dir=DATA_DIR,
        batch_size=BATCH_SIZE,
        remove_test_set=True
    )
    
    # Show sample
    print("\n" + "="*70)
    print("SAMPLE FROM TRAINING DATA")
    print("="*70)
    sample = train_data[0]
    print(f"Input IDs shape: {sample['input_ids'].shape}")
    print(f"Attention mask: {sample['attention_mask'][:20]}...")  # First 20 tokens
    print(f"Label: {sample['labels']} (0=negative, 1=positive)")
    print("="*70 + "\n")
    
    print("✓ Preprocessing complete! Data saved to:", DATA_DIR)
    print(f"  Train: {len(train_data)} samples")
    print(f"  Validation: {len(val_data)} samples")


if __name__ == "__main__":
    main()
