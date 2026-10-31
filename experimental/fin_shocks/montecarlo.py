"""Monte Carlo validation. Truth: a DAILY VAR(1) (the route-B estimate on real data), sparse window shocks with impact b = (+1 policy, +1 index, 0, 0), 4 variables (policy, index, unemployment, core PCE); daily financial data, macro observed as monthly averages.
Compared against the TRUE monthly-average response of unemployment to the shock, with the event dates of the real data (NS):
  (a) stage-0 monthly VAR (12 lags) with the exposure-weighted impact vector (EVENT) and the first-day-of-month impact vector (START)   [b computed from the TRUE daily response: isolates the aggregation bias]
  (b) route A: HAR daily block + the monthly VAR's macro equations
  (c) route B: state-space MLE
R replications of 1990-2026 (weekday calendar). Output: montecarlo.log"""
import sys, time, numpy as np, pandas as pd
import route_b as B
import mf_common as F
from mf_common import *
from route_a_pos import positions
from statsmodels.tsa.api import VAR
rng = np.random.default_rng(123); R = int(sys.argv[1]) if len(sys.argv) > 1 else 6; Hm = 36; HAR = (1, 5, 22, 66); LAGS = 12
th = np.load("route_b_theta_y2.npy"); A_t, c_t, Lq_t, mu_t = B.unpack(th)
MULT = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0            # scale the index -> unemployment link in the DGP (A[2,1])
if MULT != 1.0:
    A_t = A_t.copy(); A_t[2, 1] *= MULT; th = th.copy(); th[:16] = A_t.ravel(); c_t = mu_t - A_t @ mu_t
print(f"DGP link multiplier {MULT}; max |eig| of A {np.max(np.abs(np.linalg.eigvals(A_t))):.5f}")
idx0 = event_index("NS"); pos = positions(idx0); b = np.array([1.0, 1.0, 0.0, 0.0])
truth = B.irf_monthly(A_t, b, pos, months=Hm + 1)[:, 0]
print(f"truth (monthly-average unemployment response, per +1 pp): u6 {truth[6]:+.3f}  u12 {truth[12]:+.3f}  u24 {truth[24]:+.3f}  u36 {truth[36]:+.3f}")
cal = pd.bdate_range("1990-01-01", "2026-10-30"); mo = cal.to_period("M")
first = np.r_[True, mo[1:] != mo[:-1]]; last = np.r_[mo[1:] != mo[:-1], True]; nm = pd.Series(mo, index=cal).groupby(mo).transform("size").values.astype(float)
def simulate():
    T = len(cal); x = np.zeros((T, 4)); x[0] = mu_t; eta = rng.normal(size=(T, 4)) @ Lq_t.T
    for t in range(1, T): x[t] = c_t + A_t @ x[t - 1] + eta[t]
    obsM = np.full((T, 2), np.nan); mon = pd.DataFrame(x[:, 2:], index=mo).groupby(level=0).mean()
    for j in range(2): obsM[np.where(last)[0], j] = mon.values[:, j]
    return x, np.column_stack([x[:, 0], x[:, 1]]), obsM, mon
def macro_rows_(r0, nf=2): return r0.coefs[:, :2, :2], r0.coefs[:, :2, 2:2 + nf]
def full_irf(Bd, A, C, b_day, k0, n0, months=Hm + 1, nother=21):
    nf = Bd.shape[1]; off = max(HAR); nd = n0 + nother * (months - 1); f = np.zeros((nd + off, nf)); macro = np.zeros((months, 2)); fbar = np.zeros((months, nf))
    lens = [n0] + [nother] * (months - 1); start = np.concatenate([[0], np.cumsum(lens)])
    for t in range(months):
        if t >= 1:
            m = np.zeros(2)
            for l in range(1, LAGS + 1):
                if t - l >= 0: m += A[l - 1] @ macro[t - l] + C[l - 1] @ fbar[t - l]
            macro[t] = m
        for tau in range(start[t], start[t + 1]):
            if tau < k0: continue
            if tau == k0: f[off + tau] = b_day; continue
            x = np.concatenate([[0.0]] + [f[off + tau - h:off + tau].mean(axis=0) for h in HAR] + [macro[t - 1] if t >= 1 else np.zeros(2)])
            f[off + tau] = x @ Bd
        fbar[t] = f[off + start[t]:off + start[t + 1]].mean(axis=0)
    return macro
res = {k: [] for k in ("EVENT", "START", "A", "B")}; t0 = time.time()
for rep in range(R):
    x, obsF, obsM, mon = simulate()
    # monthly data
    mdf = pd.DataFrame({"y2": pd.DataFrame(x[:, 0], index=mo).groupby(level=0).mean()[0], "idx": pd.DataFrame(x[:, 1], index=mo).groupby(level=0).mean()[0], "u": mon[0], "p": mon[1]}); mdf.index = mdf.index.to_timestamp()
    var = VAR(mdf[["u", "p", "y2", "idx"]]).fit(12); Th = var.ma_rep(Hm)
    # true daily financial response r(k) = A^k b, exposures
    rk = [np.linalg.matrix_power(A_t, k) @ b for k in range(64)]; r = np.array(rk)[:, :2]; Ac = np.cumsum(r, axis=0)
    bE = sum(w * Ac[n0 - 1 - k0] / n0 for k0, n0, w in pos); bS = Ac[20] / 21
    for nm_, bb in (("EVENT", bE), ("START", bS)):
        res[nm_].append(np.einsum("hij,j->hi", Th, np.r_[0.0, 0.0, bb])[:, 0])
    # route A: HAR block
    f = pd.DataFrame(x[:, :2], index=cal); macprev = pd.DataFrame(x[:, 2:], index=mo).groupby(level=0).mean(); mp = macprev.shift(1).reindex(mo).values
    cols = [f.rolling(h).mean().shift(1).values for h in HAR]; Xd = np.column_stack([np.ones(len(f))] + cols + [mp]); Yd = f.values
    ok = ~np.isnan(Xd).any(axis=1); Bd = np.linalg.lstsq(Xd[ok], Yd[ok], rcond=None)[0]; Aa, Ca = macro_rows_(var)
    ua = sum(w * full_irf(Bd, Aa, Ca, np.array([1.0, 1.0]), k0, n0)[:, 0] for k0, n0, w in pos); res["A"].append(ua)
    # route B: MLE from perturbed truth
    data = (cal, obsF, obsM, first.astype(float), nm)
    th0 = th.copy()                                              # start at the true parameters (the likelihood is explosive a few 1e-3 away)
    fx, _ = B.fit_theta(th0, data, rounds=2, verbose=False)
    Ah, ch, Lh, muh = B.unpack(fx); res["B"].append(B.irf_monthly(Ah, b, pos, months=Hm + 1)[:, 0])
    print(f"rep {rep + 1}/{R} done ({time.time() - t0:.0f}s): u12 EVENT {res['EVENT'][-1][12]:+.3f} START {res['START'][-1][12]:+.3f} A {res['A'][-1][12]:+.3f} B {res['B'][-1][12]:+.3f}", flush=True)
print(f"\nTRUE u12 {truth[12]:+.3f}, u24 {truth[24]:+.3f}, u36 {truth[36]:+.3f}; mean over {R} replications (bias, RMSE):")
for k, v in res.items():
    v = np.array(v)
    print(f"   {k:6s} " + "  ".join(f"u{h}: {v[:, h].mean():+.3f} (bias {v[:, h].mean() - truth[h]:+.3f}, rmse {np.sqrt(np.mean((v[:, h] - truth[h]) ** 2)):.3f})" for h in (12, 24, 36)))
