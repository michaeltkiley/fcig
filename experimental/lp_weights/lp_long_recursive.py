"""
E7 (exploration, 29 Oct 2026): local projections on the long sample (1973-2025, 2020 excluded) with a recursive funds-rate shock, as the LP counterpart of the
1973 recursive VAR (the one VAR yardstick with the right sign).
    Data (monthly averages, as mf_var_us_long.py): core PCE inflation gap, unemployment gap; policy rate, 10-year, mortgage spread, Baa spread, 100 ln CAPE,
    100 ln real broad dollar (demeaned).
    Shock: residual of the funds rate on current inflation and unemployment gaps and 12 lags of all variables (recursive: macro first, funds rate next).
    Yardstick g_h: LP of the unemployment gap on the shock, scaled to a 1 pp funds-rate impact, controls 12 lags of all variables (h = 0..36).
        Also: the funds rate's own path after the shock (it is not held +1 for 12 months here; a plain LP impulse response).
    theta: predictive LP of u(t+12) - u(t-1) on all financial levels at t, controls: current macro, 12 lags of all variables (partial association, not causal).
    weights = theta_j / (output yardstick per 1 pp funds rate): an "LP macro-model" weighting with an LP yardstick.
Usage: python experimental/lp_weights/lp_long_recursive.py
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "fci_compare"))
import mf_var_us_long as LL
import mf_var_us as V

FIN = ["policy rate", "10-year", "mortgage spread", "Baa spread", "equities", "dollar"]
NL = 12


def main():
    F = LL.financial()[FIN]
    M = V.macro_data(False)
    D = pd.concat([M, F], axis=1).loc["1972-01":"2025-12"].dropna()
    D[FIN] = D[FIN] - D[FIN].mean()
    lags = pd.concat({f"{c}_l{l}": D[c].shift(l) for c in D for l in range(1, NL + 1)}, axis=1)
    keep = lambda idx: np.array([t.year != 2020 for t in idx]) & np.array([t >= pd.Period("1973-01", "M") for t in idx])
    # recursive shock
    Xs = pd.concat([D[["inflation gap", "unemployment gap"]], lags], axis=1)
    Z = pd.concat([D["policy rate"].rename("ffr"), Xs], axis=1).dropna(); Z = Z[keep(Z.index)]
    r = sm.OLS(Z.ffr, sm.add_constant(Z.drop(columns="ffr"))).fit()
    shock = r.resid
    print(f"recursive funds-rate shock: {len(shock)} months, sd {shock.std():.3f} pp")
    rows = []
    for h in (0, 3, 6, 12, 18, 24, 36):
        Y = pd.concat({"u": D["unemployment gap"].shift(-h) - D["unemployment gap"].shift(1), "ffr": D["policy rate"].shift(-h) - D["policy rate"].shift(1)}, axis=1)
        J = pd.concat([Y, shock.rename("e"), lags, D[["inflation gap", "unemployment gap"]].add_prefix("c_")], axis=1).dropna(); J = J[keep(J.index)]
        Xr = sm.add_constant(J.drop(columns=["u", "ffr"]))
        ru = sm.OLS(J.u, Xr).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1)})
        rf = sm.OLS(J.ffr, Xr).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1)})
        rows.append(dict(h=h, u=ru.params.e, u_se=ru.bse.e, ffr=rf.params.e, ffr_se=rf.bse.e))
    G = pd.DataFrame(rows)
    print("\nLP responses to a recursive funds-rate shock of 1 pp (impact):")
    print(G.round(3).to_string(index=False))
    cum = G.set_index("h")
    # theta: predictive LP at h = 12
    Y = (D["unemployment gap"].shift(-12) - D["unemployment gap"].shift(1)).rename("y")
    J = pd.concat([Y, D[FIN], D[["inflation gap", "unemployment gap"]].add_prefix("c_"), lags], axis=1).dropna(); J = J[keep(J.index)]
    rt = sm.OLS(J.y, sm.add_constant(J.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    th = rt.params[FIN]
    print("\ntheta (u pp at 12 months per unit level of x_t, given 12 lags of everything; se): " + ", ".join(f"{c} {th[c]:+.4f} ({rt.bse[c]:.4f})" for c in FIN))
    g12 = float(cum.loc[12, "u"])
    print(f"yardstick: u at 12 months per 1 pp funds-rate shock {g12:+.3f} (output equivalent {-2 * g12:+.3f}%; FRB/US -0.45%); funds rate itself at 12 months {cum.loc[12, 'ffr']:+.2f}")
    if g12 > 0:
        w = th / g12
        print("weights theta_j / yardstick (pp of funds rate per unit): " + ", ".join(f"{c} {w[c]:+.3f}" for c in FIN))
        idx = (D[FIN] * w).sum(axis=1)
        print(f"index: sd {idx.std():.2f}, latest {idx.iloc[-1]:+.2f}")
        pd.DataFrame({"theta": th, "se": rt.bse[FIN], "weight": w}).to_csv(os.path.join(HERE, "lp_long_recursive_weights.csv"), float_format="%.5f")
        idx.to_csv(os.path.join(HERE, "lp_long_recursive_index.csv"), float_format="%.4f", index_label="month", header=["index"])
    else:
        print("yardstick has the wrong sign; weights not computed")


if __name__ == "__main__":
    main()
