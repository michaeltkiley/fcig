"""
r* adjustment done directly in funds-rate units: take each real-rate index (funds-rate pp, demeaned; rstar_sets_daily.csv, "none (real rates)") and subtract the demeaned one-sided r*
(weight 1 on r*: one pp more neutral rate is one pp easier policy), for Kiley and Laubach-Williams r*. The earlier version (rstar_sets.py) instead subtracted r* from the policy rate and the
10-year inside the index, so r* entered with the weights on those rates (macro 0.58, market 0.60, GS 0.47 funds-rate pp per pp). Compare the two methods here.
Usage: python experimental/fci_compare/rstar_direct.py     Outputs: rstar_direct_daily.csv, rstar_direct_{macro,market,gs}.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rstar_sets as S


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    D = pd.read_csv(os.path.join(HERE, "rstar_sets_daily.csv"), parse_dates=["date"]).set_index("date")
    Rq = pd.read_csv(os.path.join(HERE, "rstar_series.csv"), index_col=0); Rq.index = pd.PeriodIndex(Rq.index, freq="Q")
    cols = {"Kiley": "Kiley_onesided", "Laubach-Williams": "LW_onesided"}
    r = {k: S.daily_rstar(Rq[c], D.index) for k, c in cols.items()}
    r = {k: v - v.mean() for k, v in r.items()}
    out = {}
    for fam in ("macro", "market", "GS"):
        base = D[f"{fam} | none (real rates)"]
        for k in cols:
            out[(fam, k, "direct")] = base - r[k]
            out[(fam, k, "in rates")] = D[f"{fam} | {k}"]
        out[(fam, "none", "base")] = base
    O = pd.concat(out, axis=1); O.columns = [" | ".join(c) for c in O.columns]
    O.to_csv(os.path.join(HERE, "rstar_direct_daily.csv"), float_format="%.4f", index_label="date")
    M = O.resample("ME").last()
    colr = {"Kiley": "#1f5fa8", "Laubach-Williams": "#2ca02c"}
    title = {"macro": "Macro-model levels index (FRB/US weights, with house prices)", "market": "Market-based index (NS-shock weights)", "GS": "GS (replication; NS-shock conversion)"}
    print("sd of demeaned r* (daily, 1990-2026):", {k: round(float(v.std()), 2) for k, v in r.items()}, "| latest demeaned r*:", {k: round(float(v.iloc[-1]), 2) for k, v in r.items()})
    for fam in ("macro", "market", "GS"):
        fig, ax = plt.subplots(figsize=(13, 6.5))
        for k in cols:
            ax.plot(M.index, M[f"{fam} | {k} | direct"], color=colr[k], lw=1.8, label=f"real index less demeaned {k} r* (one-sided)")
        ax.plot(M.index, M[f"{fam} | none | base"], color="black", lw=1.0, ls="--", label="real index, no r* adjustment")
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
        ax.set_title(f"{title[fam]}: r* subtracted directly from the real index", fontsize=11)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"rstar_direct_{fam.lower()}.png"), dpi=130); plt.close(fig)
        b = O[f"{fam} | none | base"]
        print(f"\n{fam}: sd of level: none {b.std():.2f}; " + "; ".join(f"{k}: direct {O[f'{fam} | {k} | direct'].std():.2f} / in rates {O[f'{fam} | {k} | in rates'].std():.2f}" for k in cols))
        print("   latest: none %+.2f; " % b.iloc[-1] + "; ".join(f"{k}: direct {O[f'{fam} | {k} | direct'].iloc[-1]:+.2f} / in rates {O[f'{fam} | {k} | in rates'].iloc[-1]:+.2f}" for k in cols))
        for lab, d0 in (("since 27 Feb 2026", "2026-02-27"), ("since 27 Aug 2026", "2026-08-27")):
            ch = lambda s: float(s.iloc[-1] - s.loc[:d0].iloc[-1])
            print(f"   change {lab}: none {ch(b):+.2f}; " + "; ".join(f"{k}: direct {ch(O[f'{fam} | {k} | direct']):+.2f} / in rates {ch(O[f'{fam} | {k} | in rates']):+.2f}" for k in cols))
        for k in cols:
            a, c = M[f"{fam} | {k} | direct"], M[f"{fam} | {k} | in rates"]
            print(f"   {k}: direct vs in-rates method: level corr {a.corr(c):.2f}, 12m-change corr {a.diff(12).corr(c.diff(12)):.2f}, mean abs diff {(a - c).abs().mean():.2f} pp, max {(a - c).abs().max():.2f}; direct vs no r*: corr {a.corr(M[f'{fam} | none | base']):.2f}")
        a, c = M[f"{fam} | Kiley | direct"], M[f"{fam} | Laubach-Williams | direct"]
        print(f"   Kiley vs LW (direct): level corr {a.corr(c):.2f}, 12m-change corr {a.diff(12).corr(c.diff(12)):.2f}, mean abs gap {(a - c).abs().mean():.2f} pp, max {(a - c).abs().max():.2f}")


if __name__ == "__main__":
    main()
