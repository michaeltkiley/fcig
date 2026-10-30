"""
Significance of the unemployment response to a market-index shock in the two-variable VAR (1973-01..2019-12; Cholesky, u first), 4 lags (BIC) and 12 lags.
Bands: asymptotic (90% and 95%) and residual bootstrap (1000 replications, 95% percentile; statsmodels errband_mc), for the response scaled to a 1-unit M shock
(the scaling by the impact of M uses each replication's own impact? no: bands are for the orthogonalized response divided by the point-estimate impact; the impact
of M is estimated very precisely, so the difference is negligible).
Usage: python experimental/market_macro/mkt_irf_significance.py
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
    base = F.loc["1973-01":"2019-12"]
    Ml = pd.Series((F.loc["1973-01":] - base.mean()).values @ MO.W, index=F.loc["1973-01":].index)
    u = V.macro_data(False)["unemployment gap"]
    D = pd.DataFrame({"u": u, "M": Ml}).loc["1973-01":"2019-12"].dropna(); D.index = D.index.to_timestamp()
    hs = (1, 3, 6, 9, 12, 18, 24, 36)
    for p in (4, 12):
        r = VAR(D).fit(p)
        irf = r.irf(36)
        oi = irf.orth_irfs; sc = oi[0, 1, 1]; resp = oi[:, 0, 1] / sc; se = irf.stderr(orth=True)[:, 0, 1] / sc
        lo, hi = irf.errband_mc(orth=True, repl=1000, signif=0.05, seed=7)
        blo, bhi = lo[:, 0, 1] / sc, hi[:, 0, 1] / sc
        print(f"\n[p={p}] unemployment response to a 1-unit market-index shock")
        print(f"   {'month':>5} {'resp':>7} {'t':>6} {'asy 95%':>17} {'bootstrap 95%':>17}")
        for h in hs:
            print(f"   {h:>5} {resp[h]:+7.3f} {resp[h] / se[h]:6.1f} [{resp[h] - 1.96 * se[h]:+.3f},{resp[h] + 1.96 * se[h]:+.3f}] [{blo[h]:+.3f},{bhi[h]:+.3f}]")
        sig = [h for h in range(1, 37) if blo[h] > 0]
        print(f"   months with the bootstrap 95% band above zero: {sig[0] if sig else None}..{sig[-1] if sig else None} ({len(sig)} of 36)")


if __name__ == "__main__":
    main()
