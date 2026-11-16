#!/usr/bin/env python3
"""t411: pick the mottle cell size whose lag-1 statistic lands near the
vendor's 0.23 (sidebar band), using the port's own generator."""
import numpy as np
M = (1 << 64)
def splitmix(x, y):
    z = ((x & 0xffffffff) << 32) ^ (y & 0xffffffff) ^ 0x9e3779b97f4a7c15
    z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) % M
    z = ((z ^ (z >> 27)) * 0x94d045bb41f336) % M
    return z ^ (z >> 31)
weights = [4, 15, 9, 8, 7, 7, 7, 7, 6, 4]
lums = [0, (77+113+117)/3, (85+125+125)/3, (97+146+146)/3, (69+105+109)/3,
        (97+97+97)/3, (89+134+138)/3, (89+89+89)/3, (60+93+97)/3, (73+73+85)/3]
acc = list(np.cumsum(weights))
def lum(x, y, cell):
    z = splitmix(x // cell, y // cell); r = z % 100
    i = int(np.searchsorted(acc, r, side='right'))
    return lums[i] if i < 10 else 100.0
for cell in (1, 2, 4, 6, 8):
    g = np.array([[lum(x, y, cell) for x in range(156)] for y in range(288)])
    r1 = np.abs(np.diff(g, axis=1)).mean() / np.abs(g - g.mean()).mean()
    print('cell', cell, 'lag1 ratio', round(float(r1), 2))
