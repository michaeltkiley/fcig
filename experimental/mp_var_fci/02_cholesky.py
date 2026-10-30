"""Step 2b. Cholesky baseline (MP_QA.md MP-A1, A3, A4, A5, A7, A9).

System: unemployment gap, core PCE monthly annualized, nominal funds rate, market index (order as listed; the funds rate comes before the index so the index
responds to the policy shock within the month), 2020 monthly dummies, 12 lags (checks: 6 and 24), windows long (1973-01..2026-09) and matched (1994-01..2026-09).
Index cases: nominal, real, r*-gap (main). 'Without index' = the same VAR with the index dropped.
Shock: the orthogonalized funds-rate innovation, rescaled to +1 pp on impact ('per 1 pp funds rate'); also reported per unit of the index's own impact response
('per index unit', undefined if the index barely moves on impact).
Outputs: irf_cholesky.csv (long format: case, window, system, lags, order, h, variable, irf, lo95, hi95, lo68, hi68), 02_cholesky.log, cholesky_*.png.
Usage: python 02_cholesky.py [--reps 500]
"""
import sys, warnings
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")

REPS = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 500
H = 48
WINDOWS = {"long": "1973-01", "matched": "1994-01"}
D = pd.read_csv("data/mp_monthly.csv", index_col=0); D.index = pd.PeriodIndex(D.index, freq="M")


def prep(cols, start):
    X = D.loc[start:"2026-09", cols].dropna()
    dum = pd.DataFrame({f"d{k:02d}": (X.index == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}, index=X.index)
    X = X.copy(); X.index = X.index.to_timestamp(); dum.index = X.index
    return X, dum


def irfs(r, j, H=H):
    """Orthogonalized responses to shock j, scaled to +1 on impact in variable j: array (H+1, k); also the impact of every variable per unit shock."""
    o = r.irf(H).orth_irfs
    return o[:, :, j] / o[0, j, j], o[0, :, j] / o[0, j, j]


def boot(r, X, dum, j, reps=REPS, seed=11):
    rng = np.random.default_rng(seed)
    Y, p, k = X.values, r.k_ar, X.shape[1]
    c, A, e = r.params.values, r.coefs, r.resid.values
    out = []
    for _ in range(reps):
        Yb = Y.copy(); draw = e[rng.integers(0, len(e), size=len(Y) - p)]
        for t in range(p, len(Y)):
            Yb[t] = c[0] + dum.values[t] @ c[1:13] + sum(A[l] @ Yb[t - 1 - l] for l in range(p)) + draw[t - p]
        rb = VAR(pd.DataFrame(Yb, index=X.index, columns=X.columns), exog=dum).fit(p)
        out.append(irfs(rb, j)[0])
    return np.array(out)                                # reps x (H+1) x k


rows, summ = [], []


def run(case, window, system, p, order="ffr_then_index", bands=False):
    idx = f"market_{case}"
    cols = ["u_gap", "pi_core", "ffr"] + ([idx] if system == "with index" else [])
    if system == "with index" and order == "index_then_ffr":
        cols = ["u_gap", "pi_core", idx, "ffr"]
    X, dum = prep(cols, WINDOWS[window])
    r = VAR(X, exog=dum).fit(p)
    j = cols.index("ffr")
    path, impact = irfs(r, j)
    B = boot(r, X, dum, j) if bands else None
    for v, name in enumerate(cols):
        for h in range(H + 1):
            rec = dict(case=case, window=window, system=system, lags=p, order=order, h=h, variable=name, irf=path[h, v])
            if B is not None:
                q = np.percentile(B[:, h, v], [2.5, 97.5, 16, 84]); rec.update(lo95=q[0], hi95=q[1], lo68=q[2], hi68=q[3])
            rows.append(rec)
    u = path[:, 0]
    summ.append(dict(case=case, window=window, system=system, lags=p, order=order, T=len(X),
                     u_h12=u[12], u_h24=u[24], u_h36=u[36], u_peak=u.max() if abs(u.max()) >= abs(u.min()) else u.min(), u_peak_h=int(np.argmax(np.abs(u))),
                     price_h24=path[:25, 1].sum() / 12, price_h48=path[:49, 1].sum() / 12,
                     ffr_h12=path[12, cols.index("ffr")], idx_impact=impact[cols.index(idx)] if idx in cols else np.nan,
                     idx_h12=path[12, cols.index(idx)] if idx in cols else np.nan))
    return path


if __name__ == "__main__":
    for case in ("nominal", "real", "rstar"):
        for window in WINDOWS:
            for system in ("without index", "with index"):
                if system == "without index" and case != "rstar":
                    continue                                  # the no-index system does not depend on the case
                run(case, window, system, 12, bands=True)
                print(f"done {case} {window} {system}", flush=True)
    for window in WINDOWS:
        for p in (6, 24):
            for system in ("without index", "with index"):
                run("rstar", window, system, p)
        run("rstar", window, "with index", 12, order="index_then_ffr", bands=True)
    R = pd.DataFrame(rows); R.to_csv("irf_cholesky.csv", index=False, float_format="%.5f")
    S = pd.DataFrame(summ); S.to_csv("irf_cholesky_summary.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 220)
    print("\nSummary (per +1 pp funds-rate innovation; u = unemployment gap pp; price = cumulative core PCE price level, % ; idx = market index units):")
    print(S.round(3).to_string(index=False))
