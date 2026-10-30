"""
Real market index, 1973-2026 (REAL_QA R9): existing NS announcement-window weights (pp of the 2-year yield per NS unit) applied to the real 10-year
(10-year - 10-year expected inflation), 100 ln CAPE and 100 ln real broad dollar from data_long_monthly.csv. Zero: 1973-2026 mean (main), 1990-2026 (check).
Usage: python experimental/real_case/market_real.py
Output: market_real_monthly.csv
"""
import os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W = pd.Series({"real 10-year": 0.6089, "equities": -0.0512, "dollar": 0.0654})


def main():
    D = pd.read_csv(os.path.join(HERE, "data_long_monthly.csv"), index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
    X = D[list(W.index)].loc["1973-01":"2026-10"]
    out = {}
    for lab, win in (("MKT_real", slice("1973-01", "2026-10")), ("MKT_real_z90", slice("1990-01", "2026-10"))):
        Xd = X - X.loc[win].mean()
        out[lab] = Xd @ W
        if lab == "MKT_real":
            for c in W.index:
                out[f"contrib {c}"] = Xd[c] * W[c]
    R = pd.DataFrame(out)
    R.to_csv(os.path.join(HERE, "market_real_monthly.csv"), float_format="%.4f", index_label="month")
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    mr = pd.read_csv(os.path.join(HERE, "macro_real_monthly.csv"), index_col=0); mr.index = pd.PeriodIndex(mr.index, freq="M")
    j = pd.concat([R.MKT_real_z90, tr.MKT], axis=1).loc["1990-01":].dropna()
    print(f"real MKT (1990 zero) vs nominal MKT, 1990-2026: corr levels {j.corr().iloc[0, 1]:.2f}, 12m {j.diff(12).corr().iloc[0, 1]:.2f}")
    k = pd.concat([R.MKT_real, mr.EP_4], axis=1).loc["1974-01":].dropna()
    print(f"real MKT vs real macro EP_4, 1974-2026: corr levels {k.corr().iloc[0, 1]:.2f}, 12m {k.diff(12).corr().iloc[0, 1]:.2f}")
    print(f"sd since 1974: MKT_real {R.MKT_real.loc['1974-01':].std():.2f}; latest {R.MKT_real.dropna().iloc[-1]:+.2f} (1990 zero {R.MKT_real_z90.dropna().iloc[-1]:+.2f})")
    sel = [pd.Period(m, "M") for m in ("1974-06", "1979-12", "1981-06", "1985-01", "1990-01", "2000-01", "2008-12", "2013-01", "2021-06", "2023-10", "2026-09")]
    print(R.loc[sel].round(2).to_string())


if __name__ == "__main__":
    main()
