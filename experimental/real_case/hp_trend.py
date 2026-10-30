"""
House-price-to-rent ratio, long series (Shiller real home price x CPI / CPI rent of primary residence before 1990; project ratio after, level-matched 1990-92),
from 1953, and its deviation from a trailing 15-year (180-month) average (REAL_QA R8 option under discussion).
Usage: python experimental/real_case/hp_trend.py
Outputs: hp_trend.png, hp_trend_monthly.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_long as DLG


def main():
    x, _ = DLG.DL.levels_data()
    L = DLG.long_series()["house prices"].dropna()
    p = x["house prices"].dropna()
    k = float((p.loc[DLG.OVERLAP] - L.loc[DLG.OVERLAP]).mean())
    hp = pd.concat([L.loc[:p.index[0] - 1] + k, p])
    tr = hp.rolling(180, min_periods=180).mean()
    gap = hp - tr
    J = pd.DataFrame({"ratio (100 ln, level-matched)": hp, "trailing 15-yr average": tr, "deviation from trailing 15-yr average": gap}).loc["1968-01":]
    J.to_csv(os.path.join(HERE, "hp_trend_monthly.csv"), float_format="%.3f", index_label="month")
    S = J.loc["1973-01":]
    print("from 1973: sd ratio (demeaned) {:.1f}, sd deviation {:.1f}; mean deviation {:+.1f}".format(S.iloc[:, 0].std(), S.iloc[:, 2].std(), S.iloc[:, 2].mean()))
    print(S.iloc[:, [0, 2]].loc[[pd.Period(m, "M") for m in ("1973-01", "1979-01", "1986-01", "1990-01", "1997-01", "2006-06", "2012-01", "2020-01", "2022-06", "2026-09")]].round(1).to_string())
    w = -0.0291
    print(f"contribution at the FRB/US weight ({w} pp per 1%), demeaned 1973-2026: ratio sd {abs(w) * S.iloc[:, 0].std():.2f} pp, deviation sd {abs(w) * S.iloc[:, 2].std():.2f} pp")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
    t = J.index.to_timestamp()
    axes[0].plot(t, J.iloc[:, 0], color="#8c564b", lw=1.3, label="House-price-to-rent ratio (100 ln)")
    axes[0].plot(t, J.iloc[:, 1], color="black", lw=1.1, ls="--", label="Trailing 15-year average")
    axes[0].set_title("House-price-to-rent ratio and its trailing 15-year average", fontsize=11)
    axes[1].plot(t, J.iloc[:, 2], color="#8c564b", lw=1.3, label="Deviation from trailing 15-year average (percent)")
    axes[1].axhline(0, color="gray", lw=0.8)
    axes[1].set_title("Detrended ratio", fontsize=11)
    for ax in axes:
        ax.grid(alpha=0.25); ax.legend(fontsize=9, frameon=False, loc="upper left")
        ax.axvline(pd.Timestamp("1990-01-01"), color="gray", lw=0.6, ls=":")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "hp_trend.png"), dpi=130)


if __name__ == "__main__":
    main()
