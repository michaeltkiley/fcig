"""Step 11 helpers: purging index inputs of the unemployment gap and core inflation; rebuilding indexes; a vectorised version of lib.var.bootstrap
(same moving-block residual bootstrap, same random draws, simulated for all draws at once)."""
import numpy as np, pandas as pd
from . import cases, data, indexes as I, var
from .config import RES, START, END, BLOCK, SEED
from .purge_util import monthly

LAGS = 12
FIRST_REC = "1983-01"
STEPS = ("nominal", "real", "rstar")
VARS = {"market": I.MARKET_VARS, "gs": list(I.GS_W)}


def core_inflation():
    s = monthly("PCEPILFE")
    return 100 * np.log(s / s.shift(12))


def regressors(u, pi):
    cols = {}
    for l in range(LAGS + 1):
        cols[f"u{l}"] = u.shift(l); cols[f"pi{l}"] = pi.shift(l)
    return pd.DataFrame(cols).loc[START:END]


def purge_full(x, Z):
    A = np.c_[np.ones(len(Z)), Z.values]
    b = np.linalg.lstsq(A, x.values, rcond=None)[0]; fit = A @ b
    return x - fit, 1 - ((x.values - fit) ** 2).sum() / ((x.values - x.mean()) ** 2).sum()


def purge_recursive(x, Z):
    A = np.c_[np.ones(len(Z)), Z.values]; y = x.values; res = np.full(len(y), np.nan)
    for t in range(len(y)):
        if x.index[t] < pd.Period(FIRST_REC, "M"):
            continue
        b = np.linalg.lstsq(A[:t + 1], y[:t + 1], rcond=None)[0]; res[t] = y[t] - A[t] @ b
    return pd.Series(res, index=x.index)


def build_index(X, kind, conv, w):
    """Index level from (possibly purged) inputs X, demeaned over the available sample; market weights w (y10, equities, dollar) or GS weights x conversion."""
    cols = VARS[kind]
    Xd = X[cols] - X[cols].dropna().mean()
    if kind == "market":
        return (Xd * np.asarray(w)).sum(axis=1, min_count=len(cols))
    return (Xd * pd.Series(I.GS_W)[cols] * conv).sum(axis=1, min_count=len(cols))


def all_inputs():
    D = data.load()
    return D, {s: cases.inputs(D, s, rstar="rstar LW") for s in STEPS}


def bootstrap_fast(D, dum, p, H=36, reps=500, seed=SEED, block=BLOCK):
    """Identical to lib.var.bootstrap (same draws of block starts, same recursion), vectorised over draws. Returns draws of Phi (reps x H+1)."""
    rng = np.random.default_rng(seed)
    Y, d = D.values, dum.values
    B, A, e = var._ols(Y, d, p)
    n, nd, T = len(e), 1 + d.shape[1], len(Y)
    nb = -(-n // block)
    idx = np.array([np.concatenate([np.arange(s, s + block) for s in rng.integers(0, n - block + 1, nb)])[:n] for _ in range(reps)])
    eb = e[idx]                                                   # reps x n x 2
    base = B[:nd]
    c = np.array([base[0] + (d[t] @ base[1:] if d.shape[1] else 0.0) for t in range(T)])
    Yb = np.broadcast_to(Y, (reps, T, 2)).copy()
    for t in range(p, T):
        x = c[t] + eb[:, t - p, :]
        for l in range(p):
            x = x + Yb[:, t - 1 - l, :] @ A[l].T
        Yb[:, t, :] = x
    out = []
    for r in range(reps):
        _, Ab, _ = var._ols(Yb[r], d, p)
        out.append(var.ma_phi(Ab, H)[0])
    return np.array(out)
