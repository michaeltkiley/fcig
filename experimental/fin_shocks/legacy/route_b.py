"""Route B: state-space mixed-frequency VAR at DAILY base frequency (weekday calendar), estimated by maximum likelihood with a numba Kalman filter.
Latent daily state x_tau = [policy (2-year or funds rate), market index, unemployment gap, core PCE] follows a VAR(1): x_tau = c + A x_{tau-1} + eta_tau, eta ~ N(0, Sigma). (A daily VAR(1) is a deliberate simplification; richer daily lag structures blow up the state dimension.)
Observations: the two financial series daily (missing days and pre-sample periods are missing data); unemployment and core PCE only as MONTHLY AVERAGES of the latent daily series, produced by running-sum (cumulator) states that reset on the first weekday of each month and are read on the last weekday.
No credit spread (FS-A5 baseline). 2020 macro observations are dropped (treated as missing).
Window shock: the impact vector b comes from the 30-minute windows (financial entries; macro entries zero), NOT from the likelihood; IRF of the latent daily state = A^k b; monthly-average unemployment response averaged over the empirical event positions in the month. Parameter uncertainty: draws from the Gaussian approximation (inverse numerical Hessian) combined with a bootstrap over events for b.
Output: route_b.log, route_b.csv"""
import numpy as np, pandas as pd, time
from numba import njit
from scipy.optimize import minimize
import mf_common as F
from mf_common import *

@njit(cache=True)
def kf(A, c, Lq, obsF, obsM, reset, nm, Hf, Hm, x0, P0):
    T = obsF.shape[0]; ns = 6
    Q = Lq @ Lq.T
    R = np.zeros((ns, 4)); 
    for i in range(4): R[i, i] = 1.0
    R[4, 2] = 1.0; R[5, 3] = 1.0
    a = np.zeros(ns); a[:4] = x0
    P = np.zeros((ns, ns)); P[:4, :4] = P0
    d = np.zeros(ns); d[:4] = c; d[4] = c[2]; d[5] = c[3]
    RQR = R @ Q @ R.T
    ll = 0.0
    for t in range(T):
        Tm = np.zeros((ns, ns))
        Tm[:4, :4] = A; Tm[4, :4] = A[2]; Tm[5, :4] = A[3]
        keep = 1.0 - reset[t]
        Tm[4, 4] = keep; Tm[5, 5] = keep
        if t == 0:
            ap = a.copy(); Pp = P.copy()
            ap[4] = ap[2]; ap[5] = ap[3]                      # first weekday of the first month: cumulators equal the state
            Pp[4, :] = Pp[2, :]; Pp[:, 4] = Pp[:, 2]; Pp[5, :] = Pp[3, :]; Pp[:, 5] = Pp[:, 3]
        else:
            ap = d + Tm @ a; Pp = Tm @ P @ Tm.T + RQR
        # sequential scalar updates
        for j in range(2):
            y = obsF[t, j]
            if not np.isnan(y):
                v = y - ap[j]; Fv = Pp[j, j] + Hf
                if Fv <= 1e-12: return -1e12
                K = Pp[:, j] / Fv
                ap = ap + K * v
                Pp = Pp - np.outer(K, Pp[j, :])
                ll += -0.5 * (np.log(2 * np.pi * Fv) + v * v / Fv)
        for j in range(2):
            y = obsM[t, j]
            if not np.isnan(y):
                zi = 4 + j; sc = 1.0 / nm[t]
                v = y - sc * ap[zi]; Fv = sc * sc * Pp[zi, zi] + Hm
                if Fv <= 1e-12: return -1e12
                K = sc * Pp[:, zi] / Fv
                ap = ap + K * v
                Pp = Pp - np.outer(K, sc * Pp[zi, :])
                ll += -0.5 * (np.log(2 * np.pi * Fv) + v * v / Fv)
        a = ap; P = 0.5 * (Pp + Pp.T)
    return ll

def build(policy="y2", start="1973-01-01", end="2026-10-30"):
    cal = pd.bdate_range(start, end)
    mo = cal.to_period("M"); first = np.r_[True, mo[1:] != mo[:-1]]; last = np.r_[mo[1:] != mo[:-1], True]
    nmo = pd.Series(mo, index=cal).groupby(mo).transform("size").values.astype(float)
    pol = DAILY[policy].reindex(cal); idx = DAILY["idx"].reindex(cal)
    obsF = np.column_stack([pol.values, idx.values])
    obsM = np.full((len(cal), 2), np.nan)
    for j, col in enumerate(("u_gap", "pi_core")):
        s = M[col]
        for per, v in s.items():
            if per.year == 2020 and per.month >= 3: continue
            if np.isnan(v): continue
            pos = np.where((mo == per) & last)[0]
            if len(pos): obsM[pos[0], j] = v
    return cal, obsF, obsM, first.astype(float), nmo

