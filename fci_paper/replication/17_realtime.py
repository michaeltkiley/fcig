"""Step 17. Pseudo real time: do the stance and flow results survive vintage data? Market index only (weights unchanged), unemployment-gap and payroll outcomes
(core PCE descriptive, kept in the CSV, not in the paper table).
Versions on identical origins: rev = revised data; rt1 = vintage unemployment, payrolls, core PCE (information = vintage 2 months after the origin, outcomes as first reported
in the vintage 14 months after it; ex-post NROU); rt2 = rt1 plus the CBO natural rate as published (vintages from March 2011). Real-time r*: final point of each New York Fed
Laubach-Williams vintage (2005 on; none Sep 2020-Apr 2023). Inputs are tidy CSVs in data/realtime/ (SOURCES.md); no network access.
Blocks: A long sample 1976-2025 (HAC 18 lags, recursive out-of-sample from 1995, rev vs rt1, three steps x three forms x du, pay); B real-time r* (common origins 2006-2025, HAC 12,
in sample); C vintage NROU (2011-2025, du, in sample); D core PCE (2002-2025, in sample). Level-versus-flow regressions (A2) and revision statistics.
PRE-SPECIFIED: 135 specifications in all, descriptive; primary family = the six Clark-West tests (du and pay x level, flow, mixed; Market, r* step; recursive out-of-sample),
Holm-adjusted within each version. Blocks B-D have no out-of-sample test. No bootstrap; deterministic (REPS and SEED not used).
Writes results/17_realtime_{stance,levelflow,table,revisions,primary_holm,availability}.csv and scalars_17_realtime.csv."""
import numpy as np, pandas as pd
from scipy import stats
from lib import data as RD
from lib import realtime_core as R
from lib.config import RES, DATA
from lib.report import Scalars

S = Scalars("17_realtime")
P = R.panel(); V = R.versions(P); ix_rt, gap = R.rt_index_rstar(); rs_rt = R.rstar_rt()
S.add("rt_index_check_maxdiff", gap)

def design(v, yn, f, x, form): return R.design(*V[v], yn, f, x, form)
def pair(yn, step, form, vers, lo=None, rstar=None, ix=None, common=None):
    """designs for each version on identical origins (common, or the intersection), standardised on that sample."""
    f = R.ffg(step, rstar); x = R.index(step) if ix is None else ix
    Ds = {v: design(v, yn, f, x, form) for v in vers}
    if common is None:
        common = None
        for D in Ds.values(): common = D.index if common is None else common.intersection(D.index)
        if lo: common = common[common >= pd.Period(lo, "M")]
    return {v: R.stand(D.loc[common]) for v, D in Ds.items()}

rows = []
def add(block, outcome, step, form, version, basis, D, lags, oos):
    rows.append(dict(block=block, outcome=outcome, step=step, basis=basis, form=form, version=version, **R.hacstats(D, R.own(V[version][1], outcome), lags, oos)))

# A: long sample
for yn in ("du", "pay"):
    for step in ("nominal", "real", "rstar"):
        for form in ("level", "flow", "mixed"):
            for v, D in pair(yn, step, form, ("rev", "rt1")).items(): add("A", yn, step, form, v, "full-sample r*" if step == "rstar" else step, D, 18, True)
# B: real-time r*, identical origins for the four r* variants and both data versions
B = (("nominal", None, None, "nominal"), ("real", None, None, "real"), ("rstar", None, None, "rstar_full-sample"), ("rstar", rs_rt, ix_rt, "rstar_real-time"))
common = None
for yn in ("du", "pay"):
    for step, rs, ixx, lab in B:
        for form in ("level", "flow", "mixed"):
            for v, D in pair(yn, step, form, ("rev", "rt1"), lo="2005-07", rstar=rs, ix=ixx).items(): common = D.index if common is None else common.intersection(D.index)
for yn in ("du", "pay"):
    for step, rs, ixx, lab in B:
        for form in ("level", "flow", "mixed"):
            for v, D in pair(yn, step, form, ("rev", "rt1"), rstar=rs, ix=ixx, common=common).items(): add("B", yn, step, form, v, lab, D, 12, False)
