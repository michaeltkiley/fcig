"""Purely monthly VAR benchmarks (in the baseline section): the same 252 announcements and the same monthly sample as the main model, without the daily block.

System (monthly averages, FS-A76: one data type in the paper; no trend; March-December 2020 dropped from the estimation rows by default):   y_t = c + sum_{l=1}^{L} A_l y_{t-l} + u_t,
y_t = (unemployment gap, core PCE inflation, i_t [, FCI_t]), where i_t is the month's average two-year yield in the stated step (nominal, real or r*-gap) and FCI_t, when included, the month's average
market index in the same step; months before the daily data (start 1973) use the monthly series, as in the main model. Unit of every response: +1 pp on the two-year yield in the announcement window.
A window move of 1 pp raises the month's average yield by about 0.44-0.47 in the model (the announcement falls on average mid-month), so the proxy VAR's first-stage column, estimated per +1 pp on
the month's average yield, is multiplied by that response to be in the window unit.
Moving-average matrices Theta_h (h = 0..36) map an impact vector into responses; the price level cumulates inflation / 12. Two identification schemes:

 P1  Standard proxy VAR (Stock and Watson 2018; Mertens and Ravn 2013; Gertler and Karadi 2015; with high-frequency surprises as in Bauer and Swanson 2023).
     Instrument z_t = Nakamura-Steinsson policy news (Nakamura and Steinsson 2018) summed over the announcements of month t (zero in months without one).
     Assumptions: relevance E[z_t e_1t] != 0 and exogeneity E[z_t e_jt] = 0 for the other structural shocks e_j. Then s = E[z_t u_t] / E[z_t u_{i,t}], estimated by
     regressing each VAR residual on z_t over the instrument months (first to last announcement); every entry of s, including u and inflation, is estimated.
     Unit: rescaled to +1 pp in the window (above). Inference: 90% Anderson-Rubin set for the response of a target, conditional on the VAR coefficients, with
     heteroskedasticity-robust (HC1) variance; solved exactly (a quadratic inequality in the response), so it is never cut off by a grid. "Unbounded" = weak instrument.
     (Anderson-Rubin sets for proxy VARs: Montiel Olea, Stock and Watson 2021; Lunsford 2015.)
 WE  Window impact: the impact vector is not estimated from monthly residuals but taken from the daily model: s = (0, 0, e_i, e_F), the model's response of the month's average 2-year yield and FCI in the announcement month to a +1 pp
     window surprise (e_i about 0.44-0.47, e_F the FCI's corresponding response), macro entries zero. Assumption: the shock reaches unemployment and inflation only through the 2-year yield and the FCI,
     the same restriction as the main model. Unit: +1 pp in the window. Inference: 500 draws of the block bootstrap of model.estimate (12-month blocks, recursive lags, announcements of the months drawn).
Relation to the main model: Plagborg-Moller and Wolf (2021) show that VARs and local projections estimate the same responses; a monthly VAR still observes a surprise concentrated on one day
only through one monthly average, which spreads it over the month (see also the temporal-aggregation argument of Jacobson, Matthes and Walker 2026)."""
import zlib
import numpy as np, pandas as pd
from .daily import EV, event_index
from . import model as M
from .model import MAC, fin_monthly, impact

LAGS = (3, 6, 12)
HORIZ = (12, 24, 36)
H = 36
TARGETS = [(v, h) for v in ("u", "P") for h in HORIZ]
CRIT = 2.7055                                   # chi-square(1) 90% quantile

def design(D, L, start, end="2026-09"):
    """Regressors (constant and L lags of every variable) and outcomes for months start..end; no trend, no month dropped."""
    X, Y, idx = [], [], []
    for p in D.index:
        if p < pd.Period(start, "M") or p > pd.Period(end, "M"): continue
        try: lags = np.concatenate([D.loc[p - l].values for l in range(1, L + 1)])
        except KeyError: continue
        X.append(np.r_[1.0, lags]); Y.append(D.loc[p].values); idx.append(p)
    return np.array(X), np.array(Y), pd.PeriodIndex(idx, freq="M")

