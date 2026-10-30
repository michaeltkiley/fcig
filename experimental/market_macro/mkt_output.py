"""
Option (b), answer 46: the market index in an empirical output equation, in raw market-index units (pp of the 2-year yield per NS unit), with the
non-policy part split out (weighting note: x_t = psi M_t + n_t).
    x_t   = 10-year yield, 100 ln CAPE, 100 ln real broad dollar (monthly, mf_var_us_long.financial(): GS10, Shiller/project CAPE, TWEXBPA/RTWEXBGS), demeaned 1973-2025
    w     = market-index weights (NS one-factor GLS, transmission_v3.py): 10-year 0.6089, equities -0.0512, dollar 0.0654 (w'psi = 1)
    psi   = event-window responses to a 1-unit NS surprise: 10-year 0.535, equities -7.779, dollar 4.224
    M_t   = w'x_t (the market index, applied from 1973)
    n_t   = x_t - psi M_t (non-policy residual; w'n_t = 0, so two independent directions: the equity and dollar residuals are used; the 10-year residual is implied)
Equation (local projection, monthly):
    u(t+h) - u(t-1) = c + a M_t + b_eq n_eq,t + b_usd n_usd,t + d1 u(t-1) + d2 infl(t-1) + sum_{l=1..3} e_l du(t-l) + lags (1-3) of dM and dn + err,  h = 6, 12, 24
    u = unemployment gap (UNRATE - CBO NROU); infl = core PCE 12-month less 2. Sample 1973-07..2025-12 excluding 2020 (and 1990-2025 as a check). HAC (h lags).
Reading (weighting note):
    a       = unemployment response to a unit of policy-like tightening (market-index unit); output equivalent -2a
    b = 0   = "indicator" case: non-policy moves do not matter for output beyond their policy content -> market weights are also the output weights
    output-lens weights in market-index units: v / a, with v' = a w' + b'(I - psi w') (b_10y = 0 by the normalization); a pure policy move reads 1 per unit
    compared with the market weights w and with the FRB/US weights s (s'psi = 0.995, so s is already in this unit).
Usage: python experimental/market_macro/mkt_output.py
Outputs: mkt_output.log (tee), mkt_output_weights.csv, mkt_output_index_monthly.csv
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "fci_compare"))
import mf_var_us_long as LL
import mf_var_us as V

VARS = ["10-year", "equities", "dollar"]
W = np.array([0.6089, -0.0512, 0.0654])
PSI = np.array([0.535, -7.779, 4.224])
S_FRB = np.array([0.5695, -0.0316, 0.1004])


def fit(D, h, start, end, extra_ctrl=True):
    du = D.u.diff()
    cols = {"y": D.u.shift(-h) - D.u.shift(1), "M": D.M, "n_eq": D.n_eq, "n_usd": D.n_usd, "u1": D.u.shift(1), "pi1": D.pi.shift(1),
            **{f"du{l}": du.shift(l) for l in (1, 2, 3)}}
    if extra_ctrl:
        for v in ("M", "n_eq", "n_usd"):
            for l in (1, 2, 3):
                cols[f"d{v}{l}"] = D[v].diff().shift(l)
    Z = pd.concat(cols, axis=1).loc[start:end]
    Z = Z[[t.year != 2020 for t in Z.index]].dropna()
    r = sm.OLS(Z.y, sm.add_constant(Z.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1)})
    return r, len(Z)


def main():
    F = LL.financial()[VARS]
    M_ = V.macro_data(False)
    X = F.loc["1973-01":"2025-12"]
    X = X - X.drop(index=[t for t in X.index if t.year == 2020]).mean()
    Xall = F.loc["1973-01":] - (F.loc["1973-01":"2025-12"].drop(index=[t for t in F.loc["1973-01":"2025-12"].index if t.year == 2020]).mean())
    M = Xall.values @ W
    N = Xall.values - np.outer(M, PSI)
    D = pd.DataFrame({"M": M, "n_10y": N[:, 0], "n_eq": N[:, 1], "n_usd": N[:, 2]}, index=Xall.index)
    D = D.join(M_.rename(columns={"unemployment gap": "u", "inflation gap": "pi"}), how="left")
    print(f"check w'n = 0: max {np.abs(N @ W).max():.1e};  sd since 1973: M {D.M.std():.2f}, n_10y {D.n_10y.std():.2f}, n_eq {D.n_eq.std():.1f}, n_usd {D.n_usd.std():.1f}")
    print(f"share of each variable's variance on the policy ray (var(psi_j M) / var(x_j)): " + ", ".join(f"{v} {np.var(PSI[i] * M) / np.var(Xall.values[:, i]):.2f}" for i, v in enumerate(VARS)))
    pd.set_option("display.width", 220)
    rows = []
    for (start, end, lab) in (("1973-07", "2025-12", "1973-2025"), ("1990-01", "2025-12", "1990-2025")):
        for h in (6, 12, 24):
            for ctrl in (True, False):
                r, n = fit(D, h, start, end, ctrl)
                a, b_eq, b_usd = r.params["M"], r.params["n_eq"], r.params["n_usd"]
                b = np.array([0.0, b_eq, b_usd])
                v = a * W + b - (b @ PSI) * W           # v' = a w' + b'(I - psi w')
                wald = r.wald_test("n_eq = 0, n_usd = 0", scalar=True)
                rows.append(dict(sample=lab, h=h, lag_ctrl=ctrl, n=n, a=a, a_se=r.bse["M"], output_eq=-2 * a, b_eq=b_eq, b_eq_se=r.bse["n_eq"], b_usd=b_usd, b_usd_se=r.bse["n_usd"],
                                 p_b0=float(wald.pvalue), **{f"v/a {k}": v[i] / a for i, k in enumerate(VARS)}))
    R = pd.DataFrame(rows)
    print("\nOutput equation estimates (u pp per unit; a per unit of the market index, b per unit of the non-policy residual):")
    print(R.round(4).to_string(index=False))
    print("\nweights per unit, market-index units (2-year pp per NS unit):")
    print("  market w:          " + ", ".join(f"{k} {W[i]:+.4f}" for i, k in enumerate(VARS)))
    print("  FRB/US s (s'psi=0.995): " + ", ".join(f"{k} {S_FRB[i]:+.4f}" for i, k in enumerate(VARS)))
    main_ = R[(R["sample"] == "1973-2025") & (R.h == 12) & (R.lag_ctrl)].iloc[0]
    vw = np.array([main_[f"v/a {k}"] for k in VARS])
    print("  output-lens (1973-2025, h=12): " + ", ".join(f"{k} {vw[i]:+.4f}" for i, k in enumerate(VARS)) + f"   [v'psi/a = {vw @ PSI:.3f}]")
    pd.DataFrame({"market_w": W, "frbus_s": S_FRB, "output_lens_h12": vw}, index=VARS).to_csv(os.path.join(HERE, "mkt_output_weights.csv"), float_format="%.5f")
    R.to_csv(os.path.join(HERE, "mkt_output_estimates.csv"), float_format="%.5f", index=False)
    idx = pd.DataFrame({"market index M": Xall.values @ W, "output-lens market index": Xall.values @ vw, "policy part (=M)": Xall.values @ W,
                        "non-policy part (output lens minus M)": Xall.values @ (vw - W)}, index=Xall.index)
    idx.to_csv(os.path.join(HERE, "mkt_output_index_monthly.csv"), float_format="%.4f", index_label="month")
    j = idx.loc["1990-01":]
    print(f"\nsince 1990: corr(M, output-lens) levels {j.iloc[:, 0].corr(j.iloc[:, 1]):.2f}, 12m {j.iloc[:, 0].diff(12).corr(j.iloc[:, 1].diff(12)):.2f}; sd M {j.iloc[:, 0].std():.2f}, "
          f"output-lens {j.iloc[:, 1].std():.2f}, non-policy part {j.iloc[:, 3].std():.2f}; latest M {j.iloc[-1, 0]:+.2f}, output-lens {j.iloc[-1, 1]:+.2f}")


if __name__ == "__main__":
    main()
