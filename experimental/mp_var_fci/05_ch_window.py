"""Step 5. Caldara-Herbst (2019) design on this project's data. Their window and choices: Great Moderation July 1993-June 2007 (instrument from 1994-01), scheduled FOMC surprises in the current-month funds rate futures (here MP1, the closest
USMPD analogue), assigned to the meeting month, effective federal funds rate as the policy variable, 6 lags, a credit spread (excess bond premium, EBP) and industrial production growth in the system.
Systems (policy variable ffr; shock = +25 bp on impact):
  CH           dIP, EBP, ffr (their trivariate)                     CH+idx   + market index (r*-gap)
  Ours         u gap, core PCE, ffr, index (this project)           Ours+EBP + EBP
Reported: first-stage F (anchor, robust [homoskedastic]), Lunsford F, Colombo shock-based F; proxy-SVAR response of unemployment gap (or cumulated IP) at 12 and 24 months with the 95% Anderson-Rubin set (conditional on VAR
coefficients) and the Cholesky response with the funds rate ordered (a) before the financial variable (does not react to it) and (b) after it (reacts contemporaneously, as CH find).
Output: 05_ch_window.log"""
import numpy as np, pandas as pd, warnings
import statsmodels.api as sm
import mpcommon as C
from mpcommon import *
warnings.filterwarnings("ignore")

ip = fred("INDPRO"); ip = ip.groupby(ip.index.to_period("M")).mean()
M["dIP"] = 100 * np.log(ip).diff().reindex(M.index)
eb = pd.read_csv(HERE / "data/ebp.csv"); eb.index = pd.PeriodIndex(pd.to_datetime(eb.date), freq="M"); M["ebp"] = eb.ebp.reindex(M.index)
ev = events(); sched = ev[ev.Unscheduled == 0]
mon = lambda d, k: d.groupby("m")[k].sum().reindex(M.index).fillna(0.0)
Z = {"MP1": mon(sched, "MP1"), "ns": mon(sched, "ns"), "ED4": mon(sched, "ED4"), "FF4": mon(sched, "FF4")}
LAGS, V0, V1, R0, H = 6, "1993-07", "2007-06", "1994-01", 24

def lunsford_colombo(e, z, anchor):
    X1 = sm.add_constant(z.values)
    gam = np.array([sm.OLS(e[c].values, X1).fit().params[1] for c in e.columns]); b = gam / gam[list(e.columns).index(anchor)]
    FL = sm.OLS(z.values, sm.add_constant(e.values)).fit().fvalue
    w = e.values @ np.linalg.solve(np.cov(e.values.T), b); FC = sm.OLS(w, X1).fit().tvalues[1] ** 2
    return FL, FC, b

def run(cols, inst, label, act):
    r, e = var_resid(cols, V0, V1, lags=LAGS, rstart=R0)
    z = Z[inst].reindex(e.index); p = cols.index("ffr")
    Fr, Fh, _ = first_stage(e["ffr"], z); FL, FC, b = lunsford_colombo(e, z, "ffr")
    Phi = r.ma_rep(H); irf = np.einsum("hij,j->hi", Phi, b)
    a = cols.index(act) if act != "IP" else cols.index("dIP")
    ar = ar_set(Phi[:, a, :], e.values, p, z)
    series = irf[:, a] * (np.cumsum if act == "IP" else (lambda x: x))(np.ones(1)) if False else None
    resp = np.cumsum(irf[:, a]) if act == "IP" else irf[:, a]
    # AR set for the cumulated IP response: sum of rows
    if act == "IP":
        ar = ar_set(np.cumsum(Phi[:, a, :], axis=0), e.values, p, z)
    def f(h):
        lo, hi = ar[h]; s = "unbounded" if not (np.isfinite(lo) and np.isfinite(hi)) else f"({0.25 * lo:+.2f}, {0.25 * hi:+.2f})"
        return f"{0.25 * resp[h]:+6.2f} {s:>18s}"
    print(f"  {label:9s} {inst:4s} T={len(e):3d}  F {Fr:5.1f} [{Fh:5.1f}]  Lunsford {FL:5.1f}  Colombo {FC:5.1f} | {act:3s} h12 {f(12)}  h24 {f(24)}")

def cholesky(cols, label, act):
    X = M.loc[V0:V1, cols].dropna(); X = X.copy(); X.index = X.index.to_timestamp()
    from statsmodels.tsa.api import VAR
    r = VAR(X).fit(LAGS); j = cols.index("ffr"); o = r.irf(H).orth_irfs
    path = o[:, :, j] / o[0, j, j] * 0.25; a = cols.index(act if act != "IP" else "dIP")
    resp = np.cumsum(path[:, a]) if act == "IP" else path[:, a]
    print(f"  {label:34s} {act:3s} h12 {resp[12]:+6.2f}   h24 {resp[24]:+6.2f}   (ffr 12m {path[12, j]:+.2f}; one-sd shock {o[0, j, j]:.2f} pp)")

print(f"Caldara-Herbst design: VAR {V0}..{V1}, {LAGS} lags, instrument from {R0}; shock = +25 bp funds rate; IP response cumulated, in %; unemployment gap in pp\n")
print("Proxy-SVAR (instrument: scheduled-meeting surprise), first-stage F anchor robust [homoskedastic]; AR = 95% Anderson-Rubin set")
for inst in ("MP1", "ns", "ED4", "FF4"):
    run(["dIP", "ebp", "ffr"], inst, "CH", "IP")
for inst in ("MP1", "ns"):
    run(["dIP", "ebp", "ffr", "market_rstar"], inst, "CH+idx", "IP")
for inst in ("MP1", "ns"):
    run(["u_gap", "pi_core", "ffr", "market_rstar"], inst, "Ours", "u_gap")
for inst in ("MP1", "ns"):
    run(["u_gap", "pi_core", "ffr", "market_rstar", "ebp"], inst, "Ours+EBP", "u_gap")
for inst in ("MP1",):
    run(["u_gap", "pi_core", "ffr", "ebp"], inst, "u,pi,ffr,EBP", "u_gap")
    run(["u_gap", "pi_core", "ffr"], inst, "u,pi,ffr", "u_gap")
print("\nCholesky, same window (no instrument)")
cholesky(["dIP", "ffr", "ebp"], "CH-like: ffr before EBP (no reaction)", "IP")
cholesky(["dIP", "ebp", "ffr"], "CH-like: ffr after EBP (reacts)", "IP")
cholesky(["u_gap", "pi_core", "ffr", "market_rstar"], "Ours: ffr before index", "u_gap")
cholesky(["u_gap", "pi_core", "market_rstar", "ffr"], "Ours: ffr after index (reacts)", "u_gap")
cholesky(["u_gap", "pi_core", "ffr", "ebp"], "u,pi,ffr,EBP: ffr before EBP", "u_gap")
cholesky(["u_gap", "pi_core", "ebp", "ffr"], "u,pi,ffr,EBP: ffr after EBP (reacts)", "u_gap")
cholesky(["u_gap", "pi_core", "market_rstar", "ebp", "ffr"], "Ours+EBP: ffr last (reacts to both)", "u_gap")
