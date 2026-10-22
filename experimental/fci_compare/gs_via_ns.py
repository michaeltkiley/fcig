"""
EXPERIMENTAL: convert the GS replication to funds-rate units using the Nakamura-Steinsson policy news shock (base lens), as an alternative to the monthly parallel-surprise conversion in common_unit.py.

Step 1  NS factor (path_fci_gss_ns.gss_ns): first PC of MP1, MP2, ED2, ED3, ED4, scaled so 1 unit = 1 pp on the 2-year yield (USMPD events, same sample rules as path_fci).
Step 2  Funds-rate content of one NS unit: regress MP1 (today's rate) and ED4 (year-ahead rate) on the factor; the NS unit is a tilted level shock (MP1 moves less than ED4).
        Funds-rate pp per NS unit = the average of the two slopes (alternatives: ED4 slope alone; MP1 slope alone), so a "parallel-equivalent" 1 pp funds-rate move.
Step 3  Index response per NS unit: regress each index's event-day change (close of t-1 to t; and t-1 to t+1, because the dollar input of the GS replication is a noon series) on the factor.
Step 4  Funds-rate pp per index point = (funds-rate pp per NS unit) / (index response per NS unit).
Applied to GS (daily replication), the MS-style FRB/US index (as a check: native funds-rate units) and the market-based index with NS weights.
Usage: python experimental/fci_compare/gs_via_ns.py
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import path_fci as P
import path_fci_gss_ns as Q


def main():
    ev = P.events(P.USMPD)
    P.L.REAL10 = False; P.L.RSTAR = False
    X, G = P.L.build()
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    d = d[d.Date.isin(X.index)].reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    d = d.assign(ns=ns)
    Z = sm.add_constant(d.ns)
    m = {c: sm.OLS(d[c], Z).fit(cov_type="HC1") for c in ("MP1", "ED4", "UST2Y", "ED1", "ED2")}
    print(f"{len(d)} events. Moves per 1 NS unit (1 pp on the 2-year): " + ", ".join(f"{c} {r.params['ns']:+.3f} ({r.bse['ns']:.3f})" for c, r in m.items()))
    m1, m4 = m["MP1"].params["ns"], m["ED4"].params["ns"]
    fr = {"average of MP1 and ED4": (m1 + m4) / 2, "ED4 alone": m4, "MP1 alone": m1}
    print("funds-rate pp per NS unit:", {k: round(v, 3) for k, v in fr.items()})
    # index series
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    w = pd.Series(Q.estimate(d, ns, True)[0], index=list(Q.ENDOG))        # market-based index with NS weights (units: NS unit)
    mkt = sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in w.index)
    series = {"GS (index points)": G.fci.reindex(X.index), "MS-FRB (pp funds rate)": ms, "MKT-NS (NS units)": mkt}
    pos = X.index.get_indexer(d.Date)
    res = {}
    for name, s in series.items():
        for lab, k in (("t-1 to t", 0), ("t-1 to t+1", 1)):
            y = s.values[np.minimum(pos + k, len(s) - 1)] - s.values[pos - 1]
            r = sm.OLS(y, Z).fit(cov_type="HC1")
            res[(name, lab)] = (r.params["ns"], r.bse["ns"], r.rsquared)
    print("\nResponse of each index to 1 NS unit (se; R2):")
    for (name, lab), (b, se, r2) in res.items():
        print(f"  {name:24s} {lab:11s} {b:+.3f} ({se:.3f}); R2 {r2:.2f}")
    print("\nGS conversion: funds-rate pp per GS index point = (pp per NS unit) / (GS response per NS unit)")
    for lab in ("t-1 to t", "t-1 to t+1"):
        b, se, _ = res[("GS (index points)", lab)]
        print(f"  {lab}: response {b:.3f} (se {se:.3f}) -> " + ", ".join(f"{k}: {v / b:.2f}" for k, v in fr.items()) + f"   [se on the average-case ratio about {abs(fr['average of MP1 and ED4']) * se / b ** 2:.2f}]")
    print("  compare: monthly parallel-surprise conversion 1.27 (common_unit.py); Goldman 2015 rule of thumb 0.69 (secondhand)")
    # MS-FRB and MKT-NS under the same conversion, for a consistency check
    for name, unit_scale in (("MS-FRB (pp funds rate)", None), ("MKT-NS (NS units)", None)):
        for lab in ("t-1 to t", "t-1 to t+1"):
            b, se, _ = res[(name, lab)]
            print(f"  check {name} {lab}: response {b:+.3f} per NS unit -> implied funds-rate pp per own unit {fr['average of MP1 and ED4'] / b:.2f}"
                  + ("  (native 1.00 expected for MS-FRB if the model weights agree with markets)" if name.startswith("MS") else "  (MKT-NS is in NS units, so 1.00 NS unit = 1 by construction; funds-rate pp = average slope)"))
    # level series in funds-rate pp, GS with the NS conversion
    k = fr["average of MP1 and ED4"] / res[("GS (index points)", "t-1 to t+1")][0]       # two-day window (the GS dollar input is a noon series)
    gsm = (G.fci - G.fci.mean()) * k
    ms_m = ms - ms.mean(); mkt_f = (mkt - mkt.mean()) * fr["average of MP1 and ED4"]
    out = pd.DataFrame({"GS via NS": gsm, "MS-FRB": ms_m, "MKT via NS": mkt_f}).dropna()
    mo = out.resample("ME").last()
    print(f"\nLevels in funds-rate pp (daily, 1990-2026): sd {out.std().round(2).to_dict()}; latest {out.iloc[-1].round(2).to_dict()}")
    print("monthly corr of levels:\n", mo.corr().round(2).to_string())
    print(f"GS conversion used for the chart: {k:.2f} funds-rate pp per index point (two-day window, average of MP1 and ED4)")
    print("daily-change correlation:", round(float(out['GS via NS'].diff().corr(out['MKT via NS'].diff())), 2), "; latest:", out.iloc[-1].round(2).to_dict())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.plot(out.index, out["GS via NS"], color="#2ca02c", lw=1.5, label=f"GS FCI (replication), converted by the NS shock: {k:.2f} pp of funds rate per index point")
    ax.plot(out.index, out["MKT via NS"], color="#ff7f0e", lw=1.5, label="Market-based index (10-year, equities, dollar; NS-shock weights), in funds-rate pp")
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
    ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
    ax.set_title(f"GS and the market-based index in funds-rate equivalents via the Nakamura-Steinsson shock (monthly corr of levels {mo.corr().loc['GS via NS', 'MKT via NS']:.2f})", fontsize=11)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "gs_mkt_via_ns.png"), dpi=130)


if __name__ == "__main__":
    main()
