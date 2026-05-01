"""
Data handling utilities for sentiment analysis
"""
from typing import Tuple, Dict, List
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict
import torch
from transformers import AutoTokenizer
from config import (
    MAX_LENGTH, 
    MODEL_NAME, 
    TRAIN_TEST_SPLIT as TEST_SPLIT,
    VALIDATION_SPLIT,
    SEED
)


class SentimentDataHandler:
    """Handler for sentiment analysis data processing"""
    
    def __init__(self, model_name: str = MODEL_NAME):
        """
        Initialize data handler with tokenizer
        
        Args:
            model_name: HuggingFace model name
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model_name = model_name
    
    def load_csv(self, csv_path: Path) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Pandas DataFrame
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        return pd.read_csv(csv_path)
    
    def preprocess_texts(
        self, 
        texts: List[str], 
        max_length: int = MAX_LENGTH
    ) -> Dict[str, torch.Tensor]:
        """
        Tokenize and preprocess texts
        
        Args:
            texts: List of text strings
            max_length: Maximum sequence length
            
        Returns:
            Dictionary with input_ids and attention_mask
        """
        encodings = self.tokenizer(
            texts,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return encodings
    
    def create_dataset(
        self,
        texts: List[str],
        labels: List[int]
    ) -> Dataset:
        """
        Create HuggingFace Dataset from texts and labels
        
        Args:
            texts: List of text strings
            labels: List of label integers
            
        Returns:
            HuggingFace Dataset
        """
        encodings = self.preprocess_texts(texts)
        
        dataset_dict = {
            'input_ids': encodings['input_ids'],
            'attention_mask': encodings['attention_mask'],
            'labels': torch.tensor(labels)
        }
        
        return Dataset.from_dict(dataset_dict)
    
    def train_test_split_data(
        self,
        texts: List[str],
        labels: List[int],
        test_size: float = TEST_SPLIT,
        val_size: float = VALIDATION_SPLIT,
        random_state: int = SEED
    ) -> Tuple[Dataset, Dataset, Dataset]:
        """
        Split data into train, validation, and test sets
        
        Args:
            texts: List of text strings
            labels: List of label integers
            test_size: Test set proportion
            val_size: Validation set proportion (of train set)
            random_state: Random seed
            
        Returns:
            Tuple of (train_dataset, val_dataset, test_dataset)
        """
        # First split: train+val vs test
        texts_temp, texts_test, labels_temp, labels_test = train_test_split(
            texts,
            labels,
            test_size=test_size,
            random_state=random_state,
            stratify=labels
        )
        
        # Second split: train vs val
        texts_train, texts_val, labels_train, labels_val = train_test_split(
            texts_temp,
            labels_temp,
            test_size=val_size,
            random_state=random_state,
            stratify=labels_temp
        )
        
        train_dataset = self.create_dataset(texts_train, labels_train)
        val_dataset = self.create_dataset(texts_val, labels_val)
        test_dataset = self.create_dataset(texts_test, labels_test)
        
        return train_dataset, val_dataset, test_dataset
