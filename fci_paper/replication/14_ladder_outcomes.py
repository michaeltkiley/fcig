"""Step 14. Does measuring conditions relative to neutral change what an index says about activity ahead? r* versus real versus nominal for each index family.

PRE-SPECIFIED DESIGN (ported unchanged from followup/rstar_test)
 Families (7): market level, market forward impetus, GS level, FRB/US level, FRB/US growth impetus, FCI-G 1-year, FCI-G 3-year; each at the nominal, real and r*-gap (LW) step.
 References without a step: NFCI, ANFCI (compared with the own-lag baseline only).
 Outcomes: unemployment gap, payroll growth (log PAYEMS), real GDP growth (GDPC1, quarterly), core PCE inflation, each at 6, 12, 24 months; recession within 12 months (USREC, logit).
 13 outcome-horizon cells x 7 families = 91 paired tests per contrast. Primary contrasts: r* vs nominal and r* vs real (182 tests); secondary: real vs nominal (91).
 Predictor: current reading plus the outcome's own lag (u gap level; trailing 12-month growth; USREC(t)). Covid months dropped. Samples from 1976-03.
 Out of sample: recursive forecasts from 1995-01 (training rows t' <= t-h), Diebold-Mariano on squared (Brier) loss, HAC lag max(h,12) (quarterly GDP: max(h/3,4)).
 In sample: adjusted R2 (log-likelihood for the logit) difference with a 90% moving-block bootstrap (24 months; 8 quarters for GDP; REPS draws).
 Clark-West of each step against the own-lag baseline (one-sided).
 Multiple testing: Holm adjustment within each contrast's 91 DM tests (5% and 10% levels); in-sample bootstrap intervals are reported unadjusted (500 draws cannot reach Holm thresholds).
 Counts are descriptive: families and cells share data. Five recessions (1980, 1981-82, 1990-91, 2001, 2007-09) in the logit samples.
Writes results/14_paired.csv (every paired test), 14_vs_baseline.csv, 14_subperiods.csv, 14_summary.csv (tidy table: one row per contrast and outcome), scalars_14_ladder_outcomes.csv."""
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
from lib import data
from lib.config import RES, REPS, SEED
from lib.report import Scalars
from lib.purge_util import holm
from lib import purge_outcomes as O

from lib.purge_util import single_thread_blas
single_thread_blas()
S = Scalars("14_ladder_outcomes")
rng = np.random.default_rng(SEED)
X = O.predictors(); u = data.load().u_gap
COMBOS = [(o, h) for o in ("ugap", "payroll", "gdp", "corepce") for h in O.HORIZONS] + [("recession", 12)]


def design(J, cols):
    return np.c_[np.ones(len(J)), J[["c"] + cols].values]


def hac_t(d, lag):
    d = np.asarray(d); return float(sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lag}).tvalues[0])


def oos(J, cols, h, logit):
    """Recursive forecasts at origins >= 1995-01 using rows with t' <= t-h."""
    Xm = design(J, cols); y = J.y.values; idx = J.index; out = {}; pidx = np.array([p.ordinal for p in idx])
    for i, t in enumerate(idx):
        if t < pd.Period(O.FIRST_OOS, "M"):
            continue
        tr = np.arange(0, int(np.searchsorted(pidx, (t - h).ordinal, side="right")))
        if len(tr) < 60:
            continue
        if logit:
            if y[tr].sum() < 3:
                continue
            out[t] = float(O.prob(Xm[i:i + 1], O.logit_fit(Xm[tr], y[tr]))[0])
        else:
            out[t] = float(Xm[i] @ np.linalg.lstsq(Xm[tr], y[tr], rcond=None)[0])
    return pd.Series(out)


def block_idx(n, b):
    k = int(np.ceil(n / b)); s = rng.integers(0, n - b + 1, k); return np.concatenate([np.arange(a, a + b) for a in s])[:n]


