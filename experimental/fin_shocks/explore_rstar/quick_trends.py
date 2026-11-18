"""Quick read (point estimates only, no bootstrap): the 8-year moving-average r* cases (real, nominal) and LW for reference, both baselines, with and without the FCI,
under three trend treatments in the monthly equations: none (baseline), natural cubic spline (the package's: knots at sample ends and NBER peaks), quadratic (t, t^2).
12 lags only. Writes quick_trends.csv and quick_trends.md."""
import sys, os
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], "--draws", "2"]
exec(open(HERE / "run_rstar_alt.py").read().split("if __name__")[0])          # sets up the r* measures in lib.model (M)
_orig = M.macro_data
def macro_data(form, fci, mvars, L, start, end, t2020, trend, periods=False):
    if trend != "quad": return _orig(form, fci, mvars, L, start, end, t2020, trend, periods)
    X, Y, P = _orig(form, fci, mvars, L, start, end, t2020, "none", periods=True)
    t = np.array([M._dec(p) for p in P]); X = np.c_[X, t, t ** 2]
    return (X, Y, P) if periods else (X, Y)
M.macro_data = macro_data
rows = []
import os as _os
_SETS = {"ma8": (("rstar", "LW (baseline)"), ("ma8", "MA8 real 2-year"), ("nma8", "MA8 nominal 2-year")), "fwd": (("fwd", "Forward 9-10y less e10"),),
         "ew": (("rstar", "LW (baseline)"), ("ew180", "EWMA 180 real 2-year")), "hp": (("hp129600", "HP one-sided, q1600 (m129600), real"), ("hp1296000", "HP one-sided, q16000 (m1296000), real"), ("nhp129600", "HP one-sided, q1600 (m129600), nominal"), ("nhp1296000", "HP one-sided, q16000 (m1296000), nominal"))}
_SET = _os.environ.get("QT_SET", "ma8"); _SFX = "" if _SET == "ma8" else "_" + _SET
for f, lab in _SETS[_SET]:
    for s in ("1996-01", "1973-01"):
        for tr in ("none", "spline", "quad"):
            for fci in (0, f):
                for est in M.estimate(f, fci, "u,pi", s, None, "out", tr, 2, lags=(12,)):
                    for j, n in enumerate(est["names"]):
                        rows.append(dict(rstar=lab, start=s[:4], trend=tr, fci="with FCI" if fci else "no FCI", lags=est["lags"], var=n, nobs=est["nobs"],
                                         **{f"r{h}": est["s0"][h, j] for h in (12, 24, 36)}))
                print(lab, s, tr, fci, flush=True)
R = pd.DataFrame(rows); R.to_csv(HERE / f"quick_trends{_SFX}.csv", index=False, float_format="%.4f")
md = ["# Quick read: 8-year moving-average r* under three trend treatments (point estimates, no bootstrap)", "",
      "Per +1 pp on the 2-year in the window: unemployment gap (pp), price level (percent). 2020 (March-December) dropped. Point estimates only; no intervals.", ""]
for L in (12,):
    T = R[R.lags == L].copy()
    md += [f"## {L} lags", "", "| Start | FCI | r* | trend | u 12m | u 24m | P 12m | P 24m |", "|---|---|---|---|---|---|---|---|"]
    for (s, fc, r, tr), g in T.groupby(["start", "fci", "rstar", "trend"], sort=False):
        u = g[g["var"] == "u"].iloc[0]; p = g[g["var"] == "P"].iloc[0]
        md.append(f"| {s} | {fc} | {r} | {tr} | {u.r12:+.2f} | {u.r24:+.2f} | {p.r12:+.2f} | {p.r24:+.2f} |")
    md.append("")
(HERE / f"quick_trends{_SFX}.md").write_text("\n".join(md)); print("\n".join(md[:45]))
