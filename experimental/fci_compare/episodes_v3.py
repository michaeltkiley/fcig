"""
Longer episode lists for the v3 comparison (follow-up to metric_v3.py; same metric, more windows).
Non-overlapping 6-month windows ranked by the mean cross-index range, 10 closest and 10 widest, for:
    A. levels, set EP_4, EP_4+HP, MKT, GS (no ANFCI), from 1993 (1990-92 treated as a special case: start-of-sample, high real rates, the dollar and
       equity valuations far from their 1990-2026 means)
    B. levels, same set, including ANFCI
    C. 12-month changes of EP_4, MKT, GS together with the FCI-G 1-year lookback level (the matched-horizon comparison)
For each widest window in A and C, the indexes at the extremes and the group split of their difference.
Usage: python experimental/fci_compare/episodes_v3.py
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import metric_v3 as MV


def windows(D, n=10, asc=True):
    rng = D.max(axis=1) - D.min(axis=1)
    roll = rng.rolling(6).mean().dropna()
    chosen = []
    for e, v in roll.sort_values(ascending=asc).items():
        if all(abs((e - c0).n) >= 6 for c0, _ in chosen): chosen.append((e, v))
        if len(chosen) == n: break
    return sorted(chosen)


def main():
    mm = MV.rd(os.path.join(MV.ROOT, "experimental", "ms_fci", "macro_model_v3_monthly.csv"))
    tr = MV.rd(os.path.join(HERE, "transmission_v3_monthly.csv"))
    f1 = pd.read_csv(os.path.join(MV.ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    rep = pd.read_csv(os.path.join(MV.ROOT, "fcig_replication_monthly.csv")); rep.index = pd.PeriodIndex(rep["month"], freq="M")
    f1 = pd.concat([f1, rep["1yr|FCI-G"].loc[f1.index[-1] + 1:]])
    S = pd.DataFrame({"EP_4": mm["EP_4"], "EP_4+HP": mm["EP_4+HP"], "MKT": tr["MKT"], "GS": tr["GS"], "ANFCI": tr["ANFCI"], "FCI-G 1yr": f1 / 0.4525}).loc["1990-01":"2026-10"]
    S = S - S.mean()
    G = MV.group_components()
    G["EP_4"] = G["EP_4+HP"].assign(other=0.0)          # EP_4 = EP_4+HP without house prices
    pd.set_option("display.width", 220)

    def report(lab, D, groups_for=None, chg=False):
        print(f"\n===== {lab}: {list(D.columns)} =====")
        rng = D.max(axis=1) - D.min(axis=1)
        print(f"range: mean {rng.mean():.2f}, median {rng.median():.2f}, 90th pct {rng.quantile(0.9):.2f}, latest {rng.iloc[-1]:.2f} ({rng.index[-1]})")
        for kind, asc in (("closest", True), ("widest", False)):
            print(f"  {kind}:")
            for e, v in windows(D, 10, asc):
                m = D.loc[e - 5:e].mean()
                line = f"    {e - 5}..{e} range {v:.2f}: " + ", ".join(f"{c} {m[c]:+.2f}" for c in D.columns)
                if groups_for and kind == "widest":
                    hi, lo = m.idxmax(), m.idxmin()
                    if hi in G and lo in G:
                        gh = (G[hi].loc[e - 5:e].mean() if not chg else (G[hi] - G[hi].shift(12)).loc[e - 5:e].mean())
                        gl = (G[lo].loc[e - 5:e].mean() if not chg else (G[lo] - G[lo].shift(12)).loc[e - 5:e].mean())
                        dif = (gh.reindex(MV.GROUPS).fillna(0) - gl.reindex(MV.GROUPS).fillna(0))
                        line += f"   | {hi} minus {lo} by group: " + ", ".join(f"{g} {dif[g]:+.2f}" for g in MV.GROUPS if abs(dif[g]) >= 0.005)
                print(line)

    report("A. levels, from 1993, without ANFCI", S[["EP_4", "EP_4+HP", "MKT", "GS"]].loc["1993-01":], groups_for=True)
    report("B. levels, from 1993, with ANFCI", S[["EP_4", "EP_4+HP", "MKT", "GS", "ANFCI"]].loc["1993-01":])
    C = pd.DataFrame({"EP_4 12m chg": S["EP_4"].diff(12), "MKT 12m chg": S["MKT"].diff(12), "GS 12m chg": S["GS"].diff(12), "FCI-G 1yr": S["FCI-G 1yr"]}).loc["1993-01":].dropna()
    report("C. 12-month changes with FCI-G (1-year lookback) level", C)


if __name__ == "__main__":
    main()
