"""Index inputs for the three steps of the construction: nominal, real, and gaps to r* (the baseline).

nominal  rates as published; equities 100 ln CAPE; dollar real broad (market and FRB/US indexes) or nominal broad (GS, FCI-G, as published)
real     each rate less expected inflation at a matched horizon: policy rate - 1-year, longer rates - 10-year; the dollar real; stock and house prices over CPI (FCI-G)
rstar    each real rate less r*; equities as the earnings-yield gap E/P - r* (E/P = 100 / CAPE), converted to CAPE log points at the average E/P so that each
         index keeps its CAPE weight: x = -(100 / mean E/P) (E/P - r*); spreads over the 10-year are unchanged (r* cancels)
"""
import numpy as np, pandas as pd
from .data import START, END

CASES = ["nominal", "real", "rstar"]


def house_gap(D):
    """FRB/US house-price variable: 100 ln (house price / CPI rent), as a deviation from its trailing 15-year (180-month) average."""
    r = 100 * np.log(D.house / D.rent)
    return r - r.rolling(180).mean()


def inputs(D, case, rstar="rstar LW"):
    """Monthly inputs of every index for one case. Columns:
    policy, y10, baa_yield, mortgage_yield (rates); bbb_spread, mortgage_spread; equities (CAPE log points); dollar (100 ln, real broad);
    dollar_gs (the dollar used by GS and FCI-G); house (FRB/US variable); stocks_level, house_level (FCI-G price levels)."""
    e1, e10 = (D.einf_1y, D.einf_10y) if case != "nominal" else (0.0, 0.0)
    r = D[rstar] if case == "rstar" else 0.0
    X = pd.DataFrame(index=D.index)
    X["policy"] = D.ffr - e1 - r
    X["y10"] = D.y10 - e10 - r
    X["baa_yield"] = D.baa - e10 - r
    X["mortgage_yield"] = D.mortgage - e10 - r
    X["bbb_spread"] = D.baa - D.y10
    X["mortgage_spread"] = D.mortgage - D.y10
    if case == "rstar":
        ep = 100 / D.cape
        X["equities"] = -(100 / ep.loc[START:END].mean()) * (ep - r)
    else:
        X["equities"] = 100 * np.log(D.cape)
    X["dollar"] = 100 * np.log(D.usd_real)
    X["dollar_gs"] = 100 * np.log(D.usd_nominal if case == "nominal" else D.usd_real)
    X["house"] = house_gap(D)
    X["stocks_level"] = D.sp500 if case == "nominal" else D.sp500 / D.cpi
    if case == "rstar":
        X["stocks_level"] = np.exp(X.equities / 100)          # FCI-G stock term: change of the earnings-yield gap (in CAPE log points)
    X["house_level"] = D.house if case == "nominal" else D.house / D.cpi
    return X


def demean(X):
    return X - X.loc[START:END].mean()
