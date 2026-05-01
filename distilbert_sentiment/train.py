#!/usr/bin/env python3
"""
Train DistilBERT for sentiment classification on IMDb dataset.

Features:
- Fine-tune DistilBERT with HuggingFace Trainer API
- Early stopping based on validation metrics
- Checkpoint saving and best model preservation
- Comprehensive metrics: accuracy, precision, recall, F1
- CPU-friendly defaults with gradient accumulation
- Reproducible training with fixed seed
- Memory-efficient training for limited resources

Usage:
    python train.py [--epochs 3] [--batch_size 16] [--learning_rate 2e-5]

Example:
    python train.py --epochs 3 --batch_size 8 --learning_rate 2e-5
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import torch
from datasets import load_from_disk, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import (
    MODEL_NAME,
    MAX_LENGTH,
    DATA_DIR,
    MODELS_DIR,
    OUTPUTS_DIR,
    SEED,
    DEVICE,
)
from utils import set_seed, create_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SentimentTrainer:
    """
    Trainer for DistilBERT sentiment classification.
    
    Wraps HuggingFace Trainer with:
    - Early stopping
    - Checkpoint management
    - Comprehensive metrics
    - CPU-friendly configuration
    - Reproducible training
    """
    
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        seed: int = SEED,
        device: str = DEVICE,
    ):
        """
        Initialize trainer.
        
        Args:
            model_name: HuggingFace model identifier
            seed: Random seed for reproducibility
            device: Training device (cuda or cpu)
        """
        set_seed(seed)
        
        self.model_name = model_name
        self.seed = seed
        self.device = device
        
        # Model and tokenizer will be loaded later
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        logger.info(f"Initialized SentimentTrainer (model={model_name}, device={device})")
    
    def load_model_and_tokenizer(self) -> Tuple:
        """
        Load model and tokenizer.
        
        Returns:
            Tuple of (model, tokenizer)
        
        Raises:
            RuntimeError: If model/tokenizer loading fails
        """
        try:
            logger.info(f"Loading tokenizer from {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            logger.info(f"Loading model from {self.model_name}...")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=2,  # Binary classification (negative/positive)
                torch_dtype=torch.float32,  # CPU-friendly (float32 instead of mixed precision)
            )
            
            # Move model to device
            self.model.to(self.device)
            
            logger.info(f"Model loaded successfully")
            logger.info(f"  Total parameters: {self.model.num_parameters():,}")
            logger.info(f"  Trainable parameters: {sum(p.numel() for p in self.model.parameters() if p.requires_grad):,}")
            
            return self.model, self.tokenizer
        
        except Exception as e:
            logger.error(f"Failed to load model/tokenizer: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}") from e
    
    def load_datasets(
        self,
        train_path: Path = DATA_DIR / "train",
        val_path: Path = DATA_DIR / "validation",
    ) -> Tuple[Dataset, Dataset]:
        """
        Load preprocessed datasets.
        
        Args:
            train_path: Path to training dataset
            val_path: Path to validation dataset
        
        Returns:
            Tuple of (train_dataset, eval_dataset)
        
        Raises:
            RuntimeError: If dataset loading fails
        """
        try:
            train_path = Path(train_path)
            val_path = Path(val_path)
            
            if not train_path.exists():
                raise FileNotFoundError(f"Training data not found at {train_path}")
            if not val_path.exists():
                raise FileNotFoundError(f"Validation data not found at {val_path}")
            
            logger.info(f"Loading training dataset from {train_path}...")
            train_dataset = load_from_disk(str(train_path))
            logger.info(f"  Loaded {len(train_dataset)} training samples")
            
            logger.info(f"Loading validation dataset from {val_path}...")
            eval_dataset = load_from_disk(str(val_path))
            logger.info(f"  Loaded {len(eval_dataset)} validation samples")
            
            return train_dataset, eval_dataset
        
        except (FileNotFoundError, Exception) as e:
            logger.error(f"Failed to load datasets: {str(e)}")
            raise RuntimeError(f"Dataset loading failed: {str(e)}") from e
    
    def compute_metrics(self, eval_pred) -> Dict[str, float]:
        """
        Compute metrics for evaluation.
        
        Args:
            eval_pred: EvalPrediction object with predictions and label_ids
        
        Returns:
            Dictionary with accuracy, precision, recall, f1
        
        Metrics:
            - accuracy: Fraction of correct predictions
            - precision: TP / (TP + FP) - correctness of positive predictions
            - recall: TP / (TP + FN) - coverage of actual positives
            - f1: Harmonic mean of precision and recall
        """
        predictions, labels = eval_pred
        
        # Get predicted class (argmax of logits)
        pred_labels = np.argmax(predictions, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(labels, pred_labels)
        precision = precision_score(labels, pred_labels, zero_division=0)
        recall = recall_score(labels, pred_labels, zero_division=0)
        f1 = f1_score(labels, pred_labels, zero_division=0)
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    
    def train(
        self,
        train_dataset: Dataset,
        eval_dataset: Dataset,
        num_train_epochs: int = 3,
        per_device_train_batch_size: int = 16,
        per_device_eval_batch_size: int = 32,
        learning_rate: float = 2e-5,
        warmup_ratio: float = 0.1,
        early_stopping_patience: int = 3,
        output_dir: Path = MODELS_DIR,
    ) -> Tuple[Dict, str]:
        """
        Train model using HuggingFace Trainer API.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Evaluation dataset
            num_train_epochs: Number of training epochs
            per_device_train_batch_size: Training batch size per device
            per_device_eval_batch_size: Evaluation batch size per device
            learning_rate: AdamW learning rate
            warmup_ratio: Fraction of training steps for warmup
            early_stopping_patience: Stop if no improvement for N evaluations
            output_dir: Directory to save outputs
        
        Returns:
            Tuple of (train_results, best_model_path)
        
        Features:
        - Gradient accumulation for CPU (simulates larger batches)
        - Early stopping callback
        - Checkpoint saving
        - Metric-based evaluation
        - Memory-efficient defaults
        """
        output_dir = Path(output_dir)
        create_directory(output_dir)
        
        # Calculate training steps for warmup
        num_update_steps = (len(train_dataset) // per_device_train_batch_size) * num_train_epochs
        
        logger.info("\n" + "="*80)
        logger.info("TRAINING CONFIGURATION")
        logger.info("="*80)
        logger.info(f"Model: {self.model_name}")
        logger.info(f"Device: {self.device}")
        logger.info(f"Epochs: {num_train_epochs}")
        logger.info(f"Train batch size: {per_device_train_batch_size}")
        logger.info(f"Eval batch size: {per_device_eval_batch_size}")
        logger.info(f"Learning rate: {learning_rate}")
        logger.info(f"Warmup ratio: {warmup_ratio}")
        logger.info(f"Total training steps: {num_update_steps}")
        logger.info(f"Output directory: {output_dir}")
        logger.info("="*80 + "\n")
        
        # Define training arguments
        training_args = TrainingArguments(
            output_dir=str(output_dir / "checkpoints"),
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=per_device_train_batch_size,
            per_device_eval_batch_size=per_device_eval_batch_size,
            warmup_ratio=warmup_ratio,
            learning_rate=learning_rate,
            weight_decay=0.01,
            adam_epsilon=1e-8,
            
            # Evaluation and saving strategy
            eval_strategy="epoch",
            save_strategy="epoch",
            save_total_limit=3,  # Keep only 3 best checkpoints
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            
            # Logging
            logging_strategy="steps",
            logging_steps=50,
            log_level="info",
            
            # CPU optimization
            gradient_accumulation_steps=2,  # Accumulate gradients for CPU training
            fp16=False,  # No mixed precision on CPU (use float32)
            bf16=False,  # No bfloat16 on CPU
            
            # Other settings
            seed=self.seed,
            disable_tqdm=False,
            report_to=["tensorboard"],  # Can add wandb if available
            dataloader_pin_memory=False,  # CPU doesn't benefit from pinned memory
            optim="adamw_torch",  # Use standard PyTorch AdamW (stable, not deprecated)
        )
        
        # Early stopping callback
        early_stopping = EarlyStoppingCallback(
            early_stopping_patience=early_stopping_patience,
            early_stopping_threshold=0.0,
        )
        
        # Initialize trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics,
            callbacks=[early_stopping],
        )
        
        logger.info("Starting training...\n")
        
        # Train
        try:
            train_result = self.trainer.train()
            logger.info("\n✅ Training completed successfully!")
        except KeyboardInterrupt:
            logger.warning("Training interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            raise RuntimeError(f"Training error: {str(e)}") from e
        
        # Save best model
        best_model_path = output_dir / "best_model"
        logger.info(f"\nSaving best model to {best_model_path}...")
        self.trainer.save_model(str(best_model_path))
        
        # Save training metrics
        metrics_path = output_dir / "training_metrics.json"
        logger.info(f"Saving training metrics to {metrics_path}...")
        import json
        with open(metrics_path, 'w') as f:
            json.dump(train_result.metrics, f, indent=2)
        
        logger.info("\n" + "="*80)
        logger.info("TRAINING SUMMARY")
        logger.info("="*80)
        logger.info(f"Final training loss: {train_result.metrics.get('train_loss', 'N/A'):.4f}")
        logger.info(f"Best model saved to: {best_model_path}")
        logger.info(f"Metrics saved to: {metrics_path}")
        logger.info("="*80 + "\n")
        
        return train_result.metrics, str(best_model_path)
    
    def evaluate(self, eval_dataset: Dataset) -> Dict[str, float]:
        """
        Evaluate model on dataset.
        
        Args:
            eval_dataset: Dataset to evaluate on
        
        Returns:
            Dictionary with evaluation metrics
        """
        if self.trainer is None:
            raise RuntimeError("Trainer not initialized. Call train() first.")
        
        logger.info("Running evaluation...")
        metrics = self.trainer.evaluate(eval_dataset=eval_dataset)
        
        logger.info("\n" + "="*80)
        logger.info("EVALUATION RESULTS")
        logger.info("="*80)
        logger.info(f"Accuracy:  {metrics.get('eval_accuracy', 0):.4f}")
        logger.info(f"Precision: {metrics.get('eval_precision', 0):.4f}")
        logger.info(f"Recall:    {metrics.get('eval_recall', 0):.4f}")
        logger.info(f"F1-Score:  {metrics.get('eval_f1', 0):.4f}")
        logger.info("="*80 + "\n")
        
        return metrics


def main():
    """
    Main entry point for training.
    
    Steps:
    1. Parse command-line arguments
    2. Initialize trainer
    3. Load model and datasets
    4. Run training
    5. Save results
    """
    parser = argparse.ArgumentParser(
        description="Train DistilBERT for sentiment classification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train.py                                    # Default settings
  python train.py --epochs 5 --batch_size 8         # Custom epochs and batch size
  python train.py --learning_rate 1e-5 --epochs 3   # Custom learning rate
        """
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs (default: 3)"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=16,
        help="Training batch size per device (default: 16)"
    )
    parser.add_argument(
        "--eval_batch_size",
        type=int,
        default=32,
        help="Evaluation batch size per device (default: 32)"
    )
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=2e-5,
        help="Learning rate for AdamW optimizer (default: 2e-5)"
    )
    parser.add_argument(
        "--warmup_ratio",
        type=float,
        default=0.1,
        help="Warmup ratio of total training steps (default: 0.1)"
    )
    parser.add_argument(
        "--early_stopping_patience",
        type=int,
        default=3,
        help="Early stopping patience in evaluations (default: 3)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=str(MODELS_DIR),
        help=f"Output directory for models (default: {MODELS_DIR})"
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default=str(DATA_DIR),
        help=f"Data directory with train/validation splits (default: {DATA_DIR})"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help=f"Random seed for reproducibility (default: {SEED})"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=DEVICE,
        choices=["cpu", "cuda"],
        help=f"Training device (default: {DEVICE})"
    )
    
    args = parser.parse_args()
    
    # Log configuration
    logger.info("\n" + "="*80)
    logger.info("COMMAND LINE ARGUMENTS")
    logger.info("="*80)
    for key, value in vars(args).items():
        logger.info(f"{key}: {value}")
    logger.info("="*80 + "\n")
    
    # Check if data exists
    data_dir = Path(args.data_dir)
    if not (data_dir / "train").exists():
        logger.error(f"Training data not found at {data_dir / 'train'}")
        logger.error("Please run preprocessing first: python preprocess.py")
        sys.exit(1)
    
    # Initialize trainer
    trainer = SentimentTrainer(
        model_name=MODEL_NAME,
        seed=args.seed,
        device=args.device,
    )
    
    # Load model and datasets
    trainer.load_model_and_tokenizer()
    train_dataset, eval_dataset = trainer.load_datasets(
        train_path=data_dir / "train",
        val_path=data_dir / "validation",
    )
    
    # Train
    try:
        metrics, best_model_path = trainer.train(
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            num_train_epochs=args.epochs,
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=args.eval_batch_size,
            learning_rate=args.learning_rate,
            warmup_ratio=args.warmup_ratio,
            early_stopping_patience=args.early_stopping_patience,
            output_dir=Path(args.output_dir),
        )
        
        # Final evaluation
        final_metrics = trainer.evaluate(eval_dataset)
        
        logger.info("\n" + "="*80)
        logger.info("✅ TRAINING COMPLETE")
        logger.info("="*80)
        logger.info(f"Best model: {best_model_path}")
        logger.info(f"Metrics: {final_metrics}")
        logger.info("="*80 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n❌ Training failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
