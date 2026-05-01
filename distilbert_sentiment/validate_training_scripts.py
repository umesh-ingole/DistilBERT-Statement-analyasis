#!/usr/bin/env python3
"""
Validation test for train.py and test.py.
Tests imports, class definitions, and method signatures without requiring torch/transformers.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

def check_python_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check if Python file has valid syntax."""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, "Syntax valid"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def extract_classes(file_path: Path) -> List[str]:
    """Extract class definitions from Python file."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
    
    return classes

def extract_functions(file_path: Path) -> List[str]:
    """Extract function definitions from Python file."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                functions.append(node.name)
    
    return functions

def extract_main_functions(file_path: Path) -> List[str]:
    """Extract main function."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'main':
            return [node.name]
    
    return []

def validate_file(file_path: Path) -> bool:
    """Validate a Python training file."""
    print(f"\n{'='*80}")
    print(f"VALIDATING: {file_path.name}")
    print(f"{'='*80}")
    
    # 1. Check existence
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    print(f"✅ File exists")
    
    # 2. Check syntax
    syntax_ok, syntax_msg = check_python_syntax(file_path)
    if syntax_ok:
        print(f"✅ {syntax_msg}")
    else:
        print(f"❌ {syntax_msg}")
        return False
    
    # 3. Check file size
    file_size = file_path.stat().st_size
    print(f"✅ File size: {file_size:,} bytes")
    
    # 4. Extract classes
    classes = extract_classes(file_path)
    if classes:
        print(f"✅ Classes defined: {', '.join(classes)}")
    else:
        print(f"⚠️  No classes defined")
    
    # 5. Check for main function
    main_funcs = extract_main_functions(file_path)
    if main_funcs:
        print(f"✅ Main function found")
    else:
        print(f"⚠️  No main() function found")
    
    # 6. Check imports
    with open(file_path, 'r') as f:
        content = f.read()
    
    required_imports = {
        'train.py': ['argparse', 'logging', 'pathlib', 'torch', 'datasets', 'transformers', 'sklearn'],
        'test.py': ['argparse', 'json', 'logging', 'pathlib', 'torch', 'datasets', 'transformers', 'sklearn'],
    }
    
    if file_path.name in required_imports:
        imports = required_imports[file_path.name]
        missing = []
        for imp in imports:
            if f"import {imp}" not in content and f"from {imp}" not in content:
                missing.append(imp)
        
        if missing:
            print(f"⚠️  Missing imports: {', '.join(missing)}")
        else:
            print(f"✅ All required imports present")
    
    return True

def validate_code_structure(train_path: Path, test_path: Path) -> bool:
    """Validate code structure of both files."""
    print(f"\n{'='*80}")
    print("STRUCTURE VALIDATION")
    print(f"{'='*80}")
    
    all_ok = True
    
    # Check train.py
    print("\ntrain.py Structure:")
    with open(train_path, 'r') as f:
        train_content = f.read()
    
    required_patterns = {
        'SentimentTrainer class': 'class SentimentTrainer',
        'load_model_and_tokenizer': 'def load_model_and_tokenizer',
        'load_datasets': 'def load_datasets',
        'compute_metrics': 'def compute_metrics',
        'train method': 'def train',
        'main function': 'def main():',
    }
    
    for pattern_name, pattern in required_patterns.items():
        if pattern in train_content:
            print(f"  ✅ {pattern_name}")
        else:
            print(f"  ❌ Missing: {pattern_name}")
            all_ok = False
    
    # Check test.py
    print("\ntest.py Structure:")
    with open(test_path, 'r') as f:
        test_content = f.read()
    
    test_patterns = {
        'SentimentEvaluator class': 'class SentimentEvaluator',
        'load_model_and_tokenizer': 'def load_model_and_tokenizer',
        'load_eval_dataset': 'def load_eval_dataset',
        'evaluate method': 'def evaluate',
        'get_predictions method': 'def get_predictions',
        'compute_confusion_matrix': 'def compute_confusion_matrix',
        'save_results method': 'def save_results',
        'main function': 'def main():',
    }
    
    for pattern_name, pattern in test_patterns.items():
        if pattern in test_content:
            print(f"  ✅ {pattern_name}")
        else:
            print(f"  ❌ Missing: {pattern_name}")
            all_ok = False
    
    return all_ok

def main():
    """Run validation tests."""
    script_dir = Path(__file__).parent
    train_path = script_dir / "train.py"
    test_path = script_dir / "test.py"
    
    print("\n" + "="*80)
    print("TRAINING SCRIPTS VALIDATION")
    print("="*80)
    
    # Validate individual files
    train_ok = validate_file(train_path)
    test_ok = validate_file(test_path)
    
    # Validate structure
    structure_ok = validate_code_structure(train_path, test_path)
    
    # Summary
    print(f"\n{'='*80}")
    print("VALIDATION SUMMARY")
    print(f"{'='*80}")
    
    if train_ok:
        print("✅ train.py: VALID")
    else:
        print("❌ train.py: INVALID")
    
    if test_ok:
        print("✅ test.py: VALID")
    else:
        print("❌ test.py: INVALID")
    
    if structure_ok:
        print("✅ Structure: VALID")
    else:
        print("❌ Structure: INVALID")
    
    print(f"{'='*80}\n")
    
    if train_ok and test_ok and structure_ok:
        print("🎉 ALL VALIDATIONS PASSED")
        print("\nReady to use:")
        print("  python train.py          # Train model")
        print("  python test.py           # Evaluate model")
        print("  python train.py --help   # Show training options")
        print("  python test.py --help    # Show evaluation options")
        return 0
    else:
        print("⚠️  SOME VALIDATIONS FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
