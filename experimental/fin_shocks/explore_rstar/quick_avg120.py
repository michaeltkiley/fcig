"""Quick read (point estimates, 12 lags, no trend): r* = EWMA 120 of the simple average of the real 2-, 5- and 10-year yields, against LW and EWMA 180 of the real 2-year.
Both baselines, without and with the FCI; responses at 6, 12, 18, 24, 36 months. Writes quick_avg120.csv/.md."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.argv = [sys.argv[0], "--draws", "2"]
exec(open(HERE / "run_rstar_alt.py").read().split("if __name__")[0])
HS = (6, 12, 18, 24, 36); rows = []
print("tracking LW, RMSE 1973-2026 / 1996-2026:", [round(float(np.sqrt(((D0["rstar AVG120"] - D0["rstar LW"]).loc[a:"2026-09"] ** 2).mean())), 2) for a in ("1973-01", "1996-01")])
for f, lab in (("rstar", "LW (baseline)"), ("ew180", "EWMA 180 real 2-year"), ("avg120", "EWMA 120 avg real 2/5/10")):
    for s in ("1996-01", "1973-01"):
        for fci in (0, f):
            for est in M.estimate(f, fci, "u,pi", s, None, "out", "none", 2, lags=(12,)):
                for j, n in enumerate(est["names"]):
                    rows.append(dict(rstar=lab, start=s[:4], fci="with FCI" if fci else "no FCI", var=n, nobs=est["nobs"], **{f"r{h}": est["s0"][h, j] for h in HS}))
R = pd.DataFrame(rows); R.to_csv(HERE / "quick_avg120.csv", index=False, float_format="%.4f")
md = ["# Quick read: r* = EWMA 120 of the average real 2/5/10-year yield (point estimates, 12 lags, no trend)", "", "Per +1 pp on the 2-year in the window. u = unemployment gap (pp), P = price level (percent). 2020 (March-December) dropped.", "",
      "| Start | FCI | r* | " + " | ".join(f"u {h}m" for h in HS) + " | " + " | ".join(f"P {h}m" for h in HS) + " |", "|---|---|---|" + "---|" * (2 * len(HS))]
for (s, fc, r), g in R.groupby(["start", "fci", "rstar"], sort=False):
    u = g[g["var"] == "u"].iloc[0]; p = g[g["var"] == "P"].iloc[0]
    md.append(f"| {s} | {fc} | {r} | " + " | ".join(f"{u[f'r{h}']:+.2f}" for h in HS) + " | " + " | ".join(f"{p[f'r{h}']:+.2f}" for h in HS) + " |")
(HERE / "quick_avg120.md").write_text("\n".join(md)); print("\n".join(md))
