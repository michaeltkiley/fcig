"""
Chart: eventual pressure (market index), current pressure (12-lag VAR, through data end with 2020 dummied; mkt_dynamic_full_12lag_monthly.csv) and the GS
replication (transmission_v3: x 0.945/0.98), all in pp of the 2-year yield per NS unit, 1991-2026.
Usage: python experimental/market_macro/mkt_cp_gs_chart.py
Output: mkt_cp_gs.png
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    J = pd.read_csv(os.path.join(HERE, "mkt_dynamic_full_12lag_monthly.csv"), index_col=0); J.index = pd.PeriodIndex(J.index, freq="M")
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    S = pd.DataFrame({"Eventual pressure (market index)": J.iloc[:, 0], "Current pressure (12-lag VAR)": J.iloc[:, 1], "GS (replication)": tr["GS"]}).loc["1991-01":]
    for c in S:
        print(f"{c}: corr with GS levels {S[c].corr(S['GS (replication)']):.2f}, 12m changes {S[c].diff(12).corr(S['GS (replication)'].diff(12)):.2f}; latest {S[c].dropna().iloc[-1]:+.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    t = S.index.to_timestamp()
    for c, col in zip(S.columns, ("#ff7f0e", "#1f5fa8", "#2ca02c")):
        ax.plot(t, S[c], color=col, lw=1.4, label=f"{c} (latest {S[c].dropna().iloc[-1]:+.2f})")
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25)
    ax.set_ylabel("pp of 2-year yield per NS unit; tighter above zero")
    ax.set_title("Eventual and current pressure (market-index lens) with the GS index", fontsize=11)
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "mkt_cp_gs.png"), dpi=130)


if __name__ == "__main__":
    main()
