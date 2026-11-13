"""Note B's model in state-space form on a daily clock (stage 1: the same form and restrictions M1-M7 of KF_PLAN.md).

Daily clock = the rows of the daily block (weekdays with data, from 2 January 1996 to the last day with a monthly macro value).
Latent state on day tau of month t:  a_tau = (m_t, m_{t-1}, ..., m_{t-L}),  m = (u, pi).
  Transition: within a month, a is unchanged (macro first; m_t fixed for the month). Into the first day of month t+1:
      m_{t+1} = c_m + sum_l A_l m_{t+1-l} + sum_l G_l fbar_{t+1-l} + e_{t+1},   e ~ N(0, S_m);   the lags shift.
  Observation on day tau:  f_tau = c_d + sum_h B_h f^(h)_tau + D_1 m_{t-1} + D_0 m_t + eps_tau,   eps ~ N(0, S_d)
      (f^(h)_tau = average of f over the h previous rows; the financial variables are observed, so their lags and monthly averages enter as data);
      on the last row of month t also m_t, without error.
Estimation: maximum likelihood by EM (E step: Kalman smoother; M step: the regressions of the two equations on smoothed moments).
With m_t observed at the end of each month the smoothed macro state equals the data, so EM converges in one step to equation-by-equation OLS.
Responses: the full daily system (financial lags, running monthly sum, macro and monthly-average lags) as one state vector, propagated from b on the announcement day.
Inference: Note B's 12-month block bootstrap (same seeds and sequence of random draws)."""
import zlib
import numpy as np, pandas as pd
from .inputs import Inputs, window_impact, position_bins
from . import ssm

HAR = (1, 5, 22, 66)
H = 36
CAL_BOOT = pd.period_range("1996-01", "2026-09", freq="M")
_I = None


def inputs():
    global _I
    if _I is None: _I = Inputs()
    return _I


# ---------------------------------------------------------------- data in the two blocks
class Design:
    def __init__(self, form, fci, L, start="1996-01"):
        I = inputs(); self.form, self.fci, self.L = form, fci, L
        F = I.daily(form, fci); self.nd = F.shape[1]; mac = I.mac[["u", "pi"]]; K = self.K = 2
        # daily rows
        D = F.loc["1990-01-02":].dropna(); mo = D.index.to_period("M")
        har = np.column_stack([D.rolling(h).mean().shift(1).values for h in HAR])                    # [h1 (pol, idx), h5, h22, h66]
        mlag, mnow = mac.reindex(mo - 1).values, mac.reindex(mo).values
        ok = ~np.isnan(har).any(1) & ~np.isnan(mlag).any(1) & ~np.isnan(mnow).any(1) & ~np.isnan(D.values).any(1) & (D.index >= "1996-01-01")
        self.dates, self.dmon = D.index[ok], mo[ok]
        self.Wd = np.column_stack([np.ones(ok.sum()), har[ok]])                                     # observed daily regressors
        self.Fd = D.values[ok]; self.Md = (mlag[ok], mnow[ok])
        # monthly rows
        fbar = F.groupby(F.index.to_period("M")).mean()
        P = pd.period_range(start, "2026-09", freq="M"); self.P = P
        self.Mm = np.array([mac.loc[p].values for p in P])
        self.mlags = np.array([np.concatenate([mac.loc[p - l].values for l in range(1, L + 1)]) for p in P])
        self.flags = np.array([np.concatenate([fbar.loc[p - l].values for l in range(1, L + 1)]) for p in P])
        assert not (np.isnan(self.Mm).any() or np.isnan(self.mlags).any() or np.isnan(self.flags).any())
        self.mon_of_row = np.searchsorted(P.asi8, self.dmon.asi8)                                    # monthly row of each daily row
        assert (P[self.mon_of_row] == self.dmon).all()
        self.last = np.r_[self.mon_of_row[1:] != self.mon_of_row[:-1], True]                         # last daily row of each month

    def Xm(self, mlags=None):
        return np.column_stack([np.ones(len(self.P)), self.mlags if mlags is None else mlags, self.flags])

    def Xd(self):
        return np.column_stack([self.Wd, *self.Md])


# ---------------------------------------------------------------- parameters
def ols(X, Y):
    C = np.linalg.lstsq(X, Y, rcond=None)[0]; E = Y - X @ C
    return C, E.T @ E / len(Y)


