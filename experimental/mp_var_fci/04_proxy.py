"""Step 4. Proxy-SVAR (external-instrument) impulse responses with weak-instrument-robust sets. MP-A10: 2-year yield main policy variable.
For VAR residuals e_t (k variables) and monthly instrument z_t: the impact vector is proportional to the coefficients of e_t on z_t; normalized so the policy variable (position p) moves +1 pp on impact:
    b = gamma / gamma_p,  gamma_i = coefficient of e_i on z;   IRF_h = Phi_h b   (Phi_h = reduced-form MA matrices of the VAR)
Anderson-Rubin set for the response of variable i at horizon h: all theta with  mean(z (a_h' e - theta e_p)) = 0 not rejected at 5% (a_h' = row i of Phi_h; HC variance); a quadratic inequality in theta:
bounded interval when the instrument is strong enough, unbounded (a ray, a union of rays, or the whole line) when it is not. Conditional on the VAR coefficients (their sampling error is ignored): optimistic for the set, state it.
Specs: S1 = VAR and instrument 1994-01..2026-09; S2 = VAR on the long window (2-year from 1976-06; funds rate from 1973-01), residuals and instrument from 1994-01. 12 lags (and 2 lags as a check), 2020 dummied.
Output: 04_proxy.log, irf_proxy.csv, proxy_u.png"""
import numpy as np, pandas as pd
import statsmodels.api as sm
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpcommon import *

ev = events(); Z = monthly_instruments(ev)
H = 48


def ar_set(Phi_row, e, p, z, level=3.841):
    """Phi_row: (H+1, k) rows a_h; returns list of (lo, hi) per horizon (inf allowed) and flag bounded."""
    zc = (z - z.mean()).values; ep = e[:, p]; T = len(zc)
    out = []
    for a in Phi_row:
        c = e @ a
        A, B = np.mean(zc * c), np.mean(zc * ep)
        Scc, Scp, Spp = np.mean(zc ** 2 * c * c), np.mean(zc ** 2 * c * ep), np.mean(zc ** 2 * ep * ep)
        qa, qb, qc = T * B * B - level * Spp, -2 * T * A * B + 2 * level * Scp, T * A * A - level * Scc
        if qa > 0:                                     # bounded: theta between the roots of qa th^2 + qb th + qc <= 0
            disc = qb * qb - 4 * qa * qc
            if disc < 0:
                out.append((np.nan, np.nan)); continue                 # empty set
            out.append(((-qb - np.sqrt(disc)) / (2 * qa), (-qb + np.sqrt(disc)) / (2 * qa)))
        else:
            out.append((-np.inf, np.inf))              # unbounded (reported as 'all values' / a union of rays)
    return out


def run(pv, inst, vstart, scale="policy", lags=12, system="with index"):
    cols = ["u_gap", "pi_core", pv] + (["market_rstar"] if system == "with index" else [])
    r, e = var_resid(cols, vstart, lags=lags)
    p = cols.index(pv); sc = p if scale == "policy" else cols.index("market_rstar")
    z = Z[inst].reindex(e.index); X = sm.add_constant(z.values)
    gam = np.array([sm.OLS(e[c].values, X).fit().params[1] for c in cols])
    Fr = sm.OLS(e[pv].values, X).fit(cov_type="HC1").tvalues[1] ** 2
    b = gam / gam[sc]
    Phi = r.ma_rep(H)                                  # (H+1, k, k)
    irf = np.einsum("hij,j->hi", Phi, b)
    sets = ar_set(Phi[:, 0, :] - 0, e.values, sc, z) if False else None
    ar = {i: ar_set(Phi[:, i, :], e.values, sc, z) for i in (0,)}
    return cols, irf, ar[0], Fr, len(e)


rows, store = [], {}
print("Proxy-SVAR: response of the unemployment gap (pp) to a +1 pp rise in the policy variable on impact; AR = 95% Anderson-Rubin set (conditional on the VAR coefficients); F = robust first-stage F\n")
SPECS = [("gs2", "ns"), ("gs2", "ED4"), ("gs2", "FF4"), ("ffr", "ns"), ("ffr", "MP1")]
for lags in (12, 2):
    print(f"--- {lags} lags ---")
    for pv, inst in SPECS:
        for lab, vstart in (("S1", "1994-01"), ("S2", "1976-06" if pv == "gs2" else "1973-01")):
            cols, irf, ar, F, T = run(pv, inst, vstart, lags=lags)
            def fmt(h):
                lo, hi = ar[h]
                s = "unbounded" if not np.isfinite(lo) or not np.isfinite(hi) else (f"({lo:+.2f}, {hi:+.2f})" if lo == lo else "empty")
                return f"{irf[h, 0]:+6.2f} {s:>20s}"
            print(f"  {pv:4s} {inst:4s} {lab}  F {F:4.1f}  h12 {fmt(12)}   h24 {fmt(24)}   (T={T})")
            for h in range(H + 1):
                rows.append(dict(lags=lags, policy=pv, instrument=inst, sample=lab, F=F, h=h, irf_u=irf[h, 0], ar_lo=ar[h][0], ar_hi=ar[h][1], irf_idx=irf[h, 3], irf_pi_cum=irf[:h + 1, 1].sum() / 12))
            store[(lags, pv, inst, lab)] = (irf, ar)
print("\n--- Scaled on the index instead (12 lags), 2-year main system ---")
for inst in ("ns", "ED4"):
    for lab, vstart in (("S1", "1994-01"), ("S2", "1976-06")):
        cols, irf, ar, F, T = run("gs2", inst, vstart, scale="index")
        lo, hi = ar[12]; s = "unbounded" if not np.isfinite(lo) or not np.isfinite(hi) else f"({lo:+.2f}, {hi:+.2f})"
        print(f"  {inst:4s} {lab}  u at h12 per +1 index unit: {irf[12, 0]:+6.2f} {s:>20s}   (index first-stage weak: the scaling is unstable)")
pd.DataFrame(rows).to_csv("irf_proxy.csv", index=False, float_format="%.4f")
fig, ax = plt.subplots(2, 3, figsize=(15, 6.5), sharey=True)
for j, (pv, inst) in enumerate([("gs2", "ns"), ("gs2", "ED4"), ("ffr", "MP1")]):
    for i, lab in enumerate(("S1", "S2")):
        irf, ar = store[(12, pv, inst, lab)]; a = ax[i, j]
        lo = np.array([x[0] for x in ar]); hi = np.array([x[1] for x in ar]); bd = np.isfinite(lo) & np.isfinite(hi)
        a.plot(irf[:, 0], color="#c4501f", lw=1.5, label="point estimate"); a.axhline(0, color="k", lw=0.6)
        a.fill_between(range(H + 1), np.where(bd, lo, np.nan), np.where(bd, hi, np.nan), color="#c4501f", alpha=0.15, lw=0, label="95% AR set (bounded)")
        a.set_title(f"{pv} / {inst} / {lab}  (bounded at {bd.sum()} of {H + 1} horizons)", fontsize=9); a.set_ylim(-4, 4)
ax[0, 0].legend(frameon=False, fontsize=8); ax[0, 0].set_ylabel("unemployment gap, pp per +1 pp policy"); ax[1, 0].set_ylabel("unemployment gap, pp per +1 pp policy")
fig.suptitle("Proxy-SVAR (12 lags): unemployment response; shaded = Anderson-Rubin set where bounded (conditional on VAR coefficients)", fontsize=10); fig.tight_layout(); fig.savefig("proxy_u.png", dpi=130)
