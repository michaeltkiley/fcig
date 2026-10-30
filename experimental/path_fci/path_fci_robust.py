"""
Robustness check on path_fci.py (which is unchanged): the same event-day regressions estimated by OLS, LAD (median regression) and Huber M-estimation,
and the resulting one-factor weights. Same events, variables and controls as path_fci.py; scale for the GLS weights uses each estimator's residual
variance (OLS and Huber: variance; LAD: variance of the residuals too, so the weights are comparable).

Usage:  python experimental/path_fci/path_fci_robust.py [--sample full|nonzlb]
"""
import os, sys, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE = P.HERE


def est(y, Z, how):
    ok = y.notna()
    y, Z = y[ok], Z[ok]
    if how == "OLS":
        r = sm.OLS(y, Z).fit(cov_type="HC1")
    elif how == "LAD":
        r = sm.QuantReg(y, Z).fit(q=0.5, max_iter=5000)
    else:
        r = sm.RLM(y, Z, M=sm.robust.norms.HuberT()).fit()
    res = y - Z.values @ r.params.values
    return r.params["path"], r.bse["path"], res.var(ddof=3)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    X, G = P.L.build()
    ev = ev[ev.Date.isin(X.index)].reset_index(drop=True)
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    dx = P.event_changes(X, ev)
    Z = sm.add_constant(ev[["path", "target"]])
    tab = {}
    for how in ("OLS", "LAD", "Huber"):
        rows = {n: est(dx[n], Z, how) for n in dx}
        tab[how] = pd.DataFrame(rows, index=["b", "se", "s2"]).T
    print(f"{len(ev)} events, sample {a.sample}. Response b to a +1 pp path surprise (se):")
    show = pd.DataFrame({h: tab[h].b.round(3).astype(str) + " (" + tab[h].se.round(3).astype(str) + ")" for h in tab})
    print(show.to_string())
    print("\nWeights (pp of path-rate per unit of x), one-factor GLS:")
    for sname, names in P.SETS.items():
        W = pd.DataFrame({h: P.weights(tab[h], names) for h in tab})
        print(f"[{sname}]"); print(W.round(3).to_string())
    # outliers: largest standardized residuals under OLS for BBB and equities
    for n in ("BBB spread", "Equities (ln CAPE)", "10-yr"):
        y = dx[n]; r = sm.OLS(y, Z).fit(); z = (r.resid / r.resid.std()).abs().sort_values(ascending=False).head(4)
        print(f"largest OLS residuals, {n}: " + ", ".join(f"{ev.Date[i].date()} ({r.resid[i]:+.2f})" for i in z.index))
    # kurtosis
    print("excess kurtosis of residuals:", {n: round(float(sm.OLS(dx[n], Z).fit().resid.kurt()), 1) for n in dx})
    pd.concat({h: tab[h] for h in tab}, axis=1).round(5).to_csv(os.path.join(HERE, f"path_fci_robust_{a.sample}.csv"), index_label="variable")


if __name__ == "__main__":
    main()
