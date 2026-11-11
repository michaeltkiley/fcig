"""Sensitivity of the bootstrap intervals to the resampling scheme (script 10_bootstrap_sensitivity.py). Same model, point estimates and 500 draws per variant as lib/model.estimate; only the draws differ.
Variants (name: daily block length in days; monthly residual block length in months; recursive; joint):
  base     66 days; months iid; fixed design  (the paper's default, identical to model.estimate)
  d22,d132 daily moving blocks of 22 / 132 days
  m12      monthly residuals in moving blocks of 12 months (daily 66)
  m12r     as m12, the monthly macro lags rebuilt recursively from the resampled residuals (financial lags held at the data)
  j12      joint: months drawn in blocks of 12; the monthly residuals, the daily rows and the announcements of the drawn months are used together
  j12r     as j12, with the recursive monthly lags
Announcements are resampled as in the default except in the joint variants."""
import zlib
import numpy as np, pandas as pd
from . import model as M
from .daily import EV, event_index, positions, MON, HAR

VARIANTS = {"base": dict(dlen=66, mlen=1, rec=False, joint=False), "d22": dict(dlen=22, mlen=1, rec=False, joint=False), "d132": dict(dlen=132, mlen=1, rec=False, joint=False),
            "m12": dict(dlen=66, mlen=12, rec=False, joint=False), "m12r": dict(dlen=66, mlen=12, rec=True, joint=False),
            "j12": dict(dlen=66, mlen=12, rec=False, joint=True), "j12r": dict(dlen=66, mlen=12, rec=True, joint=True)}

def macro_rows(form, fci, mvars, L, start):
    """macro_data with the period of each row (no trend, 2020 in, no end)."""
    FB = M.fin_monthly(form, fci); MMv = M.MAC[mvars]; X, Y, P = [], [], []
    for p in MMv.index:
        if p < pd.Period(start, "M") or p > M.last_month(None): continue
        try: xm = np.concatenate([MMv.loc[p - l].values for l in range(1, L + 1)]); xf = np.concatenate([FB.loc[p - l].values for l in range(1, L + 1)])
        except KeyError: continue
        x = np.r_[1.0, xm, xf]; y = MMv.loc[p].values
        if np.isnan(x).any() or np.isnan(y).any(): continue
        X.append(x); Y.append(y); P.append(p)
    return np.array(X), np.array(Y), pd.PeriodIndex(P, freq="M")

def daily_months(form, fci, mvars):
    """Month of each row of M.har_rows (same filters, 2020 in)."""
    D = M.daily_frame(form, fci).loc["1990-01-02":].dropna(); mo = D.index.to_period("M"); MMv = M.MAC[mvars]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1) & (D.index >= M.DAILY_START)
    return mo[ok]

def recursive_y(X, C, e_star, K, L, P):
    """y*_t = X*_t C + e*_t, the macro lags of X* replaced by y* (pre-sample months and the financial lags as in the data)."""
    Xs = X.copy(); Y = np.zeros((len(X), K)); pos = {p: i for i, p in enumerate(P)}
    for t, p in enumerate(P):
        for l in range(1, L + 1):
            j = pos.get(p - l)
            if j is not None and j < t: Xs[t, 1 + K * (l - 1):1 + K * l] = Y[j]
        Y[t] = Xs[t] @ C + e_star[t]
    return Y

def estimate(form, fci, variant, B=500, L=12, start="1996-01", macro="u,pi"):
    v = VARIANTS[variant]; mvars = macro.split(","); K = len(mvars); nd = M.daily_frame(form, fci).shape[1]
    idx0, pos0, bidx, bpos = M.events(B); Xd, Yd = M.har_rows(form, fci, mvars, None, "in"); Bd0 = M.har_fit(Xd, Yd, fci); dmon = daily_months(form, fci, mvars)
    X, Y, P = macro_rows(form, fci, mvars, L, start); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
    tag = f"{form}|{fci}|{macro}|{start}|None|in|{L}"; sfx = "" if variant == "base" else "|" + variant
    rng = np.random.default_rng(zlib.crc32(tag.encode())); rng_d = np.random.default_rng(zlib.crc32(("block|" + tag).encode())); rng_j = np.random.default_rng(zlib.crc32(("joint|" + tag + sfx).encode()))
    if variant not in ("base",): rng = np.random.default_rng(zlib.crc32((tag + sfx).encode())); rng_d = np.random.default_rng(zlib.crc32(("block|" + tag + sfx).encode()))
    evm = pd.PeriodIndex(EV.d.iloc[idx0].dt.to_period("M"), freq="M")
    m0, f0, e0 = M.irf(Bd0, C0, K, nd, L, idx0, pos0, fci); draws = []
    for b in range(B):
        if v["joint"]:
            n = len(P); rows = M.block_rows(n, rng_j, v["mlen"]); mo = P[rows]                          # months drawn, in blocks, with repeats
            drow = np.concatenate([np.where(dmon == m)[0] for m in mo]); ev_i = np.concatenate([idx0[np.where(evm == m)[0]] for m in mo])
            if len(ev_i) < 20: ev_i = rng.choice(idx0, size=len(idx0), replace=True)
            e_star = res[rows]; ib, pb = ev_i, positions(ev_i); Xb, Yb = Xd[drow], Yd[drow]
        else:
            rows = M.block_rows(len(res), rng, v["mlen"]) if v["mlen"] > 1 else rng.integers(0, len(res), len(res)); e_star = res[rows]
            r = M.block_rows(len(Xd), rng_d, v["dlen"]); Xb, Yb = Xd[r], Yd[r]; ib, pb = bidx[b], bpos[b]
        ys = recursive_y(X, C0, e_star, K, L, P) if v["rec"] else fit + e_star
        Cb = np.linalg.lstsq(X, ys, rcond=None)[0] if not v["rec"] else np.linalg.lstsq(_recX(X, ys, K, L, P), ys, rcond=None)[0]
        draws.append(M.irf(M.har_fit(Xb, Yb, fci), Cb, K, nd, L, ib, pb, fci))
    return dict(lags=L, nobs=len(Y), names=["P" if x == "pi" else x for x in mvars], s0=M.to_level(m0), sd=np.array([M.to_level(d[0]) for d in draws]), f0=f0, fd=np.array([d[1] for d in draws]), e0=e0)

def _recX(X, ys, K, L, P):
    """Regressors of the re-estimation in a recursive draw: lags of the macro variables are those of the simulated series."""
    Xs = X.copy(); pos = {p: i for i, p in enumerate(P)}
    for t, p in enumerate(P):
        for l in range(1, L + 1):
            j = pos.get(p - l)
            if j is not None: Xs[t, 1 + K * (l - 1):1 + K * l] = ys[j]
    return Xs