# C: vintage NROU 2011+, unemployment
for step in ("nominal", "real", "rstar"):
    for form in ("level", "flow", "mixed"):
        for v, D in pair("du", step, form, ("rev", "rt1", "rt2"), lo="2011-01").items(): add("C", "du", step, form, v, step, D, 12, False)
# D: core PCE 2002+
for step in ("real", "rstar"):
    for form in ("level", "flow", "mixed"):
        for v, D in pair("pi", step, form, ("rev", "rt1"), lo="2002-06").items(): add("D", "pi", step, form, v, step, D, 12, False)
T = pd.DataFrame(rows); T.to_csv(RES / "17_realtime_stance.csv", index=False)
S.add("rt_n_specifications", len(T))

# A2: level and flow in one regression
def lf_design(v, yn, x):
    Y, CTL = V[v]
    D = pd.concat([Y[yn].rename("y"), CTL[yn], x.rename("lvl"), (x - x.shift(12)).rename("flw")], axis=1).loc[R.START:R.LAST]
    return D[R.keep_mask(D.index)].dropna()
lf = []
for yn in ("du", "pay"):
    for step in ("nominal", "real", "rstar"):
        x = R.index(step); Ds = {v: lf_design(v, yn, x) for v in ("rev", "rt1")}; cm = Ds["rev"].index.intersection(Ds["rt1"].index)
        for v, D in Ds.items():
            D = R.stand(D.loc[cm], ("lvl", "flw")); ow = R.own(V[v][1], yn)
            r0 = R.hac_ols(D, ow, 18); rB = R.hac_ols(D, ow + ["lvl", "flw"], 18); rF = R.hac_ols(D, ow + ["flw"], 18)
            F = R.oos(D.rename(columns={"flw": "idx"}).assign(ff=D.lvl), ow); e0 = F.y - F.M0; e2 = F.y - F.M2; d = e0 ** 2 - e2 ** 2
            lf.append(dict(outcome=yn, step=step, version=v, n=len(D), t_lvl_both=rB.tvalues["lvl"], t_flw_both=rB.tvalues["flw"], b_flw_both=rB.params["flw"],
                           gain_flw=rF.rsquared_adj - r0.rsquared_adj, gain_both=rB.rsquared_adj - r0.rsquared_adj, n_oos=len(F),
                           rmse_flw=float(np.sqrt((e2 ** 2).mean() / (e0 ** 2).mean())), dm_flw=R.mean_t(d.values), cw_flw=R.mean_t((d + (F.M0 - F.M2) ** 2).values)))
LF = pd.DataFrame(lf); LF.to_csv(RES / "17_realtime_levelflow.csv", index=False)

# revisions
rev = []
Y0, C0 = V["rev"]
def comp(name, a, b, lo="1995-01", hi="2025-09"):
    d = pd.concat([a.rename("rt"), b.rename("rev")], axis=1).loc[lo:hi]; d = d[R.keep_mask(d.index)].dropna()
    rev.append(dict(variable=name, n=len(d), corr=d.corr().iloc[0, 1], rms_diff=float(np.sqrt(((d.rt - d.rev) ** 2).mean())), sd_rev=d.rev.std(), mean_diff=float((d.rt - d.rev).mean())))
for nm in ("rt1", "rt2"):
    Y, CT = V[nm]
    for yn in ("du", "pay", "pi"): comp(f"{nm}: outcome {yn}", Y[yn], Y0[yn], "2002-06" if yn == "pi" else ("2011-04" if nm == "rt2" else "1995-01"))
    comp(f"{nm}: unemployment gap level", CT["du"].u, C0["du"].u, "2011-04" if nm == "rt2" else "1995-01")
    comp(f"{nm}: payroll g12", CT["pay"].g12, C0["pay"].g12); comp(f"{nm}: core PCE p12", CT["pi"].p12, C0["pi"].p12, "2002-06")