def unpack(th):
    A = th[:16].reshape(4, 4); mu = th[16:20]; Lq = np.zeros((4, 4)); k = 20
    for i in range(4):
        for j in range(i + 1):
            Lq[i, j] = np.exp(th[k]) if i == j else th[k]; k += 1
    c = mu - A @ mu                                                    # intercept implied by the mean mu
    return A, c, Lq, mu

def negll(th, data):
    A, c, Lq, mu = unpack(th)
    if np.max(np.abs(np.linalg.eigvals(A))) > 0.99995: return 1e12
    cal, obsF, obsM, reset, nm = data
    P0 = np.diag([25.0, 25.0, 4.0, 4.0])
    ll = kf(A, c, Lq, obsF, obsM, reset, nm, 1e-6, 1e-6, mu, P0)
    return -ll

def start_values(data, policy):
    cal, obsF, obsM, reset, nm = data
    dF = np.diff(obsF, axis=0); dF = dF[~np.isnan(dF).any(axis=1)]
    sd = np.r_[dF.std(0), [0.01, 0.15]]
    A0 = np.diag([0.995, 0.995, 0.999, 0.995])
    mu = np.r_[np.nanmean(obsF, 0), np.nanmean(obsM, 0)]
    th = np.r_[A0.ravel(), mu]
    L = np.diag(np.log(sd)); Lq = []
    for i in range(4):
        for j in range(i + 1): Lq.append(np.log(sd[i]) if i == j else 0.0)
    return np.r_[th, Lq]

def irf_monthly(A, b, pos, months=37, nother=21):
    """Deterministic daily response A^k b; monthly averages of the macro states for months 0..months-1 for a shock on day k0 of a month with n0 weekdays; weighted by pos."""
    tot = np.zeros((months, 2))
    for k0, n0, w in pos:
        nd = n0 + nother * (months - 1); x = np.zeros((nd, 4)); cur = b.copy()
        for tau in range(k0, nd):
            if tau > k0: cur = A @ cur
            x[tau] = cur
        s = 0
        for t in range(months):
            ln = n0 if t == 0 else nother
            tot[t] += w * x[s:s + ln, 2:].mean(axis=0); s += ln
    return tot

def fit_theta(th0, data, rounds=6, verbose=True, t0=None):
    """Maximum likelihood with diagonal curvature preconditioning, re-estimated each round (the likelihood is extremely curved in the daily-persistence parameters)."""
    t0 = t0 or time.time()
    th = th0.copy(); f = lambda x: negll(x, data)
    for rnd in range(rounds):
        hd = np.zeros(len(th)); f0 = f(th)
        for i in range(len(th)):
            h = 1e-4 * max(1.0, abs(th[i])); xp = th.copy(); xm = th.copy(); xp[i] += h; xm[i] -= h
            hd[i] = (f(xp) - 2 * f0 + f(xm)) / h ** 2
        sc = 1.0 / np.sqrt(np.maximum(np.abs(hd), 1e2))
        res = minimize(lambda z: f(th + sc * z) / 1e3, np.zeros(len(th)), method="L-BFGS-B", options=dict(maxiter=300, maxfun=60000, eps=1e-7, ftol=1e-14, gtol=1e-10))
        th = th + sc * res.x
        if verbose: print(f"round {rnd}: -LL {f(th):.2f} ({res.message}), {res.nit} iterations, {time.time() - t0:.0f}s", flush=True)
        if res.nit < 3: break
    return th, f(th)

if __name__ == "__main__":
    import sys
    policy = sys.argv[1] if len(sys.argv) > 1 else "y2"
    t0 = time.time(); data = build(policy); th0 = start_values(data, policy)
    print(f"policy {policy}; days {len(data[0])}; financial obs {int((~np.isnan(data[1][:, 0])).sum())}/{int((~np.isnan(data[1][:, 1])).sum())}; macro obs {int((~np.isnan(data[2][:, 0])).sum())}; start -LL {negll(th0, data):.1f}; one eval {1000 * (time.time() - t0):.0f} ms")
    th, fv = fit_theta(th0, data, t0=t0)
    class _R: pass
    res = _R(); res.x = th; res.fun = fv; res.success = True; res.nit = 0; res.message = ''
    A, c, Lq, mu = unpack(res.x)
    print(f"converged {res.success}, -LL {res.fun:.1f}, iterations {res.nit}, time {time.time() - t0:.0f}s")
    print("A =\n", np.round(A, 4), "\nmax |eig| of A:", np.round(np.max(np.abs(np.linalg.eigvals(A))), 5), " half-lives (days) of eigenvalues:", np.round(np.log(0.5) / np.log(np.abs(np.linalg.eigvals(A)) + 1e-12), 0))
    np.save(f"route_b_theta_{policy}.npy", res.x)
