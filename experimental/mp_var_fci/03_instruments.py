"""Step 3 (MP_QA.md MP-A2, A3, A8). Instruments and first stages.
NS: monthly sum of the Nakamura-Steinsson factor over the month's FOMC events (data/mp_monthly.csv, from fci_note/replication).
BS (own purge, Bauer-Swanson style; the published series is not used): at the event level regress NS on information available before the meeting and keep the residual:
  payroll growth (12-month, latest payroll month published before the meeting), S&P 500 3-month change, change in the 3-month change of the curve slope (10-year less 3-month bill),
  WTI 3-month change; all from monthly data ending the month before the meeting. (Not included, unlike the published version: payroll surprise, Treasury skewness.)
First stages: reduced-form VAR residuals (12 lags, 2020 dummies) regressed on each instrument, robust (HC1) t, F = t^2, for
  S1 VAR and instrument on 1994-01..2026-09;  S2 VAR on the long window, residuals taken from 1994-01 (instrument window).
Systems: policy variable = funds rate (main) or 2-year yield (robustness, from 1976-06); index = r*-gap (main), nominal, real.
Output: data/mp_instruments.csv, 03_instruments.log"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
REP = HERE.parents[1] / "fci_note" / "replication"
sys.path.insert(0, str(REP))
from fci import data as D0, indexes as I          # noqa: E402

M = pd.read_csv(HERE / "data/mp_monthly.csv", index_col=0); M.index = pd.PeriodIndex(M.index, freq="M")
Dm = D0.load()


def fred(n):
    d = pd.read_csv(HERE / f"data/{n}.csv"); return pd.Series(d[n].values.astype(float), index=pd.to_datetime(d["observation_date"]))


pay, tb, oil = fred("PAYEMS"), fred("DTB3"), fred("DCOILWTICO")
tb_m = tb.groupby(tb.index.to_period("M")).mean(); oil_m = oil.groupby(oil.index.to_period("M")).mean()
slope = Dm.y10 - tb_m.reindex(Dm.index)

ev = I.events().copy()
rows = []
for dt in ev.Date:
    m = dt.to_period("M")
    pm = pay[pay.index < dt.replace(day=1)]
    f = lambda s, k: float(s[m - k]) if (m - k) in s.index else np.nan
    rows.append([100 * np.log(pm.iloc[-1] / pm.iloc[-13]), 100 * (np.log(f(Dm.sp500, 1)) - np.log(f(Dm.sp500, 4))), f(slope, 1) - f(slope, 4), 100 * (np.log(f(oil_m, 1)) - np.log(f(oil_m, 4)))])
C = pd.DataFrame(rows, columns=["payroll 12m", "stocks 3m", "slope 3m chg", "oil 3m"]); ok = C.notna().all(axis=1)
fit = sm.OLS(ev.ns[ok].values, sm.add_constant(C[ok].values)).fit(cov_type="HC1")
ev["bs"] = np.nan; ev.loc[ok.values, "bs"] = fit.resid
print(f"Purge regression (event level, n = {int(ok.sum())} of {len(ev)}): R2 {fit.rsquared:.3f}, joint F p-value {fit.f_pvalue:.4f}")
for nme, b, t in zip(["const"] + list(C.columns), fit.params, fit.tvalues):
    print(f"  {nme:14s} {b:+.4f}  (t {t:+.1f})")
print(f"  sd(ns) {ev.ns.std():.4f}  sd(bs) {ev.bs.std():.4f}  corr(ns, bs) {ev.ns.corr(ev.bs):.2f}")
ev["m"] = ev.Date.dt.to_period("M")
inst = pd.DataFrame({"ns": ev.groupby("m").ns.sum(), "bs": ev.groupby("m").bs.sum(min_count=1)}).reindex(M.index).fillna(0.0)
inst.index.name = "month"; inst.to_csv(HERE / "data/mp_instruments.csv", float_format="%.5f")
print(f"  monthly instruments written; sd monthly ns {inst.ns.std():.4f}, bs {inst.bs.std():.4f}; corr {inst.ns.corr(inst.bs):.2f}\n")


def resid(cols, start, vstart):
    """VAR on [vstart, 2026-09] (2020 dummied); residuals from `start` on."""
    X = M.loc[vstart:"2026-09", cols].dropna()
    dum = pd.DataFrame({f"d{k:02d}": (X.index == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}, index=X.index)
    X = X.copy(); X.index = X.index.to_timestamp(); dum.index = X.index
    r = VAR(X, exog=dum).fit(12)
    e = r.resid; e.index = e.index.to_period("M")
    return e.loc[start:]


def stage(e, z):
    z = z.reindex(e.index)
    fs = sm.OLS(e.values, sm.add_constant(z.values)).fit(cov_type="HC1")
    return fs.params[1], fs.tvalues[1], fs.tvalues[1] ** 2, fs.rsquared


def table(title, cols, start, vstart, ixname):
    e = resid(cols, start, vstart)
    print(f"{title}  (T = {len(e)})")
    print("   residual of            instrument   coefficient     t      F    R2")
    for c in cols:
        for zn in ("ns", "bs"):
            b, t, F, r2 = stage(e[c], inst[zn])
            flag = "  <-- index" if c == ixname else ("  <-- policy" if c in ("ffr", "gs2") else "")
            print(f"   {c:22s} {zn:9s}  {b:+10.3f}  {t:+7.2f} {F:6.1f} {r2:6.3f}{flag}")
    print()


for case in ("rstar", "nominal", "real"):
    ix = f"market_{case}"
    table(f"S1  VAR and instrument 1994-2026, funds rate, index {case}", ["u_gap", "pi_core", "ffr", ix], "1994-01", "1994-01", ix)
    table(f"S2  VAR 1973-2026, instrument window 1994-2026, funds rate, index {case}", ["u_gap", "pi_core", "ffr", ix], "1994-01", "1973-01", ix)
table("S1, 2-year yield as policy variable, index rstar", ["u_gap", "pi_core", "gs2", "market_rstar"], "1994-01", "1994-01", "market_rstar")
table("S2, 2-year yield as policy variable (VAR from 1976-06), index rstar", ["u_gap", "pi_core", "gs2", "market_rstar"], "1994-01", "1976-06", "market_rstar")
print("Reading: F is the squared robust t of one instrument on one residual. Rule of thumb for a usable instrument: F above about 10 on the variable used for scaling.")
