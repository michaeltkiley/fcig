"""Step 4c. Read-and-relate to Gertler-Karadi (2015), Lunsford (2015), Colombo (2025): first-stage strength under their conventions and ours.
Part A  Approximate replication of Gertler-Karadi's first stage. 4-variable VAR: 100 ln IP (INDPRO), 100 ln CPI (CPIAUCSL), 1-year Treasury yield (FRED GS1, monthly average),
        Gilchrist-Zakrajsek excess bond premium (Fed, data/ebp.csv); VAR on 1979-07..2012-06 (as GK, lag coefficients from the full sample), residuals and instrument from the instrument window.
        Instrument: FF4 surprise from USMPD (all events; USMPD starts 1994-02, GK's instruments start 1991-01, so 1991-93 is missing), made monthly as in GK's footnote 11: cumulate surprises over the previous
        31 days for each day of the month, then average over the days of the month (monthly-average rates). Lag length not available to us (replication code is behind a login): 12 assumed, 6 and 2 for sensitivity.
        Three F statistics: anchor-based (policy-variable residual on the instrument; GK Table 3 / Stock-Watson), Lunsford (instrument projected on ALL VAR errors), Colombo shock-based (shock index b' Sigma^-1 u on the instrument).
Part B  The same three F statistics for this project's systems (2-year / funds rate; r*-gap index; 12 lags; S1 and S2).
Reference values from the papers: GK (1-year, FF4, 4-variable VAR, T = 258 monthly 1991-2012): F 21.5, robust F 17.5, R2 0.078 (Table 3 col 2: 17.50). 2-year columns in Table 3: F 4.5, 5.2, 0.9, 3.8, 5.2.
Colombo (instrument window = full 1979-2012 sample, moving-block bootstrap): 4-variable anchor-based F 9.02, shock-based F 15.48; trivariate 10.27 and 11.13.
Output: 04c_gk_replication.log"""
import calendar
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from mpcommon import *

def three_F(e, z, anchor):
    """e: DataFrame of VAR residuals; z: instrument aligned; anchor: column name. Returns dict of F statistics."""
    X1 = sm.add_constant(z.values)
    a_h = sm.OLS(e[anchor].values, X1).fit(); a_r = sm.OLS(e[anchor].values, X1).fit(cov_type="HC1")
    gam = np.array([sm.OLS(e[c].values, X1).fit().params[1] for c in e.columns]); b = gam / gam[list(e.columns).index(anchor)]
    # Lunsford: proxy on all VAR errors, joint F
    L = sm.OLS(z.values, sm.add_constant(e.values)).fit()
    FL = L.fvalue
    # Colombo: shock index w = b' Sigma^-1 u regressed on z
    S = np.cov(e.values.T); w = e.values @ np.linalg.solve(S, b)
    c_h = sm.OLS(w, X1).fit(); c_r = sm.OLS(w, X1).fit(cov_type="HC1")
    return dict(anchorF=a_h.tvalues[1] ** 2, anchorF_robust=a_r.tvalues[1] ** 2, R2=a_h.rsquared, lunsfordF=FL, colomboF=c_h.tvalues[1] ** 2, colomboF_robust=c_r.tvalues[1] ** 2, n=len(e))

# ---------------------------------------------------------------- Part A
usmpd = pd.read_excel(HERE / "data/USMPD.xlsx", "Monetary Events")
usmpd["Date"] = pd.to_datetime(usmpd.Date)
days = pd.date_range("1990-01-01", "2026-10-31", freq="D")
def gk_monthly(col):
    s = pd.Series(0.0, index=days)
    for d, v in zip(usmpd.Date, usmpd[col].fillna(0.0)):
        s[d] += v
    cum31 = s.rolling(31, min_periods=1).sum()                # surprises over the last 31 days, for each day
    return cum31.groupby(cum31.index.to_period("M")).mean()   # average over the days of the month

