"""Step 4d. Nakamura-Steinsson (2018) policy news shock: rebuild it from their replication package (Harvard Dataverse doi:10.7910/DVN/HZOXKN, master.dta, saved as data/ns_master.dta)
and compare with this project's USMPD-based factor (fci_note/replication/fci/indexes.py: ns_factor).
Their construction (Programs/OLS.do, lines 98-104): first principal component of five 30-minute surprises (dffr1, dffr2, ded2, ded3, ded4) on FOMCused days (regular meetings; unscheduled and
conference calls are not in FOMCused except as flagged), rescaled so that the one-year nominal yield change (DNY1) regressed on it has slope 1. Ours: same five, scaled to the 2-year yield (UST2Y).
Output: 04d_ns_check.log"""
import numpy as np, pandas as pd, warnings
import statsmodels.api as sm
from mpcommon import *
warnings.filterwarnings("ignore")
m = pd.read_stata(HERE / "data/ns_master.dta"); f = m[m.FOMCused == 1].copy()
cols = ["dffr1_tick_wide_scaled", "dffr2_tick_wide_scaled", "ded2_tick_wide", "ded3_tick_wide", "ded4_tick_wide"]
g = f.dropna(subset=cols + ["DNY1"]).copy()
Xc = g[cols].values - g[cols].values.mean(0); U, S, Vt = np.linalg.svd(Xc, full_matrices=False); pc = U[:, 0] * S[0]
if pc @ g.ded4_tick_wide.values < 0: pc = -pc
b = sm.OLS(g.DNY1.values, sm.add_constant(pc)).fit().params[1]
g["ns_theirs"] = pc * b                                                                                      # DNY1 = a + b*pc  =>  (b*pc) has unit slope on DNY1
chk = sm.OLS(g.DNY1.values, sm.add_constant(g.ns_theirs.values)).fit().params[1]
two = sm.OLS(g.DNY2.dropna().values, sm.add_constant(g.loc[g.DNY2.notna(), "ns_theirs"].values)).fit().params[1]
print(f"Their shock rebuilt: {len(g)} regular-meeting days {g.date_daily.min().date()} to {g.date_daily.max().date()}; check: slope of 1-year yield change on it = {chk:.2f}; 2-year = {two:.2f} (NS Table I: 1.10)")
ev = events(); ev["d"] = ev.Date.dt.normalize(); g["d"] = pd.to_datetime(g.date_daily).dt.normalize()
j = ev.merge(g[["d", "ns_theirs", "unscheduled"]], on="d")
print(f"Common event dates {len(j)} of ours {len(ev)} (ours include {int((ev.Unscheduled == 1).sum())} unscheduled meetings with MP1 != 0, which NS's baseline excludes)")
print(f"Correlation of our NS (2-year scale) with theirs: {j.ns.corr(j.ns_theirs):.3f}; scheduled meetings only {j[j.Unscheduled == 0].ns.corr(j[j.Unscheduled == 0].ns_theirs):.3f}; ratio of scales (ours / theirs) {np.polyfit(j.ns_theirs, j.ns, 1)[0]:.2f}")
g["m"] = g.d.dt.to_period("M"); th = g.groupby("m").ns_theirs.sum().reindex(M.index).fillna(0.0)
evs = ev[ev.Unscheduled == 0].copy(); evs["ns"] = I.ns_factor(evs); evs["m"] = evs.Date.dt.to_period("M"); our_sched = evs.groupby("m").ns.sum().reindex(M.index).fillna(0.0)
Z = monthly_instruments(ev)
print("\nFirst-stage F for the 2-year residual, robust [homoskedastic]; 4-variable system (u gap, core PCE, 2-year, r*-gap index), 12 lags, VAR 1994-2026, residual window as stated")
r, e0 = var_resid(["u_gap", "pi_core", "gs2", "market_rstar"], "1994-01", "2026-09", rstart="1994-01")
for lab, a, b_ in (("1995-01..2014-04 (span of their shock)", "1995-01", "2014-04"), ("2015-01..2026-09 (after their shock ends)", "2015-01", "2026-09"), ("1994-01..2026-09", "1994-01", "2026-09")):
    e = e0.loc[a:b_]; row = []
    for nm, z in (("ours, all events", Z["ns"]), ("ours, scheduled only", our_sched), ("theirs", th)):
        if nm == "theirs" and a != "1995-01": row.append(f"{nm}: n/a"); continue
        x, h, _ = first_stage(e["gs2"], z.reindex(e.index)); row.append(f"{nm}: {x:4.1f} [{h:4.1f}]")
    print(f"   {lab:44s} n={len(e):3d}   " + "   ".join(row))