def unpack(Cm, Cd, K, L, nd):
    """Monthly: rows [1, m lags (l = 1..L, each K), fbar lags (each nd)]; daily: rows [1, HAR averages (4 x nd), m_{t-1}, m_t]."""
    cm, A, G = Cm[0], [Cm[1 + K * l:1 + K * (l + 1)].T for l in range(L)], [Cm[1 + K * L + nd * l:1 + K * L + nd * (l + 1)].T for l in range(L)]
    nh = 1 + len(HAR) * nd
    return dict(cm=cm, A=A, G=G, Bd=Cd[:nh].T, D1=Cd[nh:nh + K].T, D0=Cd[nh + K:nh + 2 * K].T)


# ---------------------------------------------------------------- state space and EM
def _steps(ds, par, Sm, Sd):
    K, L, nd = ds.K, ds.L, ds.nd; n = K * (L + 1)
    shift = np.zeros((n, n)); shift[K:, :K * L] = np.eye(K * L)
    Tm = shift.copy()
    for l in range(L): Tm[:K, K * l:K * (l + 1)] = par["A"][l]                                       # m_{t+1} from the current m_t..m_{t-L+1}
    I_n = np.eye(n); RQR = np.zeros((n, n)); RQR[:K, :K] = Sm; zero = np.zeros((n, n))
    Z = np.zeros((nd + K, n)); Z[:nd, :K] = par["D0"]; Z[:nd, K:2 * K] = par["D1"]; Z[nd:, :K] = np.eye(K)
    Hm = np.zeros((nd + K, nd + K)); Hm[:nd, :nd] = Sd
    dd = ds.Wd @ par["Bd"].T
    cm_next = par["cm"] + sum(ds.flags[:, nd * l:nd * (l + 1)] @ par["G"][l].T for l in range(L))       # c_m + sum G_l fbar for each month
    nm = len(ds.P)

    def step(t):
        y = np.r_[ds.Fd[t], ds.Mm[ds.mon_of_row[t]] if ds.last[t] else np.full(K, np.nan)]
        d = np.r_[dd[t], np.zeros(K)]
        if ds.last[t] and ds.mon_of_row[t] + 1 < nm:
            c = np.zeros(n); c[:K] = cm_next[ds.mon_of_row[t] + 1]; return dict(y=y, Z=Z, d=d, H=Hm, T=Tm, c=c, RQR=RQR)
        return dict(y=y, Z=Z, d=d, H=Hm, T=I_n, c=np.zeros(n), RQR=zero)
    a0 = np.r_[par["cm"] + sum(par["A"][l] @ ds.mlags[0, K * l:K * (l + 1)] for l in range(L)) + cm_next[0] - par["cm"], ds.mlags[0]]
    P0 = np.zeros((n, n)); P0[:K, :K] = Sm
    return a0, P0, step


def loglik(ds, Cm, Sm, Cd, Sd, store=False):
    par = unpack(Cm, Cd, ds.K, ds.L, ds.nd); a0, P0, step = _steps(ds, par, Sm, Sd)
    return ssm.kfilter(a0, P0, len(ds.Fd), step, store)


def em(ds, Cm, Sm, Cd, Sd, iters=3):
    """EM iterations; returns the estimates and the log-likelihood path."""
    K, L = ds.K, ds.L; path = []
    for _ in range(iters):
        ll, keep = loglik(ds, Cm, Sm, Cd, Sd, store=True); path.append(ll)
        a_s, P_s, _ = ssm.smoother(keep)
        # monthly equation: one smoothed state per month (its last row) holds m_t and all its lags
        r = np.where(ds.last)[0]; Em = a_s[r]; Vm = P_s[r]
        y, ylag = Em[:, :K], Em[:, K:]
        X = np.column_stack([np.ones(len(r)), ylag, ds.flags]); nx = X.shape[1]
        Sxx = X.T @ X; Syx = y.T @ X; Syy = y.T @ y
        Vlag = Vm[:, K:, K:].sum(0); Vyl = Vm[:, :K, K:].sum(0)
        Sxx[1:1 + K * L, 1:1 + K * L] += Vlag; Syx[:, 1:1 + K * L] += Vyl; Syy += Vm[:, :K, :K].sum(0)
        Cm = np.linalg.solve(Sxx, Syx.T); Sm = (Syy - Cm.T @ Syx.T - Syx @ Cm + Cm.T @ Sxx @ Cm) / len(r)
        # daily equation: smoothed m_{t-1}, m_t on each row
        Z = np.column_stack([ds.Wd, a_s[:, K:2 * K], a_s[:, :K]]); nw = ds.Wd.shape[1]
        Szz = Z.T @ Z; Szz[nw:, nw:] += np.block([[P_s[:, K:2 * K, K:2 * K].sum(0), P_s[:, K:2 * K, :K].sum(0)], [P_s[:, :K, K:2 * K].sum(0), P_s[:, :K, :K].sum(0)]])
        Cd = np.linalg.solve(Szz, Z.T @ ds.Fd); E = ds.Fd - Z @ Cd; Sd = (E.T @ E + Cd[nw:].T @ (Szz[nw:, nw:] - Z[:, nw:].T @ Z[:, nw:]) @ Cd[nw:]) / len(Z)
    path.append(loglik(ds, Cm, Sm, Cd, Sd)[0])
    return Cm, Sm, Cd, Sd, path


