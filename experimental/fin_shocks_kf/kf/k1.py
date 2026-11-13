"""K1 (KF-A2): latent daily macro with a within-month channel; nests Note B (stage 1) at Gamma = 0, S_nu = 0.

Day tau of month t (daily rows of the daily block; n_t rows in month t), f observed, x = (u, pi) latent daily:
  start of month t:  s_t = c_m + sum_l A_l xbar_{t-l} + sum_l G_l fbar_{t-l} + e_t,  e ~ N(0, S_m)          (Note B's monthly equation; xbar observed)
  macro before day tau's financial move:  z_tau = s_t on the first day, x_{tau-1} after
  daily block:   f_tau = c_d + sum_h B_h f^(h)_tau + D_1 xbar_{t-1} + D_0 z_tau + eps_tau,  eps ~ N(0, S_d)      (Note B with z_tau in place of m_t)
  macro after the day:  x_tau = z_tau + Gamma (f_tau - f_{tau-1}) + nu_tau,  nu ~ N(0, S_nu)
  observed: xbar_t = (1 / n_t) sum_tau x_tau, without error.
With Gamma = 0 and S_nu = 0, x_tau = s_t = xbar_t on every day: Note B.
The announcement moves f by b (macro entries zero, M6); macro then moves through Gamma on the same day.

State-space form, step tau: alpha_tau = (z_tau, S_tau = sum of x over the earlier days of the month, xbar_{t-1}, ..., xbar_{t-L}).
Observation at step tau: f_tau; on the first row of each month also xbar_{t-1} (lag 1 of the state); a final step observes the last month's average.
Estimation: maximum likelihood by EM (smoothed moments; Gamma and S_nu from w_tau = x_tau - z_tau, a linear function of alpha_tau and alpha_{tau+1})."""
import numpy as np
from . import ssm, fastkf
from .noteb import Design, ols_fit, unpack, HAR, H, to_level
from .inputs import window_impact, position_bins


class K1Data:
    def __init__(self, ds):
        self.ds = ds; I = ds
        first = np.r_[True, ds.mon_of_row[1:] != ds.mon_of_row[:-1]]
        self.first = first; self.last = ds.last
        self.n = np.bincount(ds.mon_of_row)[ds.mon_of_row]                                          # rows in the month of each row
        fd = ds.Fd; self.df = np.vstack([fd[0] - self.prev0(), np.diff(fd, axis=0)])              # f_tau - f_{tau-1}

    def prev0(self):
        """f on the daily row before the first row of the sample (the block's lags use the same rows)."""
        from .noteb import inputs
        I = inputs(); F = I.daily(self.ds.form, self.ds.fci).loc["1990-01-02":].dropna()
        return F.loc[:self.ds.dates[0]].values[-2]


