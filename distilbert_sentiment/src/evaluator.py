"""
Evaluation module for sentiment analysis model
PHASE 1: To be implemented
"""
from typing import Dict, Tuple, List
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    roc_curve
)
import numpy as np


class SentimentEvaluator:
    """
    Evaluator class for sentiment analysis model
    
    Computes metrics:
    - Accuracy
    - Precision
    - Recall
    - F1 Score
    - Confusion Matrix
    - ROC-AUC
    
    Usage (Phase 1):
        evaluator = SentimentEvaluator(model, device)
        metrics = evaluator.evaluate(test_loader)
        evaluator.print_metrics(metrics)
    """
    
    def __init__(self, model, device: torch.device):
        """
        Initialize evaluator
        
        Args:
            model: Trained SentimentModel
            device: torch device
        """
        self.model = model.get_model() if hasattr(model, 'get_model') else model
        self.device = device
    
    def evaluate(self, test_loader: DataLoader) -> Dict[str, float]:
        """
        Evaluate model on test set
        
        Returns:
            Dictionary with metrics
            
        Phase 1 Implementation:
            - Get predictions from model
            - Compare with ground truth
            - Calculate all metrics
        """
        pass
    
    def get_predictions(self, test_loader: DataLoader) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get model predictions and ground truth labels
        
        Returns:
            Tuple of (predictions, true_labels)
            
        Phase 1 Implementation:
            - Disable gradients
            - Forward pass
            - Get argmax predictions
            - Collect all batches
        """
        pass
    
    def compute_metrics(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        probabilities: np.ndarray = None
    ) -> Dict[str, float]:
        """
        Compute classification metrics
        
        Args:
            predictions: Predicted labels
            true_labels: Ground truth labels
            probabilities: Predicted probabilities for ROC-AUC
            
        Returns:
            Dictionary with all metrics
            
        Phase 1 Implementation:
            - Accuracy
            - Precision
            - Recall
            - F1 Score
            - ROC-AUC (if probabilities provided)
        """
        metrics = {}
        
        # Basic metrics (use sklearn)
        metrics['accuracy'] = accuracy_score(true_labels, predictions)
        metrics['precision'] = precision_score(true_labels, predictions, average='weighted')
        metrics['recall'] = recall_score(true_labels, predictions, average='weighted')
        metrics['f1'] = f1_score(true_labels, predictions, average='weighted')
        
        # ROC-AUC (if probabilities available)
        if probabilities is not None:
            try:
                metrics['roc_auc'] = roc_auc_score(true_labels, probabilities)
            except:
                metrics['roc_auc'] = None
        
        # Confusion matrix
        metrics['confusion_matrix'] = confusion_matrix(true_labels, predictions)
        
        return metrics
    
    def get_confusion_matrix(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray
    ) -> np.ndarray:
        """Get confusion matrix"""
        return confusion_matrix(true_labels, predictions)
    
    def print_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Pretty print metrics
        
        Phase 1 Implementation:
            - Format and display all metrics
            - Show confusion matrix
            - Include classification report
        """
        print("\n" + "="*50)
        print("EVALUATION METRICS")
        print("="*50)
        
        print(f"Accuracy:  {metrics.get('accuracy', 'N/A'):.4f}")
        print(f"Precision: {metrics.get('precision', 'N/A'):.4f}")
        print(f"Recall:    {metrics.get('recall', 'N/A'):.4f}")
        print(f"F1 Score:  {metrics.get('f1', 'N/A'):.4f}")
        if metrics.get('roc_auc'):
            print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
        
        if 'confusion_matrix' in metrics:
            print("\nConfusion Matrix:")
            print(metrics['confusion_matrix'])
        
        print("="*50 + "\n")
    
    def get_classification_report(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        target_names: List[str] = None
    ) -> str:
        """
        Get detailed classification report
        
        Args:
            predictions: Predicted labels
            true_labels: Ground truth labels
            target_names: Label names (e.g., ['negative', 'positive'])
            
        Returns:
            Classification report string
        """
        if target_names is None:
            target_names = ['Negative', 'Positive']
        
        return classification_report(
            true_labels,
            predictions,
            target_names=target_names
        )
    
    def save_metrics(self, metrics: Dict[str, float], file_path: str) -> None:
        """
        Save metrics to JSON file
        
        Phase 1 Implementation:
            - Convert numpy arrays to lists
            - Save as JSON
        """
        pass


# Phase 1 Evaluation Script Template
"""
Example usage in Phase 1:

from src.evaluator import SentimentEvaluator
from src.model import SentimentModel
from torch.utils.data import DataLoader

# Load trained model
model = SentimentModel()
model.load_model("models/best_model")

# Create test loader
test_loader = DataLoader(test_ds, batch_size=16)

# Evaluate
evaluator = SentimentEvaluator(model, device)
metrics = evaluator.evaluate(test_loader)
evaluator.print_metrics(metrics)

# Classification report
report = evaluator.get_classification_report(
    predictions,
    true_labels,
    target_names=['Negative', 'Positive']
)
print(report)

# Save metrics
evaluator.save_metrics(metrics, "outputs/metrics.json")
"""
