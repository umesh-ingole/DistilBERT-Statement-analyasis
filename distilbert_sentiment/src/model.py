"""
Model definition and management for sentiment analysis
"""
import torch
import torch.nn as nn
from transformers import AutoModelForSequenceClassification, PreTrainedModel
from typing import Dict, Tuple
from config import MODEL_NAME, NUM_CLASSES


class SentimentModel:
    """Wrapper for DistilBERT sentiment model"""
    
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        num_labels: int = NUM_CLASSES,
        device: torch.device = None
    ):
        """
        Initialize sentiment model
        
        Args:
            model_name: HuggingFace model name
            num_labels: Number of classification labels
            device: torch device (cuda or cpu)
        """
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.device = device
        self.model_name = model_name
        self.num_labels = num_labels
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        ).to(device)
    
    def get_model(self) -> PreTrainedModel:
        """Get the underlying transformer model"""
        return self.model
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass through the model
        
        Args:
            input_ids: Token IDs
            attention_mask: Attention mask
            labels: Optional labels for training
            
        Returns:
            Model output dictionary
        """
        output = self.model(
            input_ids=input_ids.to(self.device),
            attention_mask=attention_mask.to(self.device),
            labels=labels.to(self.device) if labels is not None else None
        )
        return output
    
    def save_model(self, path: str) -> None:
        """
        Save model and tokenizer
        
        Args:
            path: Directory path to save model
        """
        self.model.save_pretrained(path)
    
    def load_model(self, path: str) -> None:
        """
        Load model from checkpoint
        
        Args:
            path: Directory path of saved model
        """
        self.model = AutoModelForSequenceClassification.from_pretrained(path).to(self.device)
    
    def to_device(self, device: torch.device) -> None:
        """
        Move model to device
        
        Args:
            device: torch device
        """
        self.device = device
        self.model.to(device)