rs = pd.concat([rs_rt.rename("rt"), R.M["rstar LW"].rename("rev")], axis=1).dropna()
rev.append(dict(variable="r* LW real-time vs full-sample (2005-07+)", n=len(rs), corr=rs.corr().iloc[0, 1], rms_diff=float(np.sqrt(((rs.rt - rs.rev) ** 2).mean())), sd_rev=rs.rev.std(), mean_diff=float((rs.rt - rs.rev).mean())))
RV = pd.DataFrame(rev); RV.to_csv(RES / "17_realtime_revisions.csv", index=False)

# Holm on the six primary Clark-West tests (du, pay x level, flow, mixed), within each version
hol = []
for v in ("rev", "rt1"):
    Q = T[(T.block == "A") & (T.step == "rstar") & (T.version == v)].copy(); Q["p"] = 1 - stats.norm.cdf(Q.cw_idx_given_ff)
    m = len(Q); run = 0; Q["p_holm"] = np.nan
    for i, ix in enumerate(Q.p.sort_values().index): run = max(run, min(1, (m - i) * Q.p[ix])); Q.loc[ix, "p_holm"] = run
    hol.append(Q)
H = pd.concat(hol)[["version", "outcome", "form", "n_oos", "rmse_idx_given_ff", "cw_idx_given_ff", "p", "p_holm"]]; H.to_csv(RES / "17_realtime_primary_holm.csv", index=False)

# the paper table: Market index, r* step, unemployment and payrolls; flow t = HAC t of the index given the funds-rate gap (flow form); gain = adjusted-R2 gain of the index given the gap;
# Clark-West (recursive, from 1995) in the long sample only. Rows within a panel share origins.
def pick(block, yn, version, form, basis):
    q = T[(T.block == block) & (T.outcome == yn) & (T.version == version) & (T.form == form) & (T.basis == basis)]
    assert len(q) == 1, (block, yn, version, form, basis); return q.iloc[0]
spec = [("1976-2025", "A", "Revised data", "rev", "full-sample r*"), ("1976-2025", "A", "Vintage data", "rt1", "full-sample r*"),
        ("2011-2025", "C", "Revised data", "rev", "rstar"), ("2011-2025", "C", "Vintage data", "rt1", "rstar"), ("2011-2025", "C", "Vintage data and NROU", "rt2", "rstar"),
        ("2006-2025", "B", "Revised data, full-sample r*", "rev", "rstar_full-sample"), ("2006-2025", "B", "Revised data, real-time r*", "rev", "rstar_real-time"),
        ("2006-2025", "B", "Vintage data, real-time r*", "rt1", "rstar_real-time")]
tab = []
for yn in ("du", "pay"):
    for panel_, blk, lab, v, basis in spec:
        if blk == "C" and yn != "du": continue      # block C is run for unemployment only
        r = {"outcome": yn, "panel": panel_, "row": lab, "version": v}
        for form in ("flow", "mixed"):
            q = pick(blk, yn, v, form, basis)
            r.update({"n": q.n, "first": q["first"], "last": q["last"], f"{form}_t": q.t_idx_both, f"{form}_gain": q.gain_idx_given_ff, f"{form}_cw": q.get("cw_idx_given_ff", np.nan) if blk == "A" else np.nan,
                      f"{form}_rmse": q.get("rmse_idx_given_ff", np.nan) if blk == "A" else np.nan})
        tab.append(r)
TB = pd.DataFrame(tab); TB.to_csv(RES / "17_realtime_table.csv", index=False)

# availability table (verified by download on 11 Nov 2026; earliest vintages are those the sources serve)
def first_origin(cols):
    ok = P[cols].notna().all(axis=1); return str(P.index[ok][0]) if ok.any() else ""
