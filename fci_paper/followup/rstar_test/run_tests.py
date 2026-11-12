"""Paired comparison of nominal / real / r*-gap versions of each index in predicting later activity.
Pre-specified design: 7 index families x 3 steps (+ NFCI, ANFCI as references), horizons 6/12/24 months for ugap, payroll, gdp, corepce (12 combos
of outcome x h per family) and h=12 for recession (1 combo): 13 combos. Primary contrasts: r* vs nominal, r* vs real (secondary: real vs nominal).
Predictor: current reading x(t) plus own-lag control (u gap level; trailing 12m growth; USREC(t)).
In sample: adj. R2 (log-likelihood for the logit) difference with 90% moving-block bootstrap (24 months, 8 quarters). Out of sample: recursive from 1995-01, DM on squared (Brier) loss differential.
Writes out/paired.csv, out/vs_baseline.csv, out/subperiods.csv"""
import numpy as np, pandas as pd, statsmodels.api as sm
from common import *
import sys
NB = int(sys.argv[1]) if len(sys.argv) > 1 else 500; rng = np.random.default_rng(20261111)
X = predictors()
COMBOS = [(o, h) for o in ("ugap", "payroll", "gdp", "corepce") for h in HORIZONS] + [("recession", 12)]

def design(J, cols): return np.c_[np.ones(len(J)), J[["c"] + cols].values]

def hac_t(d, lag):
    d = np.asarray(d); return float(sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lag}).tvalues[0])

def oos(J, cols, h, logit):
    """recursive forecasts at origins >= 1995-01 using rows with t' <= t-h. Returns Series of forecasts indexed by origin."""
    Xm = design(J, cols); y = J.y.values; idx = J.index; out = {}; pidx = np.array([p.ordinal for p in idx])
    for i, t in enumerate(idx):
        if t < pd.Period(FIRST_OOS, "M"): continue
        tr = np.arange(0, int(np.searchsorted(pidx, (t - h).ordinal, side="right")))
        if len(tr) < 60: continue
        if logit:
            if y[tr].sum() < 3: continue
            out[t] = float(prob(Xm[i:i + 1], logit_fit(Xm[tr], y[tr]))[0])
        else:
            b = np.linalg.lstsq(Xm[tr], y[tr], rcond=None)[0]; out[t] = float(Xm[i] @ b)
    return pd.Series(out)

def block_idx(n, b):
    k = int(np.ceil(n / b)); s = rng.integers(0, n - b + 1, k); return np.concatenate([np.arange(a, a + b) for a in s])[:n]

def insample(J, cols_list, logit, b, draws):
    """in-sample fit stat per spec: adj R2 (or LL). returns point values, and bootstrap draws (same rows for every spec)."""
    n = len(J); y = J.y.values; Xs = [design(J, c) for c in cols_list]
    def stat(ix):
        yy = y[ix]; res = []
        for Xm in Xs:
            Xi = Xm[ix]
            if logit: res.append(loglik(Xi, yy, logit_fit(Xi, yy)))
            else:
                bb = np.linalg.lstsq(Xi, yy, rcond=None)[0]; e = yy - Xi @ bb; k = Xi.shape[1]
                res.append(1 - (e @ e / (n - k)) / (((yy - yy.mean()) ** 2).sum() / (n - 1)))
        return np.array(res)
    pt = stat(np.arange(n)); bd = np.array([stat(block_idx(n, b)) for _ in range(draws)])
    return pt, bd

