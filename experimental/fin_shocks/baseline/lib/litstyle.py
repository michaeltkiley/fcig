"""Literature-style monthly estimators, run on the same data and units as the main model so that results are comparable (08_literature_style.py).
Variables (end-of-month, unemployment gap, core PCE inflation, policy variable i_t in percentage points); 12 lags, constant, no trend; unit of every response: +1 pp on i.
 CHOL  Recursive (Cholesky) VAR, order (u, inflation, i): the policy variable responds within the month to unemployment and inflation, which do not respond to it within the month
       (Christiano, Eichenbaum and Evans 1999 style; no commodity price or other price-puzzle controls). Impact vector (0, 0, 1). Inference: 5-95% of 200 residual-bootstrap draws.
 LPIV  Local projection instrumented with the Nakamura-Steinsson policy news summed within the month (Stock and Watson 2018; Jorda 2005; Bauer and Swanson 2023 use the same logic):
       target_{t+h} on i_t, controls = constant and 12 lags of (u, inflation, i), instrument z_t, months from the first to the last announcement. Target: unemployment gap at t+h, or the price level
       (inflation cumulated from t to t+h, /12). Inference: exact 90% Anderson-Rubin set (as in lib/monthly.py) with a Bartlett (Newey-West) long-run variance with h lags.
 P1    The monthly proxy VAR of lib/monthly.py, all horizons."""
import zlib
import numpy as np, pandas as pd
from .daily import EV, event_index, fred_daily, CALW
from . import monthly as MO
from .model import MAC, fin_eom
from .paths import DATA

L = 12; H = 36; CRIT = MO.CRIT

def policy(kind):
    """Monthly end-of-month policy variable: '2y' = nominal 2-year Treasury yield (the main model's), 'ffr' = effective federal funds rate."""
    if kind == "2y": return fin_eom("nom", False)["pol"].dropna()
    d = fred_daily("DFF").reindex(CALW).ffill(); d.index = d.index.to_period("M"); return d.groupby(level=0).last()

def frame(kind, start, end):
    D = MAC[["u", "pi"]].join(policy(kind).rename("i"), how="inner").dropna()
    return D[(D.index >= pd.Period(start, "M")) & (D.index <= pd.Period(end, "M"))]

def paths_chol(D, B=200, seed="x"):
    X, Y, per = MO.design(D, L, str(D.index.min()), str(D.index.max())); K = 3
    C = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C; res = Y - fit; s = np.array([0, 0, 1.0])
    def resp(Cm): T = MO.ma(Cm, K, L, H); return {v: np.array([MO.row_of(T, v, h) @ s for h in range(H + 1)]) for v in ("u", "P")}
    pt = resp(C); rng = np.random.default_rng(zlib.crc32(seed.encode())); dr = {v: [] for v in pt}
    for _ in range(B):
        Cb = np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0]; r = resp(Cb)
        for v in pt: dr[v].append(r[v])
    return {v: (pt[v], np.percentile(dr[v], 5, axis=0), np.percentile(dr[v], 95, axis=0)) for v in pt}, len(Y)

def _lrv(p, q, m):
    out = float(p @ q)
    for k in range(1, m + 1): out += (1 - k / (m + 1)) * float(p[k:] @ q[:-k] + q[k:] @ p[:-k])
    return out

def ar_nw(a, d, z, m):
    """Exact 90% AR set for theta in Cov(z, a - theta d) = 0 with a Bartlett long-run variance (m lags); a, d, z already purged of controls. Returns (point, lo, hi, unbounded)."""
    z = z - z.mean(); w = z / (z @ z); ba, bd = w @ a, w @ d; ra, rd = a - z * ba, d - z * bd; n = len(z)
    A, B, C = _lrv(w * ra, w * ra, m), _lrv(w * ra, w * rd, m), _lrv(w * rd, w * rd, m)
    qa, qb, qc = bd ** 2 - CRIT * C, -2 * ba * bd + 2 * CRIT * B, ba ** 2 - CRIT * A
    pt = ba / bd
    if qa <= 0: return pt, -np.inf, np.inf, True
    disc = qb ** 2 - 4 * qa * qc
    if disc < 0: return pt, np.nan, np.nan, False
    return pt, (-qb - np.sqrt(disc)) / (2 * qa), (-qb + np.sqrt(disc)) / (2 * qa), False

def paths_lpiv(start="1996-01", end="2026-09"):
    """LP-IV paths 0..H for u and the price level, with exact AR sets; also the first-stage F (HC1) of the instrument for i_t."""
    D = frame("2y", start, end); idx0 = event_index(); ev = EV.iloc[idx0]; mon = ev.Date.dt.to_period("M"); z_all = ev.ns.groupby(mon).sum()
    cols = []; per = D.index; n = len(per); U = D.u.values; P = D.pi.values; I = D.i.values
    rows = []
    for t in range(L, n):
        rows.append(np.r_[1.0, [D.iloc[t - l].values for l in range(1, L + 1)]].ravel() if False else np.r_[1.0, np.concatenate([D.iloc[t - l].values for l in range(1, L + 1)])])
    X = np.array(rows); T0 = np.arange(L, n); z = z_all.reindex(per[T0]).fillna(0.0).values
    ok0 = (per[T0] >= mon.min()) & (per[T0] <= mon.max())
    out = {}
    for v in ("u", "P"):
        pts, los, his = [], [], []
        for h in range(H + 1):
            valid = T0 + h < n; ok = ok0 & valid; t = T0[ok]
            y = np.array([U[s + h] for s in t]) if v == "u" else np.array([P[s:s + h + 1].sum() / 12 for s in t])
            Xc = X[ok]; M = lambda a: a - Xc @ np.linalg.lstsq(Xc, a, rcond=None)[0]
            pt, lo, hi, unb = ar_nw(M(y), M(I[t]), M(z[ok]), h)
            pts.append(pt); los.append(lo); his.append(hi)
        out[v] = (np.array(pts), np.array(los), np.array(his))
    t = T0[ok0]; Xc = X[ok0]; M = lambda a: a - Xc @ np.linalg.lstsq(Xc, a, rcond=None)[0]; F = MO.first_stage(M(I[t]), M(z[ok0]))[1]
    return out, F, int(ok0.sum())

def paths_p1(start="1996-01"):
    """Monthly proxy VAR (P1) of lib/monthly.py for the nominal two-year yield without FCI, all horizons."""
    idx0 = event_index(); ev = EV.iloc[idx0]; mon = ev.Date.dt.to_period("M"); z_all = ev.ns.groupby(mon).sum(); first, last = mon.min(), mon.max()
    D = MAC[["u", "pi"]].join(fin_eom("nom", False), how="inner").dropna(); K = 3
    X, Y, per = MO.design(D, L, start); C = np.linalg.lstsq(X, Y, rcond=None)[0]; res = Y - X @ C; T = MO.ma(C, K, L, H)
    ok = (per >= first) & (per <= last); z = z_all.reindex(per[ok]).fillna(0.0).values; r = res[ok]
    g = np.array([MO.first_stage(r[:, j], z)[0] for j in range(K)]); F = MO.first_stage(r[:, 2], z)[1]; S = g / g[2]; out = {}
    for v in ("u", "P"):
        pts, los, his = [], [], []
        for h in range(H + 1):
            c = MO.row_of(T, v, h); lo, hi, unb = MO.ar_set(r @ c, r[:, 2], z); pts.append(float(c @ S)); los.append(lo); his.append(hi)
        out[v] = (np.array(pts), np.array(los), np.array(his))
    return out, F, int(ok.sum())
