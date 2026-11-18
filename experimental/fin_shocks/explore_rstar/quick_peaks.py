"""Quick read (point estimates, 12 lags): peak-to-peak trend alternatives in every monthly equation, for the package's baseline versions (nominal, real, r*-gap LW),
both baselines, without and with the FCI. Trend options (join points = NBER peaks strictly inside the sample, as in the package's spline):
  none   : no trend (baseline)
  spline : the package's natural cubic spline (continuous, smooth at the peaks)
  lin    : linear spline (trend-through-peaks): t and (t - k)+ for each peak k; continuous, kinked at the peaks
  brk    : broken trend: t, and for each peak k a level shift 1[t > k] and a slope change (t - k) 1[t > k]; jumps and kinks at the peaks
  lvl    : level shifts only: 1[t > k] for each peak (a separate mean in each cycle; no time slope)
Writes quick_peaks.csv/.md."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.argv = [sys.argv[0], "--draws", "2"]
exec(open(HERE / "run_rstar_alt.py").read().split("if __name__")[0])
_orig = M.macro_data
def _cols(P, start, end, kind):
    t = np.array([M._dec(p) for p in P]); a, b = pd.Period(start, "M"), M.last_month(end)
    ks = [pd.Period(k, "M") for k in M.NBER_PEAKS if a < pd.Period(k, "M") < b]; kt = [M._dec(k) for k in ks]
    after = [np.array([p > k for p in P], float) for k in ks]
    if kind == "lin": return np.c_[t, *[np.maximum(t - x, 0) for x in kt]]
    if kind == "brk": return np.c_[t, *after, *[(t - x) * d for x, d in zip(kt, after)]]
    if kind == "lvl": return np.c_[tuple(after)] if after else np.zeros((len(P), 0))
def macro_data(form, fci, mvars, L, start, end, t2020, trend, periods=False):
    if trend not in ("lin", "brk", "lvl"): return _orig(form, fci, mvars, L, start, end, t2020, trend, periods)
    X, Y, P = _orig(form, fci, mvars, L, start, end, t2020, "none", periods=True)
    C = _cols(P, start, end, trend); C = C[:, C.std(axis=0) > 0]                 # a segment with no observations (e.g. inside the dropped 2020 months) is removed
    X = np.c_[X, C]; return (X, Y, P) if periods else (X, Y)
M.macro_data = macro_data
TR = ("none", "spline", "lin", "brk", "lvl"); HS = (12, 24, 36); rows = []
for f, lab in (("nom", "Nominal"), ("real", "Real"), ("rstar", "r*-gap (LW)")):
    for s in ("1996-01", "1973-01"):
        for tr in TR:
            for fci in (0, f):
                for est in M.estimate(f, fci, "u,pi", s, None, "out", tr, 2, lags=(12,)):
                    for j, n in enumerate(est["names"]):
                        rows.append(dict(version=lab, start=s[:4], trend=tr, fci="with FCI" if fci else "no FCI", var=n, nobs=est["nobs"], **{f"r{h}": est["s0"][h, j] for h in HS}))
R = pd.DataFrame(rows); R.to_csv(HERE / "quick_peaks.csv", index=False, float_format="%.4f")
peaks = {s: [k for k in M.NBER_PEAKS if pd.Period(s, "M") < pd.Period(k, "M") < M.last_month(None)] for s in ("1996-01", "1973-01")}
md = ["# Quick read: peak-to-peak trend alternatives (point estimates, 12 lags)", "", "Per +1 pp on the 2-year in the window: u = unemployment gap (pp), P = price level (percent). 2020 (March-December) dropped. "
      f"Join points (NBER peaks inside the sample): from 1996 {', '.join(peaks['1996-01'])}; from 1973 {', '.join(peaks['1973-01'])}. "
      "Trends: none; spline = natural cubic spline (package); lin = linear spline (continuous, kinked); brk = level and slope shift at each peak; lvl = level shift at each peak only.", ""]
for fc in ("with FCI", "no FCI"):
    md += [f"## {fc}", "", "| Start | version | trend | u 12m | u 24m | u 36m | P 12m | P 24m | P 36m |", "|---|---|---|---|---|---|---|---|---|"]
    for s in ("1996", "1973"):
        for v in ("Nominal", "Real", "r*-gap (LW)"):
            for tr in TR:
                g = R[(R.start == s) & (R.version == v) & (R.trend == tr) & (R.fci == fc)]; u = g[g["var"] == "u"].iloc[0]; p = g[g["var"] == "P"].iloc[0]
                md.append(f"| {s} | {v} | {tr} | {u.r12:+.2f} | {u.r24:+.2f} | {u.r36:+.2f} | {p.r12:+.2f} | {p.r24:+.2f} | {p.r36:+.2f} |")
    md.append("")
(HERE / "quick_peaks.md").write_text("\n".join(md)); print("\n".join(md))
