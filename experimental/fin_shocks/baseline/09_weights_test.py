"""Test of the proportional-weights restriction (Note B, Robustness 4). In each monthly equation (unemployment gap, core PCE inflation) the FCI enters with one coefficient per lag
(restricted); the unrestricted equation enters its three weighted components (10-year yield, equity valuation, dollar) separately, so the restriction is that the three coefficients are
equal at each lag (2 restrictions per lag). Wald statistic with a heteroskedasticity-robust (HC1) covariance matrix; p-values from the chi-square(2L) distribution and from a residual bootstrap under the restriction
(999 draws: residuals of the restricted equation, resampled, added to its fitted values, regressors fixed). Run for the baseline sample (monthly equations from 1996) and for the monthly equations from 1973 (no trend, 2020 in).
   python3 09_weights_test.py        Output: results/weights_test.csv"""
import numpy as np, pandas as pd
from scipy import stats
from lib import model as M
from lib.paths import RESULTS

B = 999
def wald(X, y, R):
    n, k = X.shape; XX = np.linalg.inv(X.T @ X); b = XX @ X.T @ y; r = y - X @ b; V = XX @ (X.T * (r ** 2)) @ X @ XX * n / (n - k); Rb = R @ b
    return float(Rb @ np.linalg.solve(R @ V @ R.T, Rb))
rows = []
for Ls, seed in (((12,), 7), ((6, 3), 8)):                                  # 12 lags (main text), then 6 and 3 (appendix), each with its own stream
  rng = np.random.default_rng(seed)
  for start, form in [(st, f) for st in ("1996-01", "1973-01") for f in ("nom", "real", "rstar")]:
    for L in Ls:
        X, Y = M.macro_data(form, "cmp", ["u", "pi"], L, start, None, "in", "none"); n, k = X.shape; K = 2; nd = 4
        Xr, _ = M.macro_data(form, form, ["u", "pi"], L, start, None, "in", "none")                  # restricted: the FCI as one regressor per lag
        for j, name in enumerate(("u", "pi")):
            y = Y[:, j]; R = np.zeros((2 * L, k))
            for l in range(L):
                o = 1 + K * L + l * nd; R[2 * l, o + 1], R[2 * l, o + 2] = 1, -1; R[2 * l + 1, o + 2], R[2 * l + 1, o + 3] = 1, -1
            W = wald(X, y, R); fit = Xr @ np.linalg.lstsq(Xr, y, rcond=None)[0]; res = y - fit
            Wb = np.array([wald(X, fit + res[rng.integers(0, n, n)], R) for _ in range(B)])
            rows.append(dict(start=start, step=form, lags=L, eq=name, restrictions=2 * L, nobs=n, wald=W, p=1 - stats.chi2.cdf(W, 2 * L), p_boot=(1 + np.sum(Wb >= W)) / (B + 1)))
            print(f"{start} {form:6s} L={L:2d} {name:2s}: Wald({2 * L}) = {W:.1f}, chi-square p = {rows[-1]['p']:.3f}, bootstrap p = {rows[-1]['p_boot']:.3f}", flush=True)
pd.DataFrame(rows).to_csv(RESULTS / "weights_test.csv", index=False, float_format="%.4f")
