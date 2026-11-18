"""Quick read (point estimates, 12 lags, no trend): EWMA 180 r* and LW, with the excess bond premium as a third monthly variable (macro = u,pi,ebp; the package's R3a form), both baselines, without and with the FCI."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.argv = [sys.argv[0], "--draws", "2"]
exec(open(HERE / "run_rstar_alt.py").read().split("if __name__")[0])
rows = []
for f, lab in (("rstar", "LW (baseline)"), ("ew180", "EWMA 180 real 2-year")):
    for macro in ("u,pi", "u,pi,ebp"):
        for s in ("1996-01", "1973-01"):
            for fci in (0, f):
                for est in M.estimate(f, fci, macro, s, None, "out", "none", 2, lags=(12,)):
                    for j, n in enumerate(est["names"]):
                        rows.append(dict(rstar=lab, macro=macro, start=s[:4], fci="with FCI" if fci else "no FCI", var=n, nobs=est["nobs"], **{f"r{h}": est["s0"][h, j] for h in (12, 24, 36)}))
R = pd.DataFrame(rows); R.to_csv(HERE / "quick_ebp.csv", index=False, float_format="%.4f")
md = ["# Quick read: EWMA 180 r* and LW with and without the excess bond premium (point estimates, 12 lags, no trend)", "",
      "Per +1 pp on the 2-year in the window: unemployment gap (pp), price level (percent), EBP (pp). 2020 (March-December) dropped.", "",
      "| Start | FCI | r* | monthly variables | nobs | u 12m | u 24m | P 12m | P 24m | EBP 12m |", "|---|---|---|---|---|---|---|---|---|---|"]
for (s, fc, r, mc), g in R.groupby(["start", "fci", "rstar", "macro"], sort=False):
    u = g[g["var"] == "u"].iloc[0]; p = g[g["var"] == "P"].iloc[0]; e = g[g["var"] == "ebp"]
    md.append(f"| {s} | {fc} | {r} | {mc} | {u.nobs} | {u.r12:+.2f} | {u.r24:+.2f} | {p.r12:+.2f} | {p.r24:+.2f} | " + (f"{e.iloc[0].r12:+.2f} |" if len(e) else "- |"))
(HERE / "quick_ebp.md").write_text("\n".join(md)); print("\n".join(md))
