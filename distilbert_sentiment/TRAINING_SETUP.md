## TRAINING SETUP - QUICK REFERENCE

### Virtual Environment

Windows PowerShell:
```
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows CMD:
```
python -m venv venv
venv\Scripts\activate.bat
```

macOS/Linux:
```
python3 -m venv venv
source venv/bin/activate
```

---

### requirements.txt

```
torch>=2.0.0
transformers>=4.30.0,<5.0.0
datasets>=2.10.0
scikit-learn>=1.2.0
numpy>=1.23.0,<2.0.0
pandas>=1.5.0
accelerate>=0.20.0
python-dotenv>=1.0.0
tqdm>=4.65.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

### Installation

1. Activate venv (see above)

2. Upgrade pip:
```
python -m pip install --upgrade pip setuptools wheel
```

3. Install PyTorch (CPU):
```
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

4. Install all dependencies:
```
pip install -r requirements.txt
```

---

### Sanity Checks

Individual checks:
```
python -c "import torch; print(torch.__version__)"
python -c "import transformers; print(transformers.__version__)"
python -c "from datasets import load_dataset; print('OK')"
python -c "from sklearn.metrics import accuracy_score; print('OK')"
python -c "from accelerate import Accelerator; print('OK')"
python -c "import numpy; import pandas; print('OK')"
```

Complete check:
```
python << 'EOF'
import torch, transformers
from datasets import load_dataset
from sklearn.metrics import accuracy_score
from accelerate import Accelerator
import numpy as np, pandas as pd

print("PyTorch:", torch.__version__)
print("Transformers:", transformers.__version__)
print("CUDA:", torch.cuda.is_available())
print("All OK")
EOF
```

---

### Common Fixes

PyTorch DLL error (Windows):
```
pip uninstall torch -y
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Version conflicts:
```
pip install --upgrade torch transformers datasets
```

Module not found:
```
pip install -r requirements.txt
```

Fresh install:
```
deactivate
rmdir /s venv (Windows) or rm -r venv (Unix)
python -m venv venv
(activate venv)
pip install -r requirements.txt
```

---

### Project Structure

```
distilbert_sentiment/
├── src/
│   ├── config.py
│   ├── data_handler.py
│   ├── model.py
│   └── trainer.py
├── data/
├── models/
├── outputs/
├── venv/
└── requirements.txt
```

---

### Final Verification

```
python << 'EOF'
import torch, transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification

print("="*50)
print("TRAINING READY")
print("="*50)
print(f"PyTorch: {torch.__version__}")
print(f"Transformers: {transformers.__version__}")
print(f"Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")

# Test model loading
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
print("DistilBERT: ✓ Loadable")
print("="*50)
EOF
```

Status: Ready to train ✓
