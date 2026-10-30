"""
Lag-length check for mkt_dynamic.py: same VAR (unemployment gap, market index; Cholesky u first; 1973-01..2019-12), 4 lags (main) vs 12 lags.
Reports Phi(m), the yardstick Phi(12), the current-pressure lag weights, and the indexes' sd / latest / correlation with FCI-G (1-year lookback).
Also: Phi normalized at 12 months is used in both cases (effects that keep building after 12 months make the forward impetus no longer equal to EP - CP).
Usage: python experimental/market_macro/mkt_dynamic_lags.py
"""
import os, sys
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import mkt_output as MO
LL, V = MO.LL, MO.V


def main():
    F = LL.financial()[MO.VARS]
    base = F.loc["1973-01":"2019-12"]
    Ml = pd.Series((F.loc["1973-01":] - base.mean()).values @ MO.W, index=F.loc["1973-01":].index)
    u = V.macro_data(False)["unemployment gap"]
    D = pd.DataFrame({"u": u, "M": Ml}).loc["1973-01":"2019-12"].dropna(); D.index = D.index.to_timestamp()
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    M = tr["MKT"]
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep.index = pd.PeriodIndex(rep["month"], freq="M")
    fg = pd.concat([f1, rep["1yr|FCI-G"].loc[f1.index[-1] + 1:]]) / 0.4525
    out = {}
    for p in (4, 12):
        r = VAR(D).fit(p)
        irf = r.irf(36); oi = irf.orth_irfs; se = irf.stderr(orth=True)
        sc = oi[0, 1, 1]; Phi = oi[:, 0, 1] / sc; band = 1.645 * se[:, 0, 1] / sc
        print(f"\n[p={p}] u response to a 1-unit M shock (90% band): " + "  ".join(f"m{h}: {Phi[h]:+.3f} [{Phi[h] - band[h]:+.2f},{Phi[h] + band[h]:+.2f}]" for h in (3, 6, 12, 18, 24, 36)))
        print(f"        M own response: " + "  ".join(f"m{h}: {oi[h, 1, 1] / sc:+.2f}" for h in (0, 6, 12, 24, 36)) + f";  yardstick Phi(12) {Phi[12]:+.3f} (output {-2 * Phi[12]:+.2f}%)")
        wcp = np.array([Phi[m] - (Phi[m - 1] if m > 0 else 0.0) for m in range(13)]) / Phi[12]
        wgi = np.array([Phi[m + 12] - Phi[m] for m in range(12)]) / Phi[12]
        print("        current-pressure weights m0..12: " + " ".join(f"{x:.2f}" for x in wcp))
        print("        forward-impetus weights on dM m0..11: " + " ".join(f"{x:.2f}" for x in wgi))
        CP = sum(wcp[m] * M.shift(m) for m in range(13))
        GI = sum(wgi[m] * M.diff().shift(m) for m in range(12))
        J = pd.DataFrame({"M": M, "CP": CP, "forward impetus": GI, "EP - CP": M - CP, "realized impetus (CP 12m chg)": CP.diff(12), "M 12m chg": M.diff(12), "FCI-G 1yr": fg}).loc["1991-01":"2026-10"]
        print("        sd: " + ", ".join(f"{c} {J[c].std():.2f}" for c in J) )
        print("        corr with FCI-G 1yr: " + ", ".join(f"{c} {J[c].corr(J['FCI-G 1yr']):.2f}" for c in J if c != "FCI-G 1yr") + f";  corr(CP, M) {J.CP.corr(J.M):.2f}; corr(forward, EP-CP) {J['forward impetus'].corr(J['EP - CP']):.2f}")
        print("        latest: " + ", ".join(f"{c} {J[c].dropna().iloc[-1]:+.2f}" for c in J))
        out[p] = J
    print(f"\ncorrelation of the 4- and 12-lag versions: CP {out[4].CP.corr(out[12].CP):.2f}, forward impetus {out[4]['forward impetus'].corr(out[12]['forward impetus']):.2f}, "
          f"realized impetus {out[4]['realized impetus (CP 12m chg)'].corr(out[12]['realized impetus (CP 12m chg)']):.2f}")


if __name__ == "__main__":
    main()