def insample(J, cols_list, logit, b, draws):
    n = len(J); y = J.y.values; Xs = [design(J, c) for c in cols_list]

    def stat(ix):
        yy = y[ix]; res = []
        for Xm in Xs:
            Xi = Xm[ix]
            if logit:
                res.append(O.loglik(Xi, yy, O.logit_fit(Xi, yy)))
            else:
                bb = np.linalg.lstsq(Xi, yy, rcond=None)[0]; e = yy - Xi @ bb; k = Xi.shape[1]
                res.append(1 - (e @ e / (n - k)) / (((yy - yy.mean()) ** 2).sum() / (n - 1)))
        return np.array(res)
    return stat(np.arange(n)), np.array([stat(block_idx(n, b)) for _ in range(draws)])


paired, vsb, subs = [], [], []
for o, h in COMBOS:
    logit = o == "recession"; step = 3 if o == "gdp" else 1
    lag = max(h // 3, 4) if step == 3 else max(h, 12)
    ratio = (lambda a, b: float(a.mean() / b.mean())) if logit else (lambda a, b: float(np.sqrt(a.mean() / b.mean())))
    for fam in O.FAMILIES:
        J = O.sample(o, h, [X[(fam, s)] for s in O.STEPS], u).rename(columns={"x0": "x_nominal", "x1": "x_real", "x2": "x_rstar"})
        cols = {"base": [], "nominal": ["x_nominal"], "real": ["x_real"], "rstar": ["x_rstar"]}
        pt, bd = insample(J, list(cols.values()), logit, 8 if step == 3 else 24, REPS)
        F = {k: oos(J, v, h, logit) for k, v in cols.items()}
        org = F["base"].index; yv = J.y.loc[org]; E = {k: (yv - F[k]) ** 2 for k in F}
        for k in ("nominal", "real", "rstar"):
            i = list(cols).index(k); adj = E["base"] - (E[k] - (F["base"] - F[k]) ** 2)
            vsb.append(dict(outcome=o, h=h, family=fam, step=k, n_is=len(J), n_oos=len(org), is_gain=pt[i] - pt[0], oos_ratio=ratio(E[k], E["base"]), cw_t=hac_t(adj, lag)))
        for A, B, prim in (("rstar", "nominal", 1), ("rstar", "real", 1), ("real", "nominal", 0)):
            ia, ib = list(cols).index(A), list(cols).index(B)
            dd = bd[:, ia] - bd[:, ib]; d = E[B] - E[A]                      # positive = A better
            paired.append(dict(outcome=o, h=h, family=fam, A=A, B=B, primary=prim, n_is=len(J), n_oos=len(org), is_diff=pt[ia] - pt[ib], is_lo90=np.percentile(dd, 5),
                               is_hi90=np.percentile(dd, 95), oos_ratio_AoverB=ratio(E[A], E[B]), dm_t=hac_t(d, lag)))
            for sk, (a, z) in O.SUBS.items():
                m = (org >= pd.Period(a, "M")) & (org <= pd.Period(z, "M"))
                if m.sum() >= 6:
                    subs.append(dict(outcome=o, h=h, family=fam, A=A, B=B, sub=sk, n=int(m.sum()), ratio_AoverB=ratio(E[A][m], E[B][m])))
    for fam in O.REFS:                                                       # NFCI, ANFCI: own-lag baseline only
        J = O.sample(o, h, [X[(fam, "ref")]], u).rename(columns={"x0": "x_ref"}); cols = {"base": [], "ref": ["x_ref"]}
        pt, _ = insample(J, list(cols.values()), logit, 8 if step == 3 else 24, 1)   # one draw, kept so the random stream matches the follow-up
        F = {k: oos(J, v, h, logit) for k, v in cols.items()}; org = F["base"].index; yv = J.y.loc[org]; E = {k: (yv - F[k]) ** 2 for k in F}
        adj = E["base"] - (E["ref"] - (F["base"] - F["ref"]) ** 2)
        vsb.append(dict(outcome=o, h=h, family=fam, step="ref", n_is=len(J), n_oos=len(org), is_gain=pt[1] - pt[0], oos_ratio=ratio(E["ref"], E["base"]), cw_t=hac_t(adj, lag)))
    print(o, h, "done", flush=True)

P = pd.DataFrame(paired); V = pd.DataFrame(vsb); SB = pd.DataFrame(subs)
P["dm_p"] = 2 * (1 - stats.norm.cdf(P.dm_t.abs())); P["is_sig"] = (P.is_lo90 > 0) | (P.is_hi90 < 0)
P["dm_p_holm"] = np.nan
for (A, B), g in P.groupby(["A", "B"]):
    P.loc[g.index, "dm_p_holm"] = holm(g.dm_p.values)
V["cw_p"] = 1 - stats.norm.cdf(V.cw_t)
P.to_csv(RES / "14_paired.csv", index=False); V.to_csv(RES / "14_vs_baseline.csv", index=False); SB.to_csv(RES / "14_subperiods.csv", index=False)

# tidy table: one row per contrast and outcome (all cells pooled over families and horizons) and an "all" row
rows = []
for (A, B), g0 in P.groupby(["A", "B"], sort=False):
    for oc, g in list(g0.groupby("outcome", sort=False)) + [("all", g0)]:
        rows.append({"contrast": f"{A}_vs_{B}", "outcome": oc, "n_tests": len(g), "mean_rmse_ratio": g.oos_ratio_AoverB.mean(), "n_ratio_below1": int((g.oos_ratio_AoverB < 1).sum()),
                     "mean_dm_t": g.dm_t.mean(), "n_dm_sig10_better": int((g.dm_t > 1.645).sum()), "n_dm_sig10_worse": int((g.dm_t < -1.645).sum()),
                     "n_holm_sig05": int((g.dm_p_holm < 0.05).sum()), "n_holm_sig10": int((g.dm_p_holm < 0.10).sum()),
                     "n_is_excludes0": int(g.is_sig.sum()), "n_is_pos": int((g.is_lo90 > 0).sum()), "n_is_neg": int((g.is_hi90 < 0).sum())})
T = pd.DataFrame(rows); T.to_csv(RES / "14_summary.csv", index=False)
for _, r in T.iterrows():
    for k in T.columns[2:]:
        S.add(f"lad_{r.contrast}_{r.outcome}_{k}", r[k])
for (A, B), g in P.groupby(["A", "B"]):
    t = f"{A}_vs_{B}"; S.add(f"lad_{t}_min_dm_p", g.dm_p.min()); S.add(f"lad_{t}_expected_by_chance_10pct", 0.1 * len(g))
# families: mean DM t and share of cells with r* better (rstar vs nominal, rstar vs real)
for B in ("nominal", "real"):
    q = P[(P.A == "rstar") & (P.B == B)].groupby("family").agg(dm_t=("dm_t", "mean"), oos_better=("dm_t", lambda s: (s > 0).mean()))
    for fam, r in q.iterrows():
        S.add(f"lad_rstar_vs_{B}_family_{fam.lower().replace('/', '').replace(' ', '_')}_mean_dm_t", r.dm_t)
# against own lags (Clark-West one-sided 10%) and references
for (oc, st), g in V.groupby(["outcome", "step"]):
    S.add(f"lad_base_{st}_{oc}_n_cw_sig10", int((g.cw_t > 1.282).sum())); S.add(f"lad_base_{st}_{oc}_n", len(g)); S.add(f"lad_base_{st}_{oc}_mean_ratio", g.oos_ratio.mean())
S.add("lad_n_cells", len(O.FAMILIES) * len(COMBOS)); S.add("lad_n_primary_tests", int(P.primary.sum()))
sb = SB[SB.A == "rstar"].groupby(["B", "outcome", "sub"]).ratio_AoverB.mean()
for (B, oc, sk), v in sb.items():
    S.add(f"lad_sub_rstar_vs_{B}_{oc}_{sk.replace('-', '_')}_mean_ratio", v)
S.save()
