"""Step 3b. Does the first stage improve with month-END policy variables (daily DGS2 2-year yield, DFF funds rate) instead of monthly averages?
A mid-month surprise only partly enters a monthly average. Same VAR (u gap, core PCE, policy variable, r*-gap index; 12 lags; 2020 dummies; window 1994-2026 = S1 and long VAR = S2),
instrument ns and own-purge bs from data/mp_instruments.csv. The index stays a monthly average (no daily index in the data set).
Output: 03b_monthend.log, data/DGS2.csv, data/DFF.csv"""
import re, subprocess, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
UA = "fcig-replication/1.0 (+https://michaeltkiley.github.io/fcig/)"


def fred(n):
    f = HERE / f"data/{n}.csv"
    if not f.exists():
        txt = subprocess.run(["curl", "-sS", "-L", "--http1.1", "-m", "120", "-A", UA, f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={n}&cosd=1950-01-01"], capture_output=True, text=True).stdout.strip().splitlines()
        rows = [(a, b) for a, _, b in (l.partition(",") for l in txt[1:]) if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", a) and re.fullmatch(r"-?[0-9.]+", b) and b != "."]
        assert len(rows) > 1000, n
        pd.DataFrame(rows, columns=["observation_date", n]).to_csv(f, index=False)
    d = pd.read_csv(f); return pd.Series(d[n].values.astype(float), index=pd.to_datetime(d["observation_date"]))


M = pd.read_csv(HERE / "data/mp_monthly.csv", index_col=0); M.index = pd.PeriodIndex(M.index, freq="M")
Z = pd.read_csv(HERE / "data/mp_instruments.csv", index_col=0); Z.index = pd.PeriodIndex(Z.index, freq="M")
for n, new in (("DGS2", "gs2_end"), ("DFF", "ffr_end")):
    s = fred(n); M[new] = s.groupby(s.index.to_period("M")).last().reindex(M.index)


def resid(cols, vstart):
    X = M.loc[vstart:"2026-09", cols].dropna()
    dum = pd.DataFrame({f"d{k:02d}": (X.index == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}, index=X.index)
    X = X.copy(); X.index = X.index.to_timestamp(); dum.index = X.index
    e = VAR(X, exog=dum).fit(12).resid; e.index = e.index.to_period("M"); return e.loc["1994-01":]


print("First stage (robust t, F = t^2) of the monthly instrument on the VAR residual of the policy variable; index r*-gap in the system")
print("   window  policy variable          NS  F    BS  F      T")
for lab, vstart in (("S1", "1994-01"), ("S2", "1976-06")):
    for pv in ("ffr", "ffr_end", "gs2", "gs2_end"):
        e = resid(["u_gap", "pi_core", pv, "market_rstar"], vstart if not (lab == "S2" and pv.startswith("ffr")) else "1973-01")
        out = []
        for zn in ("ns", "bs"):
            r = sm.OLS(e[pv].values, sm.add_constant(Z[zn].reindex(e.index).values)).fit(cov_type="HC1"); out.append(r.tvalues[1] ** 2)
        print(f"   {lab}     {pv:10s} (VAR from {vstart if not (lab == 'S2' and pv.startswith('ffr')) else '1973-01'})  {out[0]:5.1f}   {out[1]:5.1f}   {len(e)}")
print("\nRaw: correlation of the NS sum with the same-month change of each policy variable, 1994-2026")
s94 = M.loc["1994-01":]
for pv in ("ffr", "ffr_end", "gs2", "gs2_end"):
    d = M[pv].diff().loc["1994-01":]; r = Z.ns.loc["1994-01":].corr(d); print(f"   {pv:9s} r {r:+.2f}  F {r * r * (len(d) - 3) / (1 - r * r):5.1f}")
