# Phase 1B: Implementation Guide
## Trainer & Evaluator Implementation Template

---

## trainer.py - Implementation Blueprint

```python
# src/trainer.py
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import get_linear_schedule_with_warmup
from tqdm import tqdm
import logging
from pathlib import Path
from typing import Tuple, Dict
import json

from config import MODELS_DIR, CHECKPOINT_DIR, SEED, DEVICE
from utils import set_seed, create_directory

logger = logging.getLogger(__name__)

class SentimentTrainer:
    """
    Trainer for DistilBERT sentiment classification.
    
    Responsibilities:
    - One epoch of training with loss tracking
    - Validation loop with metrics
    - Checkpoint saving and best model tracking
    - Learning rate scheduling
    """
    
    def __init__(
        self,
        model,
        train_loader,
        val_loader,
        device=DEVICE,
        learning_rate=2e-5,
        num_warmup_steps=0,
        num_training_steps=None,
        seed=SEED
    ):
        """
        Initialize trainer.
        
        Args:
            model: DistilBERT model for sequence classification
            train_loader: Training DataLoader
            val_loader: Validation DataLoader
            device: torch.device (cuda or cpu)
            learning_rate: Learning rate for AdamW
            num_warmup_steps: Warmup steps for scheduler
            num_training_steps: Total training steps
            seed: Random seed for reproducibility
        """
        set_seed(seed)
        
        self.model = model
        self.device = device
        self.train_loader = train_loader
        self.val_loader = val_loader
        
        # Initialize optimizer
        # TODO: Create AdamW optimizer with:
        # - model parameters
        # - weight_decay=0.01
        # - learning_rate
        self.optimizer = AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
        
        # Initialize scheduler
        # TODO: Create linear schedule with warmup
        # - optimizer
        # - num_warmup_steps
        # - num_training_steps
        # Hint: get_linear_schedule_with_warmup()
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=num_warmup_steps,
            num_training_steps=num_training_steps
        )
        
        # Tracking
        self.best_val_accuracy = 0.0
        self.best_model_path = None
        
        logger.info("Trainer initialized")
    
    def train_epoch(self, epoch: int) -> Tuple[float, float]:
        """
        Train for one epoch.
        
        Args:
            epoch: Current epoch number
        
        Returns:
            Tuple of (avg_loss, accuracy)
        
        Process:
        1. Set model to training mode
        2. For each batch:
           a. Move batch to device
           b. Forward pass
           c. Compute loss
           d. Backward pass
           e. Optimizer step
        3. Track loss and accuracy
        4. Return epoch metrics
        """
        # TODO: Implement training loop
        # Steps:
        # - self.model.train()
        # - Loop through self.train_loader
        # - For each batch:
        #   - Move to self.device
        #   - Forward pass: logits = self.model(input_ids, attention_mask)
        #   - Loss = CrossEntropyLoss(logits, labels)
        #   - loss.backward()
        #   - self.optimizer.step()
        #   - self.scheduler.step()
        #   - self.optimizer.zero_grad()
        #   - Track: total_loss, correct_predictions
        # - Calculate: avg_loss = total_loss / num_batches
        # - Calculate: accuracy = correct / total
        # - Return (avg_loss, accuracy)
        pass
    
    def validate(self) -> Tuple[float, float, float]:
        """
        Run validation loop.
        
        Args:
            None
        
        Returns:
            Tuple of (val_loss, accuracy, f1_score)
        
        Process:
        1. Set model to eval mode
        2. Disable gradients
        3. For each batch:
           a. Forward pass
           b. Compute loss
           c. Collect predictions
        4. Save best model if accuracy improved
        5. Return validation metrics
        """
        # TODO: Implement validation loop
        # Steps:
        # - self.model.eval()
        # - with torch.no_grad():
        # - Loop through self.val_loader
        # - For each batch:
        #   - Move to self.device
        #   - Forward pass
        #   - Collect predictions and labels
        # - Calculate accuracy, F1-score
        # - If accuracy > best:
        #   - Save model weights
        #   - Update best_val_accuracy
        # - Return (val_loss, accuracy, f1)
        pass
    
    def train(
        self,
        num_epochs: int,
        save_interval: int = 1,
        output_dir: Path = MODELS_DIR
    ) -> Dict:
        """
        Train for multiple epochs.
        
        Args:
            num_epochs: Number of epochs to train
            save_interval: Save checkpoint every N epochs
            output_dir: Directory to save checkpoints
        
        Returns:
            Dict with training history
        """
        # TODO: Implement full training loop
        # Steps:
        # - Create output_dir
        # - For each epoch (1 to num_epochs):
        #   - train_epoch()
        #   - validate()
        #   - Print progress
        #   - Save checkpoint every save_interval
        # - Save training history to JSON
        # - Return history dict
        
        create_directory(output_dir)
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
        
        # TODO: Training loop here
        
        return history
    
    def save_checkpoint(self, epoch: int, output_dir: Path = CHECKPOINT_DIR) -> None:
        """Save model checkpoint."""
        # TODO: Implement checkpoint saving
        # Save:
        # - model.state_dict()
        # - optimizer.state_dict()
        # - scheduler.state_dict()
        # - epoch number
        pass
    
    def load_checkpoint(self, checkpoint_path: Path) -> None:
        """Load model checkpoint."""
        # TODO: Implement checkpoint loading
        pass
```

