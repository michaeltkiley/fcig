"""
Two-variable VAR: unemployment gap and the market index (the full index M = w'x, not split; pp of the 2-year yield per NS unit), monthly.
    Ordering for the Cholesky decomposition: unemployment first, market index second (unemployment reacts to the market index only with a lag).
    Granger causality: do lags of the market index help predict unemployment (F test)?
    Impulse response: unemployment response to a market-index shock, scaled to a 1-unit move in the index on impact, months 0-24 (asymptotic 90% bands).
Data:
    long sample: M from 1973 with monthly-average 10-year (GS10), CAPE (Shiller spliced to the project's series), real broad dollar (mf_var_us_long.financial)
    short sample: the project's market index (transmission_v3_monthly.csv, end of month) from 1990
    u = UNRATE - CBO NROU (interpolated). Lags by BIC (max 12); 12 lags as a check. Samples end 2019-12 (the 2020 collapse excluded; a version to 2025-12 also shown).
Usage: python experimental/market_macro/var2_mkt_u.py
"""
import os, sys
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import mkt_output as MO
LL, V = MO.LL, MO.V


def run(lab, D):
    D = D.dropna()
    sel = VAR(D).select_order(12)
    pb = max(int(sel.bic), 1)
    print(f"\n===== {lab}: {D.index[0]}..{D.index[-1]} ({len(D)} months); lag order by BIC {pb} (AIC {sel.aic}) =====")
    for p in sorted({pb, 12}):
        r = VAR(D).fit(p)
        gc = r.test_causality("u", ["M"], kind="f")
        rev = r.test_causality("M", ["u"], kind="f")
        irf = r.irf(24)
        # orthogonalized (Cholesky, order u, M); shock to M scaled to 1 unit of M on impact
        oi = irf.orth_irfs                         # (h, response, shock)
        se = irf.stderr(orth=True)
        iM, iu = list(D.columns).index("M"), list(D.columns).index("u")
        scale = oi[0, iM, iM]
        resp = oi[:, iu, iM] / scale
        band = 1.645 * se[:, iu, iM] / scale
        print(f"  p={p}: market index Granger-causes unemployment: F {gc.test_statistic:.2f}, p {gc.pvalue:.4f}  | reverse (u -> M): F {rev.test_statistic:.2f}, p {rev.pvalue:.4f}")
        print(f"        unemployment response to a 1-unit market-index shock (u ordered first): " +
              "  ".join(f"m{h}: {resp[h]:+.3f} [{resp[h] - band[h]:+.3f}, {resp[h] + band[h]:+.3f}]" for h in (0, 3, 6, 12, 18, 24)))
        print(f"        market index own response: " + "  ".join(f"m{h}: {oi[h, iM, iM] / scale:+.2f}" for h in (0, 6, 12, 24)) + f";  shock sd {scale:.2f} index units")


def main():
    F = LL.financial()[MO.VARS]
    Mm = V.macro_data(False)
    base = F.loc["1973-01":"2019-12"]
    Ml = pd.Series((F.loc["1973-01":] - base.mean()).values @ MO.W, index=F.loc["1973-01":].index)
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    u = Mm["unemployment gap"]
    for lab, M, start, end in (("long sample, to 2019", Ml, "1973-01", "2019-12"), ("long sample, to 2025 (incl. 2020)", Ml, "1973-01", "2025-12"),
                               ("project market index, 1990-2019", tr["MKT"], "1990-01", "2019-12"), ("project market index, 1990-2025 (incl. 2020)", tr["MKT"], "1990-01", "2025-12")):
        D = pd.DataFrame({"u": u, "M": M}).loc[start:end]
        D.index = D.index.to_timestamp()
        run(lab, D)


if __name__ == "__main__":
    main()
