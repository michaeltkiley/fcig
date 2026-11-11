"""Real-time versus revised: stance regressions (followup2/stance design) and level-versus-flow regressions (followup/levelflow design).
PRE-SPECIFIED (before any estimate): index = Market only; outcomes du (12m change of unemployment gap), pay (12m payroll growth), pi (12m core PCE inflation, in sample only);
forms level/flow/mixed; steps nominal/real/rstar. Statistics: adjusted-R2 gain of the index given FFG, HAC t of the index (18 lags full, 12 lags sub-samples),
recursive OOS (from 1995-01) RMSE ratio and Clark-West of the index given FFG. Primary comparison = Market, r*-step, unemployment, flow and mixed forms
(A: revised vs real-time on the identical origins). Everything else descriptive. Blocks: A long sample (real-time u, payrolls; NROU ex-post; r* full-sample);
B 2006+ with real-time r* (in sample); C 2011+ with real-time CBO NROU (in sample); D core PCE 2003+ (in sample). Number of regressions counted in RESULT.md."""
from rt_common import *
V = versions(); ix_rt, _ = rt_index_rstar()
def stand(D):
    D = D.copy()
    for c in ("ff", "idx"): D[c] = (D[c] - D[c].mean()) / D[c].std()
    return D
def pair(yn, step, form, vers, rstar_name="rstar LW", ix=None, lo=None, hi=None):
    """designs for each version on identical origins; FFG and index from the revised series except where overridden."""
    f = C.ffg(step, rstar_name); x = C.index(step, "market") if ix is None else ix
    Ds = {v: design_v(*V[v], yn, f, x, form) for v in vers}
    common = None
    for D in Ds.values(): common = D.index if common is None else common.intersection(D.index)
    if lo: common = common[common >= pd.Period(lo, "M")]
    if hi: common = common[common <= pd.Period(hi, "M")]
    return {v: stand(D.loc[common]) for v, D in Ds.items()}

rows = []
# ---------------- A: long sample
for yn in ("du", "pay"):
    ow = C.own(yn)
    for step in ("nominal", "real", "rstar"):
        for form in ("level", "flow", "mixed"):
            for v, D in pair(yn, step, form, ("rev", "rt1")).items():
                rows.append(dict(block="A", outcome=yn, step=step, form=form, version=v, **hacstats(D, ow, 18)))
            print("A", yn, step, form, flush=True)
A = pd.DataFrame(rows); A.to_csv(OUT / "A_stance.csv", index=False)
# ---------------- A2: level-versus-flow (both in one regression), Market, three steps
def lf_design(Y, CTL, yn, x):
    C.Y, C.CTL = Y, CTL
    D = pd.concat([C.Y[yn].rename("y"), C.CTL[yn], x.rename("lvl"), (x - x.shift(12)).rename("flw")], axis=1).loc[C.START:C.LAST]
    C.Y, C.CTL = ORIG
    return D[C.keep_mask(D.index)].dropna()
lf = []
for yn in ("du", "pay"):
    ow = C.own(yn)
    for step in ("nominal", "real", "rstar"):
        x = C.index(step, "market"); Ds = {v: lf_design(*V[v], yn, x) for v in ("rev", "rt1")}
        cm = Ds["rev"].index.intersection(Ds["rt1"].index)
        for v, D in Ds.items():
            D = D.loc[cm].copy()
            for c in ("lvl", "flw"): D[c] = (D[c] - D[c].mean()) / D[c].std()
            r0 = C.hac_ols(D, ow, 18); rB = C.hac_ols(D, ow + ["lvl", "flw"], 18); rF = C.hac_ols(D, ow + ["flw"], 18)
            row = dict(outcome=yn, step=step, version=v, n=len(D), t_lvl_both=rB.tvalues["lvl"], t_flw_both=rB.tvalues["flw"], b_flw_both=rB.params["flw"],
                       gain_flw=rF.rsquared_adj - r0.rsquared_adj, gain_both=rB.rsquared_adj - r0.rsquared_adj)
            D2 = D.rename(columns={"flw": "idx"}); D2["ff"] = 0.0
            F = C.oos(D2.assign(ff=D2.lvl), ow)           # M0 own, M2 = own + flow ('idx'), M1/M3 include lvl as 'ff' -> we use M0 and M2 only
            e0 = F.y - F.M0; e2 = F.y - F.M2; d = e0 ** 2 - e2 ** 2
            row.update(n_oos=len(F), rmse_flw=float(np.sqrt((e2 ** 2).mean() / (e0 ** 2).mean())), dm_flw=C.mean_t(d.values), cw_flw=C.mean_t((d + (F.M0 - F.M2) ** 2).values))
            lf.append(row)
