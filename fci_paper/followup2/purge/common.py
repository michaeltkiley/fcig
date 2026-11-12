"""Shared code for the purge analysis. Reads ../../replication/{lib,data,results} and ../../followup/data; writes only to ./out.
PRE-SPECIFIED DESIGN (fixed before any estimate was looked at):
 purge   : each index input x_t (in the form it takes at the step: nominal, real, r*-gap) regressed on a constant, u_t..u_{t-12} (unemployment gap)
           and pi_t..pi_{t-12} (12-month core PCE inflation, 100 ln(P_t/P_{t-12}), PCEPILFE; chosen over CPI because Note B uses core PCE and CPI core is not in the package).
           Residuals replace the inputs; the index is rebuilt with the unchanged market weights (market: y10, equities, dollar) or GS weights x conversion (policy, y10, bbb_spread, equities, dollar_gs).
 full    : one regression on 1973-01..2026-09.   recursive: expanding window 1973-01..t, first residual 1983-01 (120 obs), coefficients re-estimated every month.
 flow    : x_t - x_{t-12}.  Index residuals are demeaned over their own available sample (level shift only).
 LP      : 12-month change in unemployment gap and 12-month payroll growth on standardised level and flow jointly, with own lags (levelflow design), HAC(18). Origins from 1976-03 (unpurged, full) and from 1983-03 (all three, same sample).
 VAR     : lib/var.py, 12 lags, 1973-01 (unpurged, full) or 1983-01 (all three), 500 block-bootstrap draws.
 primary : market r*-gap, unemployment-gap outcome: flow t-statistic and Phi(12) interval, purged vs unpurged on the same sample.
"""
import sys, numpy as np, pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
REP = HERE.parents[1] / "replication"
sys.path.insert(0, str(REP))
from lib import data, cases, indexes as I
from lib.config import START, END
LAGS = 12
FIRST_REC = "1983-01"
STEPS = ("nominal", "real", "rstar")
VARS = {"market": I.MARKET_VARS, "gs": list(I.GS_W)}

def core_inflation():
    d = pd.read_csv(HERE.parents[1] / "followup" / "data" / "PCEPILFE.csv")
    s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.PeriodIndex(pd.to_datetime(d.iloc[:, 0]), freq="M")).dropna()
    return 100 * np.log(s / s.shift(12))

def regressors(u, pi):
    cols = {}
    for l in range(LAGS + 1):
        cols[f"u{l}"] = u.shift(l); cols[f"pi{l}"] = pi.shift(l)
    return pd.DataFrame(cols).loc[START:END]

def purge_full(x, Z):
    b = np.linalg.lstsq(np.c_[np.ones(len(Z)), Z.values], x.values, rcond=None)[0]
    fit = np.c_[np.ones(len(Z)), Z.values] @ b
    r2 = 1 - ((x.values - fit) ** 2).sum() / ((x.values - x.mean()) ** 2).sum()
    return x - fit, r2

def purge_recursive(x, Z):
    A = np.c_[np.ones(len(Z)), Z.values]; y = x.values
    res = np.full(len(y), np.nan)
    for t in range(len(y)):
        if x.index[t] < pd.Period(FIRST_REC, "M"): continue
        b = np.linalg.lstsq(A[:t + 1], y[:t + 1], rcond=None)[0]
        res[t] = y[t] - A[t] @ b
    return pd.Series(res, index=x.index)

def build_index(X, kind, conv):
    """index (level) from (possibly purged) inputs X. Demeans over the available sample."""
    cols = VARS[kind]
    Xd = X[cols] - X[cols].dropna().mean()
    if kind == "market":
        w = pd.read_csv(REP / "results" / "market_weights.csv", index_col=0).weight
        return (Xd * w.values).sum(axis=1, min_count=len(cols))
    return (Xd * pd.Series(I.GS_W)[cols] * conv).sum(axis=1, min_count=len(cols))

def all_inputs():
    """dict step -> X (inputs of that step)."""
    D = data.load()
    out = {}
    for s in STEPS:
        out[s] = cases.inputs(D, "rstar" if s == "rstar" else s, rstar="rstar LW")
    return D, out

def load_purged():
    """dict (kind, step, version) -> level series; version in unpurged/full/recursive."""
    return {tuple(c.split("|")): s for c, s in pd.read_csv(OUT / "purged_indexes.csv", index_col=0).items()} if False else \
        {tuple(c.split("|")): pd.Series(v.values, index=pd.PeriodIndex(v.index, freq="M")) for c, v in pd.read_csv(OUT / "purged_indexes.csv", index_col=0).items()}
