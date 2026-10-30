"""Step 2a. Lag length for the four-variable VAR (unemployment gap, core PCE monthly, funds rate, market index), long (1973-) and matched (1994-) windows,
2020 monthly dummies. Information criteria for 1..24 lags, and a residual-autocorrelation test at the candidate lag lengths. Index case: r*-gap (main).
Output: 02a_lags.log"""
import warnings
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")

D = pd.read_csv("data/mp_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")


def dummies(idx):
    return pd.DataFrame({f"d2020_{k:02d}": (idx == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}, index=idx)


def sample(start, cols):
    X = D.loc[start:"2026-09", cols].dropna()
    dum = dummies(X.index); X.index = X.index.to_timestamp(); dum.index = X.index
    return X, dum


for lab, start in (("long 1973-01..2026-09", "1973-01"), ("matched 1994-01..2026-09", "1994-01")):
    for sysname, cols in (("with index", ["u_gap", "pi_core", "ffr", "market_rstar"]), ("without index", ["u_gap", "pi_core", "ffr"])):
        X, dum = sample(start, cols)
        # common estimation sample across lag lengths: drop first 24 observations from the fit window (statsmodels' ic uses the same T for all p when trend/exog fixed)
        res = VAR(X, exog=dum).select_order(maxlags=24)
        ic = pd.DataFrame(res.ics)
        ic.index = range(0, 25)
        print(f"\n== {lab}, {sysname}, T = {len(X)} ==  selected: " + ", ".join(f"{k.upper()} {v}" for k, v in res.selected_orders.items()))
        for p in (6, 12, 18, 24):
            r = VAR(X, exog=dum).fit(p)
            w = r.test_whiteness(nlags=p + 12, adjusted=True)           # Ljung-Box/Portmanteau for autocorrelation up to p + 12 lags
            lm = [r.test_serial_correlation_lm if hasattr(r, "test_serial_correlation_lm") else None]
            print(f"  p={p:2d}: AIC {r.aic:8.3f} BIC {r.bic:8.3f} HQIC {r.hqic:8.3f}  portmanteau({p + 12}) p-value {w.pvalue:.3f}   free params/eq {r.k_ar * len(cols) + 1 + 12}")