pd.DataFrame(lf).to_csv(OUT / "A2_levelflow.csv", index=False)
print(pd.DataFrame(lf).round(3).to_string())
# ---------------- B: real-time r*, 2006+ (in sample, HAC 12)
B = []
for yn in ("du", "pay"):
    ow = C.own(yn)
    for step, rs, ixx, lab in (("nominal", "rstar LW", None, "nominal"), ("real", "rstar LW", None, "real"),
                               ("rstar", "rstar LW", None, "rstar_full-sample"), ("rstar", "rstar RT", ix_rt, "rstar_real-time")):
        for form in ("level", "flow", "mixed"):
            C.M["rstar RT"] = rstar_rt()
            Ds = pair(yn, step, form, ("rev", "rt1"), rstar_name=rs, ix=ixx, lo="2005-07")
            # identical origins for all four r* variants: intersect later via key
            for v, D in Ds.items(): B.append(dict(block="B", outcome=yn, basis=lab, form=form, version=v, **hacstats(D, ow, 12, oos=False), _idx=D.index))
Bi = pd.DataFrame(B)
common = None
for ix_ in Bi._idx: common = ix_ if common is None else common.intersection(ix_)
print("B common origins", len(common), common[0], common[-1])
# explicit common origins (all four r* variants, both data versions)
def pair_common(yn, step, form, vers, rs, ixx, common):
    f = C.ffg(step, rs); x = C.index(step, "market") if ixx is None else ixx
    return {v: stand(design_v(*V[v], yn, f, x, form).loc[common]) for v in vers}
B = []
for yn in ("du", "pay"):
    ow = C.own(yn)
    for step, rs, ixx, lab in (("nominal", "rstar LW", None, "nominal"), ("real", "rstar LW", None, "real"),
                               ("rstar", "rstar LW", None, "rstar_full-sample"), ("rstar", "rstar RT", ix_rt, "rstar_real-time")):
        for form in ("level", "flow", "mixed"):
            for v, D in pair_common(yn, step, form, ("rev", "rt1"), rs, ixx, common).items():
                B.append(dict(block="B", outcome=yn, basis=lab, form=form, version=v, **hacstats(D, ow, 12, oos=False))); print("B", yn, lab, form, v, len(D), flush=True)
pd.DataFrame(B).to_csv(OUT / "B_rstar_rt.csv", index=False)
# ---------------- C: real-time NROU, 2011+ (in sample, du only)
Cc = []
for step in ("nominal", "real", "rstar"):
    for form in ("level", "flow", "mixed"):
        Ds = pair("du", step, form, ("rev", "rt1", "rt2"), lo="2011-01")
        for v, D in Ds.items(): Cc.append(dict(block="C", outcome="du", step=step, form=form, version=v, **hacstats(D, C.own("du"), 12, oos=False)))
pd.DataFrame(Cc).to_csv(OUT / "C_nrou_rt.csv", index=False)
# ---------------- D: core PCE, 2003+
Dd = []
for step in ("real", "rstar"):
    for form in ("level", "flow", "mixed"):
        for v, D in pair("pi", step, form, ("rev", "rt1"), lo="2002-06").items(): Dd.append(dict(block="D", outcome="pi", step=step, form=form, version=v, **hacstats(D, C.own("pi"), 12, oos=False)))
pd.DataFrame(Dd).to_csv(OUT / "D_pi.csv", index=False)
print("done")
