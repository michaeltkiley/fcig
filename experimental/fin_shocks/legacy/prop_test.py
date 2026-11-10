"""FS-A31: F test of the proportional-weights restriction. Monthly equations (u gap, core PCE) with the FCI as one regressor per lag (restricted)
versus its three weighted components entered separately (unrestricted); nested because FCI = sum of the components. Quadratic trend, 1994-02..2026-09,
2020-03..12 dropped, as in midas_core.py. Plain OLS F statistics (no serial-correlation correction)."""
import numpy as np, pandas as pd
from scipy import stats
import midas_core as mc
mc.TREND = True
rows = []
for form in ("nom", "real", "rstar"):
    for L in (3, 6, 12):
        Xr, Y = mc.macro_data(form, 1, ["u", "pi"], L); Xu, Y2 = mc.macro_data(form, "cmp", ["u", "pi"], L)
        assert len(Y) == len(Y2) and np.allclose(Y, Y2)
        n = len(Y); q = 2 * L
        for j, nm in enumerate(("u", "pi")):
            y = Y[:, j]
            rr = y - Xr @ np.linalg.lstsq(Xr, y, rcond=None)[0]; ru = y - Xu @ np.linalg.lstsq(Xu, y, rcond=None)[0]
            F = ((rr @ rr - ru @ ru) / q) / (ru @ ru / (n - Xu.shape[1])); p = 1 - stats.f.cdf(F, q, n - Xu.shape[1])
            rows.append(dict(step=form, lags=L, eq=nm, restrictions=q, n=n, F=F, p=p)); print(f"{form:6s} L={L:2d} {nm:3s}: {q} restrictions, F = {F:.2f}, p = {p:.3f}", flush=True)
pd.DataFrame(rows).to_csv("prop_test.csv", index=False, float_format="%.4f")
