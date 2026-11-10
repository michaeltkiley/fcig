"""Route B impulse responses with parameter uncertainty. Loads the maximum-likelihood estimate (route_b.py), draws parameters from the Gaussian approximation (inverse numerical Hessian), combines with a bootstrap over events for the window impact vector b,
and reports the unemployment-gap and core-PCE response (monthly averages) per +1 pp rise in the scaling variable on the event day. Usage: python route_b_irf.py y2|ff
Output: route_b.log, route_b.csv"""
import sys, numpy as np, pandas as pd
import route_b as B
import mf_common as F
from mf_common import *
policy = sys.argv[1] if len(sys.argv) > 1 else "y2"
rng = np.random.default_rng(9); Hm = 36
th = np.load(f"route_b_theta_{policy}.npy"); data = B.build(policy); f0 = B.negll(th, data)
# numerical Hessian by central differences with curvature-scaled steps
n = len(th); H = np.zeros((n, n))
def f(x): return B.negll(x, data)
hd = np.zeros(n)
for i in range(n):
    h = 1e-4 * max(1.0, abs(th[i])); xp = th.copy(); xm = th.copy(); xp[i] += h; xm[i] -= h
    hd[i] = (f(xp) - 2 * f0 + f(xm)) / h ** 2
step = 0.05 / np.sqrt(np.maximum(np.abs(hd), 1e2))
for i in range(n):
    for j in range(i, n):
        xpp = th.copy(); xpm = th.copy(); xmp = th.copy(); xmm = th.copy()
        xpp[i] += step[i]; xpp[j] += step[j]; xpm[i] += step[i]; xpm[j] -= step[j]; xmp[i] -= step[i]; xmp[j] += step[j]; xmm[i] -= step[i]; xmm[j] -= step[j]
        H[i, j] = H[j, i] = (f(xpp) - f(xpm) - f(xmp) + f(xmm)) / (4 * step[i] * step[j])
w, V = np.linalg.eigh(H); print(f"Hessian eigenvalues: min {w.min():.2e}, max {w.max():.2e}; non-positive: {int((w <= 1e-8).sum())}")
w = np.maximum(w, 1e-3); cov = V @ np.diag(1 / w) @ V.T
rows = []
for sk in ("NS", "NS-GB", "MP1") if policy == "ff" else ("NS", "NS-GB"):
    if policy == "ff" and sk == "NS-GB": pass
    idx0 = event_index(sk); wr0 = win_response(sk, idx0)
    from route_a_pos import positions
    pos0 = positions(idx0)
    key = "ff" if policy == "ff" else "y2"
    out_u, out_p = [], []; nrej = 0
    for _ in range(300):
        thd = rng.multivariate_normal(th, cov); A, c, Lq, mu = B.unpack(thd)
        if np.max(np.abs(np.linalg.eigvals(A))) >= 1: nrej += 1; continue
        ib = rng.choice(idx0, size=len(idx0), replace=True); wr = win_response(sk, ib); posb = positions(ib)
        b = np.array([wr[key], wr["idx"], 0.0, 0.0]); r = B.irf_monthly(A, b, posb, months=Hm + 1)
        out_u.append(r[:, 0]); out_p.append(r[:, 1])
    print(f"   draws kept {len(out_u)}, rejected for explosive A: {nrej}")
    out_u, out_p = np.array(out_u), np.array(out_p); lo, hi = np.percentile(out_u, [5, 95], axis=0)
    A, c, Lq, mu = B.unpack(th); b = np.array([wr0[key], wr0["idx"], 0.0, 0.0]); r0 = B.irf_monthly(A, b, pos0, months=Hm + 1)
    rows.append(dict(shock=sk, policy=policy, u12=r0[12, 0], lo12=lo[12], hi12=hi[12], u24=r0[24, 0], lo24=lo[24], hi24=hi[24], u36=r0[36, 0], pi12=r0[12, 1], P12=float(np.mean(out_u[:, 12] > 0))))
    print(f"shock {sk} (policy variable {policy}; {len(out_u)} draws): u12 {r0[12, 0]:+.3f} [{lo[12]:+.3f},{hi[12]:+.3f}]  u24 {r0[24, 0]:+.3f} [{lo[24]:+.3f},{hi[24]:+.3f}]  u36 {r0[36, 0]:+.3f}  P(u12>0) {np.mean(out_u[:, 12] > 0):.2f}  | core PCE 12m {r0[12, 1]:+.2f}")
pd.DataFrame(rows).to_csv(f"route_b_{policy}.csv", index=False, float_format="%.4f")