def ols_fit(ds):
    """Complete-data ML (the EM fixed point when the macro data are observed): OLS of each block."""
    Cm, Sm = ols(ds.Xm(), ds.Mm); Cd, Sd = ols(ds.Xd(), ds.Fd); return Cm, Sm, Cd, Sd


def closed_form_loglik(ds, Cm, Sm, Cd, Sd):
    def g(E, S):
        Li = np.linalg.cholesky(S); w = np.linalg.solve(Li, E.T)
        return -0.5 * (E.size * np.log(2 * np.pi) + 2 * len(E) * np.log(np.diag(Li)).sum() + (w * w).sum())
    return g(ds.Mm - ds.Xm() @ Cm, Sm) + g(ds.Fd - ds.Xd() @ Cd, Sd)


# ---------------------------------------------------------------- responses from the full daily state
def system(par, K, L, nd):
    """Deviation form (no constants). State s = [f lags 0..65 (nd each), running monthly sum S (nd), m_t..m_{t-L} (K each), fbar_{t-1}..fbar_{t-L} (nd each)].
    Returns T_day (a weekday inside a month) and a function T_start(n_prev) (first weekday of a month, the previous month having n_prev days)."""
    nf = 66 * nd; iS = nf; iM = iS + nd; iB = iM + K * (L + 1); n = iB + nd * L
    T = np.zeros((n, n))
    for hi, h in enumerate(HAR):
        Bh = par["Bd"][:, 1 + hi * nd:1 + (hi + 1) * nd]
        for j in range(h): T[:nd, j * nd:(j + 1) * nd] += Bh / h
    T[:nd, iM:iM + K] = par["D0"]; T[:nd, iM + K:iM + 2 * K] = par["D1"]
    T[nd:nf, :nf - nd] = np.eye(nf - nd)                                                             # lags shift
    keep = np.eye(n); keep[:nf, :] = 0; keep[iS:iS + nd, :] = 0                                      # S, M, FB carried over
    Tday = T + keep; Tday[iS:iS + nd, :] += T[:nd, :]; Tday[iS:iS + nd, iS:iS + nd] += np.eye(nd)    # S <- S + f_tau

    def Tstart(nprev):
        C = np.eye(n)                                                                                # close the month: fbar_{t-1} = S / n_prev, lags shift, S = 0
        C[iB:iB + nd, :] = 0; C[iB:iB + nd, iS:iS + nd] = np.eye(nd) / nprev
        C[iB + nd:n, :] = 0; C[iB + nd:n, iB:n - nd] = np.eye(nd * (L - 1))
        C[iS:iS + nd, :] = 0
        Mx = np.eye(n)                                                                               # m_t from its lags and the monthly averages
        Mx[iM:iM + K, :] = 0
        for l in range(1, L + 1):
            Mx[iM:iM + K, iM + K * (l - 1):iM + K * l] = par["A"][l - 1]
            Mx[iM:iM + K, iB + nd * (l - 1):iB + nd * l] = par["G"][l - 1]
        Mx[iM + K:iB, :] = 0; Mx[iM + K:iB, iM:iB - K] = np.eye(K * L)
        return Tday @ Mx @ C
    return Tday, Tstart, dict(n=n, iS=iS, iM=iM)


