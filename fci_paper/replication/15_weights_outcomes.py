"""Step 15. Which weights on the same variables say most about the economy ahead? Market (policy-news) weights against FRB/US weights, the first principal component, equal weights
and activity-fitted weights, all on the 10-year yield, equity valuation and real dollar; plus the full indexes as given.

PRE-SPECIFIED DESIGN (ported unchanged from followup/weights)
 Sets (3 variables): MKT (results/market_weights.csv), FRBUS3 (frbus_weights.csv), PC1, EQ, ACT; given: GS, FRB/US (full), NFCI, ANFCI, and in the change form FCI-G 1-year and FRB/US growth impetus.
 PC1, EQ, ACT are re-estimated at each origin on data up to the origin (ACT: sign-constrained least squares on the oriented standardised variables, own lag and constant partialled out).
 Outcomes: unemployment gap, 12-month payroll growth, real GDP growth, core PCE inflation (each y(t+h)), recession within h months (linear probability); h = 6, 12, 24; 15 outcome-horizons.
 Each forecast: y(t+h) on a constant, the outcome's own current value and one index; recursive from 1995-01 with an expanding window. Forms: level and 12-month change.
 Steps: r*-gap (primary) and real (secondary, not pooled).
 Primary family (r*-gap): 4 alternatives against MKT x 15 outcome-horizons x 2 forms = 120 two-sided paired Diebold-Mariano tests (HAC lag max(h,12)); Holm and Benjamini-Hochberg adjusted.
 Secondary: given indexes against MKT; each set against the no-index baseline (Clark-West, one-sided 5%); change form against level form within each set.
 Activity-fitted shares: 12-month-ahead outcomes, shares of the oriented standardised variables (sum 1), full sample 1976-2025, moving-block bootstrap (24 months, rows resampled jointly, REPS draws);
 OLS with HAC and Wald tests that the coefficients are proportional to the market (FRB/US) weights. 20 cells (2 steps x 2 forms x 5 outcomes).
 Not ported: the recursive path of the fitted shares. Shared data: counts are descriptive. Bootstrap seed is SEED + 1 (the follow-up seed).
Writes results/15_cells.csv, 15_pairs.csv, 15_primary_family.csv, 15_level_vs_change.csv, 15_act_weights.csv, 15_summary.csv, scalars_15_weights_outcomes.csv."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
from lib import data
from lib.config import RES, REPS, SEED
from lib.report import Scalars
from lib.purge_util import holm, bh, read_res
from lib import purge_weights as W

from lib.purge_util import single_thread_blas
single_thread_blas()
S = Scalars("15_weights_outcomes")
D = read_res("data_monthly.csv")
mw = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.reindex(W.VARS).values
fw = pd.read_csv(RES / "frbus_weights.csv", index_col=0).frbus_weight.reindex(W.VARS).values
J = pd.period_range(W.SAMPLE0, "2026-09", freq="M"); allidx = pd.period_range("1958-01", "2026-12", freq="M")
origins = list(pd.period_range(W.FIRST, "2026-09", freq="M"))
PRIM, GIVEN = ["FRBUS3", "PC1", "EQ", "ACT"], ["GS", "FRBUS_full", "NFCI", "ANFCI", "FCIG", "FRBUS_gi"]

# ---------------- forecasts
rows, pairs, ERR = [], [], {}
for case in ("rstar", "real"):
    Sx, I, Z = W.fixed_sets(D, case, mw, fw)
    assert np.abs((Z @ mw - I.market).dropna()).max() < 1e-4                      # the three-variable market index is the package's market index
    for form in ("level", "change"):
        fixed = {k: W.to_form(v, form) for k, v in Sx.items()}
        if form == "change":
            fixed["FCIG"] = I.fcig_1yr; fixed["FRBUS_gi"] = I.frbus_gi_hp               # flows as given
        Zo = W.to_form(Z * W.ORIENT, form)
        for h in W.HORIZONS:
            for oc, (y, own, valid) in W.outcomes(D, h).items():
                R = W.recursive_forecasts(J, y, own, valid, fixed, Zo, h, origins, W.OUTCOMES[oc])
                a = R["actual"]; lag = W.haclag(h); e = {k: a - R[k] for k in R if k not in ("actual", "t")}
                mse0 = (e["base"] ** 2).mean()
                for k in e:
                    ERR[f"{case}|{form}|{oc}|{h}|{k}"] = e[k]
                ERR[f"{case}|{form}|{oc}|{h}|t"] = np.array([p.ordinal for p in R["t"]])
                for k in e:
                    if k == "base":
                        continue
                    rows.append(dict(step=case, form=form, outcome=oc, h=h, set=k, n=len(a), mse_ratio_base=(e[k] ** 2).mean() / mse0, cw_t=W.cw(e["base"], e[k], R["base"], R[k], lag)))
                    if k != "MKT":
                        pairs.append(dict(step=case, form=form, outcome=oc, h=h, set=k, n=len(a), mse_ratio_mkt=(e[k] ** 2).mean() / (e["MKT"] ** 2).mean(), dm_t=W.dm(e[k] ** 2 - e["MKT"] ** 2, lag)))
        print(case, form, "done", flush=True)
K, P = pd.DataFrame(rows), pd.DataFrame(pairs)
P["p"] = 2 * (1 - norm.cdf(P.dm_t.abs())); K["p_cw"] = 1 - norm.cdf(K.cw_t)
K.to_csv(RES / "15_cells.csv", index=False)
geo = lambda x: float(np.exp(np.log(x).mean()))

# ---------------- primary family, multiple testing
out, summ = [], []
for step in ("rstar", "real"):
    q = P[(P.step == step) & P.set.isin(PRIM)].copy(); q["p_holm"] = holm(q.p.values); q["p_bh"] = bh(q.p.values); out.append(q)
    S.add(f"w_{step}_n_primary_tests", len(q)); S.add(f"w_{step}_expected_false_10pct", 0.1 * len(q))
    S.add(f"w_{step}_n_raw_sig10", int((q.p < .10).sum())); S.add(f"w_{step}_n_holm_sig10", int((q.p_holm < .10).sum())); S.add(f"w_{step}_n_bh_sig10", int((q.p_bh < .10).sum()))
    S.add(f"w_{step}_n_holm_sig05", int((q.p_holm < .05).sum()))
    for form in ("level", "change"):
        for s in PRIM + GIVEN:
            r = P[(P.step == step) & (P.form == form) & (P.set == s)]
            if len(r) == 0:
                continue
            k = K[(K.step == step) & (K.form == form) & (K.set == s)]
            qq = q[(q.form == form) & (q.set == s)]
            row = dict(step=step, form=form, set=s, n_cells=len(r), geo_mse_ratio_to_mkt=geo(r.mse_ratio_mkt), n_alt_better_raw10=int(((r.p < .1) & (r.dm_t < 0)).sum()),
                       n_alt_worse_raw10=int(((r.p < .1) & (r.dm_t > 0)).sum()), n_ratio_below1=int((r.mse_ratio_mkt < 1).sum()),
                       n_holm_sig10=int((qq.p_holm < .10).sum()) if len(qq) else np.nan, geo_mse_ratio_to_base=geo(k.mse_ratio_base), n_cw_sig05=int((k.p_cw < .05).sum()))
            summ.append(row)
            for kk, v in row.items():
                if kk not in ("step", "form", "set"):
                    S.add(f"w_{step}_{form}_{s.lower()}_{kk}", v)
        m = K[(K.step == step) & (K.form == form) & (K.set == "MKT")]
        summ.append(dict(step=step, form=form, set="MKT", n_cells=len(m), geo_mse_ratio_to_base=geo(m.mse_ratio_base), n_cw_sig05=int((m.p_cw < .05).sum()), n_ratio_below1=int((m.mse_ratio_base < 1).sum())))
        S.add(f"w_{step}_{form}_mkt_geo_mse_ratio_to_base", geo(m.mse_ratio_base)); S.add(f"w_{step}_{form}_mkt_n_cw_sig05", int((m.p_cw < .05).sum()))
        # unemployment lead of MKT over the alternatives (change form)
        for oc in ("ugap",):
            g = q[(q.form == form) & (q.outcome == oc)]
            S.add(f"w_{step}_{form}_{oc}_mean_dm_t_alt_vs_mkt", g.dm_t.mean())
pd.concat(out).to_csv(RES / "15_primary_family.csv", index=False)
# by outcome (change form, r*): MKT and alternatives relative to the no-index baseline
r = K[(K.step == "rstar") & (K.form == "change") & K.set.isin(["MKT"] + PRIM)].groupby(["outcome", "set"]).mse_ratio_base.apply(geo)
for (oc, s), v in r.items():
    S.add(f"w_rstar_change_{oc}_{s.lower()}_geo_mse_ratio_to_base", v)

# ---------------- level versus change (same set, same origins)
E = ERR; rows = []
for step in ("rstar", "real"):
    for s in ["MKT", "FRBUS3", "PC1", "EQ", "ACT", "GS", "FRBUS_full", "NFCI", "ANFCI"]:
        for oc in W.OUTCOMES:
            for h in W.HORIZONS:
                a, b = E[f"{step}|level|{oc}|{h}|{s}"], E[f"{step}|change|{oc}|{h}|{s}"]
                assert (E[f"{step}|level|{oc}|{h}|t"] == E[f"{step}|change|{oc}|{h}|t"]).all()
                rows.append(dict(step=step, set=s, outcome=oc, h=h, ratio_change_over_level=(b ** 2).mean() / (a ** 2).mean(), dm_t=W.dm(b ** 2 - a ** 2, W.haclag(h))))
L = pd.DataFrame(rows); L["p"] = 2 * (1 - norm.cdf(L.dm_t.abs())); L.to_csv(RES / "15_level_vs_change.csv", index=False)
for (step, s), g in L.groupby(["step", "set"]):
    S.add(f"w_{step}_lvc_{s.lower()}_geo_ratio", geo(g.ratio_change_over_level)); S.add(f"w_{step}_lvc_{s.lower()}_n_change_better", int((g.dm_t < -1.645).sum()))
    S.add(f"w_{step}_lvc_{s.lower()}_n_level_better", int((g.dm_t > 1.645).sum()))

# ---------------- activity-fitted weights with bootstrap intervals (12 months ahead)
rng = np.random.default_rng(SEED + 1); h = 12; rows = []


def block_idx(n, Lb):
    nb = int(np.ceil(n / Lb)); st = rng.integers(0, n - Lb + 1, nb); return np.concatenate([np.arange(s, s + Lb) for s in st])[:n]


for case in ("rstar", "real"):
    Z = W.three_vars(D, case)
    for form in ("level", "change"):
        Zo = W.to_form(Z * W.ORIENT, form)
        for oc, (y, own, valid) in W.outcomes(D, h).items():
            sg = W.OUTCOMES[oc]
            v = pd.Series(np.asarray(valid), index=allidx).reindex(J).values
            df = pd.DataFrame({"y": y.reindex(J).values, "own": own.reindex(J).values if own is not None else 0.0}, index=J)
            for vn in W.VARS:
                df[vn] = Zo[vn].reindex(J).values
            df = df[v].dropna(); sd = df[W.VARS].std().values; Zs = ((df[W.VARS] - df[W.VARS].mean()) / sd).values
            o = df.own.values if own is not None else None
            ref = {"MKT": np.abs(mw) * sd / (np.abs(mw) * sd).sum(), "FRBUS": np.abs(fw) * sd / (np.abs(fw) * sd).sum()}
            pt, w0 = W.nnls_shares(Zs, df.y.values, o, sg)
            Xd = sm.add_constant(pd.DataFrame(np.column_stack(([o] if o is not None else []) + [Zs])), has_constant="add")
            r = sm.OLS(df.y.values, Xd).fit(cov_type="HAC", cov_kwds={"maxlags": W.haclag(h)})
            nb = 1 + (1 if o is not None else 0); tt = np.asarray(r.tvalues)[nb:]
            out = dict(step=case, form=form, outcome=oc, n=len(df), **{f"ols_t_{vn}": tt[j] for j, vn in enumerate(W.VARS)}, ols_joint_p=float(r.f_test(np.eye(len(r.params))[nb:]).pvalue))
            for nm, wref in (("MKT", mw), ("FRBUS", fw)):
                q = np.abs(wref) * sd; Rm = np.zeros((2, len(r.params))); Rm[0, nb + 1] = q[0]; Rm[0, nb] = -q[1]; Rm[1, nb + 2] = q[0]; Rm[1, nb] = -q[2]
                out[f"wald_p_prop_{nm}"] = float(r.wald_test(Rm, use_f=False, scalar=True).pvalue)
            bs = []
            for _ in range(REPS):
                ii = block_idx(len(df), W.BLOCK); s_, w_ = W.nnls_shares(Zs[ii], df.y.values[ii], o[ii] if o is not None else None, sg); bs.append(np.r_[s_, w_.sum()])
            bs = np.array(bs); zero = np.isnan(bs[:, 0]).mean()
            for j, vn in enumerate(W.VARS):
                lo, hi = np.nanpercentile(bs[:, j], [5, 95]) if zero < 1 else (np.nan, np.nan)
                out.update({f"share_{vn}": pt[j], f"lo90_{vn}": lo, f"hi90_{vn}": hi, f"mkt_{vn}": ref["MKT"][j], f"frbus_{vn}": ref["FRBUS"][j]})
            out["boot_all_zero"] = zero; out["pt_all_zero"] = float(np.isnan(pt[0]))
            out["l1_to_mkt_boot_mean"] = np.nanmean(np.abs(bs[:, :3] - ref["MKT"]).sum(axis=1)); out["l1_to_frbus_boot_mean"] = np.nanmean(np.abs(bs[:, :3] - ref["FRBUS"]).sum(axis=1))
            out["l1_mkt_frbus"] = np.abs(ref["MKT"] - ref["FRBUS"]).sum()
            rows.append(out)
A = pd.DataFrame(rows)
ins = lambda r, pre: all(r[f"lo90_{v}"] <= r[f"{pre}_{v}"] <= r[f"hi90_{v}"] for v in W.VARS)
A["mkt_inside"] = A.apply(lambda r: ins(r, "mkt"), axis=1); A["frbus_inside"] = A.apply(lambda r: ins(r, "frbus"), axis=1)
A["mean_width"] = A.apply(lambda r: np.mean([r[f"hi90_{v}"] - r[f"lo90_{v}"] for v in W.VARS]), axis=1)
A.to_csv(RES / "15_act_weights.csv", index=False)
for step in ("rstar", "real"):
    a = A[A.step == step]
    S.add(f"w_{step}_act_n_cells", len(a)); S.add(f"w_{step}_act_n_mkt_inside", int(a.mkt_inside.sum())); S.add(f"w_{step}_act_n_frbus_inside", int(a.frbus_inside.sum()))
    S.add(f"w_{step}_act_mean_width", a.mean_width.mean()); S.add(f"w_{step}_act_wald_mkt_rejected10", int((a.wald_p_prop_MKT < .1).sum())); S.add(f"w_{step}_act_wald_frbus_rejected10", int((a.wald_p_prop_FRBUS < .1).sum()))
    S.add(f"w_{step}_act_l1_boot_to_mkt_min", a.l1_to_mkt_boot_mean.min()); S.add(f"w_{step}_act_l1_boot_to_mkt_max", a.l1_to_mkt_boot_mean.max()); S.add(f"w_{step}_l1_mkt_frbus", a.l1_mkt_frbus.iloc[0])
for _, r in A.iterrows():
    for vn in W.VARS:
        for q in ("share", "lo90", "hi90", "mkt", "frbus"):
            S.add(f"w_{r.step}_act_{r.form}_{r.outcome}_{q}_{vn}", r[f"{q}_{vn}"])
pd.DataFrame(summ).to_csv(RES / "15_summary.csv", index=False)
pd.DataFrame(pairs).to_csv(RES / "15_pairs.csv", index=False)
S.save()