---

## evaluator.py - Implementation Blueprint

```python
# src/evaluator.py
import torch
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve, auc
)
from typing import Dict, Tuple, List
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SentimentEvaluator:
    """
    Evaluator for sentiment analysis model.
    
    Responsibilities:
    - Compute classification metrics
    - Generate predictions
    - Create confusion matrices
    - Save and display results
    """
    
    def compute_metrics(
        self,
        predictions: np.ndarray,
        labels: np.ndarray
    ) -> Dict[str, float]:
        """
        Compute classification metrics.
        
        Args:
            predictions: Model predictions (0 or 1)
            labels: Ground truth labels (0 or 1)
        
        Returns:
            Dict with: accuracy, precision, recall, f1, roc_auc
        
        Example:
            >>> predictions = np.array([0, 1, 1, 0, 1])
            >>> labels = np.array([0, 1, 0, 0, 1])
            >>> metrics = evaluator.compute_metrics(predictions, labels)
            >>> print(metrics['f1'])  # 0.8333...
        """
        # TODO: Implement metric computation
        # Calculate:
        # - accuracy = accuracy_score(labels, predictions)
        # - precision = precision_score(labels, predictions)
        # - recall = recall_score(labels, predictions)
        # - f1 = f1_score(labels, predictions)
        # - roc_auc = roc_auc_score(labels, predictions)
        # Return as dict
        pass
    
    def evaluate(
        self,
        model,
        eval_loader,
        device
    ) -> Dict:
        """
        Evaluate model on dataset.
        
        Args:
            model: DistilBERT model
            eval_loader: Evaluation DataLoader
            device: torch.device
        
        Returns:
            Dict with predictions, labels, and metrics
        """
        # TODO: Implement evaluation
        # Steps:
        # - model.eval()
        # - with torch.no_grad():
        # - Collect all predictions and labels
        # - Call compute_metrics()
        # - Return results dict
        pass
    
    def get_predictions(
        self,
        model,
        eval_loader,
        device
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get model predictions on dataset.
        
        Returns:
            Tuple of (predictions, labels)
        """
        # TODO: Collect predictions and labels from model
        pass
    
    def get_confusion_matrix(
        self,
        predictions: np.ndarray,
        labels: np.ndarray
    ) -> Dict[str, int]:
        """
        Generate confusion matrix.
        
        Returns:
            Dict with TP, FP, TN, FN
        """
        # TODO: Compute confusion matrix
        # Use sklearn.metrics.confusion_matrix
        # Return as dict: {'TP': ..., 'FP': ..., 'TN': ..., 'FN': ...}
        pass
    
    def print_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Pretty print metrics.
        
        Example output:
            Accuracy:  0.8500
            Precision: 0.8333
            Recall:    0.8571
            F1-Score:  0.8452
            ROC-AUC:   0.9200
        """
        # TODO: Pretty print metrics
        print("\n" + "="*50)
        print("EVALUATION METRICS")
        print("="*50)
        for key, value in metrics.items():
            print(f"{key.capitalize():15s}: {value:.4f}")
        print("="*50 + "\n")
    
    def save_metrics(
        self,
        metrics: Dict,
        output_path: Path
    ) -> None:
        """
        Save metrics to JSON file.
        
        Args:
            metrics: Dict with all metrics
            output_path: Path to save JSON file
        """
        # TODO: Save metrics to JSON
        # Convert np.float32 to Python float for JSON serialization
        pass
```

---

## train.py - Implementation Blueprint

```python
# train.py
import argparse
import logging
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from datasets import load_from_disk

from src.config import (
    MODEL_NAME, MAX_LENGTH, BATCH_SIZE, NUM_EPOCHS,
    DATA_DIR, MODELS_DIR, SEED, DEVICE, BEST_MODEL_DIR
)
from src.model import SentimentModel
from src.trainer import SentimentTrainer
from src.utils import set_seed, create_directory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(args):
    """
    Main training entry point.
    
    Steps:
    1. Load preprocessed data
    2. Create DataLoaders
    3. Load model
    4. Initialize trainer
    5. Run training
    6. Save best model
    """
    
    # TODO: Implement training script
    # 1. Load preprocessed datasets
    #    - load_from_disk('data/train')
    #    - load_from_disk('data/validation')
    # 
    # 2. Create DataLoaders
    #    - train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    #    - val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    # 
    # 3. Load model
    #    - model = SentimentModel.get_model(MODEL_NAME)
    #    - model.to(DEVICE)
    # 
    # 4. Calculate training steps
    #    - num_training_steps = len(train_loader) * NUM_EPOCHS
    #    - num_warmup_steps = num_training_steps // 10
    # 
    # 5. Create trainer
    #    - trainer = SentimentTrainer(model, train_loader, val_loader, ...)
    # 
    # 6. Run training
    #    - history = trainer.train(NUM_EPOCHS)
    # 
    # 7. Save best model
    #    - model.save_model(BEST_MODEL_DIR)
    # 
    # 8. Print results
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train DistilBERT sentiment model")
    parser.add_argument("--epochs", type=int, default=NUM_EPOCHS, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=BATCH_SIZE, help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=2e-5, help="Learning rate")
    args = parser.parse_args()
    
    main(args)
```

