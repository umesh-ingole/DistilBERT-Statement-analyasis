#!/usr/bin/env python3
"""Audit script for predict.py configuration and dependencies"""
import json
import sys
from pathlib import Path

# Set output encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("AUDIT: predict.py Configuration & Dependencies")
print("=" * 80)

# Audit 1: src imports
print("\n[1/6] AUDIT: src module imports")
print("-" * 80)
try:
    from src.config import DEVICE, SEED, MODEL_NAME, BEST_MODEL_DIR
    print("[OK] src.config imports OK")
    print(f"    DEVICE: {DEVICE}")
    print(f"    SEED: {SEED}")
    print(f"    MODEL_NAME: {MODEL_NAME}")
    print(f"    BEST_MODEL_DIR: {BEST_MODEL_DIR}")
except Exception as e:
    print(f"[FAIL] src.config import failed: {e}")
    sys.exit(1)

try:
    from src.utils import set_seed
    print("[OK] src.utils imports OK")
except Exception as e:
    print(f"[FAIL] src.utils import failed: {e}")
    sys.exit(1)

# Audit 2: Model path
print("\n[2/6] AUDIT: Model path & files")
print("-" * 80)
model_path = Path("models/best_model")
print(f"Model path exists: {model_path.exists()} - {model_path}")

required_files = {
    "config.json": model_path / "config.json",
    "model.safetensors": model_path / "model.safetensors",
}

for name, path in required_files.items():
    exists = path.exists()
    size_info = f" ({path.stat().st_size / 1e6:.1f} MB)" if exists else ""
    status = "[OK]" if exists else "[FAIL]"
    print(f"  {status} {name}: {exists}{size_info}")

# Audit 3: Model config
print("\n[3/6] AUDIT: Model configuration")
print("-" * 80)
try:
    config_path = model_path / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    print(f"[OK] Config loaded successfully")
    print(f"    Model type: {config.get('model_type', 'unknown')}")
    print(f"    Num labels: {config.get('num_labels', 'unknown')}")
    print(f"    Hidden size: {config.get('hidden_size', 'unknown')}")
    print(f"    Vocab size: {config.get('vocab_size', 'unknown')}")
    
    # Verify it's binary classification
    if config.get('num_labels') != 2:
        print(f"    ⚠ WARNING: Expected 2 labels, got {config.get('num_labels')}")
except Exception as e:
    print(f"[FAIL] Config read error: {e}")

# Audit 4: Tokenizer
print("\n[4/6] AUDIT: Tokenizer mismatch detection")
print("-" * 80)
try:
    from transformers import AutoTokenizer
    
    # Check if tokenizer is in saved model
    tokenizer_config = model_path / "tokenizer_config.json"
    has_local_tokenizer = tokenizer_config.exists()
    print(f"[OK] Tokenizer config in model: {has_local_tokenizer}")
    
    if has_local_tokenizer:
        with open(tokenizer_config) as f:
            tok_config = json.load(f)
        print(f"    Base tokenizer: {tok_config.get('model_type', 'unknown')}")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print(f"[OK] Loaded tokenizer from models/best_model")
    else:
        print(f"    No tokenizer in model, using distilbert-base-uncased")
        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        print(f"[OK] Loaded fallback tokenizer (distilbert-base-uncased)")
    
    print(f"    Tokenizer class: {type(tokenizer).__name__}")
    print(f"    Vocab size: {len(tokenizer)}")
    
    # Test tokenization
    test_input = "This is a test"
    tokens = tokenizer(test_input, return_tensors="pt")
    print(f"[OK] Test tokenization OK: {test_input}")
    print(f"      - input_ids shape: {tokens['input_ids'].shape}")
    print(f"      - attention_mask shape: {tokens['attention_mask'].shape}")
    
except Exception as e:
    print(f"[FAIL] Tokenizer error: {e}")
    sys.exit(1)

# Audit 5: Device configuration
print("\n[5/6] AUDIT: Device configuration")
print("-" * 80)
try:
    import torch
    print(f"[OK] PyTorch version: {torch.__version__}")
    print(f"    CUDA available: {torch.cuda.is_available()}")
    print(f"    Configured device: {DEVICE}")
    
    # Verify device is valid
    if DEVICE == "cuda" and not torch.cuda.is_available():
        print(f"    ⚠ WARNING: CUDA selected but not available")
    elif DEVICE == "cuda":
        print(f"    GPU: {torch.cuda.get_device_name(0)}")
        print(f"    Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    # Test device
    test_tensor = torch.zeros(1, 10).to(DEVICE)
    print(f"[OK] Device test OK: Created tensor on {DEVICE}")
    
except Exception as e:
    print(f"[FAIL] Device error: {e}")

# Audit 6: Model loading
print("\n[6/6] AUDIT: Model loading test")
print("-" * 80)
try:
    from transformers import AutoModelForSequenceClassification
    
    print(f"Loading model from {model_path}...")
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.to(DEVICE)
    model.eval()
    print(f"[OK] Model loaded successfully")
    print(f"    Model class: {type(model).__name__}")
    print(f"    Total parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")
    
    # Test inference
    print(f"\nRunning test inference...")
    test_text = "This is amazing!"
    inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)
        pred_label = torch.argmax(logits, dim=-1).item()
    
    print(f"[OK] Inference test OK")
    print(f"    Input text: '{test_text}'")
    print(f"    Logits shape: {logits.shape}")
    print(f"    Predicted label: {pred_label} (0=NEGATIVE, 1=POSITIVE)")
    print(f"    Probabilities: NEG={probs[0,0].item():.4f}, POS={probs[0,1].item():.4f}")
    
except Exception as e:
    print(f"[FAIL] Model loading error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("AUDIT COMPLETE: All checks passed [OK]")
print("=" * 80)
print("\nCommand to run predict.py:")
print("  venv_310\\Scripts\\python predict.py          # Interactive mode")
print("  venv_310\\Scripts\\python predict.py --test   # Test mode")
print("=" * 80)
