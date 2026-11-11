"""Step 10. Sensitivity of the intervals to the bootstrap scheme: daily block length (22, 66, 132), monthly residuals in blocks of 12 months, recursive monthly lags, and joint resampling
of months (residuals, daily rows, announcements). 12 lags, 500 draws; variants in lib/bootsens.py.   python3 10_bootstrap_sensitivity.py [--jobs 4]
Output: results/boot_sens.csv (variant, case, variable, horizon, point, 90% interval, significance) and results/boot_sens_mult.csv (Phillips multiplier, r*-gap with FCI)."""
import os, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import pandas as pd
from lib import bootsens as BS, model as M
from lib.paths import RESULTS
ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--draws", type=int, default=500); a = ap.parse_args()
CASES = [("nom", 0), ("nom", "nom"), ("real", 0), ("real", "real"), ("rstar", 0), ("rstar", "rstar")]
JOBS = [(f, c, v) for f, c in CASES for v in BS.VARIANTS]
def work(j):
    f, c, v = j; t0 = time.time(); est = BS.estimate(f, c, v, a.draws); rows = []; mult = []
    for k, n in enumerate(est["names"]):
        for h in M.HORIZ:
            s0, sd = est["s0"][h, k], est["sd"][:, h, k]; lo, hi = pd.Series(sd).quantile([.05, .95])
            rows.append(dict(variant=v, form=f, fci=str(c), var=n, h=h, r=s0, lo=lo, hi=hi, sig=int(lo * hi > 0)))
    if (f, c) == ("rstar", "rstar"): mult = M.multiplier_rows(dict(variant=v, form=f, fci=str(c)), est)
    print(f"{f} {c} {v} {time.time() - t0:.0f}s", flush=True); return rows, mult
if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(a.jobs) as pool: out = pool.map(work, JOBS)
    pd.DataFrame([r for o in out for r in o[0]]).to_csv(RESULTS / "boot_sens.csv", index=False, float_format="%.4f")
    pd.DataFrame([r for o in out for r in o[1]]).to_csv(RESULTS / "boot_sens_mult.csv", index=False, float_format="%.4f")
