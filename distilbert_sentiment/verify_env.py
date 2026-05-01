#!/usr/bin/env python3
"""
Verify environment is ready for training
"""
import sys

print('\n' + '='*80)
print('STEP 6: VERIFY CORE IMPORTS')
print('='*80)

success = True

print('\n[1/3] torch...')
try:
    import torch
    print(f'  ✅ torch {torch.__version__}')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'  Device: {device}')
except Exception as e:
    print(f'  ❌ ERROR: {e}')
    success = False

print('\n[2/3] transformers...')
try:
    import transformers
    print(f'  ✅ transformers {transformers.__version__}')
except Exception as e:
    print(f'  ❌ ERROR: {e}')
    success = False

print('\n[3/3] datasets...')
try:
    import datasets
    print(f'  ✅ datasets {datasets.__version__}')
except Exception as e:
    print(f'  ❌ ERROR: {e}')
    success = False

print('\n' + '='*80)
if success:
    print('✅ Status: ENVIRONMENT READY FOR TRAINING')
    print('='*80 + '\n')
    sys.exit(0)
else:
    print('❌ Status: ENVIRONMENT HAS ERRORS')
    print('='*80 + '\n')
    sys.exit(1)
