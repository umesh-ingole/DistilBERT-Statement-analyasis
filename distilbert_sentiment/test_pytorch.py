#!/usr/bin/env python
"""Test PyTorch in Python 3.13 environment"""
import torch
print(f'✅ torch {torch.__version__}')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Device: {device}')
print(f'CUDA: {torch.cuda.is_available()}')

# Test tensor creation
x = torch.randn(2, 3)
print(f'\n✅ Tensor creation works:')
print(x)
