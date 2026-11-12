"""Helpers for steps 11, 13, 14, 15 (helper module `purge`): outcome series from data/, Covid rule, OLS/HAC/Wald, moving blocks, multiple-testing adjustments."""
import numpy as np, pandas as pd
from .config import DATA, RES


def covid(p):
    return p.year == 2020 or (p.year == 2021 and p.month <= 3)


def fred(name):
    d = pd.read_csv(DATA / f"{name}.csv")
    return pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()


def monthly(name):
    s = fred(name); s.index = s.index.to_period("M"); return s


def read_res(f):
    d = pd.read_csv(RES / f, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def ols(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None); return b, y - X @ b


def hac(X, e, L):
    """Newey-West (Bartlett) covariance of OLS coefficients."""
    XtXi = np.linalg.inv(X.T @ X); S = (X * e[:, None]).T @ (X * e[:, None])
    for l in range(1, L + 1):
        G = (X[l:] * e[l:, None]).T @ (X[:-l] * e[:-l, None]); S += (1 - l / (L + 1)) * (G + G.T)
    return XtXi @ S @ XtXi


def wald(b, V, R, r=None):
    from scipy import stats
    R = np.atleast_2d(R); r = np.zeros(R.shape[0]) if r is None else np.atleast_1d(r)
    d = R @ b - r; W = float(d @ np.linalg.solve(R @ V @ R.T, d)); return W, float(1 - stats.chi2.cdf(W, R.shape[0]))


def blocks(n, block, rng):
    nb = -(-n // block); return np.concatenate([np.arange(s, s + block) for s in rng.integers(0, n - block + 1, nb)])[:n] % n


def holm(p):
    """Holm step-down adjusted p-values."""
    p = np.asarray(p, float); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * p[i]); adj[i] = min(run, 1)
    return adj


def bh(p):
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(p, float); o = np.argsort(p)[::-1]; m = len(p); adj = np.empty(m); run = 1
    for r, i in enumerate(o):
        run = min(run, p[i] * m / (m - r)); adj[i] = run
    return adj


def single_thread_blas():
    """Many small least-squares solves (bootstraps) run orders of magnitude slower with a multi-threaded BLAS on shared machines: use one thread.
    Uses threadpoolctl if installed, else the bundled OpenBLAS; harmless if neither works (results do not depend on it beyond rounding)."""
    try:
        from threadpoolctl import threadpool_limits
        threadpool_limits(1); return
    except Exception:
        pass
    try:
        import ctypes, glob, os, numpy
        for f in glob.glob(os.path.join(os.path.dirname(numpy.__file__), "..", "numpy.libs", "lib*openblas*")):
            lib = ctypes.CDLL(f)
            for nm in ("scipy_openblas_set_num_threads64_", "openblas_set_num_threads64_", "openblas_set_num_threads", "scipy_openblas_set_num_threads"):
                if hasattr(lib, nm):
                    getattr(lib, nm)(1); return
    except Exception:
        pass
