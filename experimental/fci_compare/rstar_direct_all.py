"""
Direct r* adjustment (real index less demeaned one-sided r*, in funds-rate pp) with four r* series: Kiley, Laubach-Williams current one-sided, Laubach-Williams real-time (spliced, see
rstar_ny_fed_extract.py: backfilled before 2005 and in 2020Q3-2022Q3) and Holston-Laubach-Williams one-sided. Macro-model (with house prices), market-based (NS) and GS real indexes from
rstar_sets_daily.csv ("none (real rates)"). r* stamped mid-quarter, interpolated daily, held at its last value after 2026Q2; demeaned over the index sample.
Usage: python experimental/fci_compare/rstar_direct_all.py     Outputs: rstar_all_{series,macro,market,gs}.png, rstar_all_daily.csv
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rstar_sets as S

SERIES = {"Kiley": ("rstar_series.csv", "Kiley_onesided"), "LW current": ("rstar_series_ny_fed.csv", "LW_current_onesided"),
          "LW real-time": ("rstar_series_ny_fed.csv", "LW_realtime_spliced"), "HLW": ("rstar_series_ny_fed.csv", "HLW_current_onesided")}
COL = {"Kiley": "#1f5fa8", "LW current": "#2ca02c", "LW real-time": "#ff7f0e", "HLW": "#9467bd"}
TITLE = {"macro": "Macro-model levels index (FRB/US weights, with house prices)", "market": "Market-based index (NS-shock weights)", "GS": "GS (replication; NS-shock conversion)"}


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    D = pd.read_csv(os.path.join(HERE, "rstar_sets_daily.csv"), parse_dates=["date"]).set_index("date")
    q = {}
    for k, (f, c) in SERIES.items():
        t = pd.read_csv(os.path.join(HERE, f), index_col=0); t.index = pd.PeriodIndex(t.index, freq="Q"); q[k] = t[c].astype(float)
    r = {k: S.daily_rstar(v, D.index) for k, v in q.items()}
    rd = {k: v - v.mean() for k, v in r.items()}
    print("r* (quarterly, 1990-2026): mean / sd / min / max / latest")
    for k in SERIES:
        s = q[k].loc["1990Q1":].dropna(); print(f"  {k:13s} {s.mean():5.2f} {s.std():5.2f} {s.min():6.2f} {s.max():5.2f}  latest {s.iloc[-1]:.2f}")
    print("  correlations (1990-2026):\n" + pd.DataFrame(q).loc["1990Q1":].corr().round(2).to_string().replace("\n", "\n  "))
    fig, ax = plt.subplots(figsize=(13, 6.5))
    for k in SERIES:
        s = q[k].loc["1990Q1":]; ax.plot(s.index.to_timestamp(), s, color=COL[k], lw=1.7, label=k)
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(fontsize=10); ax.set_title("One-sided r* estimates (%): Kiley and three NY Fed versions", fontsize=12)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "rstar_all_series.png"), dpi=130); plt.close(fig)
    out = {}
    for fam in ("macro", "market", "GS"):
        base = D[f"{fam} | none (real rates)"]
        out[(fam, "none")] = base
        for k in SERIES: out[(fam, k)] = base - rd[k]
    O = pd.concat(out, axis=1); O.columns = [f"{a} | {b}" for a, b in O.columns]
    O.to_csv(os.path.join(HERE, "rstar_all_daily.csv"), float_format="%.4f", index_label="date")
    M = O.resample("ME").last()
    for fam in ("macro", "market", "GS"):
        fig, ax = plt.subplots(figsize=(13, 6.5))
        for k in SERIES: ax.plot(M.index, M[f"{fam} | {k}"], color=COL[k], lw=1.6, label=f"real index less demeaned r*: {k}")
        ax.plot(M.index, M[f"{fam} | none"], color="black", lw=1.0, ls="--", label="real index, no r* adjustment")
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11); ax.set_title(f"{TITLE[fam]}: r* subtracted directly", fontsize=11)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=9, frameon=False)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"rstar_all_{fam.lower()}.png"), dpi=130); plt.close(fig)
        names = ["none"] + list(SERIES)
        print(f"\n=== {fam} ===")
        print("  latest:", {n: round(float(O[f'{fam} | {n}'].iloc[-1]), 2) for n in names})
        print("  sd of level:", {n: round(float(O[f'{fam} | {n}'].std()), 2) for n in names})
        for lab, d0 in (("since 27 Feb 2026", "2026-02-27"), ("since 27 Aug 2026", "2026-08-27")):
            print(f"  change {lab}:", {n: round(float(O[f'{fam} | {n}'].iloc[-1] - O[f'{fam} | {n}'].loc[:d0].iloc[-1]), 2) for n in names})
        sub = M[[f"{fam} | {n}" for n in SERIES]]; sub.columns = list(SERIES)
        print("  monthly corr of levels:\n  " + sub.corr().round(2).to_string().replace("\n", "\n  "))
        print("  12-month changes:\n  " + sub.diff(12).corr().round(2).to_string().replace("\n", "\n  "))
        print("  mean abs gap (pp) to Kiley:", {k: round(float((sub[k] - sub['Kiley']).abs().mean()), 2) for k in SERIES if k != 'Kiley'}, "| range across the four: mean %.2f, max %.2f" % ((sub.max(axis=1) - sub.min(axis=1)).mean(), (sub.max(axis=1) - sub.min(axis=1)).max()))
        print("  since 2005 (monthly corr of levels):\n  " + sub.loc["2005":].corr().round(2).to_string().replace("\n", "\n  "))


if __name__ == "__main__":
    main()