def arrays(kd, Cm, Sm, Cd, Sd, G, Snu):
    """The state space as arrays: a0, P0, y, d, c (per step), typ (0 = within the month, 1 + j = month end with n_t = NT[j], last = identity), T, Q, Z, H, index dict."""
    ds = kd.ds; K, L, nd = ds.K, ds.L, ds.nd; par = unpack(Cm, Cd, K, L, nd)
    iz, iS, il = 0, K, 2 * K; n = 2 * K + K * L; N = len(ds.Fd); nm = len(ds.P)
    cm_next = par["cm"] + sum(ds.flags[:, nd * l:nd * (l + 1)] @ par["G"][l].T for l in range(L))
    Z = np.zeros((nd + K, n)); Z[:nd, iz:iz + K] = par["D0"]; Z[:nd, il:il + K] = par["D1"]; Z[nd:, il:il + K] = np.eye(K)
    H = np.zeros((nd + K, nd + K)); H[:nd, :nd] = Sd
    y = np.full((N + 1, nd + K), np.nan); y[:N, :nd] = ds.Fd
    fr = np.where(kd.first)[0]; mo = ds.mon_of_row
    for t in fr:
        if mo[t] > 0: y[t, nd:] = ds.Mm[mo[t] - 1]
    y[N, nd:] = ds.Mm[-1]
    d = np.zeros((N + 1, nd + K)); d[:N, :nd] = ds.Wd @ par["Bd"].T
    Tw = np.eye(n); Tw[iS:iS + K, iz:iz + K] = np.eye(K)
    Rw = np.zeros((n, K)); Rw[iz:iz + K] = np.eye(K); Rw[iS:iS + K] = np.eye(K)
    NT = sorted(set(int(v) for v in kd.n[kd.last])); A1 = par["A"][0]
    Ts, Qs, Rns = [Tw], [Rw @ Snu @ Rw.T], {}
    for nt in NT:
        T = np.zeros((n, n))
        T[il:il + K, iS:iS + K] = np.eye(K) / nt; T[il:il + K, iz:iz + K] = np.eye(K) / nt          # xbar_t = (S + x_tau) / n_t
        T[il + K:, il:n - K] = np.eye(K * (L - 1))
        T[iz:iz + K, :] = A1 @ T[il:il + K, :]
        for l in range(2, L + 1): T[iz:iz + K, il + K * (l - 2):il + K * (l - 1)] += par["A"][l - 1]
        Rn = np.zeros((n, K)); Rn[il:il + K] = np.eye(K) / nt; Rn[iz:iz + K] = A1 / nt
        Re = np.zeros((n, K)); Re[iz:iz + K] = np.eye(K)
        Ts.append(T); Qs.append(Re @ Sm @ Re.T + Rn @ Snu @ Rn.T); Rns[nt] = Rn
    Ts.append(np.eye(n)); Qs.append(np.zeros((n, n)))
    typ = np.zeros(N + 1, dtype=np.int64); typ[N] = len(Ts) - 1
    gdf = kd.df @ G.T; c = np.zeros((N + 1, n))
    inm = ~kd.last; c[:N][inm, iz:iz + K] = gdf[inm]; c[:N][inm, iS:iS + K] = gdf[inm]
    for t in np.where(kd.last)[0]:
        nt = int(kd.n[t]); typ[t] = 1 + NT.index(nt); c[t] = Rns[nt] @ gdf[t]                      # the day's Gamma df enters xbar_t like nu
        if mo[t] + 1 < nm: c[t, iz:iz + K] += cm_next[mo[t] + 1]
    a0 = np.zeros(n); a0[iz:iz + K] = cm_next[0] + sum(par["A"][l] @ ds.mlags[0, K * l:K * (l + 1)] for l in range(L)); a0[il:] = ds.mlags[0]
    P0 = np.zeros((n, n)); P0[iz:iz + K, iz:iz + K] = Sm
    return a0, P0, y, d, c, typ, np.array(Ts), np.array(Qs), Z, H, dict(iz=iz, iS=iS, il=il, n=n)


def loglik(kd, theta, store=False):
    a0, P0, y, d, c, typ, T, Q, Z, H, ix = arrays(kd, *theta)
    if not store: return fastkf.loglik(a0, P0, y, d, c, typ, T, Q, Z, H)
    step = lambda t: dict(y=y[t], Z=Z, d=d[t], H=H, T=T[typ[t]], c=c[t], RQR=Q[typ[t]])
    ll, keep = ssm.kfilter(a0, P0, len(y), step, True)
    return ll, keep, ix


def em_step(kd, theta):
    """One EM step: returns (log-likelihood at theta, updated theta)."""
    ds = kd.ds; K, L, nd = ds.K, ds.L, ds.nd
    Xm = ds.Xm(); nw = ds.Wd.shape[1]; N = len(ds.Fd); df = kd.df
    ll, keep, ix = loglik(kd, theta, store=True)
    a, P, C = ssm.smoother(keep); iz, iS, il = ix["iz"], ix["iS"], ix["il"]
    # monthly equation: s_t = z on the first row of month t
    r = np.where(kd.first)[0]; Es = a[r, iz:iz + K]; Vs = P[r, iz:iz + K, iz:iz + K].sum(0)
    Cm = np.linalg.lstsq(Xm, Es, rcond=None)[0]; E = Es - Xm @ Cm; Sm = (E.T @ E + Vs) / len(r); Sm = (Sm + Sm.T) / 2
    # daily block: regressors [Wd, xbar_{t-1}, z_tau]
    Zr = np.column_stack([ds.Wd, a[:N, il:il + K], a[:N, iz:iz + K]])
    idx = np.r_[np.arange(il, il + K), np.arange(iz, iz + K)]
    V = P[:N][:, idx][:, :, idx].sum(0)
    Szz = Zr.T @ Zr; Szz[nw:, nw:] += V
    Cd = np.linalg.solve(Szz, Zr.T @ ds.Fd); R = ds.Fd - Zr @ Cd; Sd = (R.T @ R + Cd[nw:].T @ V @ Cd[nw:]) / N; Sd = (Sd + Sd.T) / 2
    # w_tau = x_tau - z_tau: z_{tau+1} - z_tau within the month; n_t xbar_t - S_tau - z_tau at the month end (xbar_t = lag 1 of alpha_{tau+1})
    n = ix["n"]; Ew = np.zeros((N, K)); Vw = np.zeros((K, K))
    Ain = np.zeros((K, n)); Ain[:, iz:iz + K] = np.eye(K); Bin = -Ain
    Bend = np.zeros((K, n)); Bend[:, iS:iS + K] = -np.eye(K); Bend[:, iz:iz + K] = -np.eye(K)
    for t in range(N):
        if kd.last[t]: Ap = np.zeros((K, n)); Ap[:, il:il + K] = kd.n[t] * np.eye(K); Bp = Bend
        else: Ap, Bp = Ain, Bin
        Ew[t] = Ap @ a[t + 1] + Bp @ a[t]; X = Ap @ C[t] @ Bp.T
        Vw += Ap @ P[t + 1] @ Ap.T + Bp @ P[t] @ Bp.T + X + X.T
    G = np.linalg.solve(df.T @ df, df.T @ Ew).T; U = Ew - df @ G.T; Snu = (U.T @ U + Vw) / N; Snu = (Snu + Snu.T) / 2
    return ll, (Cm, Sm, Cd, Sd, G, Snu)