def ma(C, K, L, H=H):
    """Moving-average matrices Theta_0..Theta_H of the VAR with coefficient matrix C."""
    A = [C[1 + K * l:1 + K * (l + 1)].T for l in range(L)]; T = [np.eye(K)]
    for h in range(1, H + 1): T.append(sum(A[l] @ T[h - 1 - l] for l in range(min(L, h))))
    return np.array(T)

def row_of(T, var, h):
    """Row vector mapping an impact vector into the target: the unemployment gap at h, or the price level (cumulated inflation / 12) at h."""
    return T[h, 0] if var == "u" else T[:h + 1, 1].sum(axis=0) / 12

def first_stage(e, z):
    """OLS of residual e on [1, z]: coefficient on z and its robust (HC1) F statistic."""
    x = np.column_stack([np.ones(len(z)), z]); xx = np.linalg.inv(x.T @ x); b = xx @ x.T @ e; r = e - x @ b; n, k = x.shape
    V = xx @ (x.T * (r ** 2)) @ x @ xx * n / (n - k)
    return b[1], b[1] ** 2 / V[1, 1]

def ar_set(a, d, z):
    """Exact 90% Anderson-Rubin set for theta in H0: Cov(z, a - theta d) = 0, with a (target combination of residuals) and d (policy residual) fixed.
    The statistic b(theta)^2 / V(theta) <= CRIT is a quadratic inequality in theta (b linear, V quadratic in theta). Returns (lo, hi, unbounded):
    an interval if the quadratic opens upward; unbounded (the whole line, or two rays) if it does not, i.e. the instrument cannot reject large effects."""
    x = np.column_stack([np.ones(len(z)), z]); xx = np.linalg.inv(x.T @ x); n, k = x.shape; s = n / (n - k)
    proj = xx @ x.T; w = proj[1]; ra, rd = a - x @ (proj @ a), d - x @ (proj @ d); ba, bd = w @ a, w @ d
    A, B, C = np.sum(w ** 2 * ra ** 2), np.sum(w ** 2 * ra * rd), np.sum(w ** 2 * rd ** 2)
    qa, qb, qc = bd ** 2 - CRIT * s * C, -2 * ba * bd + 2 * CRIT * s * B, ba ** 2 - CRIT * s * A
    if qa <= 0: return -np.inf, np.inf, True
    disc = qb ** 2 - 4 * qa * qc
    if disc < 0: return np.nan, np.nan, False
    return (-qb - np.sqrt(disc)) / (2 * qa), (-qb + np.sqrt(disc)) / (2 * qa), False

END = "2026-09"
C2020 = pd.period_range("2020-03", "2020-12", freq="M")

def data(step, fci):
    """Monthly averages (FS-A76: one data type): unemployment gap, core PCE inflation, the month's average 2-year yield [and FCI] in the step; months before the daily data from the monthly series."""
    D = MAC[["u", "pi"]].join(fin_monthly(step, fci), how="inner").dropna(); return D[D.index <= pd.Period(END, "M")]

def window_column(step, fci, t2020):
    """Response of the month's average yield [and FCI] in the announcement month per +1 pp window surprise, from Note B's daily block (it does not depend on the monthly equations,
    the start or the lag length: the macro variables are zero in the announcement month)."""
    return next(M.estimate(step, fci, "u,pi", "1996-01", None, t2020, "none", 1, (12,)))["f0"][0]

