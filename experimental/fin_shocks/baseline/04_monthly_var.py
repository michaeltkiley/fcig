"""Monthly VAR benchmarks (Robustness): standard proxy VAR (P1) and window impact with announcement timing (WE), without and with the FCI, in the three steps,
on the same 1996 sample and the same announcements as the main model (specification and references in lib/monthly.py).
   python3 04_monthly_var.py [--draws 200] [--jobs 4] [--force]
Output: results/monthly_<step>_<fci>.csv (u and price level at 12/24/36 months, 3/6/12 lags, with first-stage F statistics and the estimated impact of the proxy VAR)."""
import os, sys, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import pandas as pd
import cases as CS
from lib import monthly as MO
from lib.paths import RESULTS

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=200); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--force", action="store_true"); a = ap.parse_args()
jobs = [m for m in CS.MONTHLY if a.force or not (RESULTS / f"{CS.monthly_id(m)}.csv").exists()]
print(f"{len(CS.MONTHLY)} systems, {len(jobs)} to run", flush=True)

def work(m):
    t0 = time.time(); pd.DataFrame(MO.run_case(m["step"], m["fci"], CS.MONTHLY_START, a.draws)).to_csv(RESULTS / f"{CS.monthly_id(m)}.csv", index=False, float_format="%.4f")
    return f"{CS.monthly_id(m)} done in {time.time() - t0:.0f}s"

if __name__ == "__main__" and jobs:
    if a.jobs > 1:
        from multiprocessing import Pool
        with Pool(a.jobs) as pool:
            for msg in pool.imap_unordered(work, jobs): print(msg, flush=True)
    else:
        for m in jobs: print(work(m), flush=True)
