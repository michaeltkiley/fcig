"""Shared loading and design for the level-versus-flow analysis. Reads ../../replication/{data,results} and ../data; writes only to ./out.
PRE-SPECIFIED DESIGN (fixed before any estimate was looked at):
 series : market, GS, FRB/US (level), FCI-G 1-year lookback at nominal/real/rstar; NFCI, ANFCI as given (14 series)
 level  : x_t ; flow : x_t - x_{t-12}  (both standardised; fit is invariant to scale)
 outcomes (h=12): change in unemployment gap u(t+12)-u(t); payroll growth 100 ln(PAYEMS(t+12)/PAYEMS(t)); GDP growth 100 ln(GDP(q+4)/GDP(q)) (quarterly)
 own lags: u: u_t and 12m change of u; payrolls: past 12m growth and past 3m growth (annualised); GDP: past 4q growth
 sample : t from 1976-03 (common start); any t whose window t-12..t+12 touches 2020-01..2021-03 is dropped; same rule in quarters
 OOS    : recursive from 1995-01 (1995Q1), training sample ends h before the forecast origin
"""
import numpy as np, pandas as pd, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
REP = HERE.parent.parent / "replication"
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
H = 12
START, FIRST_OOS, LAST = "1976-03", "1995-01", "2026-09"

def fred(name):
    d = pd.read_csv(HERE.parent / "data" / f"{name}.csv")
    return pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()

def monthly(name):
    s = fred(name); s.index = s.index.to_period("M"); return s

def covid(p): return p.year == 2020 or (p.year == 2021 and p.month <= 3)

def load_indexes():
    """dict label -> (step, monthly series)"""
    out = {}
    for step in ("nominal", "real", "rstar"):
        I = pd.read_csv(REP / "results" / f"indexes_{step}.csv", index_col=0); I.index = pd.PeriodIndex(I.index, freq="M")
        for k, lab in (("market", "Market"), ("gs", "GS"), ("frbus", "FRB/US"), ("fcig_1yr", "FCI-G")):
            out[f"{lab}|{step}"] = I[k]
        if step == "rstar":
            out["NFCI|given"] = I["nfci"]; out["ANFCI|given"] = I["anfci"]
    return out

def u_gap():
    D = pd.read_csv(REP / "results" / "data_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
    return D.u_gap

def outcomes():
    u = u_gap(); pay = np.log(monthly("PAYEMS")) * 100
    y = pd.DataFrame({"du": u.shift(-H) - u, "pay": pay.shift(-H) - pay})
    ctl = {"du": pd.DataFrame({"u": u, "du12": u - u.shift(12)}), "pay": pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))})}
    return y, ctl

def keep_mask(idx):
    return np.array([not any(covid(t + k) for k in range(-12, 13, 1)) for t in idx])

def monthly_design(x, yname):
    """DataFrame y, own lag controls, lvl, flow (standardised); rows = origins t."""
    y, ctl = outcomes()
    D = pd.concat([y[yname].rename("y"), ctl[yname], x.rename("lvl"), (x - x.shift(12)).rename("flw")], axis=1)
    D = D.loc[START:LAST]
    D = D[keep_mask(D.index)].dropna()
    for c in ("lvl", "flw"): D[c] = (D[c] - D[c].mean()) / D[c].std()
    return D

def quarterly_design(x):
    g = np.log(fred("GDPC1")) * 100; g.index = g.index.to_period("Q")
    y = g.shift(-4) - g; own = (g - g.shift(4)).rename("g4")
    xq = x.copy(); xq = xq[xq.index.month.isin([3, 6, 9, 12])]; xq.index = xq.index.asfreq("Q")  # quarter-end reading
    D = pd.concat([y.rename("y"), own, xq.rename("lvl"), (xq - xq.shift(4)).rename("flw")], axis=1).loc["1976Q1":"2026Q2"]
    D = D[[not any((q + k).year == 2020 or ((q + k).year == 2021 and (q + k).quarter == 1) for k in range(-4, 5)) for q in D.index]].dropna()
    for c in ("lvl", "flw"): D[c] = (D[c] - D[c].mean()) / D[c].std()
    return D

def recession_months():
    r = monthly("USREC"); return r
