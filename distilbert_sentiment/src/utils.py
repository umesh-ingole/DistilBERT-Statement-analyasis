"""
Utility functions for sentiment analysis project
"""
import os
import random
import numpy as np
import torch
from typing import Dict, Any
from pathlib import Path
from src.config import SEED


def set_seed(seed: int = SEED) -> None:
    """
    Set random seed for reproducibility across all libraries
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_device() -> torch.device:
    """
    Get the appropriate device (GPU or CPU)
    
    Returns:
        torch.device object
    """
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def print_gpu_info() -> None:
    """
    Print GPU information if available
    """
    if torch.cuda.is_available():
        print(f"GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("GPU not available. Using CPU.")


def create_directory(path: Path) -> None:
    """
    Create directory if it doesn't exist
    
    Args:
        path: Path object for directory
    """
    path.mkdir(parents=True, exist_ok=True)


def save_dict_to_json(data: Dict[str, Any], file_path: Path) -> None:
    """
    Save dictionary to JSON file
    
    Args:
        data: Dictionary to save
        file_path: Path to save JSON file
    """
    import json
    create_directory(file_path.parent)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def load_dict_from_json(file_path: Path) -> Dict[str, Any]:
    """
    Load dictionary from JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded dictionary
    """
    import json
    with open(file_path, 'r') as f:
        return json.load(f)
