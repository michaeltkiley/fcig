"""Step 2d (MP-Q9). Does the wrong-sign Cholesky response in the 1994- window come from the zero-lower-bound (ZLB) years and the hiking cycle?
Same VAR as 02_cholesky.py (u gap, core PCE monthly, nominal funds rate, r*-gap market index; 12 lags; order as listed), windows:
  pre-ZLB long   1973-01..2008-11      pre-ZLB matched 1994-01..2008-11      pre-COVID 1994-01..2019-12 (ZLB included)
  ZLB months dummied  1994-01..2026-09 with a dummy for each ZLB month (2008-12..2015-12, 2020-03..2022-03; the old repo convention) and each 2020 month
Reports unemployment, funds-rate and index responses per +1 pp funds-rate innovation, the one-sd innovation, with and without the index, 95% bootstrap bands.
Output: 02d_exzlb.log, irf_exzlb.csv, cholesky_exzlb_u.png"""
import warnings
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

REPS, H, P = 500, 48, 12
D = pd.read_csv("data/mp_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")
ZLB = [("2008-12", "2015-12"), ("2020-03", "2022-03")]


def dummy_months(idx, zlb):
    months = set(pd.period_range("2020-01", "2020-12", freq="M"))
    if zlb:
        for a, b in ZLB:
            months |= set(pd.period_range(a, b, freq="M"))
    months = [m for m in sorted(months) if m in idx]
    return pd.DataFrame({f"d{m}": (idx == m).astype(float) for m in months}, index=idx)


def prep(cols, start, end, zlb):
    X = D.loc[start:end, cols].dropna()
    dum = dummy_months(X.index, zlb)
    X = X.copy(); X.index = X.index.to_timestamp(); dum.index = X.index
    if dum.shape[1] == 0:
        dum = None
    return X, dum


def fit(X, dum):
    return VAR(X, exog=dum).fit(P)


def irfs(r, j):
    o = r.irf(H).orth_irfs
    return o[:, :, j] / o[0, j, j], o[0, j, j]


def boot(r, X, dum, j, seed=11):
    rng = np.random.default_rng(seed)
    Y, p = X.values, r.k_ar
    c, A, e = r.params.values, r.coefs, r.resid.values
    nd = 0 if dum is None else dum.shape[1]
    out = []
    for _ in range(REPS):
        Yb = Y.copy(); draw = e[rng.integers(0, len(e), size=len(Y) - p)]
        for t in range(p, len(Y)):
            xd = (dum.values[t] @ c[1:1 + nd]) if nd else 0.0
            Yb[t] = c[0] + xd + sum(A[l] @ Yb[t - 1 - l] for l in range(p)) + draw[t - p]
        out.append(irfs(fit(pd.DataFrame(Yb, index=X.index, columns=X.columns), dum), j)[0])
    return np.array(out)


SPECS = [("pre-ZLB long 1973-2008m11", "1973-01", "2008-11", False), ("pre-ZLB matched 1994-2008m11", "1994-01", "2008-11", False),
         ("pre-COVID 1994-2019", "1994-01", "2019-12", False), ("1994-2026, ZLB months dummied", "1994-01", "2026-09", True)]
rows, fig_data = [], {}
for lab, a, b, zlb in SPECS:
    for system, cols in (("without index", ["u_gap", "pi_core", "ffr"]), ("with index", ["u_gap", "pi_core", "ffr", "market_rstar"])):
        X, dum = prep(cols, a, b, zlb)
        r = fit(X, dum); j = cols.index("ffr")
        path, sd = irfs(r, j); B = boot(r, X, dum, j)
        lo, hi = np.percentile(B[:, :, 0], [2.5, 97.5], axis=0)
        fig_data[(lab, system)] = (path[:, 0], lo, hi)
        k = cols.index("market_rstar") if system == "with index" else None
        rows.append(dict(window=lab, system=system, T=len(X), sd_shock=sd, u12=path[12, 0], u12_lo=lo[12], u12_hi=hi[12], u24=path[24, 0], u24_lo=lo[24], u24_hi=hi[24],
                         ffr12=path[12, j], idx0=path[0, k] if k else np.nan, idx12=path[12, k] if k else np.nan, price48=path[:49, 1].sum() / 12))
        for h in range(H + 1):
            pass
R = pd.DataFrame(rows); R.to_csv("irf_exzlb.csv", index=False, float_format="%.4f")
pd.set_option("display.width", 230)
print("Unemployment-gap response to +1 pp funds-rate innovation (95% band); sd_shock = one-sd innovation, pp; ffr12 = funds-rate response at 12 months")
for _, w in R.iterrows():
    print(f"  {w.window:32s} {w.system:14s} T={w['T']:3d} sd={w.sd_shock:.2f}  u12 {w.u12:+.2f} ({w.u12_lo:+.2f},{w.u12_hi:+.2f})  u24 {w.u24:+.2f} ({w.u24_lo:+.2f},{w.u24_hi:+.2f})  ffr12 {w.ffr12:+.2f}"
          + (f"  index h0 {w.idx0:+.2f} h12 {w.idx12:+.2f}" if not np.isnan(w.idx0) else ""))
fig, ax = plt.subplots(1, 4, figsize=(15, 3.6), sharey=True)
for a_, (lab, *_r) in zip(ax, SPECS):
    for system, col in (("without index", "#8a8a8a"), ("with index", "#c4501f")):
        m, lo, hi = fig_data[(lab, system)]; a_.fill_between(range(H + 1), lo, hi, color=col, alpha=0.13, lw=0); a_.plot(m, color=col, lw=1.5, label=system)
    a_.axhline(0, color="k", lw=0.6); a_.set_title(lab, fontsize=8.5); a_.set_xlabel("months")
ax[0].set_ylabel("unemployment gap, pp per +1 pp"); ax[0].legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig("cholesky_exzlb_u.png", dpi=140)
