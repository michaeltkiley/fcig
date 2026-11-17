"""Route 2: historical and variance decompositions of monetary policy shocks recovered from monthly VAR innovations (exploratory; not part of Note B's package).

System (as Note B's monthly benchmarks, lib/monthly.py):  y_t = c + sum_{l=1..L} A_l y_{t-l} + u_t,   y_t = (u gap, core PCE inflation, i_t [, FCI_t]),
i_t the 2-year yield in the stated step (nominal, real, r*-gap) and FCI_t Note B's index (FS-A75 weights) in the same step.

Data (DECOMP_QA D-A2):
  avg  monthly averages, 1973 on: the series of Note B's own monthly equations (model.fin_monthly; months before 1990 from monthly series; robustness R1a).
  eom  end-of-month values, 1990 on (model.fin_eom; the daily block starts in 1990): the check.

Impact column b (one column of the impact matrix; DECOMP_QA D-A3):
  WE  window impact (main): b = (0, 0, r_i, r_F), the daily model's response of the month's average (avg) or end-of-month value (eom) of the yield and the FCI in the
      month of the announcement to a +1 pp window surprise, averaged over the announcement's position in the month (model.estimate: f0[0] or e0[0]); macro entries zero
      (Note B's restriction: no response of unemployment or inflation within the month).
  P1  proxy (comparison): b_j proportional to Cov(z_t, u_jt) over the instrument months (January 1996 to the last announcement), z_t = sum of the month's
      Nakamura-Steinsson policy news (in window 2-year pp: slope 1.000 on Note B's 252 events), rescaled so that its yield entry equals WE's (unit: +1 pp window move).
  The scale of b does not affect the recovered shock's contribution, the historical decomposition or the variance shares; only the units of the shock and the IRF.

Shock recovery under invertibility (Stock and Watson 2018 [recall]; algebra in REPORT.md): with Sigma = Var(u_t),
  e_t = b' Sigma^{-1} u_t / (b' Sigma^{-1} b),   Var(e_t) = 1 / (b' Sigma^{-1} b)  (shock in units of a +1 pp window move of the 2-year yield).
  Without invertibility e_t is the projection of the shock on u_t and 1/(b'S^-1 b) is an upper bound on the shock variance [inference].
Historical decomposition: H_t = sum_{j=0}^{t-t0} Theta_j b e_{t-j}  (t0 = first month of the estimation sample).
Variance shares at horizon h:  sigma^2 sum_{j<h} (Theta_j b)_k^2 / sum_{j<h} (Theta_j Sigma Theta_j')_kk,
  upper bound: sigma^2 = 1/(b'S^-1 b) (invertibility); lower bound (post-1996 only): sigma^2 = mean of z_t^2 over 1996-2026 months, i.e. the shock is the measured
  window surprise and nothing else (Route 1 in the monthly VAR) [inference; in the spirit of Plagborg-Moller and Wolf 2022, recall].
"""
import sys, zlib
from pathlib import Path
import numpy as np, pandas as pd

BASE = Path(__file__).resolve().parents[1] / "baseline"
sys.path.insert(0, str(BASE))
from lib import model as M            # noqa: E402  (Note B's package, read only)
from lib import monthly as MO         # noqa: E402
from lib.daily import EV, event_index  # noqa: E402

END = pd.Period("2026-09", "M")
C2020 = pd.period_range("2020-03", "2020-12", freq="M")
NAMES = ["u", "pi", "pol", "idx"]

# ---------------------------------------------------------------- instrument (monthly sums of the policy news, window 2-year pp)
_idx0 = event_index(); _ev = EV.iloc[_idx0]; _mon = _ev.Date.dt.to_period("M")
Z = _ev.ns.groupby(_mon).sum()
Z_FIRST, Z_LAST = _mon.min(), _mon.max()
ZCAL = pd.period_range(Z_FIRST, END, freq="M")          # instrument months: zero where there was no announcement
ZFULL = Z.reindex(ZCAL).fillna(0.0)

