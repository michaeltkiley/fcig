"""Shared design for the 1996+ re-run of the paper's core results (Note A; NO FOMC-window surprise identification; only already-estimated weights).
Reads ../../replication/{data,results,lib} and ../../followup/data; writes only ./out.

PRE-SPECIFIED DESIGN (fixed before any estimate was looked at)
 series  : Market, GS, FRB/US at nominal, real, r* (Laubach-Williams) steps (results/indexes_<step>.csv). Weights fixed (full 1996-2026 announcement sample).
 rows    : a  main: VAR 1973-01+, 12 lags, 2020 dummied; regressions origins 1976-03+, OOS from 1995-01 (as in followup/levelflow, followup2/stance)
           b  fixed 1996+ throughout: VAR 1996-01+ (12 and 4 lags, 2020 dummied); regressions origins 1996-01+; recursive OOS from the first origin with >= 96 training months
           c  excluding 2008-15: VAR with a dummy for every month 2008-01..2015-12 (and 2020); regressions drop every origin whose window t-12..t+12 touches 2008-01..2015-12
              (same rule as for 2020-21); OOS from 1995-01
           d  weights estimated on announcements through 2019 (results/weights_variants.csv, to_2019): Market only (GS, FRB/US do not use the weights); VAR 1973+, regressions as a
           e  1973+ extrapolated sample for the regressions: origins from 1974-01 (earliest with a 12-month change), OOS from the first origin with >= 100 training months
 (i)   VAR Phi(12) of the unemployment gap to a unit index shock (u first), 12 lags (4 lags in b), block bootstrap (12-month blocks, 500 draws, lib/var.py) 90% interval; Granger p (index -> u)
 (ii)  level versus flow: du = u(t+12)-u(t) and payroll growth on own lags + level + 12m flow (standardised), HAC 18: t(flow), t(level), adj-R2 gain of the flow alone
 (iii) stance: index given the funds-rate gap (FFG, step-matched): forms flow and mixed (FFG level, index flow); du and payrolls; adj-R2 gain M1->M3, t(index), recursive OOS
       Clark-West M1->M3 (training ends 12 months before the origin, expanding window), HAC 12; report first OOS date, n, number of NBER recessions in the OOS outcome windows
 (iv)  r* ladder: for du, own lags + index flow, steps compared pairwise: in-sample R2 difference (same y, same dof) with moving-block (24) paired bootstrap of origins, 1000 draws,
       and OOS MSE difference (positive = later step better) with Diebold-Mariano HAC 12 and the same block bootstrap, on the same samples
 Tests are counted in RESULT.md; shared data, so counts are descriptive. Verdict rule: COMMON.md 'holds up / fails'.
"""
import numpy as np, pandas as pd, statsmodels.api as sm, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
REP = HERE.parent.parent / "replication"
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(REP))
H = 12
STEPS = ["nominal", "real", "rstar"]
SERIES = [("market", "Market"), ("gs", "GS"), ("frbus", "FRB/US")]

def pcols(path):
    d = pd.read_csv(path, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d
def fred(name):
    d = pd.read_csv(REP.parent / "followup" / "data" / f"{name}.csv")
    s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    s.index = s.index.to_period("M"); return s

M = pcols(REP / "results" / "data_monthly.csv")
REC = fred("USREC")
IDX = {s: pcols(REP / "results" / f"indexes_{s}.csv") for s in STEPS}

def index(step, key, w2019=False):
    if w2019 and key == "market": return W2019[step]
    return IDX[step][key]

def _w2019():
    from lib import data, cases, indexes as I
    V = pd.read_csv(REP / "results" / "weights_variants.csv").set_index("variant")
    w = V.loc["to_2019", ["w_ten", "w_eq", "w_usd"]].values.astype(float)
    D = data.load(); out = {}
    for case, rs in (("nominal", None), ("real", None), ("rstar", "rstar LW")):
        X = cases.inputs(D, "rstar" if rs else case, rstar=rs or "rstar LW")
        out[case] = I.market(X, w)[0].loc["1973-01":"2026-09"]
    return out
W2019 = _w2019()

def ffg(step):
    return {"nominal": M.ffr, "real": M.ffr - M.einf_1y, "rstar": M.ffr - M.einf_1y - M["rstar LW"]}[step]

def outcomes():
    u = M.u_gap; pay = np.log(fred("PAYEMS")) * 100
    y = pd.DataFrame({"du": u.shift(-H) - u, "pay": pay.shift(-H) - pay})
    ctl = {"du": pd.DataFrame({"u": u, "du12": u - u.shift(12)}), "pay": pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))})}
    return y, ctl