paired, vsb, subs = [], [], []
for o, h in COMBOS:
    logit = o == "recession"; step = 3 if o == "gdp" else 1
    for fam in FAMILIES:
        xs = [X[(fam, s)] for s in STEPS]
        J, _ = sample(o, h, xs); J = J.rename(columns={"x0": "x_nominal", "x1": "x_real", "x2": "x_rstar"})
        cols = {"base": [], "nominal": ["x_nominal"], "real": ["x_real"], "rstar": ["x_rstar"]}
        # in sample
        b = 8 if step == 3 else 24
        pt, bd = insample(J, list(cols.values()), logit, b, NB)
        # out of sample forecasts
        F = {k: oos(J, v, h, logit) for k, v in cols.items()}
        org = F["base"].index; yv = J.y.loc[org]
        E = {k: (yv - F[k]) ** 2 for k in F}  # squared (Brier) loss
        lag = max(h // 3, 4) if step == 3 else max(h, 12)
        for k in ("nominal", "real", "rstar"):
            i = list(cols).index(k)
            # Clark-West vs baseline (nested); for the logit the adjustment is the same on probabilities
            adj = E["base"] - (E[k] - (F["base"] - F[k]) ** 2)
            vsb.append(dict(outcome=o, h=h, family=fam, step=k, n_is=len(J), n_oos=len(org), is_gain=pt[i] - pt[0], oos_ratio=float(np.sqrt(E[k].mean() / E["base"].mean())) if not logit else float(E[k].mean() / E["base"].mean()),
                            cw_t=hac_t(adj, lag), dm_vs_base_t=hac_t(E["base"] - E[k], lag)))
        for A, B, prim in (("rstar", "nominal", 1), ("rstar", "real", 1), ("real", "nominal", 0)):
            ia, ib = list(cols).index(A), list(cols).index(B)
            dd = bd[:, ia] - bd[:, ib]; d = E[B] - E[A]  # positive = A better
            paired.append(dict(outcome=o, h=h, family=fam, A=A, B=B, primary=prim, n_is=len(J), n_oos=len(org), is_diff=pt[ia] - pt[ib],
                               is_lo90=np.percentile(dd, 5), is_hi90=np.percentile(dd, 95),
                               is_boot_p_pos=float((dd > 0).mean()), oos_ratio_AoverB=float(np.sqrt(E[A].mean() / E[B].mean())) if not logit else float(E[A].mean() / E[B].mean()),
                               dm_t=hac_t(d, lag)))
            for sk, (a, z) in SUBS.items():
                m = (org >= pd.Period(a, "M")) & (org <= pd.Period(z, "M"))
                if m.sum() < 6: continue
                subs.append(dict(outcome=o, h=h, family=fam, A=A, B=B, sub=sk, n=int(m.sum()), ratio_AoverB=float(np.sqrt(E[A][m].mean() / E[B][m].mean())) if not logit else float(E[A][m].mean() / E[B][m].mean()),
                                 diff_share_of_mseB=float(d[m].sum() / E[B].sum())))

    for fam in REFS:  # NFCI, ANFCI: no step; compared with the own-lag baseline only
        J, _ = sample(o, h, [X[(fam, "ref")]]); J = J.rename(columns={"x0": "x_ref"})
        cols = {"base": [], "ref": ["x_ref"]}
        pt, bd = insample(J, list(cols.values()), logit, 8 if step == 3 else 24, 1)
        F = {k: oos(J, v, h, logit) for k, v in cols.items()}; org = F["base"].index; yv = J.y.loc[org]; E = {k: (yv - F[k]) ** 2 for k in F}
        lag = max(h // 3, 4) if step == 3 else max(h, 12); adj = E["base"] - (E["ref"] - (F["base"] - F["ref"]) ** 2)
        vsb.append(dict(outcome=o, h=h, family=fam, step="ref", n_is=len(J), n_oos=len(org), is_gain=pt[1] - pt[0], oos_ratio=float(np.sqrt(E["ref"].mean() / E["base"].mean())) if not logit else float(E["ref"].mean() / E["base"].mean()),
                        cw_t=hac_t(adj, lag), dm_vs_base_t=hac_t(E["base"] - E["ref"], lag)))
    print(o, h, "done", flush=True)
P = pd.DataFrame(paired)
P.to_csv(OUT / "paired.csv", index=False); pd.DataFrame(vsb).to_csv(OUT / "vs_baseline.csv", index=False); pd.DataFrame(subs).to_csv(OUT / "subperiods.csv", index=False)
