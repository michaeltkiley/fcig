"""Purely monthly VAR benchmarks (in the baseline section): the same 252 announcements and the same monthly sample as the main model, without the daily block.

System (end-of-month values, no trend, nothing dropped):   y_t = c + sum_{l=1}^{L} A_l y_{t-l} + u_t,     y_t = (unemployment gap, core PCE inflation, i_t [, FCI_t]),
where i_t is the two-year yield on the last weekday of month t in the stated step (nominal, real or r*-gap) and FCI_t, when included, the Note A index in the same step on that day.
End-of-month values follow Bauer and Swanson (2023), who argue that they correspond more naturally to a high-frequency surprise than the month-average yield of Gertler and Karadi (2015); in this model
the end-of-month yield responds to a window surprise by 0.95 to 0.99 of the window move, so the unit of every response in the paper is the same: +1 pp on the two-year yield.
Moving-average matrices Theta_h (h = 0..36) map an impact vector into responses; the price level cumulates inflation / 12. Two identification schemes:

 P1  Standard proxy VAR (Stock and Watson 2018; Mertens and Ravn 2013; Gertler and Karadi 2015; with high-frequency surprises as in Bauer and Swanson 2023).
     Instrument z_t = Nakamura-Steinsson policy news (Nakamura and Steinsson 2018) summed over the announcements of month t (zero in months without one).
     Assumptions: relevance E[z_t e_1t] != 0 and exogeneity E[z_t e_jt] = 0 for the other structural shocks e_j. Then s = E[z_t u_t] / E[z_t u_{i,t}], estimated by
     regressing each VAR residual on z_t over the instrument months (first to last announcement); every entry of s, including u and inflation, is estimated.
     Unit: +1 pp on the end-of-month 2-year yield. Inference: 90% Anderson-Rubin set for the response of a target, conditional on the VAR coefficients, with
     heteroskedasticity-robust (HC1) variance; solved exactly (a quadratic inequality in the response), so it is never cut off by a grid. "Unbounded" = weak instrument.
     (Anderson-Rubin sets for proxy VARs: Montiel Olea, Stock and Watson 2021; Lunsford 2015.)
 WE  Window impact: the impact vector is not estimated from monthly residuals but taken from the daily model: s = (0, 0, e_i, e_F), the model's response of the end-of-month 2-year yield and FCI to a +1 pp
     window surprise (e_i = 0.95-0.99, e_F the FCI's corresponding response), macro entries zero. Assumption: the shock reaches unemployment and inflation only through the 2-year yield and the FCI,
     the same restriction as the main model. Unit: +1 pp in the window (= +1 pp end-of-month yield up to 5%). Inference: 200 draws that resample announcements and monthly residuals.
Relation to the main model: Plagborg-Moller and Wolf (2021) show that VARs and local projections estimate the same responses; a monthly VAR still observes a surprise concentrated on one day
only through one end-of-month value per month (see also the temporal-aggregation argument of Jacobson, Matthes and Walker 2026)."""
import zlib
import numpy as np, pandas as pd
from .daily import EV, event_index
from . import model as M
from .model import MAC, fin_eom, impact

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

def run_case(step, fci, start="1996-01", B=200, lags=LAGS, design_fn=design):
    """Rows for one (step, FCI): both identification schemes, 3/6/12 lags, u and price level at 12/24/36 months, plus first-stage diagnostics."""
    idx0 = event_index(); ev = EV.iloc[idx0]; mon = ev.Date.dt.to_period("M"); first, last = mon.min(), mon.max()
    z_all = ev.ns.groupby(mon).sum(); K = 3 + int(bool(fci)); rows = []; b0 = impact(fci, idx0)
    D = MAC[["u", "pi"]].join(fin_eom(step, fci), how="inner").dropna()
    for L in lags:
        e = next(M.estimate(step, fci, "u,pi", start, None, "in", "none", 1, (L,)))["e0"][0]           # model: end-of-month 2-year (and FCI) response per +1 pp window surprise
        X, Y, per = design_fn(D, L, start); C = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C; res = Y - fit; T = ma(C, K, L)
        ok = (per >= first) & (per <= last); z = z_all.reindex(per[ok]).fillna(0.0).values; r = res[ok]
        g = np.array([first_stage(r[:, j], z)[0] for j in range(K)]); F = first_stage(r[:, 2], z)[1]; S = g / g[2]
        info = dict(step=step, fci=fci, start=start, lags=L, nobs=len(Y), n_instr=int(ok.sum()), F=F, impact_u=S[0], impact_pi=S[1], impact_fci=(S[3] if fci else np.nan),
                    eom_pol=e[0], eom_fci=(e[1] / e[0] if fci else np.nan))
        for var, h in TARGETS:                                                                  # P1: point estimate and exact AR set
            c = row_of(T, var, h); lo, hi, unb = ar_set(r @ c, r[:, 2], z)
            rows.append(dict(**info, ident="P1", var=var, h=h, r=float(c @ S), lo=lo, hi=hi, unbounded=int(unb)))
        s0 = np.r_[0, 0, e]; rng = np.random.default_rng(zlib.crc32(f"monthly|{step}|{fci}|{start}|{L}".encode()))
        dr = {t: [] for t in TARGETS}
        for _ in range(B):
            Cb = np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0]; Tb = ma(Cb, K, L)
            ib = rng.choice(idx0, size=len(idx0), replace=True); sb = np.r_[0, 0, e * (impact(fci, ib) / b0)]      # window ratio of the resampled announcements
            for t in TARGETS: dr[t].append(row_of(Tb, *t) @ sb)
        for t in TARGETS:
            rows.append(dict(**info, ident="WE", var=t[0], h=t[1], r=float(row_of(T, *t) @ s0), lo=np.percentile(dr[t], 5), hi=np.percentile(dr[t], 95), unbounded=0))
    return rows