# ---------------------------------------------------------------- data and impact columns
_IMP = {}
def note_b(step, fci, start="1996-01", L=12):
    """Note B's model responses per +1 pp window surprise (point estimate): macro (u, price level), monthly-average and end-of-month yield (and FCI), h = 0..36."""
    key = (step, fci, start, L)
    if key not in _IMP:
        est = next(M.estimate(step, fci, "u,pi", start, None, "in", "none", 1, (L,)))
        _IMP[key] = dict(s0=est["s0"], f0=est["f0"], e0=est["e0"])
    return _IMP[key]

def path_vector(step, fci, kind, h, start="1996-01", L=12):
    """Note B's response at month h as a vector in the VAR's variables: (u, monthly inflation at an annual rate, yield [, FCI]); inflation = 12 x change in the price level."""
    nb = note_b(step, fci, start, L); s = nb["s0"]; fin = nb["f0"] if kind == "avg" else nb["e0"]
    pi = 12 * (s[h, 1] - (s[h - 1, 1] if h else 0.0))
    return np.r_[s[h, 0], pi, fin[h]]

def window_column(step, fci, kind):
    """Month-of-announcement response of the yield (and FCI) per +1 pp window surprise from Note B's daily model; macro entries zero (they are zero in Note B's model)."""
    return path_vector(step, fci, kind, 0)

def data(step, fci, kind, start):
    fin = M.fin_monthly(step, fci) if kind == "avg" else M.fin_eom(step, fci)
    D = M.MAC[["u", "pi"]].join(fin, how="inner").dropna()
    D = D[D.index <= END]
    D.attrs["start"] = start                 # estimation rows from max(start, first month with L lags); earlier months supply lags (as lib/monthly.py)
    return D

# ---------------------------------------------------------------- VAR
def design(D, L, t2020):
    """Constant and L lags; rows from the first month with L lags in D. t2020 = 'dummy': March-December 2020 removed from the estimation (= one dummy per month)."""
    first = max(D.index[L], pd.Period(D.attrs.get("start", str(D.index[L])), "M"))
    X, Y, per = MO.design(D, L, str(first), str(END))
    keep = np.ones(len(per), bool) if t2020 == "in" else ~per.isin(C2020)
    return X, Y, per, keep

def fit(X, Y, keep):
    C = np.linalg.lstsq(X[keep], Y[keep], rcond=None)[0]
    U = Y - X @ C
    n, k = keep.sum(), X.shape[1]
    S = U[keep].T @ U[keep] / (n - k)
    return C, U, S

def proxy_column(U, per, keep, b_we):
    ok = (per >= Z_FIRST) & (per <= Z_LAST) & keep
    z = ZFULL.reindex(per[ok]).fillna(0.0).values; r = U[ok]
    zc = z - z.mean(); g = (r - r.mean(0)).T @ zc / (zc @ zc)
    return g / g[2] * b_we[2], g

def first_stage_F(U, per, keep):
    ok = (per >= Z_FIRST) & (per <= Z_LAST) & keep
    z = ZFULL.reindex(per[ok]).fillna(0.0).values
    return MO.first_stage(U[ok][:, 2], z)[1]

def recover(U, S, b, keep):
    Si = np.linalg.inv(S); w = Si @ b; d = float(b @ w)
    e = U @ w / d
    e[~keep] = 0.0                      # 2020 months absorbed by the dummies in the 'dummy' version
    return e, 1.0 / d, w / d            # shock, its variance under invertibility, weights on the innovations

def ma(C, K, L, H): return MO.ma(C, K, L, H)

def hd(r, e):
    """H_t[k] = sum_{j=0}^{t} r_j[k] e_{t-j}, r = impulse responses to a unit shock (Theta_j b, or Theta_j b0 + Theta_{j-1} b1 in WE2)."""
    n = len(e); out = np.zeros((n, r.shape[1]))
    for k in range(r.shape[1]): out[:, k] = np.convolve(e, r[:, k])[:n]
    return out

def all_shocks(T, U, keep):
    """Stochastic part of y_t: sum_j Theta_j u_{t-j} (deviation from the deterministic path given the initial conditions)."""
    Uk = U.copy(); Uk[~keep] = 0.0
    n, K = U.shape; out = np.zeros((n, K))
    for i in range(K):
        for m in range(K): out[:, i] += np.convolve(Uk[:, m], T[:, i, m])[:n]
    return out