ip = fred("INDPRO"); cpi = fred("CPIAUCSL"); gs1 = fred("GS1"); gs2s = fred("GS2")
mm = lambda s: s.groupby(s.index.to_period("M")).mean()
ebp = pd.read_csv(HERE / "data/ebp.csv"); ebp.index = pd.PeriodIndex(pd.to_datetime(ebp.date), freq="M")
G = pd.DataFrame({"lnIP": 100 * np.log(mm(ip)), "lnCPI": 100 * np.log(mm(cpi)), "gs1": mm(gs1), "gs2": mm(gs2s), "ebp": ebp.ebp}).loc["1979-07":"2012-06"].dropna()
Zg = pd.DataFrame({k: gk_monthly(k) for k in ("FF4", "ED4", "MP1", "FF1")}).reindex(G.index).fillna(0.0)
print("Part A. Approximation of Gertler-Karadi's first stage (instrument FF4 from USMPD, 1994-02 on; GK use 1991-01 on)")
print("   VAR 1979-07..2012-06, 4 variables, constant, no other dummies.   GK Table 3, column 2 (1-year, FF4, T = 258): F 17.50 (robust t); text: F 21.5, robust F 17.5, R2 0.078")
print("   lags  policy  instr  window            n   anchorF [robust]    R2   Lunsford F   Colombo F [robust]")
for p in (12, 6, 2):
    for pv in ("gs1", "gs2"):
        cols = ["lnIP", "lnCPI", pv, "ebp"]
        r = VAR(G[cols], ).fit(p); e = pd.DataFrame(r.resid, columns=cols)
        for inst in (["FF4", "ED4"] if pv == "gs2" else ["FF4", "ED4", "MP1"]):
            for lab, a in (("1994-02..2012-06", "1994-02"), ("1991-01..2012-06*", "1991-01")):
                ee = e.loc[a:"2012-06"]
                if lab.endswith("*"):
                    continue                      # no instrument data before 1994-02 in USMPD
                z = Zg[inst].reindex(ee.index)
                f = three_F(ee, z, pv)
                print(f"   {p:3d}   {pv:5s}  {inst:4s}   {lab:17s} {f['n']:3d}   {f['anchorF']:5.1f} [{f['anchorF_robust']:5.1f}]   {f['R2']:.3f}   {f['lunsfordF']:6.1f}   {f['colomboF']:6.1f} [{f['colomboF_robust']:6.1f}]")

# ---------------------------------------------------------------- Part B
print("\nPart B. The same three F statistics for this project's systems (u gap, core PCE, policy variable, r*-gap index), 12 lags, 2020 dummied")
ev = events(); Z = monthly_instruments(ev)
print("   system                        instr   sample   n   anchorF [robust]    R2   Lunsford F   Colombo F [robust]")
for pv in ("gs2", "ffr"):
    for inst in (["ns", "ED4", "FF4"] if pv == "gs2" else ["ns", "MP1"]):
        for lab, vstart in (("S1", "1994-01"), ("S2", "1976-06" if pv == "gs2" else "1973-01")):
            cols = ["u_gap", "pi_core", pv, "market_rstar"]
            r, e = var_resid(cols, vstart)
            f = three_F(e, Z[inst].reindex(e.index), pv)
            print(f"   {'+'.join(cols):28s}  {inst:5s}  {lab}  {f['n']:3d}   {f['anchorF']:5.1f} [{f['anchorF_robust']:5.1f}]   {f['R2']:.3f}   {f['lunsfordF']:6.1f}   {f['colomboF']:6.1f} [{f['colomboF_robust']:6.1f}]")
print("\n   Without the index (u gap, core PCE, policy variable):")
for pv in ("gs2",):
    for inst in ("ns", "ED4"):
        for lab, vstart in (("S1", "1994-01"), ("S2", "1976-06")):
            cols = ["u_gap", "pi_core", pv]
            r, e = var_resid(cols, vstart)
            f = three_F(e, Z[inst].reindex(e.index), pv)
            print(f"   {'+'.join(cols):28s}  {inst:5s}  {lab}  {f['n']:3d}   {f['anchorF']:5.1f} [{f['anchorF_robust']:5.1f}]   {f['R2']:.3f}   {f['lunsfordF']:6.1f}   {f['colomboF']:6.1f} [{f['colomboF_robust']:6.1f}]")