def irf(par, K, L, nd, b, bins, months=H + 1, mlen=21):
    """Monthly macro, monthly-average and end-of-month financial responses to b on the announcement day, averaged over the position bins."""
    Tday, Tstart, ix = system(par, K, L, nd); cache = {}
    out_m = np.zeros((months, K)); out_f = np.zeros((months, nd)); out_e = np.zeros((months, nd))
    for k0, n0, wgt in bins:
        s = np.zeros(ix["n"]); s[:nd] = b; s[ix["iS"]:ix["iS"] + nd] = b                         # event day: f = b, monthly sum = b (earlier days of the month are zero)
        for _ in range(k0 + 1, n0): s = Tday @ s
        mm = [s[ix["iM"]:ix["iM"] + K].copy()]; fb = [s[ix["iS"]:ix["iS"] + nd] / n0]; fe = [s[:nd].copy()]; nprev = n0
        for t in range(1, months):
            if nprev not in cache: cache[nprev] = Tstart(nprev)
            s = cache[nprev] @ s
            for _ in range(1, mlen): s = Tday @ s
            mm.append(s[ix["iM"]:ix["iM"] + K].copy()); fb.append(s[ix["iS"]:ix["iS"] + nd] / mlen); fe.append(s[:nd].copy()); nprev = mlen
        out_m += wgt * np.array(mm); out_f += wgt * np.array(fb); out_e += wgt * np.array(fe)
    return out_m, out_f, out_e


def to_level(m):
    z = m.copy(); z[:, 1] = np.cumsum(z[:, 1]) / 12; return z


# ---------------------------------------------------------------- Note B's block bootstrap
def block_rows(n, rng, length):
    nb = -(-n // length); st = rng.integers(0, n - length + 1, nb)
    return np.concatenate([np.arange(a, a + length) for a in st])[:n]


def estimate(form, fci, L, B=500):
    """Point responses (by EM on the state space) and B bootstrap draws. Returns a dict as in Note B: s0 (H+1, 2) with the price level, sd (B, H+1, 2), f0, fd, e0, checks."""
    I = inputs(); ds = Design(form, fci, L); K, nd = ds.K, ds.nd; idx0 = I.used
    start = ols_fit(ds); Cm0 = np.zeros_like(start[0]); Cd0 = np.zeros_like(start[2])
    Cm, Sm, Cd, Sd, path = em(ds, Cm0, np.eye(K), Cd0, np.eye(nd), iters=2)                       # EM from zero coefficients
    chk = dict(em_vs_ols_m=float(np.abs(Cm - start[0]).max()), em_vs_ols_d=float(np.abs(Cd - start[2]).max()),
               kf_ll=path[-1], closed_ll=closed_form_loglik(ds, *start), em_path=path)
    par = unpack(Cm, Cd, K, L, nd); bins0 = position_bins(I.ev, idx0); b0 = window_impact(I.ev, idx0)[:nd]
    m0, f0, e0 = irf(par, K, L, nd, b0, bins0)
    # bootstrap (Note B, FS-A64: 12-month blocks of calendar months; residuals, daily rows and announcements of the months drawn; recursive macro lags)
    X = ds.Xm(); res = ds.Mm - X @ Cm; nm = len(ds.P)
    prow = {p: i for i, p in enumerate(ds.P)}
    drows = {m: np.where(ds.dmon == m)[0] for m in CAL_BOOT}
    evm = I.ev.day.iloc[idx0].dt.to_period("M").values; erows = {m: idx0[evm == m] for m in CAL_BOOT}
    rng = np.random.default_rng(zlib.crc32(f"{form}|u,pi|1996-01|None|in|{L}".encode()))
    Xd, Fd = ds.Xd(), ds.Fd; sd, fd = [], []
    for _ in range(B):
        mo, e = [], []
        while len(e) < nm:
            for r in block_rows(len(CAL_BOOT), rng, 12): mo.append(CAL_BOOT[r]); e += [res[prow[CAL_BOOT[r]]]] if CAL_BOOT[r] in prow else []
        e = np.array(e[:nm])
        ys = np.zeros((nm, K)); ml = ds.mlags.copy()
        for t in range(nm):                                                                         # rebuild the macro series forward; lags inside the sample from it
            for l in range(1, L + 1):
                if t - l >= 0: ml[t, K * (l - 1):K * l] = ys[t - l]
            ys[t] = np.r_[1.0, ml[t], ds.flags[t]] @ Cm + e[t]
        Cb = ols(ds.Xm(ml), ys)[0]
        dr = np.concatenate([drows[m] for m in mo]); Cdb = ols(Xd[dr], Fd[dr])[0]
        ib = np.concatenate([erows[m] for m in mo]); ib = ib if len(ib) >= 20 else idx0
        mb, fb_, _ = irf(unpack(Cb, Cdb, K, L, nd), K, L, nd, window_impact(I.ev, ib)[:nd], position_bins(I.ev, ib))
        sd.append(to_level(mb)); fd.append(fb_)
    return dict(s0=to_level(m0), sd=np.array(sd), f0=f0, fd=np.array(fd), e0=e0, nobs=nm, ndays=len(Fd), checks=chk)
