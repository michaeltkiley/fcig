"""Test of the proportional-weights restriction (Note B, Robustness 4). In each monthly equation (unemployment gap, core PCE inflation) the FCI enters with one coefficient per lag
(restricted); the unrestricted equation enters its three weighted components (10-year yield, equity valuation, dollar) separately, so the restriction is that the three coefficients are
equal at each lag (2 restrictions per lag). Wald statistic with a heteroskedasticity-robust (HC1) covariance matrix, chi-square(2L) p-value. Baseline sample (1996-2026, no trend, 2020 in).
   python3 09_weights_test.py        Output: results/weights_test.csv"""
import numpy as np, pandas as pd
from scipy import stats
from lib import model as M
from lib.paths import RESULTS

rows = []
for form in ("nom", "real", "rstar"):
    for L in (3, 6, 12):
        X, Y = M.macro_data(form, "cmp", ["u", "pi"], L, "1996-01", None, "in", "none"); n, k = X.shape; K = 2; nd = 4
        for j, name in enumerate(("u", "pi")):
            y = Y[:, j]; XX = np.linalg.inv(X.T @ X); b = XX @ X.T @ y; r = y - X @ b; V = XX @ (X.T * (r ** 2)) @ X @ XX * n / (n - k)
            R = np.zeros((2 * L, k))
            for l in range(L):
                o = 1 + K * L + l * nd; R[2 * l, o + 1], R[2 * l, o + 2] = 1, -1; R[2 * l + 1, o + 2], R[2 * l + 1, o + 3] = 1, -1
            Rb = R @ b; W = float(Rb @ np.linalg.solve(R @ V @ R.T, Rb)); rows.append(dict(step=form, lags=L, eq=name, restrictions=2 * L, nobs=n, wald=W, p=1 - stats.chi2.cdf(W, 2 * L)))
            print(f"{form:6s} L={L:2d} {name:2s}: Wald({2 * L}) = {W:.1f}, p = {rows[-1]['p']:.3f}", flush=True)
pd.DataFrame(rows).to_csv(RESULTS / "weights_test.csv", index=False, float_format="%.4f")