def _vec(th): return np.concatenate([x.ravel() for x in th])
def _unvec(v, like):
    out, i = [], 0
    for x in like: out.append(v[i:i + x.size].reshape(x.shape)); i += x.size
    return tuple(out)
def _psd(th): return all(np.linalg.eigvalsh(th[j]).min() > 0 for j in (1, 3, 5))


def em(kd, theta, iters=300, tol=1e-5, verbose=False):
    """EM accelerated by SQUAREM (Varadhan and Roland 2008, scheme S3); an extrapolated point is kept only if its covariances are positive definite
    and its log-likelihood is not below that of the plain EM step. Stops when the gain per cycle is below tol. Returns theta and the log-likelihood path."""
    path = []
    for it in range(iters):
        ll0, th1 = em_step(kd, theta); _, th2 = em_step(kd, th1)
        v0, v1, v2 = _vec(theta), _vec(th1), _vec(th2); r = v1 - v0; v = v2 - 2 * v1 + v0
        alpha = -np.sqrt(r @ r) / np.sqrt(v @ v) if v @ v > 0 else -1.0; alpha = min(alpha, -1.0)
        cand = _unvec(v0 - 2 * alpha * r + alpha ** 2 * v, theta)
        ll2 = loglik(kd, th2); new, llnew = th2, ll2
        if _psd(cand):
            llc, thc = em_step(kd, cand)                                                             # stabilising EM step from the extrapolated point
            llc2 = loglik(kd, thc)
            if llc2 >= ll2: new, llnew = thc, llc2
        path.append(llnew)
        if verbose: print(f"  SQUAREM {it}: loglik {llnew:.4f} (alpha {alpha:.1f})", flush=True)
        if it > 0 and llnew - path[-2] < tol: theta = new; break
        theta = new
    return theta, path


