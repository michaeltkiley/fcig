"""Step 3c. First stage of alternative USMPD instruments (monthly sums over the NS event set): MP1 (current-meeting funds-rate surprise), MP2 (next-meeting), ED4 (about 9-12 months ahead; closest to
the one-year horizon of Gertler-Karadi's policy indicator), path = ED4 not explained by MP1, UST2Y (event-window change of the 2-year yield), and ns. VAR residuals as in 03_instruments.py (r*-gap index,
12 lags, 2020 dummies). Output: 03c_alt_instruments.log"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "fci_note" / "replication"))
from fci import indexes as I

M = pd.read_csv(HERE / "data/mp_monthly.csv", index_col=0); M.index = pd.PeriodIndex(M.index, freq="M")
ev = I.events().copy(); ev["m"] = ev.Date.dt.to_period("M")
b = sm.OLS(ev.ED4.values, sm.add_constant(ev.MP1.values)).fit(); ev["path"] = b.resid
S = {k: ev.groupby("m")[k].sum().reindex(M.index).fillna(0.0) for k in ("ns", "MP1", "MP2", "ED4", "path", "UST2Y")}
print("Monthly instruments: sd (pp)  " + "  ".join(f"{k} {v.std():.3f}" for k, v in S.items()))


def resid(cols, vstart):
    X = M.loc[vstart:"2026-09", cols].dropna()
    dum = pd.DataFrame({f"d{k:02d}": (X.index == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}, index=X.index)
    X = X.copy(); X.index = X.index.to_timestamp(); dum.index = X.index
    e = VAR(X, exog=dum).fit(12).resid; e.index = e.index.to_period("M"); return e.loc["1994-01":]


print("\nFirst-stage F (robust t^2) of each instrument on the VAR residual; S1 = VAR from 1994, S2 = long VAR (funds rate from 1973, 2-year from 1976-06)")
print("   instrument   |  S1: ffr   gs2   index |  S2: ffr   gs2   index")
res = {}
for lab, vs in (("S1", {"ffr": "1994-01", "gs2": "1994-01"}), ("S2", {"ffr": "1973-01", "gs2": "1976-06"})):
    for pv in ("ffr", "gs2"):
        res[(lab, pv)] = resid(["u_gap", "pi_core", pv, "market_rstar"], vs[pv])
for k, z in S.items():
    row = []
    for lab in ("S1", "S2"):
        for what in ("ffr", "gs2", "market_rstar"):
            e = res[(lab, "ffr" if what != "gs2" else "gs2")][what]
            r = sm.OLS(e.values, sm.add_constant(z.reindex(e.index).values)).fit(cov_type="HC1"); row.append(r.tvalues[1] ** 2)
    print(f"   {k:11s} |  {row[0]:5.1f} {row[1]:5.1f} {row[2]:6.1f} |  {row[3]:5.1f} {row[4]:5.1f} {row[5]:6.1f}")
