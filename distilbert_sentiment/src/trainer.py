"""
Training module for sentiment analysis model
PHASE 1: To be implemented
"""
from typing import Tuple, Dict, Any
import torch
from torch.utils.data import DataLoader
from transformers import AdamW, get_linear_schedule_with_warmup
from tqdm import tqdm
from pathlib import Path

from config import (
    LEARNING_RATE,
    NUM_EPOCHS,
    WARMUP_STEPS,
    CHECKPOINT_DIR,
    BEST_MODEL_DIR
)


class SentimentTrainer:
    """
    Trainer class for sentiment analysis model
    
    Usage (Phase 1):
        trainer = SentimentTrainer(model, train_loader, val_loader)
        trainer.train()
        trainer.save_best_model()
    """
    
    def __init__(
        self,
        model,
        train_loader: DataLoader,
        val_loader: DataLoader,
        device: torch.device,
        learning_rate: float = LEARNING_RATE,
        num_epochs: int = NUM_EPOCHS,
        warmup_steps: int = WARMUP_STEPS
    ):
        """
        Initialize trainer
        
        Args:
            model: SentimentModel instance
            train_loader: Training DataLoader
            val_loader: Validation DataLoader
            device: torch device
            learning_rate: Learning rate
            num_epochs: Number of training epochs
            warmup_steps: Warmup steps for scheduler
        """
        self.model = model.get_model()
        self.device = device
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.num_epochs = num_epochs
        
        # Optimizer and scheduler
        self.optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * num_epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        self.best_val_loss = float('inf')
        self.best_epoch = 0
    
    def train_epoch(self) -> Tuple[float, float]:
        """
        Train for one epoch
        
        Returns:
            Tuple of (train_loss, train_accuracy)
            
        Phase 1 Implementation:
            - Forward pass through model
            - Calculate loss
            - Backward pass
            - Update weights
            - Track metrics
        """
        pass
    
    def validate(self) -> Tuple[float, float]:
        """
        Validate model
        
        Returns:
            Tuple of (val_loss, val_accuracy)
            
        Phase 1 Implementation:
            - Disable gradients
            - Forward pass
            - Calculate validation metrics
            - No weight updates
        """
        pass
    
    def train(self) -> Dict[str, Any]:
        """
        Full training loop
        
        Returns:
            Dictionary with training history
            
        Phase 1 Implementation:
            - Loop through epochs
            - Call train_epoch()
            - Call validate()
            - Save checkpoints
            - Track best model
            - Return metrics
        """
        pass
    
    def save_best_model(self) -> None:
        """Save best model checkpoint"""
        pass
    
    def load_checkpoint(self, checkpoint_path: Path) -> None:
        """Load model from checkpoint"""
        pass


# Phase 1 Training Script Template
"""
Example usage in Phase 1:

from src.trainer import SentimentTrainer
from src.model import SentimentModel
from src.utils import set_seed, get_device
from torch.utils.data import DataLoader

# Setup
set_seed(42)
device = get_device()

# Initialize model
model = SentimentModel(device=device)

# Create dataloaders (train_ds, val_ds from data_handler)
train_loader = DataLoader(train_ds, batch_size=16, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=16)

# Train
trainer = SentimentTrainer(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    device=device
)

history = trainer.train()
trainer.save_best_model()

# Results
print(f"Best validation loss: {trainer.best_val_loss:.4f}")
print(f"Best epoch: {trainer.best_epoch}")
"""
