"""Step 12. Direct monthly projections on the announcement surprise (a benchmark with no financial block; appendix).   python3 12_direct_projection.py      Output: results/direct_projection.csv

For each announcement month t (January 1996 to September 2026, nothing dropped) and horizon h = 12 and 24 months:
    outcome_{t+h} = a + b_h S_t + controls_{t-1} + e,
S_t = sum of the policy-news surprises of the announcements in month t (zero in months without one), the outcome is the unemployment gap in month t+h (event month = 0, as in the model) or the core price
level, the cumulated core PCE inflation of months t..t+h divided by 12 (as the model's price level, percent). Controls (all dated before the shock month): 12 lags of the unemployment gap and inflation
('macro lags'), and, second version, 12 lags of the monthly averages of the r*-gap 2-year yield and FCI, the information in the monthly equations of the model; never the contemporaneous FCI.
Scaling: b_h divided by the window slope of the 2-year yield on the surprise (the same 252 announcements), so the unit is +1 pp on the 2-year yield in the window, as everywhere else.
There is no monthly first stage: the surprise is the regressor and the scaling is the window slope.  Inference: moving blocks of 12 (h = 12) or 24 (h = 24) calendar months of rows and announcements, the
scaling re-estimated in each draw, 2,000 draws, 90% percentile intervals; Newey-West (h + 12 lags) standard errors reported alongside.  A model-free benchmark: all channels operate and nothing is imposed."""
import numpy as np, pandas as pd
from lib import model as M, daily as D
from lib.paths import RESULTS
EV = D.EV; ie = D.event_index(); s_ev = EV.ns.values[ie]; w_ev = EV.UST2Y.values[ie]; m_ev = pd.PeriodIndex(EV.d.iloc[ie].dt.to_period("M"))
MAC = M.MAC[["u", "pi"]]; FB = M.fin_monthly("rstar", "rstar")
P0, P1 = pd.Period("1996-01", "M"), pd.Period("2026-09", "M"); L = 12; HS = (12, 24)
Sm = pd.Series(s_ev, index=m_ev).groupby(level=0).sum()
def build(h, fin):
    rows = []
    for t in pd.period_range(P0, P1 - h, freq="M"):
        try:
            x = np.r_[1.0, np.concatenate([MAC.loc[t - l].values for l in range(1, L + 1)]), (np.concatenate([FB.loc[t - l].values for l in range(1, L + 1)]) if fin else [])]
            yu = MAC.u.loc[t + h]; yp = MAC.pi.loc[t:t + h].sum() / 12
        except KeyError: continue
        if np.isnan(x).any() or np.isnan(yu) or np.isnan(yp): continue
        rows.append((t, Sm.get(t, 0.0), yu, yp, x))
    return rows
def slope(y, x, ctrl):
    Z = np.c_[x, ctrl]; return np.linalg.lstsq(Z, y, rcond=None)[0][0]
def nw(y, Z, lags):
    b = np.linalg.lstsq(Z, y, rcond=None)[0]; e = y - Z @ b; g = Z * e[:, None]; S = g.T @ g
    for k in range(1, lags + 1): G = g[k:].T @ g[:-k]; S += (1 - k / (lags + 1)) * (G + G.T)
    Zi = np.linalg.inv(Z.T @ Z); return b, Zi @ S @ Zi
rng = np.random.default_rng(12); out = []
evby = {m: (s_ev[m_ev == m], w_ev[m_ev == m]) for m in pd.period_range(P0, P1, freq="M")}
def wslope(months):
    s = np.concatenate([evby[m][0] for m in months]); w = np.concatenate([evby[m][1] for m in months]); return np.sum((s - s.mean()) * (w - w.mean())) / np.sum((s - s.mean()) ** 2)
sw = wslope(list(evby))
for fin in (False, True):
    for h in HS:
        rows = build(h, fin); T = np.array([r[0].ordinal for r in rows]); S = np.array([r[1] for r in rows]); X = np.array([r[4] for r in rows]); Y = {"u": np.array([r[2] for r in rows]), "P": np.array([r[3] for r in rows])}
        n = len(rows); blk = 12 if h == 12 else 24; mons = [r[0] for r in rows]
        est = {v: slope(Y[v], S, X) / sw for v in Y}; nwr = {}
        for v in Y:
            Z = np.c_[S, X]; b, V = nw(Y[v], Z, h + 12); nwr[v] = (b[0] / sw, np.sqrt(V[0, 0]) / sw)
        dr = {v: [] for v in Y}
        for b in range(2000):
            idx = np.concatenate([np.arange(a, a + blk) for a in rng.integers(0, n - blk + 1, -(-n // blk))])[:n]
            swb = wslope([mons[i] for i in idx])
            for v in Y: dr[v].append(slope(Y[v][idx], S[idx], X[idx]) / swb)
        for v in Y:
            d = np.array(dr[v]); out.append(dict(controls="macro and financial lags" if fin else "macro lags", var=v, h=h, nobs=n, est=est[v], lo=np.percentile(d, 5), hi=np.percentile(d, 95), lo68=np.percentile(d, 16), hi68=np.percentile(d, 84),
                                                 nw_se=nwr[v][1], nw_lo=est[v] - 1.645 * nwr[v][1], nw_hi=est[v] + 1.645 * nwr[v][1], window_slope=sw))
R = pd.DataFrame(out); R.to_csv(RESULTS / "direct_projection.csv", index=False, float_format="%.4f"); print(R.round(3).to_string())