Y, CTL = outcomes()
def own(yn): return list(CTL[yn].columns)

# ---- row definitions
def _in(p, a, b): return pd.Period(a, "M") <= p <= pd.Period(b, "M")
ROWS = {  # start of origins, exclusion windows (months), first OOS date gate, min training months, VAR start, VAR dummies, VAR lags
    "a": dict(start="1976-03", excl=[], first_oos="1995-01", nmin=100, var_start="1973-01", var_dum=[], lags=[12]),
    "b": dict(start="1996-01", excl=[], first_oos=None, nmin=96, var_start="1996-01", var_dum=[], lags=[12, 4]),
    "c": dict(start="1976-03", excl=[("2008-01", "2015-12")], first_oos="1995-01", nmin=100, var_start="1973-01", var_dum=[("2008-01", "2015-12")], lags=[12]),
    "d": dict(start="1976-03", excl=[], first_oos="1995-01", nmin=100, var_start="1973-01", var_dum=[], lags=[12], w2019=True),
    "e": dict(start="1974-01", excl=[], first_oos=None, nmin=100, var_start="1973-01", var_dum=[], lags=[12]),
}
ROW_LABEL = {"a": "a main (1973+ VAR; regressions 1976+)", "b": "b fixed 1996+", "c": "c excl. 2008-15", "d": "d weights thru 2019", "e": "e 1973+ extrapolated (origins 1974+)"}

def covid(p): return p.year == 2020 or (p.year == 2021 and p.month <= 3)
def keep(idx, excl):
    def bad(p):
        if covid(p): return True
        return any(_in(p, a, b) for a, b in excl)
    return np.array([not any(bad(t + k) for k in range(-12, 13)) for t in idx])

def design(yn, step, key, form, row, ff=True):
    """origins x [y, own lags, ff, idx] (+ idx_lvl, idx_flw for level-flow); regressors standardised on the sample. form: flow | mixed | lf (level+flow, no ff)."""
    R = ROWS[row]
    x = index(step, key, R.get("w2019", False)); f = ffg(step)
    cols = {"y": Y[yn]}
    for c in CTL[yn]: cols[c] = CTL[yn][c]
    if form == "lf":
        cols["lvl"] = x; cols["flw"] = x.diff(12)
    else:
        cols["ff"] = f.diff(12) if form == "flow" else f
        cols["idx"] = x.diff(12)
    D = pd.DataFrame(cols).loc[R["start"]:"2026-09"]
    D = D[keep(D.index, R["excl"])].dropna()
    for c in D.columns:
        if c not in ["y"] + own(yn): D[c] = (D[c] - D[c].mean()) / D[c].std()
    return D

def hac_ols(D, cols, lags=18):
    return sm.OLS(D.y, sm.add_constant(D[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
def mean_t(d, lags=12):
    return float(sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lags}).tvalues[0])

def oos(D, sets, row):
    """recursive (expanding) forecasts for each model in sets {name: columns}; returns DataFrame indexed by origin with y and forecasts."""
    R = ROWS[row]; rows = {}
    for t in D.index:
        if R["first_oos"] and t < pd.Period(R["first_oos"], "M"): continue
        tr = D.loc[:t - H]
        if len(tr) < R["nmin"]: continue
        r = {"y": D.loc[t, "y"]}
        for k, c in sets.items():
            b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[c].values], tr.y.values, rcond=None)[0]
            r[k] = float(b @ np.r_[1, D.loc[t, c].values.astype(float)])
        rows[t] = r
    return pd.DataFrame(rows).T

def n_recessions(origins):
    """NBER recession episodes with a month inside the outcome window (t, t+12] of some OOS origin."""
    rm = REC[REC == 1].index
    hit = set()
    for t in origins:
        for k in range(1, 13):
            if (t + k) in rm: hit.add(t + k)
    hit = sorted(hit); n = 0; prev = None
    for p in hit:
        if prev is None or (p - prev).n > 1: n += 1
        prev = p
    return n
