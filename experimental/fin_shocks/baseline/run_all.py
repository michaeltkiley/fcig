"""Run every case in cases.py (resumable: a case with a results file is skipped unless --force).
   python3 run_all.py [--draws 200] [--jobs 4] [--panel B] [--force] [--list]
One CSV per case in results/. Needs statsmodels, scipy, pandas, openpyxl; the data are in the repo (see ../README.md)."""
import os, sys, argparse
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cases as CS
ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=200); ap.add_argument("--jobs", type=int, default=4)
ap.add_argument("--panel"); ap.add_argument("--force", action="store_true"); ap.add_argument("--list", action="store_true"); a = ap.parse_args()
todo = [c for p in CS.PANELS if (not a.panel or p["id"] == a.panel) for c in p["cases"]]
seen, jobs = set(), []
for c in todo:
    i = CS.case_id(c)
    if i in seen: continue
    seen.add(i)
    if a.force or not os.path.exists(os.path.join(HERE, "results", i + ".csv")): jobs.append(c)
print(f"{len(todo)} cases requested, {len(jobs)} to run")
if a.list or not jobs: sys.exit()
import engine as E, pandas as pd, time
def work(c):
    t0 = time.time(); i = CS.case_id(c)
    pd.DataFrame(E.run_case(c["form"], c["fci"], c["macro"], c["start"], c["end"], c["t2020"], a.draws)).to_csv(os.path.join(HERE, "results", i + ".csv"), index=False, float_format="%.4f")
    return f"{i} done in {time.time() - t0:.0f}s"
if a.jobs > 1:
    from multiprocessing import Pool
    with Pool(a.jobs) as pool:
        for m in pool.imap_unordered(work, jobs): print(m, flush=True)
else:
    for c in jobs: print(work(c), flush=True)