av = pd.DataFrame([
    ("Unemployment rate (UNRATE)", "yes", "1962 (ALFRED)", "1977-01 vintages; origins from " + first_origin(["u_k", "u_h_f"]), "vintage 2 months after the origin; outcomes from vintage 14 months after", "ALFRED"),
    ("Payroll employment (PAYEMS)", "yes", "1956 (ALFRED)", "1977-01 vintages; origins from " + first_origin(["p_k", "p_h_f"]), "as unemployment", "ALFRED"),
    ("Core PCE price index (PCEPILFE)", "yes, from 2001", "2000-10 (ALFRED)", "2001-06 vintages; origins from " + first_origin(["c_k", "c_h_f"]), "as unemployment; no pre-2001 origins, so no 1995 out-of-sample test", "ALFRED"),
    ("CBO natural rate of unemployment (NROU)", "partly", "2011-03 (ALFRED)", "origins from " + first_origin(["n_k", "n_h_f"]), "earlier origins use the ex-post series", "ALFRED"),
    ("Laubach-Williams r*", "partly", "2005Q1 (NY Fed real-time file)", "origins from 2005-07", "final point of each vintage, step function; none Sep 2020-Apr 2023; three mistyped release dates corrected", "NY Fed"),
    ("Cleveland Fed expected inflation", "no", "none (current file only)", "", "revised series kept", ""),
    ("Market-index weights", "no", "none", "", "unchanged (estimated on the full sample)", ""),
    ("Kiley r*; Shiller CAPE earnings; FRB/US", "no", "none", "", "unchanged", "")],
    columns=["input", "real_time_version_obtainable", "earliest_vintage", "vintages_used", "treatment", "source"])
av.to_csv(RES / "17_realtime_availability.csv", index=False)

# scalars
for _, q in T[(T.block == "A") & (T.step == "rstar") & (T.form != "level")].iterrows():
    k = f"rt_A_{q.outcome}_{q.form}_{q.version}"
    for a, b in (("t", "t_idx_both"), ("gain", "gain_idx_given_ff"), ("cw", "cw_idx_given_ff"), ("rmse", "rmse_idx_given_ff")): S.add(f"{k}_{a}", q[b])
S.add("rt_A_n", int(T[(T.block == "A")].n.iloc[0])); S.add("rt_A_n_oos", int(T[(T.block == "A")].n_oos.iloc[0]))
for _, q in T[(T.block == "B") & (T.step == "rstar") & (T.form != "level")].iterrows():
    k = f"rt_B_{q.outcome}_{q.form}_{q.version}_{'rt' if q.basis.endswith('real-time') else 'fs'}"
    S.add(f"{k}_t", q.t_idx_both); S.add(f"{k}_gain", q.gain_idx_given_ff)
S.add("rt_B_n", int(T[T.block == "B"].n.iloc[0])); S.add("rt_B_first", T[T.block == "B"]["first"].iloc[0]); S.add("rt_B_last", T[T.block == "B"]["last"].iloc[0])
for _, q in T[(T.block == "C") & (T.step == "rstar") & (T.form != "level")].iterrows():
    k = f"rt_C_{q.outcome}_{q.form}_{q.version}"; S.add(f"{k}_t", q.t_idx_both); S.add(f"{k}_gain", q.gain_idx_given_ff)
S.add("rt_C_n", int(T[T.block == "C"].n.iloc[0]))
for _, q in T[(T.block == "D") & (T.step == "rstar") & (T.form == "flow")].iterrows(): S.add(f"rt_D_pi_flow_{q.version}_t", q.t_idx_both)
for _, q in LF[LF.step == "rstar"].iterrows():
    for a in ("t_lvl_both", "t_flw_both", "gain_flw", "gain_both", "cw_flw"): S.add(f"rt_A2_{q.outcome}_{q.version}_{a}", q[a])
for _, q in H.iterrows(): S.add(f"rt_holm_{q.outcome}_{q.form}_{q.version}", q.p_holm)
for _, q in RV.iterrows():
    k = "rt_rev_" + q.variable.replace(": ", "_").replace("outcome ", "").replace(" ", "_").replace("*", "star").replace("(", "").replace(")", "").replace("+", "").replace("-", "_").replace("unemployment_gap_level", "ugap").lower()
    S.add(k + "_corr", q["corr"]); S.add(k + "_meandiff", q.mean_diff)
S.save()
print(TB.round(3).to_string())
