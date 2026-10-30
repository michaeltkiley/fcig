"""Two-variable VAR (unemployment gap, index), Cholesky with unemployment first, 2020 months as dummies; the index's flow (forward impetus)."""
import warnings
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")


def fit(u, m, p, start="1973-01", end="2026-09"):
    D = pd.DataFrame({"u": u, "M": m}).loc[start:end].dropna()
    dum = pd.DataFrame({f"d2020_{k:02d}": (D.index == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}, index=D.index)
    D.index = D.index.to_timestamp(); dum.index = D.index
    return VAR(D, exog=dum).fit(p), D, dum


def response(r, H=36):
    """Unemployment response to a shock that moves the index by 1 on impact (months 0..H), its standard error, and the index's own path."""
    irf = r.irf(H); oi = irf.orth_irfs; sc = oi[0, 1, 1]
    return oi[:, 0, 1] / sc, irf.stderr(orth=True)[:, 0, 1] / sc, oi[:, 1, 1] / sc


def bootstrap(r, D, dum, H=36, reps=500, seed=7):
    """Residual bootstrap (recursive, dummies fixed): 95% percentile bands of the scaled unemployment response."""
    rng = np.random.default_rng(seed)
    Y, p = D.values, r.k_ar
    A, c, e = r.coefs, r.params.values, r.resid.values
    out = []
    for _ in range(reps):
        Yb = Y.copy(); draw = e[rng.integers(0, len(e), size=len(Y) - p)]
        for t in range(p, len(Y)):
            x = c[0] + dum.values[t] @ c[1:13] + sum(A[l] @ Yb[t - 1 - l] for l in range(p))
            Yb[t] = x + draw[t - p]
        rb = VAR(pd.DataFrame(Yb, index=D.index, columns=D.columns), exog=dum).fit(p)
        out.append(response(rb, H)[0])
    return np.percentile(out, 2.5, axis=0), np.percentile(out, 97.5, axis=0)


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
