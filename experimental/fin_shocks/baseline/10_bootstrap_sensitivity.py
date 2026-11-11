"""Step 10. The default bootstrap (joint 12-month blocks, recursive monthly lags; lib/model.estimate) against the simple bootstrap in which announcements, monthly residuals (fixed design) and
daily rows (moving blocks of 66 days) are resampled independently (boot="iid"). 12 lags, 500 draws, six cases (nominal, real and r*-gap 2-year yield without and with the FCI).
   python3 10_bootstrap_sensitivity.py [--jobs 4]       Output: results/boot_sens.csv (variant, case, variable, horizon, point, 90% and 95% intervals)"""
import os, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np, pandas as pd
from lib import model as M
from lib.paths import RESULTS
ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--draws", type=int, default=500); a = ap.parse_args()
CASES = [("nom", 0), ("nom", "nom"), ("real", 0), ("real", "real"), ("rstar", 0), ("rstar", "rstar")]
JOBS = [(f, c, v) for f, c in CASES for v in ("j12r", "iid")]
def work(j):
    f, c, v = j; t0 = time.time(); est = next(M.estimate(f, c, boot=v, B=a.draws, lags=(12,))); rows = []
    for k, n in enumerate(est["names"]):
        for h in M.HORIZ:
            s0, sd = est["s0"][h, k], est["sd"][:, h, k]; lo, hi = np.percentile(sd, [5, 95]); lo95, hi95 = np.percentile(sd, [2.5, 97.5])
            rows.append(dict(variant=v, form=f, fci=str(c), var=n, h=h, r=s0, lo=lo, hi=hi, lo95=lo95, hi95=hi95))
    print(f"{f} {c} {v} {time.time() - t0:.0f}s", flush=True); return rows
if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(a.jobs) as pool: out = pool.map(work, JOBS)
    pd.DataFrame([r for o in out for r in o]).to_csv(RESULTS / "boot_sens.csv", index=False, float_format="%.4f")
