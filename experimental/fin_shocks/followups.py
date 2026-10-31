"""Stage-0 follow-ups (MF_PLAN section 6; FS-A5 drops the macro-prior robustness).
(1) Contamination test. Same monthly VAR as stage 0; compare the unemployment response when the impact vector b is
    W  = from the windows (macro entries zero)                                      [stage 0]
    P  = from the monthly proxy-SVAR: coefficients of the VAR residuals on the monthly NS sum, rescaled so the policy-variable entry equals W's
    P0 = P with the macro entries set to zero (isolates the financial ratio index/policy)
    WM = W for the financial entries with the macro entries taken from P (isolates the macro entries)
    If P differs from W because of the macro entries, WM reproduces P and P0 reproduces W.
(2) Credit and financial-conditions variables added to the VAR: EBP (window response mapped from the daily Baa-10y response by a monthly regression of the EBP on the Baa-10y) and NFCI (impact zero, a conservative variant).
(3) Baseline with 150 bootstrap draws (events and VAR residuals).
Unit: unemployment gap (pp) per +1 pp rise in the 2-year yield on the event day; EVENT timing; NS shock; median [90% interval].
Output: followups.log, followups.csv"""
import numpy as np, pandas as pd
import mf_common as F
from mf_common import *
rng = np.random.default_rng(77); B, H = 150, 36
Zns = C.monthly_instruments(C.events(), ("ns",))["ns"]
idx0 = event_index("NS"); P0, _, idx0 = slopes(idx0, "NS")
SPECS = [("long 1976- (2-year) + Baa", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10"], "1976-06"),
         ("short 1994- (2-year) + Baa", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10"], "1994-01")]
rows = []
def proxy_gamma(r, cols):
    e = pd.DataFrame(r.resid.values, index=r.resid.index.to_period("M"), columns=cols).loc["1994-01":]
    z = Zns.reindex(e.index); X = sm.add_constant(z.values)
    return np.array([sm.OLS(e[c].values, X).fit().params[1] for c in cols])
print("(1) Contamination test: unemployment response at 12 and 24 months, point estimates (VAR-bootstrap 90% interval for 12 months)\n")
for lab, cols, vs in SPECS:
    r0, X, dum = fit_var(cols, vs); pol = cols.index("gs2")
    ex = exposure(P0, idx0, [DV[c] for c in cols if c in DV]); bW = bvec(cols, ex)
    g = proxy_gamma(r0, cols); bP = g / g[pol] * bW[pol]
    bP0 = bP.copy(); bP0[[0, 1]] = 0.0
    bWM = bW.copy(); bWM[[0, 1]] = bP[[0, 1]]
    Th = r0.ma_rep(H)
    out = {}
    for nm, b in (("W (windows, macro 0)", bW), ("P (monthly proxy)", bP), ("P0 (proxy, macro 0)", bP0), ("WM (windows + proxy macro)", bWM)):
        irf = np.einsum("hij,j->hi", Th, b); d = []
        for _ in range(60):
            rb = boot_var(r0, X, dum, rng); d.append(np.einsum("hij,j->hi", rb.ma_rep(H), b)[:, 0])
        lo, hi = np.percentile(np.array(d), [5, 95], axis=0); out[nm] = (irf, lo, hi, b)
        rows.append(dict(spec=lab, variant=nm, u12=irf[12, 0], lo12=lo[12], hi12=hi[12], u24=irf[24, 0]))
    print(f"{lab}:  b entries (u, pi, policy, index, Baa)")
    for nm, (irf, lo, hi, b) in out.items():
        print(f"   {nm:28s} b = [{', '.join(f'{x:+.2f}' for x in b)}]   u12 {irf[12, 0]:+.3f} [{lo[12]:+.3f},{hi[12]:+.3f}]   u24 {irf[24, 0]:+.3f}")
print("\n(2) EBP and NFCI added to the long-sample VAR (1976-06-), EVENT timing; NFCI with zero impact\n")
# EBP window response from the Baa-10y daily response via a monthly regression of the EBP on the Baa-10y spread
d = pd.concat([M.ebp.diff(), M.baa10.diff()], axis=1, keys=["e", "b"]).dropna().loc["1990-01":]
slope_e = sm.OLS(d.e.values, sm.add_constant(d.b.values)).fit().params[1]
print(f"   monthly slope of the EBP change on the Baa-10y change (1990-): {slope_e:.2f}")
cols = ["u_gap", "pi_core", "gs2", "market_rstar", "baa10", "ebp"]
for lab, cl, vs in (("long + Baa + EBP", cols, "1976-06"), ("short + Baa + EBP", cols, "1994-01"), ("long + NFCI", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10", "nfci"], "1976-06"), ("short + NFCI", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10", "nfci"], "1994-01")):
    r0, X, dum = fit_var(cl, vs); ex = exposure(P0, idx0, ["y2", "idx", "baa10"]); b = bvec(cl, ex)
    if "ebp" in cl: b[cl.index("ebp")] = slope_e * ex["baa10"]
    irf = np.einsum("hij,j->hi", r0.ma_rep(H), b); d = []
    for _ in range(60):
        rb = boot_var(r0, X, dum, rng); d.append(np.einsum("hij,j->hi", rb.ma_rep(H), b)[:, 0])
    lo, hi = np.percentile(np.array(d), [5, 95], axis=0)
    rows.append(dict(spec=lab, variant="added", u12=irf[12, 0], lo12=lo[12], hi12=hi[12], u24=irf[24, 0]))
    print(f"   {lab:20s} b = [{', '.join(f'{x:+.2f}' for x in b)}]   u12 {irf[12, 0]:+.3f} [{lo[12]:+.3f},{hi[12]:+.3f}]   u24 {irf[24, 0]:+.3f}")
print("\n(3) Baseline (windows, macro 0, EVENT timing), 150 draws over events and VAR residuals\n")
for lab, cols, vs in SPECS + [("long 1973- (funds rate)", ["u_gap", "pi_core", "ffr", "market_rstar"], "1973-01"), ("short 1994- (2-year, no Baa)", ["u_gap", "pi_core", "gs2", "market_rstar"], "1994-01")]:
    r0, X, dum = fit_var(cols, vs); dv = [DV[c] for c in cols if c in DV]
    b0 = bvec(cols, exposure(P0, idx0, dv)); irf0 = np.einsum("hij,j->hi", r0.ma_rep(H), b0); dr = []
    for _ in range(B):
        ib = rng.choice(idx0, size=len(idx0), replace=True); Pb, _, ib = slopes(ib, "NS"); rb = boot_var(r0, X, dum, rng)
        dr.append(np.einsum("hij,j->hi", rb.ma_rep(H), bvec(cols, exposure(Pb, ib, dv)))[:, 0])
    dr = np.array(dr); lo, hi = np.percentile(dr, [5, 95], axis=0)
    rows.append(dict(spec=lab, variant="baseline150", u12=irf0[12, 0], lo12=lo[12], hi12=hi[12], u24=irf0[24, 0], lo24=lo[24], hi24=hi[24]))
    print(f"   {lab:30s} u12 {irf0[12, 0]:+.3f} [{lo[12]:+.3f},{hi[12]:+.3f}]  u24 {irf0[24, 0]:+.3f} [{lo[24]:+.3f},{hi[24]:+.3f}]  u36 {irf0[36, 0]:+.3f}  P(u12>0) {np.mean(dr[:, 12] > 0):.2f}")
pd.DataFrame(rows).to_csv("followups.csv", index=False, float_format="%.4f")
