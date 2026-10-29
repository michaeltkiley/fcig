"""
E6 (exploration, 29 Oct 2026): do NS surprises purged of pre-announcement news (Bauer and Swanson 2023 style) give conventional activity responses?
Orthogonalization: event-level regression of the NS surprise on information available before the announcement (approximating Bauer-Swanson's set):
    12-month log change in nonfarm payrolls (latest month before the meeting), 3-month log change in stock prices (CAPE price proxy, to the day before),
    3-month change in the yield-curve slope (10-year less 3-month bill), 3-month log change in WTI oil. (Not included: payroll surprise, Treasury skewness.)
The residual (ns_perp) is summed by month. Then: monthly LP responses of the unemployment gap, core inflation gap and the financial variables to ns_perp;
and, if activity responds conventionally, the multi-horizon theta (g_h = theta' psi_h) and the LP-IV with several instruments are re-estimated.
Inputs not in git: raw/PAYEMS.csv, raw/DTB3.csv, raw/DCOILWTICO.csv (FRED).
Usage: python experimental/lp_weights/lp_orthogonal.py
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lp_explore as L

P, Q, V, DL = L.P, L.Q, L.V, L.DL


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    d = d.assign(ns=ns, gss=gss)
    P.L.REAL10 = False; P.L.RSTAR = False
    X, _ = P.L.build()
    tb = V.fred_m("DTB3"); oil = V.fred_m("DCOILWTICO"); pay = V.fred_m("PAYEMS")
    slope = (X.y10 - tb.reindex(X.index).ffill())
    lo = np.log(oil.reindex(X.index).ffill())
    rows = []
    for dt in pd.to_datetime(d.Date):
        prev = X.index[X.index < dt]
        if len(prev) < 70: rows.append([np.nan] * 4); continue
        t1, t0 = prev[-1], prev[-64]
        pm = pay[pay.index < dt - pd.offsets.MonthBegin(1)]
        rows.append([100 * np.log(pm.iloc[-1] / pm.iloc[-13]), 100 * (X.lncape[t1] - X.lncape[t0]), slope[t1] - slope[t0], 100 * (lo[t1] - lo[t0])])
    R = pd.DataFrame(rows, columns=["payroll growth 12m", "stocks 3m", "slope 3m", "oil 3m"])
    ok = R.notna().all(axis=1)
    r = sm.OLS(d.ns[ok], sm.add_constant(R[ok])).fit(cov_type="HC1")
    print(f"NS on pre-announcement news ({ok.sum()} events): R2 {r.rsquared:.3f}; " + ", ".join(f"{c} {r.params[c]:+.4f} (t {r.tvalues[c]:.1f})" for c in R.columns))
    d["ns_perp"] = np.nan; d.loc[ok, "ns_perp"] = d.ns[ok] - r.fittedvalues + r.params["const"]
    d["m"] = pd.PeriodIndex(d.Date, freq="M")
    sp = d.groupby("m").ns_perp.sum().reindex(L.RNG).fillna(0.0)
    sn = d.groupby("m").ns.sum().reindex(L.RNG).fillna(0.0)
    print(f"corr(monthly ns, ns_perp) {sn.corr(sp):.3f}")
    x, _ = DL.levels_data()
    M = V.macro_data(False)
    u, pi = M["unemployment gap"], M["inflation gap"]
    hs = (0, 3, 6, 12, 18, 24)
    print("\nResponses to a 1-unit surprise (pp), monthly LP:")
    for lab, s in (("raw NS", sn), ("orthogonalized NS", sp)):
        for nm_, y in (("unemployment gap", u), ("core inflation gap", pi)):
            out = [L.lp(y, s, h) for h in hs]
            print(f"  {lab:18s} {nm_:18s} " + "  ".join(f"h={h}: {b:+.2f} ({se:.2f})" for h, (b, se) in zip(hs, out)))
    # robustness: exclude the 2008-09 crisis months from the LP sample
    keep0 = L.keep
    L.keep = lambda idx: np.array([(t.year != 2020) and not (pd.Period("2008-07", "M") <= t <= pd.Period("2009-12", "M")) for t in idx])
    out = [L.lp(u, sp, h) for h in hs]
    print("  orthogonalized NS, excluding 2008-07..2009-12: unemployment " + "  ".join(f"h={h}: {b:+.2f} ({se:.2f})" for h, (b, se) in zip(hs, out)))
    L.keep = keep0
    out = [L.lp(u, sp, h, ctrl={"u_lag": u.shift(1), "pi_lag": pi.shift(1), "ffr_lag": x["policy rate"].shift(1)}) for h in hs]
    print("  orthogonalized NS, adding lagged u, inflation and the policy rate as controls: unemployment " + "  ".join(f"h={h}: {b:+.2f} ({se:.2f})" for h, (b, se) in zip(hs, out)))
    pd.DataFrame({"ns": sn, "ns_perp": sp}).to_csv(os.path.join(HERE, "ns_orthogonal_monthly.csv"), float_format="%.6f", index_label="month")


if __name__ == "__main__":
    main()