# ---------------------------------------------------------------- responses from the full daily state
def irf(theta, K, L, nd, b, bins, months=H + 1, mlen=21):
    """State: [f lags 0..65, running sum of f, fbar_{t-1..t-L}, x_cur (macro after the latest day), running sum of x, xbar_{t-1..t-L}] in deviations.
    Returns monthly averages of macro (the observed xbar) and of f, and end-of-month f."""
    Cm, Sm, Cd, Sd, G, Snu = theta; par = unpack(Cm, Cd, K, L, nd)
    nf = 66 * nd; iSf = nf; iFb = iSf + nd; ix = iFb + nd * L; iSx = ix + K; iXb = iSx + K; n = iXb + K * L
    T = np.zeros((n, n))                                                                            # one day: f_tau, then x_tau, sums
    for hi, h in enumerate(HAR):
        Bh = par["Bd"][:, 1 + hi * nd:1 + (hi + 1) * nd]
        for j in range(h): T[:nd, j * nd:(j + 1) * nd] += Bh / h
    T[:nd, ix:ix + K] += par["D0"]; T[:nd, iXb:iXb + K] += par["D1"]
    T[nd:nf, :nf - nd] = np.eye(nf - nd)
    T[iSf:iSf + nd] = T[:nd]; T[iSf:iSf + nd, iSf:iSf + nd] += np.eye(nd)
    T[iFb:ix, iFb:ix] = np.eye(nd * L)
    T[ix:ix + K] = G @ T[:nd]; T[ix:ix + K, ix:ix + K] += np.eye(K); T[ix:ix + K, :nd] -= G       # x_tau = x_{tau-1} + Gamma (f_tau - f_{tau-1})
    T[iSx:iSx + K] = T[ix:ix + K]; T[iSx:iSx + K, iSx:iSx + K] += np.eye(K)
    T[iXb:n, iXb:n] = np.eye(K * L)

    def Tstart(nprev):
        Cl = np.eye(n)
        Cl[iFb:iFb + nd] = 0; Cl[iFb:iFb + nd, iSf:iSf + nd] = np.eye(nd) / nprev; Cl[iFb + nd:ix] = 0; Cl[iFb + nd:ix, iFb:ix - nd] = np.eye(nd * (L - 1))
        Cl[iXb:iXb + K] = 0; Cl[iXb:iXb + K, iSx:iSx + K] = np.eye(K) / nprev; Cl[iXb + K:n] = 0; Cl[iXb + K:n, iXb:n - K] = np.eye(K * (L - 1))
        Cl[iSf:iSf + nd] = 0; Cl[iSx:iSx + K] = 0
        Mx = np.eye(n); Mx[ix:ix + K] = 0                                                           # x_cur = s_t
        for l in range(1, L + 1):
            Mx[ix:ix + K, iXb + K * (l - 1):iXb + K * l] = par["A"][l - 1]; Mx[ix:ix + K, iFb + nd * (l - 1):iFb + nd * l] = par["G"][l - 1]
        return T @ Mx @ Cl
    cache = {}; om = np.zeros((months, K)); of = np.zeros((months, nd)); oe = np.zeros((months, nd))
    for k0, n0, wgt in bins:
        s = np.zeros(n); s[:nd] = b; s[iSf:iSf + nd] = b; s[ix:ix + K] = G @ b; s[iSx:iSx + K] = G @ b   # announcement day: f = b, x = Gamma b
        for _ in range(k0 + 1, n0): s = T @ s
        mm = [s[iSx:iSx + K] / n0]; fb = [s[iSf:iSf + nd] / n0]; fe = [s[:nd].copy()]; nprev = n0
        for _t in range(1, months):
            if nprev not in cache: cache[nprev] = Tstart(nprev)
            s = cache[nprev] @ s
            for _ in range(1, mlen): s = T @ s
            mm.append(s[iSx:iSx + K] / mlen); fb.append(s[iSf:iSf + nd] / mlen); fe.append(s[:nd].copy()); nprev = mlen
        om += wgt * np.array(mm); of += wgt * np.array(fb); oe += wgt * np.array(fe)
    return om, of, oe


# ---------------------------------------------------------------- ECME: EM for Note B's blocks, direct maximisation over (Gamma, S_nu)
def _phi(G, Snu):
    Lc = np.linalg.cholesky(Snu); K = len(Lc); i = np.tril_indices(K)
    v = Lc[i].copy(); v[[j for j, (a, b) in enumerate(zip(*i)) if a == b]] = np.log(np.diag(Lc)); return np.r_[G.ravel(), v]


def _from_phi(phi, K, nd):
    G = phi[:K * nd].reshape(K, nd); i = np.tril_indices(K); Lc = np.zeros((K, K)); Lc[i] = phi[K * nd:]
    Lc[np.diag_indices(K)] = np.exp(np.diag(Lc)); return G, Lc @ Lc.T


def fit(kd, theta, cycles=200, tol=1e-4, verbose=False):
    """ECME from theta. Each cycle: one EM step for (Cm, Sm, Cd, Sd) holding (Gamma, S_nu); then L-BFGS over (Gamma, chol S_nu) holding the rest.
    Stops when a cycle gains less than tol. Returns theta and the log-likelihood path."""
    from scipy.optimize import minimize
    K, nd = kd.ds.K, kd.ds.nd; path = [loglik(kd, theta)]
    for it in range(cycles):
        _, th = em_step(kd, theta); theta = th[:4] + theta[4:]
        f = lambda p: -loglik(kd, theta[:4] + _from_phi(p, K, nd))
        r = minimize(f, _phi(*theta[4:]), method="L-BFGS-B", options=dict(maxiter=200))
        theta = theta[:4] + _from_phi(r.x, K, nd); path.append(-r.fun)
        if verbose: print(f"  ECME {it}: loglik {path[-1]:.4f}", flush=True)
        if path[-1] - path[-2] < tol: break
    return theta, path
