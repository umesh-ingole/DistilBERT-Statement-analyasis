#!/usr/bin/env python3
"""
Minimal PyTorch test - ensure tensor operations work
"""
import torch

print('\n' + '='*80)
print('STEP 7: MINIMAL PYTORCH TEST')
print('='*80)

try:
    print('\n[Test 1] Create tensor...')
    x = torch.randn(2, 3)
    print(f'  ✅ Tensor created: shape {x.shape}')
    
    print('\n[Test 2] Matrix multiplication...')
    y = torch.randn(3, 4)
    z = torch.matmul(x, y)
    print(f'  ✅ Result shape: {z.shape}')
    
    print('\n[Test 3] Gradient computation...')
    a = torch.randn(5, requires_grad=True)
    b = (a ** 2).sum()
    b.backward()
    print(f'  ✅ Gradients computed: {a.grad[:3]}')
    
    print('\n[Test 4] Device compatibility...')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    c = torch.randn(2, 2, device=device)
    print(f'  ✅ Device: {device}, Tensor device: {c.device}')
    
    print('\n' + '='*80)
    print('✅ ALL PYTORCH TESTS PASSED')
    print('='*80 + '\n')
    
except Exception as e:
    print(f'\n❌ ERROR: {e}')
    print('='*80 + '\n')
    import sys
    sys.exit(1)
