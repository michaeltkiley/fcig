"""Two-variable VAR in the unemployment gap u and the market index M (Cholesky, u first), 2020 months as dummies.

With u ordered first, the response of u to a shock that moves M by one unit on impact is the moving-average coefficient Theta_h[u, M], so the
scaled response Phi(h) does not depend on the residual covariance. Point estimates use statsmodels (for the Granger test); the bootstrap uses the
same regression in numpy: moving blocks of residual pairs (12 months), recursive simulation, dummies and initial values fixed."""
import warnings
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR
from .config import BLOCK, SEED
warnings.filterwarnings("ignore")


def frame(u, m, start="1973-01", end="2026-09"):
    D = pd.DataFrame({"u": u, "M": m}).loc[start:end].dropna()
    dum = pd.DataFrame({f"d2020_{k:02d}": (D.index == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}, index=D.index)
    dum = dum.loc[:, dum.any()]                                  # no 2020 months in the sample: no dummies
    D.index = D.index.to_timestamp(); dum.index = D.index
    return D, dum


def fit(u, m, p, start="1973-01", end="2026-09"):
    """statsmodels fit; returns result, data, dummies."""
    D, dum = frame(u, m, start, end)
    return VAR(D, exog=dum if dum.shape[1] else None).fit(p), D, dum


def ma_phi(A, H=36):
    """Theta_h for h = 0..H from VAR coefficient matrices A[l] (l = 0..p-1 for lags 1..p); returns Phi(h) = Theta_h[u,M] and M's own path Theta_h[M,M]."""
    p = len(A)
    Th = [np.eye(2)]
    for h in range(1, H + 1):
        Th.append(sum(A[l] @ Th[h - 1 - l] for l in range(min(h, p))))
    Th = np.array(Th)
    return Th[:, 0, 1], Th[:, 1, 1]


def response(r, H=36):
    Phi, own = ma_phi(r.coefs, H)
    return Phi, own


def _ols(Y, dum, p):
    T = len(Y)
    Z = np.column_stack([np.ones(T - p), dum[p:]] + [Y[p - l:T - l] for l in range(1, p + 1)])
    B, *_ = np.linalg.lstsq(Z, Y[p:], rcond=None)
    nd = 1 + dum.shape[1]
    A = np.array([B[nd + 2 * l: nd + 2 * l + 2].T for l in range(p)])
    return B, A, Y[p:] - Z @ B


def bootstrap(D, dum, p, H=36, reps=500, seed=SEED, block=BLOCK):
    """Moving-block residual bootstrap. Returns draws of Phi (reps x H+1) and of the M path."""
    rng = np.random.default_rng(seed)
    Y, d = D.values, dum.values
    B, A, e = _ols(Y, d, p)
    n, nd = len(e), 1 + d.shape[1]
    base = B[:nd]
    nb = -(-n // block)
    out_phi, out_own = [], []
    for _ in range(reps):
        idx = np.concatenate([np.arange(s, s + block) for s in rng.integers(0, n - block + 1, nb)])[:n]
        eb = e[idx]
        Yb = Y.copy()
        for t in range(p, len(Y)):
            x = base[0] + d[t] @ base[1:] if d.shape[1] else base[0].copy()
            for l in range(p):
                x = x + A[l] @ Yb[t - 1 - l]
            Yb[t] = x + eb[t - p]
        _, Ab, _ = _ols(Yb, d, p)
        ph, ow = ma_phi(Ab, H)
        out_phi.append(ph); out_own.append(ow)
    return np.array(out_phi), np.array(out_own)


def bands(draws, level):
    a = (1 - level) / 2 * 100
    return np.percentile(draws, a, axis=0), np.percentile(draws, 100 - a, axis=0)


def forward_impetus(m, Phi):
    """FCI-G form: effect over the next 12 months of the last 12 months of index changes, in units of the 12-month effect of a one-unit shift:
    FI(t) = sum_{k<12} [Phi(k+12) - Phi(k)] / Phi(12) * dM(t-k)."""
    w = [(Phi[k + 12] - Phi[k]) / Phi[12] for k in range(12)]
    dm = m.diff()
    return sum(w[k] * dm.shift(k) for k in range(12))


def current_pressure(m, Phi):
    """Appendix: the part of the level already passed through, sum_{k<=12} [Phi(k) - Phi(k-1)] / Phi(12) * M(t-k) (weights sum to 1)."""
    w = [(Phi[k] - (Phi[k - 1] if k else 0.0)) / Phi[12] for k in range(13)]
    return sum(w[k] * m.shift(k) for k in range(13))
