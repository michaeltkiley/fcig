"""NFCI follow-up. Reads ../../replication/{data,results}, ../../followup/data; writes only ./out.
PRE-SPECIFIED DESIGN (fixed before estimates were seen):
 indexes: MKT flow = 12m change of market r*-gap index (results/indexes_rstar.csv); MKT level; NFCI, ANFCI level = monthly mean of raw weekly series (data/NFCI.csv, ANFCI.csv)
 all regressors standardised on the estimation sample. Own lags as in followup/levelflow: du: u_t, 12m change in u; pay: past 12m growth, past 3m growth (annualised); GDP: past 4q growth.
 outcomes: du = u(t+h)-u(t), pay = 100 ln(PAYEMS(t+h)/PAYEMS(t)), h=6,12,24 months; GDP growth over 2,4,8 quarters; recession = any NBER recession month in t+1..t+12 (logit).
 sample: origins 1976-03 on (common to all); origins whose window t-12..t+h touches 2020-01..2021-03 dropped.
 (a) joint: own + MKT flow + NFCI level; own + MKT flow + ANFCI level. 2 x (3 outcomes x 3 horizons) = 18 mean regressions + 2 logits = 20 joint models, 40 coefficients of interest.
     inference: HAC with h+6 lags (>=12) as primary; moving-block bootstrap of rows (block h+6, 999 draws) 90% interval as a check.
 (b) recursive OOS from 1995-01 (1995Q1), training ends h before origin, expanding: models Mkt, NFCI, ANFCI, joint, equal-weight combo. Tests: Clark-West (joint vs each single; nested),
     DM on MSE for combo vs each single, encompassing regression (y-fN) on (fM-fN).
 (c) R2 of NFCI on market weights variables (10y, CAPE, real dollar) and plus Baa-10y; levels and 12m changes. NFCI contributions file absent locally -> skipped.
 (d) NFCI/ANFCI level vs flow vs both, same outcomes.
"""
import numpy as np, pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent
REP = HERE.parent.parent / "replication"
FDATA = HERE.parent.parent / "followup" / "data"
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
START, FIRST_OOS, LAST = "1976-03", "1995-01", "2026-09"

def fred(path):
    d = pd.read_csv(path)
    return pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
def monthly_fdata(name):
    s = fred(FDATA / f"{name}.csv"); s.index = s.index.to_period("M"); return s
def weekly_to_month(name):
    s = fred(REP / "data" / f"{name}.csv"); return s.groupby(s.index.to_period("M")).mean()
def covid(p): return p.year == 2020 or (p.year == 2021 and p.month <= 3)

def M():
    I = pd.read_csv(REP / "results" / "indexes_rstar.csv", index_col=0); I.index = pd.PeriodIndex(I.index, freq="M")
    D = pd.read_csv(REP / "results" / "data_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
    X = pd.DataFrame({"mkt": I["market"], "nfci": weekly_to_month("NFCI"), "anfci": weekly_to_month("ANFCI")})
    X["mkt_flw"] = X.mkt - X.mkt.shift(12)
    return X, D

def design(h, outcome, xcols, X=None, D=None):
    """monthly design for outcome in {du,pay}; returns DataFrame y, own lags, xcols standardised"""
    if X is None: X, D = M()
    u = D.u_gap; pay = np.log(monthly_fdata("PAYEMS")) * 100
    if outcome == "du": y = u.shift(-h) - u; own = pd.DataFrame({"u": u, "du12": u - u.shift(12)})
    else: y = pay.shift(-h) - pay; own = pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))})
    F = pd.concat([y.rename("y"), own, X[xcols]], axis=1).loc[START:LAST]
    F = F[[not any(covid(t + k) for k in range(-12, h + 1)) for t in F.index]].dropna()
    for c in xcols: F[c] = (F[c] - F[c].mean()) / F[c].std()
    return F, list(own.columns)

def design_rec(xcols, X=None, D=None):
    if X is None: X, D = M()
    rec = monthly_fdata("USREC").reindex(pd.period_range("1970-01", "2026-12", freq="M")).fillna(0)
    F = X[xcols].loc[START:LAST].copy()
    F["y"] = [rec.loc[t + 1:t + 12].max() for t in F.index]
    F = F[[not any(covid(t + k) for k in range(-12, 13)) for t in F.index]].dropna()
    for c in xcols: F[c] = (F[c] - F[c].mean()) / F[c].std()
    return F

def design_gdp(hq, xcols, X=None, D=None):
    if X is None: X, D = M()
    g = np.log(monthly_fdata("GDPC1") if False else _q("GDPC1")) * 100
    y = g.shift(-hq) - g; own = (g - g.shift(4)).rename("g4")
    Xq = X[xcols][X.index.month.isin([3, 6, 9, 12])].copy(); Xq.index = Xq.index.asfreq("Q")
    F = pd.concat([y.rename("y"), own, Xq], axis=1).loc["1976Q1":"2026Q2"]
    F = F[[not any(((q + k).year == 2020) or ((q + k).year == 2021 and (q + k).quarter == 1) for k in range(-4, hq + 1)) for q in F.index]].dropna()
    for c in xcols: F[c] = (F[c] - F[c].mean()) / F[c].std()
    return F, ["g4"]
def _q(name):
    s = fred(FDATA / f"{name}.csv"); s.index = s.index.to_period("Q"); return s