FH = (1, 3, 6, 12, 24, 36, 60)
def fevd(T, S, r, s2, H=FH):
    """Share of the h-month forecast-error variance due to the shock with responses r (unit shock) and variance s2."""
    num = np.cumsum(r ** 2, axis=0) * s2
    den = np.cumsum(np.einsum("hij,jk,hik->hi", T, S, T), axis=0)
    return {h: num[h - 1] / den[h - 1] for h in H}

def lead_lag_test(U, per, keep, k=6, lags=False):
    """z_t on u_t and u_{t+1..t+k} (leads) or u_{t-1..t-k} (lags) over the instrument months; HC1 Wald test that the lead (lag) coefficients are zero.
    Under invertibility the policy news is not predicted by future innovations; leads matter if the shock is not recoverable from u_t (or if the monthly average spreads
    a late-month shock into the next month). Returns (R2 with u_t only, R2 with the extra terms, Wald p-value, number of restrictions)."""
    from scipy import stats
    pos = {p: i for i, p in enumerate(per)}
    rows, z = [], []
    for p in ZCAL:
        sh = [p + (j if not lags else -j) for j in range(1, k + 1)]
        if p not in pos or not all(q in pos for q in sh) or not keep[pos[p]] or not all(keep[pos[q]] for q in sh): continue
        rows.append(np.concatenate([U[pos[p]]] + [U[pos[q]] for q in sh])); z.append(ZFULL[p])
    Xr = np.column_stack([np.ones(len(rows)), np.array(rows)]); z = np.array(z); K = U.shape[1]
    def ols(X):
        xx = np.linalg.pinv(X.T @ X); bb = xx @ X.T @ z; r = z - X @ bb; return bb, r, xx
    b0, r0, _ = ols(Xr[:, :1 + K]); bb, r, xx = ols(Xr)
    n, m = Xr.shape; V = xx @ (Xr.T * r ** 2) @ Xr @ xx * n / (n - m)
    R = np.arange(1 + K, m); W = bb[R] @ np.linalg.pinv(V[np.ix_(R, R)]) @ bb[R]
    tss = ((z - z.mean()) ** 2).sum()
    return 1 - (r0 ** 2).sum() / tss, 1 - (r ** 2).sum() / tss, float(1 - stats.chi2.cdf(W, len(R))), len(R)

# ---------------------------------------------------------------- one case
def run(step, fci, kind="avg", start="1973-01", L=12, ident="WE", t2020="in", H=60):
    """ident: WE (window column, shock from u_t), P1 (proxy column, shock from u_t), WE2 (monthly averages: the window shock moves the month of the announcement
    and, through the rest of the month, the next month; column b0 for month t and b1 = Note B's month-1 response minus Theta_1 b0 for month t+1; shock recovered
    by GLS from (u_t, u_{t+1}))."""
    D = data(step, fci, kind, start); K = D.shape[1]
    X, Y, per, keep = design(D, L, t2020)
    C, U, S = fit(X, Y, keep)
    n = len(per); T = ma(C, K, L, max(H, n))
    bwe = window_column(step, fci, kind)[:K]
    b1 = np.zeros(K)
    if ident == "P1": b = proxy_column(U, per, keep, bwe)[0]
    else: b = bwe
    if ident == "WE2":
        b1 = path_vector(step, fci, kind, 1)[:K] - T[1] @ b
        Si = np.linalg.inv(S); d = float(b @ Si @ b + b1 @ Si @ b1)
        Uk = U.copy(); Uk[~keep] = 0.0; Un = np.vstack([Uk[1:], np.zeros((1, K))])
        e = (Uk @ Si @ b + Un @ Si @ b1) / d; e[~keep] = 0.0; s2 = 1.0 / d; w = Si @ b / d
    else:
        e, s2, w = recover(U, S, b, keep)
    r = T @ b; r[1:] += T[:-1] @ b1
    return dict(step=step, fci=fci, kind=kind, start=start, L=L, ident=ident, t2020=t2020, D=D, X=X, Y=Y, per=per, keep=keep, C=C, U=U, S=S, b=b, b1=b1, bwe=bwe,
                T=T, r=r, e=e, s2=s2, w=w, K=K, names=NAMES[:K])
