#!/usr/bin/env python3
"""
Comprehensive Evaluation Script for DistilBERT Sentiment Classification

Evaluates trained model on test dataset and displays:
- Test accuracy, precision, recall, F1-score
- Confusion matrix visualization
- Sample predictions with confidence scores
- Per-class metrics
- ROC-AUC score

Usage:
    python evaluate.py
    python evaluate.py --model_path models/best_model --batch_size 64
    python evaluate.py --help
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import torch
from datasets import load_from_disk
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

# Local imports
from src.config import DEVICE, SEED, MODEL_NAME
from src.utils import set_seed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SentimentEvaluator:
    """Comprehensive evaluator for sentiment classification model."""

    def __init__(self, model_path: str = "models/best_model", device: str = DEVICE, seed: int = SEED):
        """
        Initialize evaluator.

        Args:
            model_path: Path to trained model
            device: Device to use (cpu, cuda)
            seed: Random seed for reproducibility
        """
        set_seed(seed)
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None
        self.trainer = None
        logger.info(f"Initializing evaluator with device: {self.device}")

    def load_model_and_tokenizer(self) -> bool:
        """
        Load trained model and tokenizer from checkpoint.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Loading model from: {self.model_path}")
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")

            logger.info("Loading tokenizer")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            logger.info("Tokenizer loaded successfully")
            return True

        except FileNotFoundError:
            logger.error(f"Model not found at: {self.model_path}")
            logger.error("Make sure training completed successfully: python train.py")
            return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def load_eval_dataset(self, data_dir: str = "data") -> bool:
        """
        Load evaluation dataset.

        Args:
            data_dir: Directory containing dataset

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            test_path = Path(data_dir) / "test"
            if not test_path.exists():
                logger.error(f"Test dataset not found at: {test_path}")
                logger.error("Make sure preprocessing completed: python preprocess.py")
                return False

            logger.info(f"Loading test dataset from: {test_path}")
            self.test_dataset = load_from_disk(str(test_path))
            logger.info(f"Test dataset loaded: {len(self.test_dataset)} samples")
            return True

        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return False

    def get_predictions(self, batch_size: int = 32) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get model predictions on test dataset.

        Args:
            batch_size: Batch size for inference

        Returns:
            Tuple of (predictions, logits, labels)
        """
        logger.info(f"Running inference on {len(self.test_dataset)} samples...")

        # Create trainer for inference
        training_args = TrainingArguments(
            output_dir="./temp_eval",
            per_device_eval_batch_size=batch_size,
            dataloader_pin_memory=False,
        )

        trainer = Trainer(model=self.model, args=training_args)

        # Get raw predictions
        predictions = trainer.predict(self.test_dataset)
        logits = predictions.predictions
        labels = predictions.label_ids

        # Convert logits to class predictions
        preds = np.argmax(logits, axis=1)

        logger.info("Inference completed")
        return preds, logits, labels

    def compute_metrics(self, predictions: np.ndarray, logits: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """
        Compute all metrics.

        Args:
            predictions: Predicted class labels
            logits: Raw model outputs
            labels: True labels

        Returns:
            Dictionary of metrics
        """
        logger.info("Computing metrics...")

        metrics = {
            "accuracy": float(accuracy_score(labels, predictions)),
            "precision": float(precision_score(labels, predictions)),
            "recall": float(recall_score(labels, predictions)),
            "f1": float(f1_score(labels, predictions)),
            "roc_auc": float(roc_auc_score(labels, logits[:, 1])),
        }

        return metrics

    def get_confusion_matrix(self, predictions: np.ndarray, labels: np.ndarray) -> Dict[str, int]:
        """
        Compute confusion matrix.

        Args:
            predictions: Predicted class labels
            labels: True labels

        Returns:
            Dictionary with TP, FP, TN, FN
        """
        tn, fp, fn, tp = confusion_matrix(labels, predictions).ravel()

        return {
            "TP": int(tp),  # True Positives (predicted positive, actually positive)
            "FP": int(fp),  # False Positives (predicted positive, actually negative)
            "TN": int(tn),  # True Negatives (predicted negative, actually negative)
            "FN": int(fn),  # False Negatives (predicted negative, actually positive)
        }

    def get_sample_predictions(self, num_samples: int = 10) -> List[Dict[str, Any]]:
        """
        Get sample predictions with confidence scores.

        Args:
            num_samples: Number of samples to show

        Returns:
            List of sample predictions
        """
        logger.info(f"Extracting {num_samples} sample predictions...")

        # Get indices for diverse samples
        indices = []
        # Get some correct predictions
        correct_mask = self.predictions == self.labels
        correct_indices = np.where(correct_mask)[0]
        indices.extend(correct_indices[: num_samples // 2].tolist())

        # Get some incorrect predictions
        incorrect_mask = self.predictions != self.labels
        incorrect_indices = np.where(incorrect_mask)[0]
        indices.extend(incorrect_indices[: num_samples // 2].tolist())

        indices = indices[:num_samples]

        samples = []
        label_names = {0: "NEGATIVE", 1: "POSITIVE"}

        for idx in indices:
            sample = self.test_dataset[int(idx)]
            pred = self.predictions[idx]
            actual = self.labels[idx]
            confidence = self.logits[idx, int(pred)]

            samples.append({
                "index": int(idx),
                "text": sample.get("text", "")[:100] + "..." if len(sample.get("text", "")) > 100 else sample.get("text", ""),
                "true_label": label_names[int(actual)],
                "predicted_label": label_names[int(pred)],
                "confidence": float(confidence),
                "correct": int(pred) == int(actual),
            })

        return samples

    def print_metrics(self, metrics: Dict[str, float]) -> None:
        """Pretty-print metrics."""
        print("\n" + "=" * 80)
        print("EVALUATION METRICS")
        print("=" * 80)
        print(f"Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        print(f"Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
        print(f"Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
        print(f"F1-Score:  {metrics['f1']:.4f} ({metrics['f1']*100:.2f}%)")
        print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
        print("=" * 80 + "\n")

    def print_confusion_matrix(self, cm: Dict[str, int]) -> None:
        """Pretty-print confusion matrix."""
        print("\n" + "=" * 80)
        print("CONFUSION MATRIX")
        print("=" * 80)
        print(f"\nTrue Positives (TP):   {cm['TP']:,}  (predicted POSITIVE, actually POSITIVE)")
        print(f"False Positives (FP):  {cm['FP']:,}  (predicted POSITIVE, actually NEGATIVE)")
        print(f"True Negatives (TN):   {cm['TN']:,}  (predicted NEGATIVE, actually NEGATIVE)")
        print(f"False Negatives (FN):  {cm['FN']:,}  (predicted NEGATIVE, actually POSITIVE)")

        # Calculate derived metrics
        total = cm["TP"] + cm["FP"] + cm["TN"] + cm["FN"]
        sensitivity = cm["TP"] / (cm["TP"] + cm["FN"]) if (cm["TP"] + cm["FN"]) > 0 else 0
        specificity = cm["TN"] / (cm["TN"] + cm["FP"]) if (cm["TN"] + cm["FP"]) > 0 else 0

        print(f"\nTotal samples: {total:,}")
        print(f"Sensitivity (True Positive Rate): {sensitivity:.4f}")
        print(f"Specificity (True Negative Rate): {specificity:.4f}")
        print("=" * 80 + "\n")

    def print_sample_predictions(self, samples: List[Dict[str, Any]]) -> None:
        """Pretty-print sample predictions."""
        print("\n" + "=" * 80)
        print("SAMPLE PREDICTIONS")
        print("=" * 80)

        correct_count = sum(1 for s in samples if s["correct"])
        print(f"\nShowing {len(samples)} samples ({correct_count} correct, {len(samples) - correct_count} incorrect)\n")

        for i, sample in enumerate(samples, 1):
            status = "✓ CORRECT" if sample["correct"] else "✗ WRONG"
            print(f"{i}. [{status}]")
            print(f"   Text: {sample['text']}")
            print(f"   True Label:      {sample['true_label']}")
            print(f"   Predicted Label: {sample['predicted_label']} (confidence: {sample['confidence']:.4f})")
            print()

        print("=" * 80 + "\n")

    def print_classification_report(self, predictions: np.ndarray, labels: np.ndarray) -> None:
        """Print detailed classification report."""
        print("\n" + "=" * 80)
        print("CLASSIFICATION REPORT")
        print("=" * 80 + "\n")
        print(classification_report(labels, predictions, target_names=["NEGATIVE", "POSITIVE"]))
        print("=" * 80 + "\n")

    def evaluate(self, batch_size: int = 32, output_dir: str = "outputs", data_dir: str = "data") -> bool:
        """
        Run complete evaluation.

        Args:
            batch_size: Batch size for inference
            output_dir: Directory to save results
            data_dir: Directory containing dataset

        Returns:
            bool: True if successful, False otherwise
        """
        # Load model and data
        if not self.load_model_and_tokenizer():
            return False

        if not self.load_eval_dataset(data_dir=data_dir):
            return False

        # Get predictions
        self.predictions, self.logits, self.labels = self.get_predictions(batch_size)

        # Compute metrics
        metrics = self.compute_metrics(self.predictions, self.logits, self.labels)
        cm = self.get_confusion_matrix(self.predictions, self.labels)
        samples = self.get_sample_predictions(num_samples=10)

        # Print results to terminal
        self.print_metrics(metrics)
        self.print_confusion_matrix(cm)
        self.print_sample_predictions(samples)
        self.print_classification_report(self.predictions, self.labels)

        # Save results to JSON
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        results = {
            "metrics": metrics,
            "confusion_matrix": cm,
            "samples": samples,
            "num_samples": len(self.test_dataset),
        }

        results_file = output_path / "evaluation_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to: {results_file}")

        print("\n" + "=" * 80)
        print("EVALUATION COMPLETE")
        print("=" * 80)
        print(f"Results saved to: {results_file}")
        print("=" * 80 + "\n")

        return True


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(
        description="Evaluate DistilBERT sentiment classification model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python evaluate.py
  python evaluate.py --model_path models/best_model
  python evaluate.py --batch_size 64 --output_dir results/
        """,
    )

    parser.add_argument(
        "--model_path",
        type=str,
        default="models/best_model",
        help="Path to trained model checkpoint (default: models/best_model)",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=32,
        help="Batch size for inference (default: 32)",
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="data",
        help="Directory containing dataset (default: data)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="outputs",
        help="Directory to save results (default: outputs)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help=f"Random seed for reproducibility (default: {SEED})",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=DEVICE,
        choices=["cpu", "cuda"],
        help=f"Device to use (default: {DEVICE})",
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("DISTILBERT SENTIMENT CLASSIFICATION - EVALUATION")
    logger.info("=" * 80)
    logger.info(f"Model path: {args.model_path}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Device: {args.device}")
    logger.info("=" * 80)

    # Run evaluation
    evaluator = SentimentEvaluator(
        model_path=args.model_path,
        device=args.device,
        seed=args.seed,
    )

    success = evaluator.evaluate(
        batch_size=args.batch_size,
        output_dir=args.output_dir,
        data_dir=args.data_dir,
    )

    if success:
        logger.info("Evaluation completed successfully!")
        return 0
    else:
        logger.error("Evaluation failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
