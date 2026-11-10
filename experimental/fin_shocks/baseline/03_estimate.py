"""Step 3. Estimate every case in cases.py (resumable: a case with a results file is skipped unless --force).
   python3 03_estimate.py [--draws 200] [--jobs 4] [--panel B] [--force]
Output per case: results/<id>.csv (responses at 12/24/36 months, 3/6/12 lags), results/<id>_paths.csv (response paths with bands, incl. the 2-year yield and FCI),
output/draws/<id>_L<lags>.npz (bootstrap draws, used by 04_tradeoff.py; not kept in the repository)."""
import os, sys, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np, pandas as pd
import cases as CS
from lib import model as M
from lib.paths import RESULTS, OUT

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=200); ap.add_argument("--jobs", type=int, default=4)
ap.add_argument("--panel"); ap.add_argument("--force", action="store_true"); a = ap.parse_args()
(OUT / "draws").mkdir(exist_ok=True)
jobs = [c for c in CS.unique_cases(a.panel) if a.force or not (RESULTS / f"{CS.case_id(c)}.csv").exists()]
print(f"{len(CS.unique_cases(a.panel))} cases, {len(jobs)} to run", flush=True)

def work(c):
    t0 = time.time(); i = CS.case_id(c); sp = CS.spec(c); rows, paths = [], []
    for est in M.estimate(c["form"], c["fci"], c["macro"], c["start"], c["end"], c["t2020"], c["trend"], a.draws):
        rows += M.summary_rows(sp, est); paths.append(M.path_rows(sp, est))
        np.savez_compressed(OUT / "draws" / f"{i}_L{est['lags']}.npz", s0=est["s0"], sd=est["sd"], f0=est["f0"], fd=est["fd"], names=est["names"])
    pd.DataFrame(rows).to_csv(RESULTS / f"{i}.csv", index=False, float_format="%.4f")
    pd.concat(paths).to_csv(RESULTS / f"{i}_paths.csv", index=False, float_format="%.4f")
    return f"{i} done in {time.time() - t0:.0f}s"

if __name__ == "__main__" and jobs:
    if a.jobs > 1:
        from multiprocessing import Pool
        with Pool(a.jobs) as pool:
            for m in pool.imap_unordered(work, jobs): print(m, flush=True)
    else:
        for c in jobs: print(work(c), flush=True)
