"""
EXPERIMENTAL add-on to path_fci.py (unchanged): reverse (multivariate) regression of the path surprise on the event-day changes of the variables,
    path_e = a + sum_j w_j dx_j,e + e_e ,
so the coefficients are the weights directly (pp of path surprise per unit of x_j) and sum_j w_j (x_j - mean) is the best linear predictor of the surprise.
Compared with the forward-regression (GLS) weights of path_fci.py. Also an intraday version using only the variables USMPD has in its window
(10-year, S&P 500, dollar index; no BBB or oil) where non-FOMC news is much smaller.

Usage:  python experimental/path_fci/path_fci_reverse.py [--sample full|nonzlb]
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
SETS = {"MS": ["10-yr", "BBB spread", "Equities (ln CAPE)", "Dollar (ln real)", "Oil (ln real)"],
        "GS": ["Fed funds", "10-yr", "BBB spread", "Equities (ln CAPE)", "Dollar (ln real)"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    X, G = P.L.build()
    ev = ev[ev.Date.isin(X.index)].reset_index(drop=True)
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    dx = P.event_changes(X, ev)
    B = P.fit(dx, ev)
    out = {}
    print(f"sample {a.sample}, {len(ev)} events. Weights: pp of path surprise per unit of x (reverse regression, HC1 se); GLS = forward-regression weights of path_fci.py")
    for sname, names in SETS.items():
        for ctl in (False, True):
            Z = dx[names] if not ctl else pd.concat([dx[names], ev[["target"]]], axis=1)
            r = sm.OLS(ev.path, sm.add_constant(Z)).fit(cov_type="HC1")
            t = pd.DataFrame({"reverse": r.params[names], "se": r.bse[names], "t": r.tvalues[names]})
            if not ctl:
                t["GLS (forward)"] = P.weights(B, names)
            print(f"\n[{sname}] reverse{' + target control' if ctl else ''}: R2 {r.rsquared:.3f}")
            print(t.round(3).to_string())
            if not ctl:
                out[sname] = r.params[names]
                print("  sum w*b (forward betas) =", round(float((r.params[names] * B.loc[names, "b"].astype(float)).sum()), 3), "(1 for GLS by construction)")
    # intraday version
    cols = {"10-yr": "UST10Y", "Equities": "SP500", "Dollar": "DXY"}
    e2 = ev.dropna(subset=list(cols.values()))
    r = sm.OLS(e2.path, sm.add_constant(e2[list(cols.values())])).fit(cov_type="HC1")
    print(f"\n[intraday window, {len(e2)} events] path on UST10Y (pp), SP500 (%), DXY (%): R2 {r.rsquared:.3f}")
    print(pd.DataFrame({"w": r.params[list(cols.values())], "se": r.bse[list(cols.values())]}).round(4).to_string())
    # index levels
    D = {}
    for sname, names in SETS.items():
        w = out[sname]
        D[f"{sname} set, reverse weights"] = sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
        wg = P.weights(B, names)
        D[f"{sname} set, GLS weights"] = sum(wg[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
    D = pd.DataFrame(D); D["GS FCI"] = G.fci.reindex(X.index)
    print("\nCorrelation of daily changes, 1990-2026:\n", D.diff().corr().round(2).to_string())
    print("Correlation of levels, 1990-2026:\n", D.corr().round(2).to_string())
    print("latest:", D.iloc[-1].round(2).to_dict(), "\nsd of daily change:", D.diff().std().round(3).to_dict())


if __name__ == "__main__":
    main()
