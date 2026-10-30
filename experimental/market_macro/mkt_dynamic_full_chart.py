"""
Chart: market-index output lens, 12-lag VAR estimated through data end with 2020 dummied (mkt_dynamic_full.py; Phi from mkt_dynamic_full_phi.csv):
eventual pressure (the market index), current pressure (1-year lookback) and forward impetus (1-year lookback), pp of the 2-year yield per NS unit.
Usage: python experimental/market_macro/mkt_dynamic_full_chart.py
Output: mkt_dynamic_full_12lag.png, mkt_dynamic_full_12lag_monthly.csv
"""
import os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    Phi = pd.read_csv(os.path.join(HERE, "mkt_dynamic_full_phi.csv"), index_col=0)["12"].values
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    M = tr["MKT"]
    wcp = np.array([Phi[m] - (Phi[m - 1] if m > 0 else 0.0) for m in range(13)]) / Phi[12]
    wgi = np.array([Phi[m + 12] - Phi[m] for m in range(12)]) / Phi[12]
    CP = sum(wcp[m] * M.shift(m) for m in range(13))
    GI = sum(wgi[m] * M.diff().shift(m) for m in range(12))
    J = pd.DataFrame({"eventual pressure (market index)": M, "current pressure": CP, "forward impetus": GI}).loc["1991-01":]
    J.to_csv(os.path.join(HERE, "mkt_dynamic_full_12lag_monthly.csv"), float_format="%.4f", index_label="month")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    t = J.index.to_timestamp()
    for c, col, lw in zip(J.columns, ("#ff7f0e", "#1f5fa8", "#d62728"), (1.4, 1.4, 1.2)):
        ax.plot(t, J[c], color=col, lw=lw, label=f"{c[0].upper() + c[1:]} (latest {J[c].dropna().iloc[-1]:+.2f})")
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25)
    ax.set_ylabel("pp of 2-year yield per NS unit; tighter above zero")
    ax.set_title("Market-index output lens: VAR(12) of unemployment gap and market index, 1973-2026 with 2020 dummied", fontsize=11)
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "mkt_dynamic_full_12lag.png"), dpi=130)
    print(J.describe().loc[["std"]].round(2).to_string()); print("latest", J.iloc[-1].round(2).to_dict(), J.index[-1])


if __name__ == "__main__":
    main()
