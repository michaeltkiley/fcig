"""Shared designs for steps 09 (level versus flow) and 10 (NFCI). Reads RES and DATA only.
Own lags: unemployment-gap change: u_t and its 12-month change; payroll growth: past 12-month growth and past 3-month growth (annualised).
Regressors are standardised on the estimation sample (fit is invariant to scale). Origins from 1976-03; any origin whose window touches
2020-01..2021-03 is dropped."""
import numpy as np, pandas as pd
from .config import RES, DATA

START, FIRST_OOS, LAST = "1976-03", "1995-01", "2026-09"


def fred(name):
    d = pd.read_csv(DATA / f"{name}.csv")
    return pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()


def monthly(name):
    s = fred(name); s.index = s.index.to_period("M"); return s


def weekly_to_month(name):
    s = fred(name); return s.groupby(s.index.to_period("M")).mean()


def covid(p):
    return p.year == 2020 or (p.year == 2021 and p.month <= 3)


def read_res(name):
    d = pd.read_csv(RES / name, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def u_gap():
    return read_res("data_monthly.csv").u_gap


def outcomes(h):
    """dict: du and pay -> (y, own-lag frame) at horizon h."""
    u = u_gap(); pay = np.log(monthly("PAYEMS")) * 100
    return {"du": (u.shift(-h) - u, pd.DataFrame({"u": u, "du12": u - u.shift(12)})),
            "pay": (pay.shift(-h) - pay, pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))}))}


def recession_future(idx):
    rec = monthly("USREC").reindex(pd.period_range("1970-01", "2026-12", freq="M")).fillna(0)
    return pd.Series([rec.loc[t + 1:t + 12].max() for t in idx], index=idx)


def standardise(F, cols):
    for c in cols:
        F[c] = (F[c] - F[c].mean()) / F[c].std()
    return F
