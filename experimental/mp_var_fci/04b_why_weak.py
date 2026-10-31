"""Step 4b. Why might others report usable instruments from similar data? Variants of the first stage (VAR residual of the policy variable on the monthly instrument).
Policy variable: 2-year yield (main) unless stated. Reports robust F (HC1) and, in brackets, homoskedastic F. Output: 04b_why_weak.log"""
import numpy as np, pandas as pd
import statsmodels.api as sm
from mpcommon import *

ev = events(); Z = monthly_instruments(ev)
gs1 = fred("GS1"); M["gs1"] = gs1.groupby(gs1.index.to_period("M")).mean().reindex(M.index)
print("Events:", len(ev), "(FF4 missing for", int(ev.FF4.isna().sum()), "events, set to 0). Monthly instrument sd (pp):", "  ".join(f"{k} {Z[k].std():.3f}" for k in ("ns", "MP1", "ED4", "FF4")))
fmt = lambda t: f"{t[0]:5.1f} [{t[1]:5.1f}]"

print("\n(1) Same data, different level of aggregation. 2-year window change on the NS surprise at the EVENT level (253 events), and monthly average 2-year change on the monthly sum:")
r = sm.OLS(ev.UST2Y.values, sm.add_constant(ev.ns.values)).fit(cov_type="HC1")
print(f"   event-day regression: coefficient {r.params[1]:+.2f}, t {r.tvalues[1]:.1f}, F {r.tvalues[1] ** 2:.0f}   (strong by construction: NS is built from yield surprises in the same window)")
d = M.gs2.diff().loc["1994-01":]; rr = Z.ns.loc["1994-01":].corr(d); print(f"   monthly change of the 2-year on the monthly NS sum: r {rr:+.2f}, F {rr * rr * (len(d) - 3) / (1 - rr * rr):.0f}")
print("   VAR-residual first stage (what proxy-SVARs need): see (2).")

print("\n(2) VAR-residual first stage by instrument and window (4-variable VAR with r*-gap index, 12 lags). robust F [homoskedastic F]")
print("   window (VAR and residuals)        policy |   ns            MP1            ED4            FF4")
for a, b in (("1994-01", "2007-12"), ("1994-01", "2012-12"), ("1994-01", "2019-12"), ("1994-01", "2026-09")):
    for pv in ("gs2", "ffr"):
        r, e = var_resid(["u_gap", "pi_core", pv, "market_rstar"], a, b, rstart=a)
        print(f"   {a}..{b}  {pv:5s} |  " + "  ".join(fmt(first_stage(e[pv], Z[k])) for k in ("ns", "MP1", "ED4", "FF4")))

print("\n(3) Lag length of the VAR (window 1994-2026, 2-year): robust F [homoskedastic F]")
for p in (2, 6, 12):
    r, e = var_resid(["u_gap", "pi_core", "gs2", "market_rstar"], "1994-01", lags=p)
    print(f"   {p:2d} lags |  " + "  ".join(f"{k} {fmt(first_stage(e['gs2'], Z[k]))}" for k in ("ns", "ED4", "FF4")))

print("\n(4) Policy variable: 1-year (as Gertler-Karadi) vs 2-year vs funds rate, window 1994-2026, 12 lags: robust F [homoskedastic F]")
for pv in ("gs1", "gs2", "ffr"):
    r, e = var_resid(["u_gap", "pi_core", pv, "market_rstar"], "1994-01")
    print(f"   {pv:4s} |  " + "  ".join(f"{k} {fmt(first_stage(e[pv], Z[k]))}" for k in ("ns", "MP1", "ED4", "FF4")))

print("\n(5) Timing: surprise assigned to the event month (simple) vs split between the event month and the next in proportion to the days left (suited to monthly averages), 2-year, 1994-2026")
r, e = var_resid(["u_gap", "pi_core", "gs2", "market_rstar"], "1994-01")
for k in ("ns", "ED4", "FF4", "MP1"):
    print(f"   {k:4s} simple {fmt(first_stage(e['gs2'], Z[k]))}    timing-adjusted {fmt(first_stage(e['gs2'], Z[k + '_adj']))}")

print("\n(6) Smaller systems (12 lags), 2-year, 1994-2026: does the VAR size matter? robust F [homoskedastic F]")
for cols in (["u_gap", "gs2"], ["u_gap", "pi_core", "gs2"], ["u_gap", "pi_core", "gs2", "market_rstar"]):
    r, e = var_resid(cols, "1994-01")
    print(f"   {'+'.join(cols):34s} " + "  ".join(f"{k} {fmt(first_stage(e['gs2'], Z[k]))}" for k in ("ns", "ED4", "FF4")))