def _blocks(idx, n, rng, length=12):
    nb = -(-n // length); st = rng.integers(0, len(idx) - length + 1, nb); return np.concatenate([idx[s:s + length] for s in st])[:n]

def run_case(step, fci, start="1996-01", B=500, lags=LAGS, t2020="out", tag=None):
    """Rows for one (step, FCI, start): proxy VAR (P1) and window-impact VAR (WE), u and price level at 12/24/36 months, 3/6/12 lags, with first-stage diagnostics. Unit: +1 pp on the
    2-year yield in the window (P1's first-stage column is scaled so that its yield entry equals WE's, the month-average response to a window move of 1 pp, about 0.44-0.47).
    t2020 = "out": March-December 2020 dropped from the estimation rows (their values still enter as lags), as in the main model. Bootstrap (WE): 12-month moving blocks of residuals,
    pre-1996 and post-1996 rows drawn separately, the VAR rebuilt recursively; the FCI entry rescaled by the window ratio of the drawn months' announcements.
    Ported from explore_decomp/A2_monthly.py (tag = its seed tag reproduces it)."""
    idx0 = event_index(); ev = EV.iloc[idx0]; evm = ev.Date.dt.to_period("M").values; zm = ev.Date.dt.to_period("M")
    z_all = ev.ns.groupby(zm).sum(); first, last = zm.min(), zm.max(); b0 = impact(fci, idx0)
    D = data(step, fci); K = D.shape[1]; win = window_column(step, fci, t2020); b_we = np.r_[0, 0, win]; rows = []
    for L in lags:
        X, Y, per = design(D, L, str(max(D.index[L], pd.Period(start, "M"))), END)
        keep = np.ones(len(per), bool) if t2020 == "in" else ~per.isin(C2020)
        X, Y, per = X[keep], Y[keep], per[keep]                                                 # 2020 rows dropped; lags of later months still read the 2020 data
        C = np.linalg.lstsq(X, Y, rcond=None)[0]; U = Y - X @ C; T = ma(C, K, L)
        ok = (per >= first) & (per <= last); z = z_all.reindex(per[ok]).fillna(0.0).values; r = U[ok]
        g = np.array([first_stage(r[:, j], z)[0] for j in range(K)]); F = first_stage(r[:, 2], z)[1]; s_p1 = g / g[2]
        info = dict(step=step, fci=fci, start=str(per[0]), lags=L, t2020=t2020, nobs=len(per), n_instr=int(ok.sum()), F=F, win_pol=win[0], win_fci=(win[1] if K == 4 else np.nan),
                    impact_u=s_p1[0], impact_pi=s_p1[1], impact_fci=(s_p1[3] if K == 4 else np.nan))
        for var, h in TARGETS:                                                                  # P1: per +1 pp on the month's average yield, rescaled to the window unit by win[0]
            c = row_of(T, var, h); lo, hi, unb = ar_set(r @ c, r[:, 2], z)
            rows.append(dict(**info, ident="P1", var=var, h=h, r=float(c @ s_p1) * win[0], lo=lo * win[0], hi=hi * win[0], unbounded=int(unb)))
        pre = np.where(per < pd.Period("1996-01", "M"))[0]; post = np.where(per >= pd.Period("1996-01", "M"))[0]; LI = M._lag_index(per, L)
        rng = np.random.default_rng(zlib.crc32((tag or f"monthly|{step}|{start}|{L}|{t2020}").format(step=step, start=start, L=L).encode()))     # FCI not in the tag: pairs share draws
        dr = {t: [] for t in TARGETS}
        for _ in range(B):
            rb = np.concatenate([_blocks(pre, len(pre), rng) if len(pre) else np.array([], int), _blocks(post, len(post), rng)])
            Ys = M._recursive(X, C, U[rb], K, L, LI); Tb = ma(np.linalg.lstsq(M._rebuild(X, K, L, LI, Ys), Ys, rcond=None)[0], K, L)
            mo_b = per[rb[rb >= len(pre)]]; ib = idx0[np.isin(evm, mo_b.values)] if len(mo_b) else idx0; ib = ib if len(ib) >= 20 else idx0
            sb = np.r_[0, 0, win * (impact(fci, ib) / b0)[:K - 2]]
            for t in TARGETS: dr[t].append(row_of(Tb, *t) @ sb)
        for t in TARGETS:
            rows.append(dict(**info, ident="WE", var=t[0], h=t[1], r=float(row_of(T, *t) @ b_we), lo=np.percentile(dr[t], 5), hi=np.percentile(dr[t], 95), unbounded=0))
    return rows
