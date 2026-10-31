"""Within-month MIDAS test. Monthly macro equations of the route-A type: m_t on 12 lags of the macro variables and 12 monthly lags of a WEIGHTED within-month average of each daily financial variable (policy, index), where the weight of weekday d (of n) in the month is proportional to 1 + delta (d - (n+1)/2)/((n-1)/2).
delta = 0 is the equal-weight monthly average used by the monthly VAR and route A; delta > 0 gives late-month days more weight, delta < 0 early-month days. One common delta per equation, profiled on a grid by OLS (12 monthly lags free). Months 2020-03..12 dropped.
Reports delta-hat, the F statistic for delta = 0 (1 restriction), and the R2 gain, for each equation and sample. Output: within_month_test.log"""
import numpy as np, pandas as pd
import midas_var as V
from midas_var import *
rows = []
def weighted_avgs(pol, delta, months):
    fin = np.stack([V.POL[pol].values, V.IDX.values], axis=1); out = {}
    for p in months:
        pos = np.where(V.MON == p)[0]; d = np.arange(1, len(pos) + 1); n = len(pos)
        w = 1 + delta * (d - (n + 1) / 2) / ((n - 1) / 2); w = w / w.sum()
        out[p] = w @ fin[pos]
    return out
def design(pol, first, delta):
    allm = [p for p in M.index if p >= pd.Period(first, "M") - 13 and p <= pd.Period("2026-09", "M")]
    fa = weighted_avgs(pol, delta, allm); X, Y, ms = [], [], []
    for p in allm:
        if p < pd.Period(first, "M") or (p.year == 2020 and p.month >= 3): continue
        try:
            lm = [M[["u_gap", "pi_core"]].loc[p - l].values for l in range(1, 13)]; lf = [fa[p - l] for l in range(1, 13)]
        except KeyError: continue
        y = M[["u_gap", "pi_core"]].loc[p].values
        row = np.concatenate([[1.0], np.concatenate(lm), np.concatenate(lf)])
        if np.isnan(row).any() or np.isnan(y).any(): continue
        X.append(row); Y.append(y); ms.append(p)
    return np.array(X), np.array(Y), ms
print("Within-month timing weights: delta-hat (grid -1..1), F test of delta = 0, R2 at delta = 0 and delta-hat\n")
grid = np.round(np.arange(-1.0, 1.01, 0.25), 2)
for lab, pol, first in (("long 1977- (2-year)", "y2", "1977-06"), ("short 1994- (2-year)", "y2", "1994-02"), ("long 1974- (funds rate)", "ff", "1974-01")):
    rss = {}
    for dl in grid:
        X, Y, ms = design(pol, first, dl)
        rss[dl] = [float(np.sum((Y[:, i] - X @ np.linalg.lstsq(X, Y[:, i], rcond=None)[0]) ** 2)) for i in range(2)]
    T, K = X.shape
    for i, nm in enumerate(("unemployment gap", "core PCE")):
        r = np.array([rss[d][i] for d in grid]); j = int(np.argmin(r)); d0 = list(grid).index(0.0)
        Fst = (r[d0] - r[j]) / (r[j] / (T - K - 1)); tss = np.sum((Y[:, i] - Y[:, i].mean()) ** 2)
        print(f"   {lab:26s} {nm:17s} T={T}  delta-hat {grid[j]:+.2f}  F(delta=0) {Fst:5.2f} (5% critical 3.9)  R2 {1 - r[d0] / tss:.4f} -> {1 - r[j] / tss:.4f}")
