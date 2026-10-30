"""
Longest-sample version of var2_mkt_u.py: 1973-01..2025-12, market index (long construction) and unemployment gap, Cholesky (u first).
    (a) including 2020 as is; (b) excluding 2020 through 12 monthly dummies for 2020 as exogenous regressors (2021-2025 kept).
Lags by BIC (max 12) and 12 lags. Granger test and unemployment response to a 1-unit index shock, months 0-24 (asymptotic 90% bands).
Usage: python experimental/market_macro/var2_mkt_u_long.py
"""
import os, sys
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkt_output as MO
LL, V = MO.LL, MO.V


def main():
    F = LL.financial()[MO.VARS]
    base = F.loc["1973-01":"2025-12"]; base = base[[t.year != 2020 for t in base.index]]
    M = pd.Series((F.loc["1973-01":] - base.mean()).values @ MO.W, index=F.loc["1973-01":].index)
    u = V.macro_data(False)["unemployment gap"]
    D = pd.DataFrame({"u": u, "M": M}).loc["1973-01":"2025-12"].dropna()
    dum = pd.DataFrame({f"d{m}": (D.index == pd.Period(f"2020-{m:02d}", "M")).astype(float) for m in range(1, 13)}, index=D.index)
    D.index = D.index.to_timestamp(); dum.index = D.index
    for lab, ex in (("(a) including 2020", None), ("(b) excluding 2020 (monthly dummies)", dum)):
        sel = VAR(D, exog=ex).select_order(12)
        pb = max(int(sel.bic), 1)
        print(f"\n===== 1973-2025, {lab}: {len(D)} months; BIC lag order {pb} (AIC {sel.aic}) =====")
        for p in sorted({pb, 12}):
            r = VAR(D, exog=ex).fit(p)
            gc = r.test_causality("u", ["M"], kind="f"); rev = r.test_causality("M", ["u"], kind="f")
            irf = r.irf(24); oi = irf.orth_irfs; se = irf.stderr(orth=True)
            sc = oi[0, 1, 1]; resp = oi[:, 0, 1] / sc; band = 1.645 * se[:, 0, 1] / sc
            print(f"  p={p}: index -> u F {gc.test_statistic:.2f}, p {gc.pvalue:.4f} | u -> index F {rev.test_statistic:.2f}, p {rev.pvalue:.4f}")
            print("        u response to 1-unit index shock: " + "  ".join(f"m{h}: {resp[h]:+.3f} [{resp[h] - band[h]:+.3f}, {resp[h] + band[h]:+.3f}]" for h in (3, 6, 12, 18, 24)))
            print("        index own response: " + "  ".join(f"m{h}: {oi[h, 1, 1] / sc:+.2f}" for h in (0, 6, 12, 24)))


if __name__ == "__main__":
    main()
