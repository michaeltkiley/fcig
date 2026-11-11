"""Step 12. The paper's core results re-run on 1996+ beside 1973+ (checks table rows a-e) and the reconciliation of the VAR yardstick across sub-periods.
Ported from followup3/core_1996 (no FOMC-window surprise identification; weights fixed at the full 1996-2026 announcement sample, row d uses weights through 2019).

DESIGN (pre-specified before any estimate was looked at)
 series : Market, GS, FRB/US at the nominal, real and r* (Laubach-Williams) steps (results/indexes_<step>.csv).
 rows   : a main  VAR 1973-01+, 12 lags, 2020 dummied; regressions origins 1976-03+, recursive OOS from 1995-01
          b fixed 1996+ throughout: VAR 1996-01+ (12 and 4 lags), origins 1996-01+, OOS from the first origin with >= 96 training months
          c excluding 2008-15: VAR with a dummy for every month 2008-01..2015-12; regressions drop every origin whose window t-12..t+12 touches 2008-01..2015-12; OOS from 1995-01
          d weights estimated on announcements through 2019 (Market only); VAR 1973+, regressions as a
          e origins from 1974-01 (earliest with a 12-month change), OOS from the first origin with >= 100 training months; VAR as a
 (i)   VAR Phi(12) of the unemployment gap to a unit index shock (u first), 90% moving-block bootstrap interval (12-month blocks, REPS draws), Granger p (index -> u)
 (ii)  level versus flow: du and payroll growth on own lags + level + 12-month flow (standardised), HAC 18: t(flow), t(level), adjusted-R2 gain of the flow alone
 (iii) stance: index given the funds-rate gap (step-matched), forms flow and mixed, du and payrolls: adjusted-R2 gain M1 -> M3, t(index), recursive OOS Clark-West M1 -> M3 (HAC 12);
       first OOS date, n, number of NBER recessions in the OOS outcome windows
 (iv)  r* ladder, du, own lags + index flow: pairwise step comparisons: in-sample R2 difference (same y, same dof) with a moving-block (24) paired bootstrap of origins (2 x REPS draws,
       = 1000 at the default) and the OOS MSE difference (positive = later step better) with Diebold-Mariano HAC 12 and the same block bootstrap; samples a, a_pre96 (origins before 1996),
       a_post96 (origins from 1996), b, c, e
 (v)   sub-period reconciliation: Phi(12) for the market r* index by VAR sample 1973-89, 1990-2007, 1996-2007, 1996-2019, 2009-2026, 1996-2026, 12 and 4 lags, same bootstrap
 Test counts are descriptive (shared data; nothing multiple-testing adjusted): VAR 39 (+12 sub-period) cases, level-flow 78, stance 156, ladder 54.
Writes results/12_<table>.csv and scalars_12_checks1996.csv."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(_v, "1")      # one BLAS thread per worker
import numpy as np, pandas as pd
from multiprocessing import Pool
from lib.config import RES, REPS, SEED
from lib.report import Scalars
from lib.stance_core import *

S = Scalars("12_checks1996")
LAB = dict(SERIES)

# ---- (i) VARs and (v) sub-periods, run in parallel (var_job is a module-level function of lib.stance_core)
jobs = []
for row, R in ROWS.items():
    if row == "e": continue
    for p in R["lags"]:
        for step in STEPS:
            for key, _ in SERIES:
                if R.get("w2019") and key != "market": continue
                jobs.append((row, step, key, p, R["var_start"], "2026-09", R["var_dum"], R.get("w2019", False), REPS))
SUB = {"1973-89": ("1973-01", "1989-12"), "1990-2007": ("1990-01", "2007-12"), "1996-2007": ("1996-01", "2007-12"), "1996-2019": ("1996-01", "2019-12"),
       "2009-2026": ("2009-01", "2026-09"), "1996-2026": ("1996-01", "2026-09")}
for lab, (a, z) in SUB.items():
    for p in (12, 4): jobs.append((f"sub_{lab}", "rstar", "market", p, a, z, [], False, REPS))
with Pool(4) as pl: res = pl.map(var_job, jobs)
V = pd.DataFrame(res).rename(columns={"spec": "row"})
V[~V.row.str.startswith("sub_")].to_csv(RES / "12_var.csv", index=False)
SV = V[V.row.str.startswith("sub_")].copy(); SV["period"] = SV.row.str[4:]; SV = SV.drop(columns=["row", "step", "series"])
SV.to_csv(RES / "12_var_subperiods.csv", index=False)
V = V[~V.row.str.startswith("sub_")]
Ve = V[V.row == "a"].copy(); Ve["row"] = "e"; V = pd.concat([V, Ve])          # row e's VAR is row a's
for _, r in SV.iterrows():
    t = f"chk_sub_{r.period.replace('-', '_')}_L{r.lags}"
    S.add(f"{t}_phi", r.phi12); S.add(f"{t}_lo", r.lo90); S.add(f"{t}_hi", r.hi90); S.add(f"{t}_n", int(r.n)); S.add(f"{t}_gp", r.granger_p)

# ---- (ii) level versus flow and (iii) stance
LF, ST = [], []
for row, R in ROWS.items():
    for yn in ("du", "pay"):
        ow = own(yn)
        for step in STEPS:
            for key, _ in SERIES:
                if R.get("w2019") and key != "market": continue
                D = row_design(yn, step, key, "lf", row)
                r0 = hac_ols(D, ow); rB = hac_ols(D, ow + ["lvl", "flw"]); rF = hac_ols(D, ow + ["flw"])
                LF.append(dict(row=row, outcome=yn, step=step, series=key, n=len(D), t_flw=rB.tvalues["flw"], t_lvl=rB.tvalues["lvl"], b_flw=rB.params["flw"],
                               t_flw_alone=rF.tvalues["flw"], gain_flw=rF.rsquared_adj - r0.rsquared_adj, gain_both=rB.rsquared_adj - r0.rsquared_adj))
                for form in ("flow", "mixed"):
                    D = row_design(yn, step, key, form, row)
                    r1, r2, r3 = (hac_ols(D, ow + c) for c in (["ff"], ["idx"], ["ff", "idx"]))
                    F = oos(D, {"M1": ow + ["ff"], "M3": ow + ["ff", "idx"]}, R["first_oos"], R["nmin"])
                    e1, e3 = F.y - F.M1, F.y - F.M3; d = e1 ** 2 - e3 ** 2; cw = d + (F.M1 - F.M3) ** 2
                    ST.append(dict(row=row, outcome=yn, step=step, series=key, form=form, n=len(D), gain_idx_given_ff=r3.rsquared_adj - r1.rsquared_adj,
                                   gain_ff_given_idx=r3.rsquared_adj - r2.rsquared_adj, t_idx_both=r3.tvalues["idx"], t_ff_both=r3.tvalues["ff"],
                                   first_oos=str(F.index[0]), n_oos=len(F), n_rec_oos=n_recessions(F.index), rmse_ratio=float(np.sqrt((e3 ** 2).mean() / (e1 ** 2).mean())),
                                   cw=mean_t(cw.values), dm=mean_t(d.values)))
LF = pd.DataFrame(LF); ST = pd.DataFrame(ST)
LF.to_csv(RES / "12_levelflow.csv", index=False); ST.to_csv(RES / "12_stance.csv", index=False)

# ---- (iv) r* ladder
rng = np.random.default_rng(SEED); B = 2 * REPS; BL = 24


def blocks(n):
    nb = -(-n // BL)
    return [np.concatenate([np.arange(s, s + BL) for s in rng.integers(0, n - BL + 1, nb)])[:n] for _ in range(B)]


def r2(y, X):
    Z = np.c_[np.ones(len(y)), X]; b = np.linalg.lstsq(Z, y, rcond=None)[0]; e = y - Z @ b
    return 1 - (e @ e) / (((y - y.mean()) ** 2).sum())


PAIRS = [("real", "nominal"), ("rstar", "real"), ("rstar", "nominal")]            # (later, earlier)
SAMPLES = [("a", "a", None, None), ("a_pre96", "a", None, "1995-12"), ("a_post96", "a", "1996-01", None), ("b", "b", None, None), ("c", "c", None, None), ("e", "e", None, None)]
LD = []
for lab, row, lo, hi in SAMPLES:
    R = ROWS[row]
    for key, _ in SERIES:
        ow = own("du"); D = {s: row_design("du", s, key, "flow", row) for s in STEPS}
        idx = D["nominal"].index
        for s in STEPS: assert (D[s].index == idx).all()
        sel = np.ones(len(idx), bool)
        if lo: sel &= idx >= pd.Period(lo, "M")
        if hi: sel &= idx <= pd.Period(hi, "M")
        Ds = {s: D[s][sel].copy() for s in STEPS}
        for s in STEPS: Ds[s]["idx"] = (Ds[s].idx - Ds[s].idx.mean()) / Ds[s].idx.std()     # refit within the subsample
        y = Ds["nominal"].y.values; C = Ds["nominal"][ow].values
        X = {s: np.c_[C, Ds[s].idx.values] for s in STEPS}
        draws = blocks(len(y))
        F = {s: oos(D[s], {"M": ow + ["idx"]}, R["first_oos"], R["nmin"]) for s in STEPS}
        for later, earlier in PAIRS:
            diff = r2(y, X[later]) - r2(y, X[earlier])
            sb = [r2(y[ix], X[later][ix]) - r2(y[ix], X[earlier][ix]) for ix in draws]
            Fl, Fe = F[later], F[earlier]; m = np.ones(len(Fl), bool)
            if lo: m &= Fl.index >= pd.Period(lo, "M")
            if hi: m &= Fl.index <= pd.Period(hi, "M")
            Fl, Fe = Fl[m], Fe[m]
            r_ = dict(sample=lab, series=key, later=later, earlier=earlier, n=len(y), r2_later=r2(y, X[later]), r2_earlier=r2(y, X[earlier]), dr2=diff, dr2_lo90=np.percentile(sb, 5), dr2_hi90=np.percentile(sb, 95))
            if len(Fl) >= 40:
                dv = ((Fe.y - Fe.M) ** 2 - (Fl.y - Fl.M) ** 2).values; n = len(dv); nb = -(-n // BL)
                bs = [dv[np.concatenate([np.arange(s, s + BL) for s in rng.integers(0, max(n - BL, 1), nb)])[:n]].mean() for _ in range(B)]
                r_.update(first_oos=str(Fl.index[0]), last_oos=str(Fl.index[-1]), n_oos=len(Fl), n_rec_oos=n_recessions(Fl.index), rmse_ratio=float(np.sqrt(((Fl.y - Fl.M) ** 2).mean() / ((Fe.y - Fe.M) ** 2).mean())),
                          dm_t=mean_t(dv), dmse=float(dv.mean()), dmse_lo90=float(np.percentile(bs, 5)), dmse_hi90=float(np.percentile(bs, 95)))
            LD.append(r_)
LD = pd.DataFrame(LD); LD.to_csv(RES / "12_ladder.csv", index=False)

# ---- the checks table (rows a-e, identical statistics), long over series
out = []
for row in ROWS:
    for lags in ROWS[row]["lags"]:
        for key, nm in SERIES:
            if row == "d" and key != "market": continue
            for step in STEPS:
                v = V[(V.row == row) & (V.lags == lags) & (V.series == key) & (V.step == step)].iloc[0]
                l = LF[(LF.row == row) & (LF.series == key) & (LF.step == step)]; ld = l[l.outcome == "du"].iloc[0]; lp = l[l.outcome == "pay"].iloc[0]
                s = ST[(ST.row == row) & (ST.series == key) & (ST.step == step) & (ST.outcome == "du")]; sf = s[s.form == "flow"].iloc[0]; sm_ = s[s.form == "mixed"].iloc[0]
                sp = ST[(ST.row == row) & (ST.series == key) & (ST.step == step) & (ST.outcome == "pay") & (ST.form == "flow")].iloc[0]
                out.append(dict(row=row, lags=lags, series=nm, step=step, var_n=v.n, phi12=v.phi12, phi12_lo90=v.lo90, phi12_hi90=v.hi90, granger_p=v.granger_p,
                                lf_n=ld.n, du_t_flow=ld.t_flw, du_t_level=ld.t_lvl, du_gain_flow=ld.gain_flw, pay_t_flow=lp.t_flw, pay_gain_flow=lp.gain_flw,
                                st_du_flow_gain=sf.gain_idx_given_ff, st_du_flow_t=sf.t_idx_both, st_du_mixed_gain=sm_.gain_idx_given_ff, st_du_mixed_t=sm_.t_idx_both,
                                oos_first=sf.first_oos, oos_n=sf.n_oos, oos_rec=sf.n_rec_oos, cw_du_flow=sf.cw, rmse_du_flow=sf.rmse_ratio, cw_du_mixed=sm_.cw, rmse_du_mixed=sm_.rmse_ratio,
                                st_pay_flow_gain=sp.gain_idx_given_ff, st_pay_flow_t=sp.t_idx_both, cw_pay_flow=sp.cw))
T = pd.DataFrame(out); T.to_csv(RES / "12_checks.csv", index=False)

# ---- scalars: Market, every row and step
for _, r in T[T.series == "Market"].iterrows():
    base = f"chk_{r.row}_{r.step}"
    vt = f"chk_var_{r.row}{r.lags if r.row == 'b' else ''}_{r.step}"
    S.add(f"{vt}_phi", r.phi12); S.add(f"{vt}_lo", r.phi12_lo90); S.add(f"{vt}_hi", r.phi12_hi90); S.add(f"{vt}_gp", r.granger_p); S.add(f"{vt}_n", int(r.var_n))
    if r.row == "b" and r.lags == 4: continue
    for c in ("du_t_flow", "du_t_level", "du_gain_flow", "pay_t_flow", "pay_gain_flow", "st_du_flow_gain", "st_du_flow_t", "st_du_mixed_gain", "st_du_mixed_t",
              "cw_du_flow", "rmse_du_flow", "cw_du_mixed", "rmse_du_mixed", "st_pay_flow_gain", "st_pay_flow_t", "cw_pay_flow", "oos_first", "oos_n", "oos_rec", "lf_n"):
        S.add(f"{base}_{c}", r[c])
for _, r in LD[LD.series == "market"].iterrows():
    t = f"chk_ladder_{r['sample']}_{r.later}_{r.earlier}"
    for c in ("n", "dr2", "dr2_lo90", "dr2_hi90", "r2_later", "r2_earlier", "n_oos", "n_rec_oos", "rmse_ratio", "dm_t", "dmse", "dmse_lo90", "dmse_hi90", "first_oos"):
        if c in r and pd.notna(r[c]): S.add(f"{t}_{c}", r[c])
S.add("chk_n_boot_ladder", B)
S.save()
print(T[T.series == "Market"][["row", "lags", "step", "phi12", "phi12_lo90", "phi12_hi90", "du_t_flow", "st_du_flow_gain", "cw_du_flow", "oos_first", "oos_n", "oos_rec"]].round(2).to_string())
print(SV[["period", "lags", "n", "phi12", "lo90", "hi90"]].round(2).to_string())
print(LD[LD.series == "market"].round(3).to_string())
