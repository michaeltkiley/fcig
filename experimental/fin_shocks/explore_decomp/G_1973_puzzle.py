"""Why are Note B's 1973 results weaker? Point-estimate diagnostics (D-A18).
(1) Regular recursive (Cholesky) monthly VARs in our data: (u gap, core inflation, policy rate), policy rate last, monthly averages, 12 lags; policy rate = funds rate or
    nominal 2-year; samples 1973-2026, 1973-2007, 1984-2007, 1996-2026; responses to a +1 pp policy-rate innovation (and to a one-sd innovation).
(2) Note B's model with the monthly equations estimated on 1973-1995 only and on 1996-2026 only (daily block as in the paper, from 1996), r*-gap and nominal, with and without
    the FCI; responses per +1 pp window surprise.
   python3 G_1973_puzzle.py -> results_core/puzzle_1973.csv"""
import numpy as np, pandas as pd
import lib_r2 as R
from lib.daily import event_index, positions
M, MO = R.M, R.MO
OUT = R.Path(__file__).resolve().parent / "results_core"; rows = []

dff = R.MO  # placeholder to keep names short
ff = pd.read_csv(R.BASE / "data" / "DFF.csv", parse_dates=[0]).set_index("observation_date").DFF; FFM = ff.groupby(ff.index.to_period("M")).mean()
for pol_name, pol in (("funds rate", FFM), ("2-year (nominal)", M.RATEM["nom"])):
    D = M.MAC[["u", "pi"]].join(pol.rename("i"), how="inner").dropna()
    for a, b in (("1973-01", "2026-09"), ("1973-01", "2007-12"), ("1984-01", "2007-12"), ("1996-01", "2026-09")):
        X, Y, per = MO.design(D, 12, a, b); C = np.linalg.lstsq(X, Y, rcond=None)[0]; U = Y - X @ C; S = U.T @ U / (len(Y) - X.shape[1]); T = MO.ma(C, 3, 12)
        ch = np.linalg.cholesky(S)[:, 2]
        for unit, s in (("+1 pp", ch / ch[2]), ("1 sd", ch)):
            rows.append(dict(part="Cholesky VAR", policy=pol_name, sample=f"{a[:4]}-{b[:4]}", spec=unit, **{f"u{h}": MO.row_of(T, "u", h) @ s for h in (12, 24, 36)},
                             **{f"P{h}": MO.row_of(T, "P", h) @ s for h in (12, 24, 36)}, sd_policy=np.sqrt(S[2, 2])))

idx0 = event_index(); pos0 = positions(idx0)
def noteb(form, fci, start, end, L=12):
    mv = ["u", "pi"]; Xd, Yd = M.har_rows(form, fci, mv, None, "in"); Bd = M.har_fit(Xd, Yd, fci)
    X, Y = M.macro_data(form, fci, mv, L, start, end, "in", "none"); C = np.linalg.lstsq(X, Y, rcond=None)[0]
    m, fb, fe, _ = M.irf(Bd, C, 2, Yd.shape[1], L, idx0, pos0, fci); s = M.to_level(m); return s, fb
for form in ("rstar", "nom"):
    for fci in (form, 0):
        for start, end, lab in (("1973-01", None, "1973-2026"), ("1973-01", 1995, "1973-1995"), ("1996-01", None, "1996-2026")):
            s, fb = noteb(form, fci, start, end)
            rows.append(dict(part="Note B model, monthly equations", policy=f"{form}{' + FCI' if fci else ''}", sample=lab, spec="+1 pp window", **{f"u{h}": s[h, 0] for h in (12, 24, 36)},
                             **{f"P{h}": s[h, 1] for h in (12, 24, 36)}))
D = pd.DataFrame(rows); D.to_csv(OUT / "puzzle_1973.csv", index=False, float_format="%.4f"); print(D.round(3).to_string())