---

## test.py - Implementation Blueprint

```python
# test.py
import logging
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from datasets import load_from_disk

from src.config import BEST_MODEL_DIR, DATA_DIR, OUTPUTS_DIR
from src.model import SentimentModel
from src.evaluator import SentimentEvaluator
from src.utils import create_directory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Evaluate trained model on validation set.
    
    Steps:
    1. Load best model
    2. Load validation data
    3. Run evaluation
    4. Print metrics
    5. Save results
    """
    
    # TODO: Implement evaluation script
    # 1. Load best model
    #    - model = SentimentModel.load_model(BEST_MODEL_DIR)
    # 
    # 2. Load validation data
    #    - val_dataset = load_from_disk('data/validation')
    #    - val_loader = DataLoader(val_dataset, batch_size=16)
    # 
    # 3. Create evaluator
    #    - evaluator = SentimentEvaluator()
    # 
    # 4. Run evaluation
    #    - results = evaluator.evaluate(model, val_loader, DEVICE)
    # 
    # 5. Print metrics
    #    - evaluator.print_metrics(results['metrics'])
    # 
    # 6. Save results
    #    - evaluator.save_metrics(results['metrics'], OUTPUTS_DIR / 'metrics.json')
    pass

if __name__ == "__main__":
    main()
```

---

## Key Points for Implementation

### 1. Training Loop Structure
```python
for epoch in range(num_epochs):
    train_loss, train_acc = trainer.train_epoch(epoch)
    val_loss, val_acc, val_f1 = trainer.validate()
    
    print(f"Epoch {epoch}:")
    print(f"  Train - Loss: {train_loss:.4f}, Acc: {train_acc:.4f}")
    print(f"  Val   - Loss: {val_loss:.4f}, Acc: {val_acc:.4f}, F1: {val_f1:.4f}")
```

### 2. Device Management
```python
batch = {
    'input_ids': input_ids.to(self.device),
    'attention_mask': attention_mask.to(self.device),
    'labels': labels.to(self.device)
}
```

### 3. Model Output
```python
outputs = self.model(
    input_ids=batch['input_ids'],
    attention_mask=batch['attention_mask']
)
logits = outputs.logits  # (batch_size, 2)
predictions = torch.argmax(logits, dim=1)  # (batch_size,)
```

### 4. Loss Computation
```python
criterion = torch.nn.CrossEntropyLoss()
loss = criterion(logits, labels)
```

### 5. Metrics Computation
```python
from sklearn.metrics import accuracy_score, f1_score

predictions = torch.argmax(logits, dim=1).cpu().numpy()
labels = batch['labels'].cpu().numpy()

acc = accuracy_score(labels, predictions)
f1 = f1_score(labels, predictions)
```

### 6. Model Saving
```python
torch.save(model.state_dict(), model_path / 'pytorch_model.bin')
```

---

## Expected Training Output

```
Epoch 1/3:
  Train - Loss: 0.6543, Acc: 0.6250
  Val   - Loss: 0.5834, Acc: 0.7100, F1: 0.7050
  Best model saved ✓

Epoch 2/3:
  Train - Loss: 0.3421, Acc: 0.8450
  Val   - Loss: 0.3156, Acc: 0.8600, F1: 0.8580
  Best model saved ✓

Epoch 3/3:
  Train - Loss: 0.1234, Acc: 0.9200
  Val   - Loss: 0.2456, Acc: 0.8750, F1: 0.8740

Training complete!
Best model saved to: models/best_model/

EVALUATION METRICS
==================================================
Accuracy:  0.8750
Precision: 0.8700
Recall:    0.8800
F1-Score:  0.8740
ROC-AUC:   0.9350
==================================================
```

---

## Implementation Checklist

**Trainer Implementation**:
- ✅ __init__(): Initialize optimizer and scheduler
- ⏳ train_epoch(): Implement training loop
- ⏳ validate(): Implement validation loop
- ⏳ train(): Main training loop
- ⏳ save_checkpoint(): Save model state

**Evaluator Implementation**:
- ⏳ compute_metrics(): Calculate all metrics
- ⏳ evaluate(): Run full evaluation
- ⏳ get_predictions(): Extract predictions
- ⏳ get_confusion_matrix(): Generate confusion matrix
- ⏳ print_metrics(): Pretty print results
- ⏳ save_metrics(): Save to JSON

**Entry Points**:
- ⏳ train.py: Complete training script
- ⏳ test.py: Complete evaluation script

---

**Status**: Ready for implementation  
**Files to modify**: src/trainer.py, src/evaluator.py, train.py, test.py  
**Estimated time**: 2-3 hours for complete implementation
