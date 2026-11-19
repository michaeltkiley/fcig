"""Bootstrap confidence intervals used everywhere in baseline_real (FS-A108, 19 Nov 2026).

Default: Efron's bias-corrected (BC) percentile interval (Efron 1981, 1987; Efron and Tibshirani 1993, ch. 14). With B draws d_b of an estimator whose point
estimate is t, the bias-correction constant is z0 = Phi^-1(share of draws below t, ties counted half), and the interval for nominal coverage 1 - 2a is the
pair of percentiles Phi(2 z0 + z_a) and Phi(2 z0 + z_{1-a}) of the draws. When the draws are centred on t (z0 = 0) it equals the plain percentile interval.
The acceleration of BCa is set to zero (it needs a jackknife of the whole estimation).
Set the environment variable CI=pct to get Efron's plain percentile interval (the convention before FS-A108), e.g. to compare.
"""
import os
import numpy as np
from scipy.stats import norm

METHOD = os.environ.get("CI", "bc")

def _z0(d, t):
    B = d.shape[0]; share = (np.sum(d < t, axis=0) + 0.5 * np.sum(d == t, axis=0)) / B
    return norm.ppf(np.clip(share, 0.5 / B, 1 - 0.5 / B))

def quantiles(d, t, qs):
    """The bootstrap quantiles that replace the plain percentiles qs (in percent) of the draws d (B x ...) around the point estimate t (shape d.shape[1:] or scalar).
    Returns an array (len(qs), ...)."""
    d = np.asarray(d, float); t = np.broadcast_to(np.asarray(t, float), d.shape[1:])
    if METHOD == "pct": return np.array([np.percentile(d, q, axis=0) for q in qs])
    z0 = _z0(d, t); ds = np.sort(d, axis=0); B = d.shape[0]; out = []
    for q in qs:
        a = norm.cdf(2 * z0 + norm.ppf(q / 100.0)); pos = a * (B - 1); lo = np.floor(pos).astype(int); hi = np.minimum(lo + 1, B - 1); fr = pos - lo
        out.append(np.take_along_axis(ds, lo[None, ...] if np.ndim(lo) else np.array(lo).reshape(1), axis=0)[0] * (1 - fr)
                   + np.take_along_axis(ds, hi[None, ...] if np.ndim(hi) else np.array(hi).reshape(1), axis=0)[0] * fr)
    return np.array(out)

def ci(d, t, lo=5, hi=95):
    """(lower, upper) bounds for one interval."""
    q = quantiles(d, t, (lo, hi)); return q[0], q[1]
