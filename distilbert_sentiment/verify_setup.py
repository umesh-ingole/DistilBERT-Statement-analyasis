#!/usr/bin/env python3
"""
Verification script for training environment
Run: python verify_setup.py
"""

import sys
import subprocess

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}", end="")
    if version.major >= 3 and version.minor >= 8:
        print(" ✓")
        return True
    else:
        print(" ✗ (Need 3.8+)")
        return False

def check_library(name, import_name=None):
    """Check if library is installed and return version"""
    import_name = import_name or name
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'OK')
        print(f"{name}: {version} ✓")
        return True
    except ImportError:
        print(f"{name}: NOT INSTALLED ✗")
        return False

def check_pytorch_cuda():
    """Check if CUDA is available"""
    try:
        import torch
        cuda = torch.cuda.is_available()
        device = "CUDA" if cuda else "CPU"
        print(f"Device: {device}")
        if cuda:
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            mem = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"GPU Memory: {mem:.1f} GB")
        return True
    except Exception as e:
        print(f"Device check failed: {e}")
        return False

def check_model_loading():
    """Test DistilBERT model loading"""
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert-base-uncased", 
            num_labels=2
        )
        print("DistilBERT: Loadable ✓")
        return True
    except Exception as e:
        print(f"DistilBERT: Failed to load ✗")
        print(f"  Error: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("TRAINING ENVIRONMENT VERIFICATION")
    print("="*50 + "\n")
    
    checks = []
    
    # Check Python
    checks.append(("Python Version", check_python()))
    
    # Check libraries
    print("\nCore Libraries:")
    checks.append(("PyTorch", check_library("torch")))
    checks.append(("Transformers", check_library("transformers")))
    checks.append(("Datasets", check_library("datasets")))
    checks.append(("Scikit-learn", check_library("sklearn")))
    checks.append(("Accelerate", check_library("accelerate")))
    
    print("\nData Processing:")
    checks.append(("NumPy", check_library("numpy")))
    checks.append(("Pandas", check_library("pandas")))
    
    print("\nOptional Libraries:")
    check_library("matplotlib")
    check_library("seaborn")
    check_library("jupyter")
    
    # Check device
    print("\nDevice:")
    check_pytorch_cuda()
    
    # Test model loading
    print("\nModel Loading:")
    model_ok = check_model_loading()
    
    # Summary
    print("\n" + "="*50)
    total = len(checks)
    passed = sum(1 for _, result in checks if result)
    
    if passed == total:
        print(f"✓ ALL CHECKS PASSED ({passed}/{total})")
        print("="*50)
        print("\n✓ READY FOR TRAINING\n")
        return 0
    else:
        print(f"✗ SOME CHECKS FAILED ({passed}/{total})")
        print("="*50)
        print("\nFix missing libraries:")
        print("  pip install -r requirements.txt\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
