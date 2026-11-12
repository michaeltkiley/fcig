"""Helpers for step 18 (agreement of the market and FRB/US weights): fast policy-news fits, FRB/US responses to temporary shocks and to arbitrary asset paths,
summary statistics of the weight difference D_h(x) and of its runs. No network, no files written here."""
import numpy as np, pandas as pd
from .config import DATA

MV = ["y10", "equities", "dollar"]                       # market variables
FRB = {"y10": "rg10", "equities": "req", "dollar": "fpxr"}
NQ = 32


# ------------------------------------------------------------------ policy-news fits in numpy (same algebra as lib.indexes.ns_factor / gls_weights)

def ns_arr(X5, u2):
    """Nakamura-Steinsson factor from the five surprises (columns MP1, MP2, ED2, ED3, ED4), scaled so one unit moves the 2-year yield 1 pp."""
    U, S, Vt = np.linalg.svd(X5, full_matrices=False)
    f = U[:, 0] * S[0]
    if f @ X5[:, 4] < 0:
        f = -f
    return f * (f @ u2) / (f @ f)


def fit(X5, u2, Y):
    """One-factor GLS on window moves Y (n x 3): returns market weights w (w'psi = 1) and responses psi."""
    f = ns_arr(X5, u2)
    fc = f - f.mean(); Yc = Y - Y.mean(0)
    psi = (fc @ Yc) / (fc @ fc)
    R = Yc - np.outer(fc, psi)
    S = R.T @ R / (len(f) - 2)
    w = np.linalg.solve(S, psi)
    return w / (psi @ w), psi


# ------------------------------------------------------------------ FRB/US responses

def load_frbus():
    """Persistent and temporary GDP responses per unit (zfree design), quarters 1..32, indexed so that arrays have element q = quarter q (element 0 = 0);
    G = GDP response to a persistent 1 pp funds-rate hike (negative)."""
    p = pd.read_csv(DATA / "frbus_paths.csv")
    out = {}
    for v, e in FRB.items():
        for sh in ("persistent", "temporary"):
            g = p[(p.design == "zfree") & (p.experiment == e) & (p["shape"] == sh)].sort_values("quarter").gdp_per_unit.values
            out[(v, sh)] = np.r_[0.0, g]
    G = np.r_[0.0, pd.read_csv(DATA / "frbus_hike_paths.csv").sort_values("quarter").gdp.values]
    return out, G


def path_x(h, hl):
    """Asset path x_s, s = 1..h: 1 for a persistent shift (hl = inf), else 0.5 ** ((s - 1) / hl) (half-life hl quarters; x_1 = 1 is the initial movement)."""
    s = np.arange(1, h + 1)
    return np.ones(h) if np.isinf(hl) else 0.5 ** ((s - 1) / hl)


def b_path(R, G, h, hl):
    """Funds-rate-equivalent GDP effect at horizon h per unit initial movement of each market variable that follows path_x with half-life hl[v] (tuple y10, eq, usd).
    By linearity the GDP effect of the path x is sum_s x_s Tmp(h - s + 1) (temporary-shock responses), divided by the funds-rate yardstick G(h)."""
    out = []
    for v, hv in zip(MV, hl):
        x = path_x(h, hv); T = R[(v, "temporary")]
        out.append(sum(x[s - 1] * T[h - s + 1] for s in range(1, h + 1)) / G[h])
    return np.array(out)


def b_persist(R, G, h):
    """Persistent-shift experiment as the package uses it: Phi(h) / G(h)."""
    return np.array([R[(v, "persistent")][h] for v in MV]) / G[h]


# ------------------------------------------------------------------ summaries

def runs(flag):
    f = np.r_[0, np.asarray(flag, int), 0]; d = np.diff(f)
    return np.where(d == -1)[0] - np.where(d == 1)[0]


def mbb(T, L, rng):
    """Moving-block bootstrap indices (length T, blocks of L)."""
    nb = int(np.ceil(T / L)); st = rng.integers(0, T - L + 1, nb)
    return (st[:, None] + np.arange(L)).ravel()[:T]


THR = (0.25, 0.5)


def dstats(D, m):
    """Summary of D (weight difference applied to the movement) and m (market-index movement w_M'x) over a series: absolute size, size relative to m,
    frequency above thresholds (policy-rate points) and run lengths (consecutive observations) above them."""
    a = np.abs(D)
    o = {"mean_abs": a.mean(), "median_abs": np.median(a), "p90_abs": np.percentile(a, 90), "mean_abs_market_move": np.abs(m).mean(),
         "ratio_mean_abs": a.mean() / np.abs(m).mean(), "sd_ratio": D.std() / m.std(), "share_gt_half_move": (a > 0.5 * np.abs(m)).mean(),
         "corr_D_m": np.corrcoef(D, m)[0, 1]}
    for t in THR:
        r = runs(a > t); tag = f"{t:g}".replace(".", "p")
        o[f"share_gt_{tag}"] = (a > t).mean(); o[f"mean_run_{tag}"] = r.mean() if len(r) else 0.0
        o[f"max_run_{tag}"] = r.max() if len(r) else 0; o[f"n_runs_{tag}"] = len(r)
    return o


def ci(a, lo=5, hi=95):
    a = np.asarray(a, float)
    return float(np.nanpercentile(a, lo)), float(np.nanpercentile(a, hi))
