"""
Real GS replication, 1973-2026 (REAL_QA R10): Goldman weights applied to data_long_monthly.csv:
    0.044 real policy rate + 0.451 real 10-year + 0.396 BBB spread - 0.049 * 100 ln CAPE + 0.060 * 100 ln real broad dollar
Zero: 1973-2026 mean (main), 1990-2026 (check). GS points (pp); "GS_real_2y" = x 0.945 / 0.98 (2-year-yield units per NS unit, nominal-case conversion; item 8 open).
Usage: python experimental/real_case/gs_real.py
Output: gs_real_monthly.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W = pd.Series({"real policy rate": 0.044, "real 10-year": 0.451, "BBB spread": 0.396, "equities": -0.049, "dollar": 0.060})


def main():
    D = pd.read_csv(os.path.join(HERE, "data_long_monthly.csv"), index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
    X = D[list(W.index)].loc["1973-01":"2026-10"]
    out = {}
    for lab, win in (("GS_real", slice("1973-01", "2026-10")), ("GS_real_z90", slice("1990-01", "2026-10"))):
        Xd = X - X.loc[win].mean()
        out[lab] = Xd @ W
        if lab == "GS_real":
            for c in W.index:
                out[f"contrib {c}"] = Xd[c] * W[c]
    R = pd.DataFrame(out)
    R.insert(1, "GS_real_2y", R.GS_real * 0.945 / 0.98)
    R.to_csv(os.path.join(HERE, "gs_real_monthly.csv"), float_format="%.4f", index_label="month")
    G = pd.read_csv(os.path.join(ROOT, "fcig_gs_daily.csv"), parse_dates=["date"]).set_index("date").fci
    g = G.groupby(G.index.to_period("M")).mean()
    j = pd.concat([R.GS_real_z90, g], axis=1).loc["1990-01":].dropna()
    print(f"real GS (1990 zero) vs nominal GS replication, 1990-2026: corr levels {j.corr().iloc[0, 1]:.2f}, 12m {j.diff(12).corr().iloc[0, 1]:.2f}")
    mk = pd.read_csv(os.path.join(HERE, "market_real_monthly.csv"), index_col=0); mk.index = pd.PeriodIndex(mk.index, freq="M")
    mr = pd.read_csv(os.path.join(HERE, "macro_real_monthly.csv"), index_col=0); mr.index = pd.PeriodIndex(mr.index, freq="M")
    for lab, s in (("real market index", mk.MKT_real), ("real FRB/US EP_4", mr.EP_4)):
        k = pd.concat([R.GS_real, s], axis=1).loc["1974-01":].dropna()
        print(f"real GS vs {lab}, 1974-2026: corr levels {k.corr().iloc[0, 1]:.2f}, 12m {k.diff(12).corr().iloc[0, 1]:.2f}")
    print(f"sd since 1974: {R.GS_real.loc['1974-01':].std():.2f} GS points; latest {R.GS_real.dropna().iloc[-1]:+.2f} (1990 zero {R.GS_real_z90.dropna().iloc[-1]:+.2f})")
    sel = [pd.Period(m, "M") for m in ("1974-06", "1979-12", "1981-06", "1985-01", "1990-01", "2000-01", "2008-12", "2013-01", "2021-06", "2023-10", "2026-09")]
    pd.set_option("display.width", 230)
    print(R.loc[sel].round(2).to_string())


if __name__ == "__main__":
    main()
