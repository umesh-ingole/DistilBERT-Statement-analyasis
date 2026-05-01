#!/usr/bin/env python
"""
Test script to verify environment setup
"""
import sys

print('\n' + '='*80)
print('ENVIRONMENT VERIFICATION')
print('='*80)

print('\n[1/3] Testing torch...')
try:
    import torch
    print(f'  ✅ torch {torch.__version__}')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'  Device: {device}')
    print(f'  CUDA available: {torch.cuda.is_available()}')
except Exception as e:
    print(f'  ❌ ERROR: {e}')
    sys.exit(1)

print('\n[2/3] Testing transformers...')
try:
    import transformers
    print(f'  ✅ transformers {transformers.__version__}')
except Exception as e:
    print(f'  ❌ ERROR: {e} (need to install)')

print('\n[3/3] Testing datasets...')
try:
    import datasets
    print(f'  ✅ datasets {datasets.__version__}')
except Exception as e:
    print(f'  ❌ ERROR: {e} (need to install)')

print('\n' + '='*80)
print('Status: Core packages need installation via requirements.txt')
print('='*80 + '\n')
