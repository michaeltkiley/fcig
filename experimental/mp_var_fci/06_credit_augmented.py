"""Step 6 (MP-A11). Add the excess bond premium (EBP) or the Chicago Fed NFCI/ANFCI to the system, in three samples:
  FULL-S1  VAR and instrument 1994-01..2026-09 (12 lags, 2020 dummied)      FULL-S2  VAR long (2-year from 1976-06, funds rate from 1973-01), residuals and instrument from 1994-01
  CH       Caldara-Herbst window: VAR 1993-07..2007-06, 6 lags, residuals and instrument from 1994-01, scheduled meetings only
Policy variable: 2-year yield (main; instruments NS, ED4) and funds rate (robustness; instruments MP1, NS). Systems (all contain u gap, core PCE, policy variable): +none, +index, +EBP, +index+EBP, +NFCI, +index+NFCI, +ANFCI.
Reported per cell: anchor first-stage F (robust [homoskedastic]), Lunsford F, Colombo shock-based F; proxy-SVAR response of the unemployment gap (pp) to a +25 bp policy rise at 12 and 24 months with the 95% Anderson-Rubin set
(conditional on VAR coefficients; 'unb' = unbounded); Cholesky response with the policy variable ordered last (reacts to the financial variables within the month, as Caldara-Herbst find) and first.
Output: 06_credit_augmented.log, credit_augmented.csv"""
import numpy as np, pandas as pd, warnings
from statsmodels.tsa.api import VAR
from mpcommon import *
warnings.filterwarnings("ignore")

eb = pd.read_csv(HERE / "data/ebp.csv"); eb.index = pd.PeriodIndex(pd.to_datetime(eb.date), freq="M"); M["ebp"] = eb.ebp.reindex(M.index)
for nm in ("NFCI", "ANFCI"):
    s = pd.read_csv(HERE.parents[1] / "fci_note/replication/data" / f"{nm}.csv"); s = pd.Series(s.iloc[:, 1].values, index=pd.to_datetime(s.iloc[:, 0]))
    M[nm.lower()] = s.groupby(s.index.to_period("M")).mean().reindex(M.index)
ev = events(); Zall = monthly_instruments(ev)
evs = ev[ev.Unscheduled == 0].copy(); evs["ns"] = I.ns_factor(evs)
Zsch = pd.DataFrame({k: evs.groupby("m")[k].sum().reindex(M.index).fillna(0.0) for k in ("ns", "ED4", "MP1", "FF4")})
H = 24
SYS = {"base": [], "+index": ["market_rstar"], "+EBP": ["ebp"], "+index+EBP": ["market_rstar", "ebp"], "+NFCI": ["nfci"], "+index+NFCI": ["market_rstar", "nfci"], "+ANFCI": ["anfci"]}
SAMPLES = {"FULL-S1": dict(vstart=lambda pv: "1994-01", vend="2026-09", lags=12, Z=Zall), "FULL-S2": dict(vstart=lambda pv: "1976-06" if pv == "gs2" else "1973-01", vend="2026-09", lags=12, Z=Zall),
           "CH": dict(vstart=lambda pv: "1993-07", vend="2007-06", lags=6, Z=Zsch)}
rows = []

def cell(sample, pv, inst, sysname):
    sp = SAMPLES[sample]; cols = ["u_gap", "pi_core", pv] + SYS[sysname]; p = cols.index(pv)
    r, e = var_resid(cols, sp["vstart"](pv), sp["vend"], lags=sp["lags"], rstart="1994-01")
    z = sp["Z"][inst].reindex(e.index)
    Fr, Fh, _ = first_stage(e[pv], z); FL, FC, b = lunsford_colombo(e, z, pv)
    Phi = r.ma_rep(H); irf = np.einsum("hij,j->hi", Phi, b); ar = ar_set(Phi[:, 0, :], e.values, p, z)
    fmt = lambda h: ("unb" if not (np.isfinite(ar[h][0]) and np.isfinite(ar[h][1])) else f"({0.25 * ar[h][0]:+.2f},{0.25 * ar[h][1]:+.2f})")
    # Cholesky: policy last (reacts to financial variables) and first among the added variables
    X = M.loc[sp["vstart"](pv):sp["vend"], cols].dropna().copy()
    ms = [m for m in sorted(set(pd.period_range("2020-01", "2020-12", freq="M"))) if m in X.index]
    dum = pd.DataFrame({f"d{m}": (X.index == m).astype(float) for m in ms}, index=X.index) if ms else None
    X.index = X.index.to_timestamp()
    if dum is not None: dum.index = X.index
    out = {}
    for lab, order in (("last", ["u_gap", "pi_core"] + SYS[sysname] + [pv]), ("first", ["u_gap", "pi_core", pv] + SYS[sysname])):
        rr = VAR(X[order], exog=dum).fit(sp["lags"]); j = order.index(pv); o = rr.irf(H).orth_irfs
        pth = o[:, :, j] / o[0, j, j] * 0.25; out[lab] = (pth[12, 0], pth[24, 0])
    rows.append(dict(sample=sample, policy=pv, inst=inst, system=sysname, T=len(e), F=Fr, Fhomo=Fh, Lunsford=FL, Colombo=FC, u12=0.25 * irf[12, 0], u24=0.25 * irf[24, 0],
                     ar12_lo=0.25 * ar[12][0], ar12_hi=0.25 * ar[12][1], chol_last_12=out["last"][0], chol_last_24=out["last"][1], chol_first_12=out["first"][0], chol_first_24=out["first"][1]))
    print(f"  {sysname:12s} {inst:4s} T={len(e):3d}  F {Fr:5.1f} [{Fh:5.1f}] L {FL:4.1f} C {FC:5.1f} | proxy u12 {0.25 * irf[12, 0]:+.2f} {fmt(12):>16s} u24 {0.25 * irf[24, 0]:+.2f} {fmt(24):>16s} | Chol last {out['last'][0]:+.2f}/{out['last'][1]:+.2f} first {out['first'][0]:+.2f}/{out['first'][1]:+.2f}", flush=True)

print("Unemployment-gap response (pp) to a +25 bp rise in the policy variable; proxy-SVAR with 95% AR set, and Cholesky (12m/24m)")
for sample in SAMPLES:
    for pv, insts in (("gs2", ("ns", "ED4")), ("ffr", ("MP1", "ns"))):
        if sample == "CH" and pv == "gs2": continue
        print(f"\n== {sample}, policy variable {pv} ==")
        for inst in insts:
            for sysname in SYS:
                cell(sample, pv, inst, sysname)
pd.DataFrame(rows).to_csv("credit_augmented.csv", index=False, float_format="%.4f")
