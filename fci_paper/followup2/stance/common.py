"""Shared design for the stance analysis (Note A; NO FOMC-window surprises; only the already-estimated market weights). Reads ../../replication/{data,results} and ../../followup/data; writes only ./out.
PRE-SPECIFIED DESIGN (fixed before any estimate was looked at):
 question : does an index add to the funds-rate gap (FFG) in explaining the economy 12 months ahead?
 FFG      : nominal step FEDFUNDS; real step FEDFUNDS - 1-year expected inflation; r* step FEDFUNDS - 1-year expected inflation - r* (Laubach-Williams) [lib/cases.py, same series as the indexes]
 indexes  : Market, GS, FRB/US at each step (results/indexes_<step>.csv)
 forms    : level   FFG_t and index_t
            flow    12-month changes of both
            mixed   FFG level with index 12-month change
 outcomes : h=12 change of the unemployment gap; 12-month payroll growth; 12-month core PCE inflation (own lags: u, 12m change of u; payroll g12, g3; inflation pi12, pi3)
 models   : M0 own lags; M1 +FFG; M2 +index; M3 +FFG +index (all regressors standardised on the common sample)
 sample   : origins 1976-03 to 2025-09; origins whose window t-12..t+12 touches 2020-01..2021-03 dropped
 in sample: HAC (Newey-West) 18 lags full sample, 12 lags in sub-periods
 OOS      : recursive from 1995-01, training sample ends h before the origin; RMSE ratio, Diebold-Mariano and Clark-West (nested), HAC 12; t>0 = larger model better
 periods  : full; pre2009 (1995-2008 OOS); zlb 2009-01..2015-12; post 2022-01..2026-09 (origins 2022-04..2025-09 survive the covid rule)
 primary  : Market, r* step, 3 outcomes x 3 forms, full-sample OOS Clark-West M1 -> M3 (index given FFG): 9 tests, Holm. Everything else is descriptive; shared data.
"""
import numpy as np, pandas as pd, statsmodels.api as sm
from pathlib import Path
HERE = Path(__file__).resolve().parent
REP = HERE.parent.parent / "replication"
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
H = 12; START, FIRST_OOS, LAST = "1976-03", "1995-01", "2026-09"
STEPS = ["nominal", "real", "rstar"]; INDEXES = {"market": "Market", "gs": "GS", "frbus": "FRB/US"}
FORMS = ["level", "flow", "mixed"]; OUTCOMES = ["du", "pay", "pi"]
PERIODS = {"full": ("1995-01", "2026-09"), "pre2009": ("1995-01", "2008-12"), "zlb": ("2009-01", "2015-12"), "post": ("2022-01", "2026-09")}

def pcols(path):
    d = pd.read_csv(path, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d
def fred(name):
    d = pd.read_csv(REP.parent / "followup" / "data" / f"{name}.csv")
    s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    s.index = s.index.to_period("M"); return s
def covid(p): return p.year == 2020 or (p.year == 2021 and p.month <= 3)
def keep_mask(idx): return np.array([not any(covid(t + k) for k in range(-12, 13)) for t in idx])

M = pcols(REP / "results" / "data_monthly.csv")
def ffg(step, rstar="rstar LW"):
    return {"nominal": M.ffr, "real": M.ffr - M.einf_1y, "rstar": M.ffr - M.einf_1y - M[rstar]}[step]
def index(step, key):
    return pcols(REP / "results" / f"indexes_{step}.csv")[key]

def outcomes():
    u = M.u_gap; pay = np.log(fred("PAYEMS")) * 100; px = np.log(fred("PCEPILFE")) * 100
    y = pd.DataFrame({"du": u.shift(-H) - u, "pay": pay.shift(-H) - pay, "pi": px.shift(-H) - px})
    ctl = {"du": pd.DataFrame({"u": u, "du12": u - u.shift(12)}),
           "pay": pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))}),
           "pi": pd.DataFrame({"p12": px - px.shift(12), "p3": 4 * (px - px.shift(3))})}
    return y, ctl
Y, CTL = outcomes()

def design(yname, f, x, form):
    """origins x [y, own lags, ff, idx], regressors standardised; f, x are level series."""
    ff = f.diff(12) if form == "flow" else f
    ix = x.diff(12) if form in ("flow", "mixed") else x
    D = pd.concat([Y[yname].rename("y"), CTL[yname], ff.rename("ff"), ix.rename("idx")], axis=1).loc[START:LAST]
    D = D[keep_mask(D.index)].dropna()
    for c in ("ff", "idx"): D[c] = (D[c] - D[c].mean()) / D[c].std()
    return D

def own(yname): return list(CTL[yname].columns)
def hac_ols(D, cols, lags):
    return sm.OLS(D.y, sm.add_constant(D[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
def mean_t(d, lags=12):
    r = sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lags}); return float(r.tvalues[0])

def oos(D, ow):
    """recursive forecasts for M0..M3; returns DataFrame of forecasts and actual indexed by origin."""
    sets = {"M0": ow, "M1": ow + ["ff"], "M2": ow + ["idx"], "M3": ow + ["ff", "idx"]}
    rows = {}
    for t in pd.period_range(FIRST_OOS, "2025-09", freq="M"):
        if t not in D.index: continue
        tr = D.loc[:t - H]
        if len(tr) < 100: continue
        r = {"y": D.loc[t, "y"]}
        for k, c in sets.items():
            b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[c].values], tr.y.values, rcond=None)[0]
            r[k] = float(b @ np.r_[1, D.loc[t, c].values.astype(float)])
        rows[t] = r
    return pd.DataFrame(rows).T
