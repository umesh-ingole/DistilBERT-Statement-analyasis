#!/usr/bin/env python3
"""
Evaluate DistilBERT sentiment classification model on validation set.

Features:
- Load trained model from checkpoint
- Comprehensive metrics: accuracy, precision, recall, F1, ROC-AUC
- Confusion matrix analysis
- Per-class performance breakdown
- Save results to JSON
- CPU-friendly evaluation

Usage:
    python test.py [--model_path models/best_model] [--batch_size 32]

Example:
    python test.py --model_path models/best_model --batch_size 32
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch
from datasets import load_from_disk, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    classification_report,
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import DATA_DIR, OUTPUTS_DIR, SEED, DEVICE
from utils import set_seed, create_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SentimentEvaluator:
    """
    Evaluator for sentiment classification model.
    
    Computes:
    - Overall accuracy, precision, recall, F1
    - ROC-AUC score
    - Confusion matrix
    - Per-class metrics
    - Classification report
    """
    
    def __init__(
        self,
        model_path: Path,
        seed: int = SEED,
        device: str = DEVICE,
    ):
        """
        Initialize evaluator.
        
        Args:
            model_path: Path to trained model
            seed: Random seed for reproducibility
            device: Evaluation device (cuda or cpu)
        """
        set_seed(seed)
        
        self.model_path = Path(model_path)
        self.seed = seed
        self.device = device
        
        self.model = None
        self.tokenizer = None
        
        logger.info(f"Initialized SentimentEvaluator (device={device})")
    
    def load_model_and_tokenizer(self) -> Tuple:
        """
        Load model and tokenizer from checkpoint.
        
        Returns:
            Tuple of (model, tokenizer)
        
        Raises:
            RuntimeError: If loading fails
        """
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found at {self.model_path}")
            
            logger.info(f"Loading tokenizer from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
            
            logger.info(f"Loading model from {self.model_path}...")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                str(self.model_path),
                num_labels=2,
                torch_dtype=torch.float32,
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info("Model and tokenizer loaded successfully")
            
            return self.model, self.tokenizer
        
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}") from e
    
    def load_eval_dataset(self, eval_path: Path = DATA_DIR / "validation") -> Dataset:
        """
        Load evaluation dataset.
        
        Args:
            eval_path: Path to evaluation dataset
        
        Returns:
            HuggingFace Dataset
        
        Raises:
            RuntimeError: If dataset loading fails
        """
        try:
            eval_path = Path(eval_path)
            
            if not eval_path.exists():
                raise FileNotFoundError(f"Evaluation data not found at {eval_path}")
            
            logger.info(f"Loading evaluation dataset from {eval_path}...")
            eval_dataset = load_from_disk(str(eval_path))
            logger.info(f"  Loaded {len(eval_dataset)} evaluation samples")
            
            return eval_dataset
        
        except Exception as e:
            logger.error(f"Failed to load evaluation dataset: {str(e)}")
            raise RuntimeError(f"Dataset loading failed: {str(e)}") from e
    
    def compute_metrics(self, eval_pred) -> Dict[str, float]:
        """
        Compute evaluation metrics.
        
        Args:
            eval_pred: EvalPrediction with predictions and labels
        
        Returns:
            Dictionary with metrics
        """
        predictions, labels = eval_pred
        
        # Get predicted class (argmax of logits)
        pred_labels = np.argmax(predictions, axis=1)
        
        # Compute metrics
        accuracy = accuracy_score(labels, pred_labels)
        precision = precision_score(labels, pred_labels, zero_division=0)
        recall = recall_score(labels, pred_labels, zero_division=0)
        f1 = f1_score(labels, pred_labels, zero_division=0)
        roc_auc = roc_auc_score(labels, predictions[:, 1])  # Use positive class scores
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "roc_auc": roc_auc,
        }
    
    def evaluate(
        self,
        eval_dataset: Dataset,
        batch_size: int = 32,
    ) -> Dict:
        """
        Run evaluation using HuggingFace Trainer.
        
        Args:
            eval_dataset: Dataset to evaluate on
            batch_size: Batch size for evaluation
        
        Returns:
            Dictionary with evaluation results and metrics
        """
        logger.info(f"\nRunning evaluation with batch size {batch_size}...")
        
        # Create trainer for evaluation only
        training_args = TrainingArguments(
            output_dir=str(Path("/tmp/eval_output")),  # Temporary directory
            per_device_eval_batch_size=batch_size,
            fp16=False,
            bf16=False,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            compute_metrics=self.compute_metrics,
        )
        
        # Evaluate
        try:
            metrics = trainer.evaluate(eval_dataset=eval_dataset)
            logger.info("Evaluation completed successfully")
            return metrics
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            raise RuntimeError(f"Evaluation error: {str(e)}") from e
    
    def get_predictions(
        self,
        eval_dataset: Dataset,
        batch_size: int = 32,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get model predictions on evaluation set.
        
        Args:
            eval_dataset: Dataset to predict on
            batch_size: Batch size for prediction
        
        Returns:
            Tuple of (predictions, predicted_labels, true_labels)
        """
        logger.info("Getting predictions...")
        
        # Create trainer for prediction
        training_args = TrainingArguments(
            output_dir=str(Path("/tmp/pred_output")),
            per_device_eval_batch_size=batch_size,
            fp16=False,
            bf16=False,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
        )
        
        # Get predictions
        predictions, labels, _ = trainer.predict(eval_dataset)
        pred_labels = np.argmax(predictions, axis=1)
        
        return predictions, pred_labels, labels
    
    def compute_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, int]:
        """
        Compute confusion matrix elements.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
        
        Returns:
            Dict with TP, FP, TN, FN
        """
        cm = confusion_matrix(y_true, y_pred)
        
        # For binary classification, confusion matrix is 2x2
        # [[TN, FP],
        #  [FN, TP]]
        tn, fp = cm[0]
        fn, tp = cm[1]
        
        return {
            "TP": int(tp),
            "FP": int(fp),
            "TN": int(tn),
            "FN": int(fn),
        }
    
    def get_roc_metrics(
        self,
        y_true: np.ndarray,
        y_probs: np.ndarray,
    ) -> Dict:
        """
        Compute ROC curve metrics.
        
        Args:
            y_true: True labels
            y_probs: Predicted probabilities (positive class)
        
        Returns:
            Dict with FPR, TPR, AUC
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_probs)
        auc = roc_auc_score(y_true, y_probs)
        
        return {
            "auc": float(auc),
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist(),
        }
    
    def print_results(self, results: Dict) -> None:
        """
        Pretty print evaluation results.
        
        Args:
            results: Results dictionary from evaluate()
        """
        logger.info("\n" + "="*80)
        logger.info("EVALUATION RESULTS")
        logger.info("="*80)
        
        # Main metrics
        logger.info("\nClassification Metrics:")
        logger.info(f"  Accuracy:  {results.get('eval_accuracy', 0):.4f}")
        logger.info(f"  Precision: {results.get('eval_precision', 0):.4f}")
        logger.info(f"  Recall:    {results.get('eval_recall', 0):.4f}")
        logger.info(f"  F1-Score:  {results.get('eval_f1', 0):.4f}")
        logger.info(f"  ROC-AUC:   {results.get('eval_roc_auc', 0):.4f}")
        
        # Confusion matrix
        if "confusion_matrix" in results:
            cm = results["confusion_matrix"]
            logger.info("\nConfusion Matrix:")
            logger.info(f"  True Negatives:  {cm['TN']:6d}  |  False Positives: {cm['FP']:6d}")
            logger.info(f"  False Negatives: {cm['FN']:6d}  |  True Positives:  {cm['TP']:6d}")
            
            # Calculate derived metrics
            specificity = cm['TN'] / (cm['TN'] + cm['FP']) if (cm['TN'] + cm['FP']) > 0 else 0
            sensitivity = cm['TP'] / (cm['TP'] + cm['FN']) if (cm['TP'] + cm['FN']) > 0 else 0
            logger.info(f"\n  Sensitivity (Recall): {sensitivity:.4f}")
            logger.info(f"  Specificity:          {specificity:.4f}")
        
        # Per-class metrics
        if "classification_report" in results:
            logger.info("\nPer-Class Metrics:")
            logger.info(results["classification_report"])
        
        logger.info("="*80 + "\n")
    
    def save_results(
        self,
        results: Dict,
        output_path: Path = OUTPUTS_DIR / "evaluation_results.json",
    ) -> None:
        """
        Save evaluation results to JSON.
        
        Args:
            results: Results dictionary
            output_path: Path to save results
        """
        output_path = Path(output_path)
        create_directory(output_path.parent)
        
        # Convert numpy types to Python types for JSON serialization
        def convert_to_native(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(v) for v in obj]
            return obj
        
        results_json = convert_to_native(results)
        
        logger.info(f"Saving results to {output_path}...")
        with open(output_path, 'w') as f:
            json.dump(results_json, f, indent=2)
        
        logger.info(f"Results saved successfully")


def main():
    """
    Main entry point for evaluation.
    
    Steps:
    1. Parse arguments
    2. Initialize evaluator
    3. Load model and dataset
    4. Run evaluation
    5. Print and save results
    """
    parser = argparse.ArgumentParser(
        description="Evaluate DistilBERT sentiment classification model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py                                        # Default (best_model)
  python test.py --model_path models/best_model         # Specific model
  python test.py --batch_size 16                        # Custom batch size
  python test.py --data_dir data/validation             # Custom data path
        """
    )
    
    parser.add_argument(
        "--model_path",
        type=str,
        default="models/best_model",
        help="Path to trained model (default: models/best_model)"
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default=str(DATA_DIR / "validation"),
        help=f"Path to validation dataset (default: {DATA_DIR / 'validation'})"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=32,
        help="Evaluation batch size (default: 32)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=str(OUTPUTS_DIR),
        help=f"Output directory for results (default: {OUTPUTS_DIR})"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help=f"Random seed (default: {SEED})"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=DEVICE,
        choices=["cpu", "cuda"],
        help=f"Evaluation device (default: {DEVICE})"
    )
    
    args = parser.parse_args()
    
    # Log configuration
    logger.info("\n" + "="*80)
    logger.info("EVALUATION CONFIGURATION")
    logger.info("="*80)
    for key, value in vars(args).items():
        logger.info(f"{key}: {value}")
    logger.info("="*80 + "\n")
    
    # Check if model exists
    model_path = Path(args.model_path)
    if not model_path.exists():
        logger.error(f"Model not found at {model_path}")
        logger.error("Please train a model first: python train.py")
        sys.exit(1)
    
    # Initialize evaluator
    evaluator = SentimentEvaluator(
        model_path=model_path,
        seed=args.seed,
        device=args.device,
    )
    
    try:
        # Load model and dataset
        evaluator.load_model_and_tokenizer()
        eval_dataset = evaluator.load_eval_dataset(eval_path=args.data_dir)
        
        # Run evaluation
        metrics = evaluator.evaluate(
            eval_dataset=eval_dataset,
            batch_size=args.batch_size,
        )
        
        # Get predictions for confusion matrix and ROC
        predictions, pred_labels, true_labels = evaluator.get_predictions(
            eval_dataset=eval_dataset,
            batch_size=args.batch_size,
        )
        
        # Compute additional metrics
        confusion_mat = evaluator.compute_confusion_matrix(true_labels, pred_labels)
        roc_metrics = evaluator.get_roc_metrics(true_labels, predictions[:, 1])
        
        # Classification report
        class_report = classification_report(
            true_labels,
            pred_labels,
            target_names=["Negative", "Positive"],
        )
        
        # Compile all results
        all_results = {
            **metrics,
            "confusion_matrix": confusion_mat,
            "roc_metrics": roc_metrics,
            "classification_report": class_report,
        }
        
        # Print results
        evaluator.print_results(all_results)
        
        # Save results
        output_path = Path(args.output_dir) / "evaluation_results.json"
        evaluator.save_results(all_results, output_path)
        
        logger.info("\n" + "="*80)
        logger.info("✅ EVALUATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Results saved to: {output_path}")
        logger.info("="*80 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
