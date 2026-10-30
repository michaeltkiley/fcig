"""
One chart of the real versions in funds-rate pp: market-based index (NS-shock weights, real 10-year), GS (real funds rate, real 10-year, real dollar; NS-shock conversion 0.945 pp per point)
and the macro-model levels index with house prices (real policy rate and 10-year). Monthly (end-of-month), demeaned over 1990-2026.
Usage: python experimental/fci_compare/real_three.py        Output: real_three.png
"""
import os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    w = pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG))
    P.L.REAL10 = True; P.L.RSTAR = False
    X, G = P.L.build()
    mkt = sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in w.index) * 0.983
    gs_real = G.fci.reindex(X.index) - (0.044 + 0.451) * X.einf + 0.06 * (100 * X.lnrusd - 100 * np.log(G.x_usd.reindex(X.index)))
    gs = (gs_real - gs_real.mean()) * 0.945
    mm = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "macro_model_levels_daily_real10.csv"), parse_dates=["date"]).set_index("date")["with house prices"]
    D = pd.concat({"MKT": mkt, "GS": gs, "MACRO": mm}, axis=1).dropna()
    M = D.resample("ME").last()
    print("monthly corr of levels:\n", M.corr().round(2).to_string())
    print("12-month changes:\n", M.diff(12).corr().round(2).to_string())
    print("since 1998, levels:", M.loc["1998":].corr().round(2).values[np.triu_indices(3, 1)], "(MKT/GS, MKT/MACRO, GS/MACRO)")
    print("sd:", D.std().round(2).to_dict(), "| latest:", D.iloc[-1].round(2).to_dict())
    for lab, d0 in (("since 27 Feb 2026", "2026-02-27"), ("since 27 Aug 2026", "2026-08-27")):
        print(lab, {k: round(float(D[k].iloc[-1] - D[k].loc[:d0].iloc[-1]), 2) for k in D})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(M.index, M.MKT, color="#ff7f0e", lw=1.7, label="Market-based index (10-year, equities, dollar; NS-shock weights), real")
    ax.plot(M.index, M.GS, color="#2ca02c", lw=1.7, label="GS (real funds rate, real 10-year, real dollar), converted by the NS shock: 0.945 pp per point")
    ax.plot(M.index, M.MACRO, color="#d62728", lw=1.7, label="Macro-model levels index with house prices (FRB/US weights), real")
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
    ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
    ax.set_title("Real versions in funds-rate equivalents (monthly)", fontsize=12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "real_three.png"), dpi=130)


if __name__ == "__main__":
    main()
