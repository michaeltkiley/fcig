"""Step 2e (MP-A10). Cholesky with the 2-year yield (monthly average, FRED GS2, from 1976-06) as the policy variable, across samples.
System: u gap, core PCE monthly, 2-year yield, r*-gap market index (order as listed); 12 lags; 2020 months dummied (+ ZLB months dummied in the last window); 200-draw bootstrap.
Windows: long 1976-06..2026-09; 1994-01..2026-09 (matched); pre-ZLB long 1976-06..2008-11; pre-ZLB matched 1994-01..2008-11; pre-COVID 1994-01..2019-12; 1994-2026 ZLB months dummied.
Shock: orthogonalized 2-year innovation scaled to +1 pp on impact. Output: 02e_cholesky_gs2.log, irf_cholesky_gs2.csv, cholesky_gs2_u.png"""
import warnings
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
REPS, H, P = 200, 48, 12
D = pd.read_csv("data/mp_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
ZLB = [("2008-12", "2015-12"), ("2020-03", "2022-03")]


def prep(cols, a, b, zlb):
    X = D.loc[a:b, cols].dropna()
    ms = set(pd.period_range("2020-01", "2020-12", freq="M"))
    if zlb:
        for s, e in ZLB:
            ms |= set(pd.period_range(s, e, freq="M"))
    ms = [m for m in sorted(ms) if m in X.index]
    dum = pd.DataFrame({f"d{m}": (X.index == m).astype(float) for m in ms}, index=X.index)
    X = X.copy(); X.index = X.index.to_timestamp(); dum.index = X.index
    return X, (dum if dum.shape[1] else None)


def irfs(r, j):
    o = r.irf(H).orth_irfs
    return o[:, :, j] / o[0, j, j], o[0, j, j]


def boot(r, X, dum, j):
    rng = np.random.default_rng(5)
    Y, p = X.values, r.k_ar
    c, A, e = r.params.values, r.coefs, r.resid.values
    nd = 0 if dum is None else dum.shape[1]
    out = []
    for _ in range(REPS):
        Yb = Y.copy(); dr = e[rng.integers(0, len(e), size=len(Y) - p)]
        for t in range(p, len(Y)):
            Yb[t] = c[0] + ((dum.values[t] @ c[1:1 + nd]) if nd else 0.0) + sum(A[l] @ Yb[t - 1 - l] for l in range(p)) + dr[t - p]
        out.append(irfs(VAR(pd.DataFrame(Yb, index=X.index, columns=X.columns), exog=dum).fit(p), j)[0][:, 0])
    return np.percentile(np.array(out), [2.5, 97.5], axis=0)


W = [("long 1976-2026", "1976-06", "2026-09", False), ("matched 1994-2026", "1994-01", "2026-09", False), ("pre-ZLB long 1976-2008m11", "1976-06", "2008-11", False),
     ("pre-ZLB matched 1994-2008m11", "1994-01", "2008-11", False), ("pre-COVID 1994-2019", "1994-01", "2019-12", False), ("1994-2026 ZLB dummied", "1994-01", "2026-09", True)]
rows, fig = [], {}
print("Unemployment-gap response to +1 pp 2-year-yield innovation (95% band); sd = one-sd innovation (pp); gs2 12 = 2-year response at 12 months; idx = index response")
for lab, a, b, z in W:
    for system, cols in (("without index", ["u_gap", "pi_core", "gs2"]), ("with index", ["u_gap", "pi_core", "gs2", "market_rstar"])):
        X, dum = prep(cols, a, b, z); r = VAR(X, exog=dum).fit(P); j = 2
        path, sd = irfs(r, j); lo, hi = boot(r, X, dum, j)
        fig[(lab, system)] = (path[:, 0], lo, hi)
        k = 3 if system == "with index" else None
        rows.append(dict(window=lab, system=system, T=len(X), sd=sd, u12=path[12, 0], lo12=lo[12], hi12=hi[12], u24=path[24, 0], lo24=lo[24], hi24=hi[24], gs2_12=path[12, 2], idx0=path[0, k] if k else np.nan, idx12=path[12, k] if k else np.nan, price48=path[:49, 1].sum() / 12))
        w = rows[-1]
        print(f"  {lab:30s} {system:14s} T={w['T']:3d} sd={sd:.2f}  u12 {w['u12']:+.2f} ({w['lo12']:+.2f},{w['hi12']:+.2f})  u24 {w['u24']:+.2f} ({w['lo24']:+.2f},{w['hi24']:+.2f})  gs2@12 {w['gs2_12']:+.2f}" + (f"  idx0 {w['idx0']:+.2f} idx12 {w['idx12']:+.2f}" if k else ""), flush=True)
pd.DataFrame(rows).to_csv("irf_cholesky_gs2.csv", index=False, float_format="%.4f")
f, ax = plt.subplots(1, 6, figsize=(20, 3.4), sharey=True)
for a_, (lab, *_r) in zip(ax, W):
    for system, col in (("without index", "#8a8a8a"), ("with index", "#c4501f")):
        m, lo, hi = fig[(lab, system)]; a_.fill_between(range(H + 1), lo, hi, color=col, alpha=0.13, lw=0); a_.plot(m, color=col, lw=1.4, label=system)
    a_.axhline(0, color="k", lw=0.6); a_.set_title(lab, fontsize=8); a_.set_xlabel("months")
ax[0].set_ylabel("unemployment gap, pp per +1 pp 2-year"); ax[0].legend(frameon=False, fontsize=7); f.tight_layout(); f.savefig("cholesky_gs2_u.png", dpi=130)
