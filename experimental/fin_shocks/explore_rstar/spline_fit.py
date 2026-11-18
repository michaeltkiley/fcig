"""How much does each trend absorb in the two samples? (author's question, 18 Nov 2026: does the spline overfit from 1996?)
For the real case with the FCI, 12 lags, estimation months of Note B's model: (1) R^2 of each variable (u, pi, real 2-year, real FCI) on the trend alone (constant + trend basis);
(2) the increase in R^2 of the u and pi monthly equations when the trend is added to the 12-lag regressors (the share of the remaining variance the trend takes);
(3) the number of trend parameters and knots. Writes spline_fit.md."""
import os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
exec(open(HERE / "real_trends.py").read().split("HS = (6, 12")[0])
def r2(y, X): b = np.linalg.lstsq(X, y, rcond=None)[0]; e = y - X @ b; return 1 - e.var() / y.var()
md = ["# What each trend absorbs (real case with the FCI, 12 lags, Note B's estimation months)", ""]
FB = M.fin_monthly("real", "real")
for start in ("1996-01", "1973-01"):
    X0, Y, P = M._orig_macro if False else _orig("real", "real", ["u", "pi"], 12, start, None, "out", "none", periods=True)
    peaks = [k for k in M.NBER_PEAKS if pd.Period(start, "M") < pd.Period(k, "M") < M.last_month(None)]
    md += [f"## From {start[:4]} ({len(P)} months, {P[0]} to {P[-1]}; NBER peaks inside: {', '.join(peaks)})", "",
           "| trend | parameters | R^2 on trend alone: u | pi | real 2-year | real FCI | added R^2 in the u equation (12 lags) | in the pi equation | share of remaining u variance | of remaining pi variance |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    fin = FB.reindex(P)
    for tr, lab in (("quad", "quadratic"), ("spline", "cubic spline"), ("lvl", "level jumps at peaks")):
        Xt, _, _ = macro_data("real", "real", ["u", "pi"], 12, start, None, "out", tr, periods=True); T = Xt[:, X0.shape[1]:]; C1 = np.c_[np.ones(len(P)), T]
        a = [r2(Y[:, 0], C1), r2(Y[:, 1], C1), r2(fin.pol.values, C1), r2(fin.idx.values, C1)]
        b = []
        for j in (0, 1):
            r0, r1 = r2(Y[:, j], X0), r2(Y[:, j], Xt); b += [r1 - r0, (r1 - r0) / (1 - r0)]
        md.append(f"| {lab} | {T.shape[1]} | {a[0]:.2f} | {a[1]:.2f} | {a[2]:.2f} | {a[3]:.2f} | {b[0]:.3f} | {b[2]:.3f} | {b[1]:.2f} | {b[3]:.2f} |")
    md.append("")
# the fitted spline trend of u and pi alone, by segment: how closely does it follow the cycle?
for start in ("1996-01", "1973-01"):
    Xt, Y, P = macro_data("real", "real", ["u", "pi"], 12, start, None, "out", "spline", periods=True); X0 = _orig("real", "real", ["u", "pi"], 12, start, None, "out", "none")[0]
    C1 = np.c_[np.ones(len(P)), Xt[:, X0.shape[1]:]]; fu = C1 @ np.linalg.lstsq(C1, Y[:, 0], rcond=None)[0]
    md.append(f"From {start[:4]}: correlation of the spline-alone fit of the unemployment gap with the gap itself {np.corrcoef(fu, Y[:, 0])[0, 1]:.2f}; sd of the fit {fu.std():.2f} vs sd of the gap {Y[:, 0].std():.2f}.")
(HERE / "spline_fit.md").write_text("\n".join(md)); print("\n".join(md))
