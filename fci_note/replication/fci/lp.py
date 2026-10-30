"""Local projections of the unemployment gap: u(t+h) on u(t..t-L+1) and x(t..t-L+1); months touching 2020-01..2021-03 dropped; HAC errors."""
import numpy as np, pandas as pd
import statsmodels.api as sm

covid = lambda p: p.year == 2020 or (p.year == 2021 and p.month <= 3)


def design(u, x, h, L):
    cols = {"y": u.shift(-h)}
    for l in range(L):
        cols[f"u{l}"] = u.shift(l)
        if x is not None:
            cols[f"x{l}"] = x.shift(l)
    J = pd.DataFrame(cols)
    return J[[not (covid(t + h) or any(covid(t - l) for l in range(L))) for t in J.index]]


def fit(u, x, h=12, L=1, start="1976-03", end="2026-09"):
    """Returns the sum of the index coefficients, its se, and the gain in adjusted R2 over u lags alone."""
    J = design(u, x, h, L).loc[start:end].dropna()
    X = sm.add_constant(J.drop(columns="y"))
    r = sm.OLS(J.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1) + 1})
    s = np.array([1.0 if c.startswith("x") else 0.0 for c in X.columns])
    t = r.t_test(s)
    r0 = sm.OLS(J.y, sm.add_constant(J[[f"u{l}" for l in range(L)]])).fit()
    return float(np.ravel(t.effect)[0]), float(np.ravel(t.sd)[0]), r.rsquared_adj - r0.rsquared_adj


def oos(u, x, h=12, L=1, start="1976-03", first="1995-01", last="2025-09"):
    """Recursive out-of-sample forecasts of u(t+h): RMSE ratio to the projection on u lags alone, and a Diebold-Mariano t (HAC 12; negative = index better)."""
    J = design(u, x, h, L).loc[start:]
    uc = [f"u{l}" for l in range(L)]
    e1, e0 = [], []
    for t in pd.period_range(first, last, freq="M"):
        if t not in J.index or J.loc[t].isna().any():
            continue
        tr = J.loc[:t - h].dropna()
        b1 = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr.drop(columns="y").values], tr.y.values, rcond=None)[0]
        b0 = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[uc].values], tr.y.values, rcond=None)[0]
        row = J.loc[t]
        e1.append(row.y - b1 @ np.r_[1, row.drop("y").values]); e0.append(row.y - b0 @ np.r_[1, row[uc].values])
    e1, e0 = np.array(e1), np.array(e0)
    d = e1 ** 2 - e0 ** 2
    dm = sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": 12}).tvalues[0]
    return float(np.sqrt((e1 ** 2).mean() / (e0 ** 2).mean())), float(dm)
