"""Event-position bins shared by routes A and B."""
import numpy as np
from mf_common import EV
def positions(idx):
    k = np.array([int(EV.k[i]) for i in idx]); n = np.array([int(EV.n[i]) for i in idx])
    bins = [(0, 3), (4, 7), (8, 11), (12, 15), (16, 19), (20, 23)]; out = []
    for lo, hi in bins:
        m = (k >= lo) & (k <= hi)
        if m.sum(): out.append((int(round(k[m].mean())), int(round(n[m].mean())), m.mean()))
    return out

