"""(c) What does the Granger test on 12 lags of the level pick up? One-step equation of the VAR for the unemployment gap:
u(t+1) on 12 lags of u and 12 lags of the index x (t..t-11), 1974-2026, months touching 2020-01..2021-03 dropped.
Reparametrise the 12 lags of x as: the level x_t (coefficient = SUM of the 12 lag coefficients) and 11 differences dx_{t-k} (k=0..10).
Report F tests (classical and HAC Wald, 12 lags): all 12 lags; the sum only; the 11 differences only. Same for the 12-month-ahead direct projection of du.
Also the sum of lag coefficients with its t-stat, and the cumulative lag profile."""
import numpy as np, pandas as pd, statsmodels.api as sm
from common import *

u = u_gap(); res = []
for lab, x in load_indexes().items():
    cols = {"y": u.shift(-1)}
    for l in range(12): cols[f"u{l}"] = u.shift(l); cols[f"x{l}"] = x.shift(l)
    J = pd.DataFrame(cols).loc["1974-03":"2026-08"]
    J = J[[not (covid(t) or covid(t + 1) or any(covid(t - l) for l in range(12))) for t in J.index]].dropna()
    # reparametrise: x_t (level, sum of lags) and differences dxk = x_{t-k} - x_{t-k-1}, k=0..10
    R = pd.DataFrame({"y": J.y}); R[[f"u{l}" for l in range(12)]] = J[[f"u{l}" for l in range(12)]]
    R["xsum"] = J.x0
    for k in range(11): R[f"dx{k}"] = J[f"x{k}"] - J[f"x{k+1}"]
    # coefficient on x0 in this param. equals sum of the original lag coefficients; the dx terms carry the profile
    X = sm.add_constant(R.drop(columns="y")); m = sm.OLS(R.y, X).fit(); mh = sm.OLS(R.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    xs = [c for c in X.columns if c.startswith("xsum") or c.startswith("dx")]
    def F(cl):
        A = np.zeros((len(cl), len(X.columns)))
        for i, c in enumerate(cl): A[i, list(X.columns).index(c)] = 1
        f = m.f_test(A); w = mh.wald_test(A, scalar=True, use_f=True)
        return float(f.fvalue), float(f.pvalue), float(w.statistic), float(w.pvalue)
    Fall = F(xs); Fsum = F(["xsum"]); Fdif = F([c for c in xs if c.startswith("dx")])
    # Granger on all 12 original lags equals xs jointly (invertible transformation); check
    X0 = sm.add_constant(J.drop(columns="y")); m0 = sm.OLS(J.y, X0).fit()
    A0 = np.zeros((12, X0.shape[1]))
    for l in range(12): A0[l, list(X0.columns).index(f"x{l}")] = 1
    f0 = m0.f_test(A0)
    # long-run effect: sum of lag coefs per standard deviation of the index
    sd = x.loc["1974-03":"2026-08"].std()
    res.append({"series": lab, "n": len(J), "F_all12": Fall[0], "p_all12": Fall[1], "check_p_orig": float(f0.pvalue), "p_all12_HAC": Fall[3],
                "F_sum": Fsum[0], "p_sum": Fsum[1], "p_sum_HAC": Fsum[3], "sum_coef_per_sd": float(m.params["xsum"] * sd), "t_sum_HAC": float(mh.tvalues["xsum"]),
                "F_diff11": Fdif[0], "p_diff11": Fdif[1], "p_diff11_HAC": Fdif[3]})
    print(lab, round(Fall[1], 4), round(Fsum[1], 4), round(Fdif[1], 4), flush=True)
pd.DataFrame(res).to_csv(OUT / "granger_results.csv", index=False)
