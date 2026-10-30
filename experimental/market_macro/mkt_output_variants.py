"""
Variants of mkt_output.py (same w, psi, equation, controls, HAC):
    (i)  flows: regressors are 12-month changes of M, n_eq, n_usd (the FCI-G-like flow form); dependent u(t+h) - u(t-1)
    (ii) real 10-year: x uses the 10-year less 12-month core PCE inflation (expected inflation proxy available from 1973), levels
    (iii) real 10-year, flows
Samples 1973-2025 and 1990-2025, excluding 2020. Reports a, b, the joint test b = 0, and output-lens weights v/a (market-index units).
Usage: python experimental/market_macro/mkt_output_variants.py
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkt_output as MO
LL, V = MO.LL, MO.V


def build(real):
    F = LL.financial()[MO.VARS].copy()
    Mm = V.macro_data(False)
    if real:
        F["10-year"] = F["10-year"] - (Mm["inflation gap"] + 2.0).reindex(F.index)
    base = F.loc["1973-01":"2025-12"]
    base = base[[t.year != 2020 for t in base.index]]
    X = (F.loc["1973-01":] - base.mean()).dropna()
    M = X.values @ MO.W
    N = X.values - np.outer(M, MO.PSI)
    D = pd.DataFrame({"M": M, "n_eq": N[:, 1], "n_usd": N[:, 2]}, index=X.index)
    return D.join(Mm.rename(columns={"unemployment gap": "u", "inflation gap": "pi"}), how="left"), X


def fit(D, h, start, end, flows):
    du = D.u.diff()
    R = D[["M", "n_eq", "n_usd"]].diff(12) if flows else D[["M", "n_eq", "n_usd"]]
    cols = {"y": D.u.shift(-h) - D.u.shift(1), **{c: R[c] for c in R}, "u1": D.u.shift(1), "pi1": D.pi.shift(1), **{f"du{l}": du.shift(l) for l in (1, 2, 3)}}
    for v in ("M", "n_eq", "n_usd"):
        for l in (1, 2, 3):
            cols[f"d{v}{l}"] = D[v].diff().shift(l)
    Z = pd.concat(cols, axis=1).loc[start:end]
    Z = Z[[t.year != 2020 for t in Z.index]].dropna()
    return sm.OLS(Z.y, sm.add_constant(Z.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": max(h, 1)}), len(Z)


def main():
    pd.set_option("display.width", 230)
    rows = []
    for lab, real, flows in (("(i) nominal, 12m flows", False, True), ("(ii) real 10y, levels", True, False), ("(iii) real 10y, 12m flows", True, True)):
        D, X = build(real)
        for start, end, slab in (("1973-07", "2025-12", "1973-2025"), ("1990-01", "2025-12", "1990-2025")):
            for h in (6, 12, 24):
                r, n = fit(D, h, start, end, flows)
                a = r.params["M"]; b = np.array([0.0, r.params["n_eq"], r.params["n_usd"]])
                v = a * MO.W + b - (b @ MO.PSI) * MO.W
                p = float(r.wald_test("n_eq = 0, n_usd = 0", scalar=True).pvalue)
                rows.append(dict(variant=lab, sample=slab, h=h, n=n, a=a, a_t=a / r.bse["M"], output_eq=-2 * a, b_eq=b[1], b_eq_t=b[1] / r.bse["n_eq"], b_usd=b[2], b_usd_t=b[2] / r.bse["n_usd"],
                                 p_b0=p, **{f"v/a {k}": v[i] / a for i, k in enumerate(MO.VARS)}))
    R = pd.DataFrame(rows)
    print(R.round(4).to_string(index=False))
    R.to_csv(os.path.join(HERE, "mkt_output_variants.csv"), float_format="%.5f", index=False)
    print("\nmarket w: " + ", ".join(f"{k} {MO.W[i]:+.4f}" for i, k in enumerate(MO.VARS)) + " | FRB/US s: " + ", ".join(f"{k} {MO.S_FRB[i]:+.4f}" for i, k in enumerate(MO.VARS)))


if __name__ == "__main__":
    main()
