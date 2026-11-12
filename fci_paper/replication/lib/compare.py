"""Comparison metrics: correlations, cross-index range, closest and widest six-month windows."""
import numpy as np, pandas as pd


def corr(a, b, change=False):
    j = pd.concat([a, b], axis=1).dropna()
    if change:
        j = j.diff(12).dropna()
    return float(j.corr().iloc[0, 1])


def spread(D):
    """Cross-index range (max - min) each month."""
    D = D.dropna()
    return D.max(axis=1) - D.min(axis=1)


def windows(D, n=5, widest=True):
    """Non-overlapping six-month windows ranked by the mean cross-index range."""
    roll = spread(D).rolling(6).mean().dropna()
    out = []
    for e, v in roll.sort_values(ascending=not widest).items():
        if all(abs((e - c).n) >= 6 for c, _ in out):
            out.append((e, v))
        if len(out) == n:
            break
    return sorted(out)
