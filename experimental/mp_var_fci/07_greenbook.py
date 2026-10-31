"""Step 7 (MP-A11). Miranda-Agrippino and Ricco (2021) information-robust instrument, applied to this project's surprises.
Greenbook/Tealbook forecasts: Philadelphia Fed real-time data set (data/greenbook/*, vintages 1985-02..2020-12, one per FOMC meeting): real GDP growth (gRGDP), GDP-deflator inflation (gPGDP), unemployment rate (UNEMP).
MAR steps: (1) at meeting frequency regress the surprise on Greenbook forecast LEVELS for growth and inflation at horizons q-1..q+3 and on REVISIONS (this vintage minus the previous one, same target quarter) at q-1..q+2,
plus the unemployment NOWCAST level; keep the residual; for unscheduled events the latest available vintage is used. (2) Sum within the month. (3) Remove the autoregressive component of the monthly series
(12 lags, estimated only on months with a non-zero reading; lags of the full monthly series enter the regressors). 'GB' = after steps 1-2, 'GB+AR' = after step 3.
Surprises purged: MP1, FF4, ns, ED4 (FOMC events of the note's set; instrument window 1994-02..2020-12). First stages as before (anchor robust [homoskedastic], Lunsford, Colombo), in the CH window and on 1994-2019.
Output: 07_greenbook.log, data/mp_instruments_gb.csv"""
import numpy as np, pandas as pd, warnings
import statsmodels.api as sm
from mpcommon import *
warnings.filterwarnings("ignore")
GBD = HERE / "data/greenbook"

def load_gb(name):
    out = {}
    for f in (f"{name}_1967_1984.xlsx", f"{name}_1985_Last.xlsx"):
        d = pd.read_excel(GBD / f)
        q = d["Date"].astype(float)
        idx = pd.PeriodIndex([f"{int(x)}Q{int(round((x - int(x)) * 10))}" for x in q], freq="Q")
        for c in d.columns:
            if c == "Date": continue
            out[pd.Timestamp(c.split("_")[1])] = pd.Series(d[c].values, index=idx)
    return out

GB = {k: load_gb(k) for k in ("gRGDP", "gPGDP", "UNEMP")}
gb_dates = sorted(GB["gRGDP"])

def regressors(date):
    """Greenbook regressors for an event on `date`: latest vintage on or before the event (within 35 days) and the one before it."""
    prev = [d for d in gb_dates if d <= date]
    if len(prev) < 2 or (date - prev[-1]).days > 35: return None
    v, v0 = prev[-1], prev[-2]; q = pd.Period(v, "Q"); row = {}
    for var in ("gRGDP", "gPGDP"):
        for j in range(-1, 4):
            row[f"{var}_L{j}"] = GB[var][v].get(q + j, np.nan)
        for j in range(-1, 3):
            row[f"{var}_R{j}"] = GB[var][v].get(q + j, np.nan) - GB[var][v0].get(q + j, np.nan)
    row["UNEMP_L0"] = GB["UNEMP"][v].get(q, np.nan)
    return row

ev = events()
R = pd.DataFrame([regressors(d) or {} for d in ev.Date], index=ev.index)
ok = R.notna().all(axis=1) & (ev.Date <= "2020-12-31")
print(f"Events in the note's set: {len(ev)}; with Greenbook regressors (vintage within 35 days, through 2020-12): {int(ok.sum())}; first {ev.Date[ok].min().date()}, last {ev.Date[ok].max().date()}")
X = sm.add_constant(R[ok].values)
Z = {}
print("\nStep 1: regression of each surprise on Greenbook forecasts and revisions (19 regressors), R2 [adjusted R2]; share of the surprise variance explained")
for k in ("MP1", "FF4", "ns", "ED4"):
    y = ev.loc[ok, k].fillna(0.0).values
    f = sm.OLS(y, X).fit()
    print(f"   {k:4s} n={int(ok.sum())}  R2 {f.rsquared:.3f} [{f.rsquared_adj:.3f}]  joint F p-value {f.f_pvalue:.3f}")
    s = pd.Series(np.nan, index=ev.index); s[ok] = f.resid
    evk = ev[["m"]].copy(); evk["s"] = s
    Z[k] = evk.dropna().groupby("m").s.sum().reindex(M.index).fillna(0.0)
# step 3: remove the AR(12) component, non-zero months only
def deAR(z):
    lags = pd.concat({j: z.shift(j) for j in range(1, 13)}, axis=1)
    nz = (z != 0) & lags.notna().all(axis=1)
    f = sm.OLS(z[nz].values, sm.add_constant(lags[nz].values)).fit()
    out = z.copy(); out[nz] = f.resid
    return out, f.rsquared
ZAR = {}
print("\nStep 3: AR(12) component of the monthly purged series (non-zero months only), R2")
for k in Z:
    ZAR[k], r2 = deAR(Z[k]); print(f"   {k:4s} R2 {r2:.3f}")
raw = {k: monthly_instruments(ev, (k,))[k] for k in ("MP1", "FF4", "ns", "ED4")}
raw_gbwindow = {k: raw[k].where(raw[k].index <= pd.Period("2020-12", "M"), 0.0) for k in raw}
pd.DataFrame({**{f"{k}_gb": Z[k] for k in Z}, **{f"{k}_gbar": ZAR[k] for k in ZAR}}).to_csv(HERE / "data/mp_instruments_gb.csv", float_format="%.5f")
print("\nCorrelation of the monthly raw and purged instruments (1994-2020):")
for k in Z:
    print(f"   {k:4s} raw vs GB {raw[k].loc['1994-01':'2020-12'].corr(Z[k].loc['1994-01':'2020-12']):.2f}   raw vs GB+AR {raw[k].loc['1994-01':'2020-12'].corr(ZAR[k].loc['1994-01':'2020-12']):.2f}")

def stats(cols, z, vstart, vend, lags, rend, rstart="1994-01"):
    r, e = var_resid(cols, vstart, vend, lags=lags, rstart=rstart); e = e.loc[:rend]
    zz = z.reindex(e.index); pv = cols[2]
    Fr, Fh, _ = first_stage(e[pv], zz); FL, FC, b = lunsford_colombo(e, zz, pv)
    return Fr, Fh, FL, FC, r, e, b

def line(cols, insts, vstart, vend, lags, rend, label):
    print(f"\n{label}  (system {'+'.join(cols)}; first stage robust [homoskedastic] | Lunsford | Colombo)")
    for k in insts:
        row = []
        for nm, z in (("raw", raw_gbwindow[k]), ("GB", Z[k]), ("GB+AR", ZAR[k])):
            Fr, Fh, FL, FC, *_ = stats(cols, z, vstart, vend, lags, rend)
            row.append(f"{nm}: {Fr:4.1f} [{Fh:5.1f}] {FL:4.1f} {FC:5.1f}")
        print(f"   {k:4s}  " + "   ".join(row))
for pv, insts in (("ffr", ("MP1", "FF4", "ns")), ("gs2", ("ns", "ED4"))):
    line(["u_gap", "pi_core", pv, "market_rstar"], insts, "1993-07", "2007-06", 6, "2007-06", f"CH window 1994-2007 (6 lags), policy variable {pv}")
    line(["u_gap", "pi_core", pv, "market_rstar"], insts, "1994-01", "2026-09", 12, "2019-12", f"1994-2019 residuals (VAR 1994-2026, 12 lags), policy variable {pv}")
