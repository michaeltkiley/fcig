"""Note B's model, real case (real 2-year, real FCI), 12 lags, from 1996 and from 1973, under four trend treatments in every monthly equation (point estimates; author, 18 Nov 2026):
  none   : no trend (the package's real baseline)
  quad   : quadratic time trend (t, t^2)
  spline : the package's natural cubic spline (knots at the sample ends and the NBER peaks inside the sample)
  spl74  : the cubic spline with its first knot at the first estimation month (from 1973: 1974-01, so the 1973-11 peak drops out; from 1996: identical to spline)
  lvl    : constant within each cycle, level jump at each NBER peak inside the sample (1[t > peak])
Without and with the FCI. March-December 2020 dropped. Writes real_trends.md, real_trends.csv."""
import os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from lib import model as M
_orig = M.macro_data
def macro_data(form, fci, mvars, L, start, end, t2020, trend, periods=False):
    if trend not in ("quad", "lvl", "spl74"): return _orig(form, fci, mvars, L, start, end, t2020, trend, periods)
    X, Y, P = _orig(form, fci, mvars, L, start, end, t2020, "none", periods=True); t = np.array([M._dec(p) for p in P])
    if trend == "quad": C = np.c_[t, t ** 2]
    elif trend == "spl74": C = M.trend_cols(P, str(P[0]), end)          # the package's natural spline with its first knot at the first estimation month (1974-01 from 1973; unchanged from 1996)
    else:
        a, b = pd.Period(start, "M"), M.last_month(end)
        C = np.column_stack([np.array([p > pd.Period(k, "M") for p in P], float) for k in M.NBER_PEAKS if a < pd.Period(k, "M") < b]); C = C[:, C.std(axis=0) > 0]
    X = np.c_[X, C]; return (X, Y, P) if periods else (X, Y)
M.macro_data = macro_data
HS = (6, 12, 18, 24, 36); TR = {"none": "no trend", "quad": "quadratic", "spline": "cubic spline", "lvl": "level jumps at peaks"}; rows = []
for start in ("1996-01", "1973-01"):
    for fci in ("real", 0):
        for tr in TR:
            est = next(M.estimate("real", fci, "u,pi", start, None, "out", tr, 2, lags=(12,)))
            for j, v in enumerate(est["names"]): rows.append(dict(start=start[:4], fci="with FCI" if fci else "no FCI", trend=TR[tr], var=v, **{f"r{h}": est["s0"][h, j] for h in HS}))
R = pd.DataFrame(rows); R.to_csv(HERE / "real_trends.csv", index=False, float_format="%.4f")
md = ["# Real case under four trend treatments (Note B's model, 12 lags, point estimates)", "", "Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent). 2020 (March-December) dropped.", ""]
for fc in ("with FCI", "no FCI"):
    md += [f"## {fc}", "", "| start | trend | " + " | ".join(f"u {h}m" for h in HS) + " | " + " | ".join(f"P {h}m" for h in HS) + " |", "|---|---|" + "---|" * 10]
    for (s, tr), g in R[R.fci == fc].groupby(["start", "trend"], sort=False):
        q = g.set_index("var"); md.append(f"| {s} | {tr} | " + " | ".join(f"{q.loc['u', f'r{h}']:+.2f}" for h in HS) + " | " + " | ".join(f"{q.loc['P', f'r{h}']:+.2f}" for h in HS) + " |")
    md.append("")
(HERE / "real_trends.md").write_text("\n".join(md)); print("\n".join(md))
