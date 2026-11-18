"""Part A1: Note B's core results (the mixed-frequency model of the paper, unchanged) with the monthly equations from 1973, for all three steps without and with the FCI,
next to the 1996 baseline, on Note B's own code (baseline/lib/model.py, read only). Same specification as the paper: 3/6/12 lags, no trend, 2020 in, 500 block-bootstrap draws;
the seed tag omits the FCI, so each pair without/with the FCI shares draws and differences are paired.
   python3 A1_core.py [--draws 500] [--jobs 4]
Writes results_core/<id>.csv and <id>_paths.csv (as baseline/results) and results_core/draws/<id>_L<lags>.npz (not committed)."""
import os, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np, pandas as pd
import lib_r2 as R
import cases as CS            # noqa: E402 (Note B case naming)

HERE = R.Path(__file__).resolve().parent; OUT = HERE / "results_core"; (OUT / "draws").mkdir(parents=True, exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--force", action="store_true"); a = ap.parse_args()
CASES = [dict(form=f, fci=x, macro="u,pi", start=s, end=None, t2020="in", trend="none") for s in ("1973-01", "1996-01") for f in ("nom", "real", "rstar") for x in (0, f)]

def work(c):
    t0 = time.time(); i = CS.case_id(c); sp = CS.spec(c); rows, paths = [], []
    for est in R.M.estimate(c["form"], c["fci"], c["macro"], c["start"], c["end"], c["t2020"], c["trend"], a.draws):
        rows += R.M.summary_rows(sp, est); paths.append(R.M.path_rows(sp, est))
        np.savez_compressed(OUT / "draws" / f"{i}_L{est['lags']}.npz", s0=est["s0"], sd=est["sd"], f0=est["f0"], fd=est["fd"], e0=est["e0"], names=est["names"],
                            **{k: est[k] for k in ("ord0", "ordd", "s0B", "sdB") if k in est})
    pd.DataFrame(rows).to_csv(OUT / f"{i}.csv", index=False, float_format="%.4f"); pd.concat(paths).to_csv(OUT / f"{i}_paths.csv", index=False, float_format="%.4f")
    return f"{i} done in {time.time() - t0:.0f}s"

if __name__ == "__main__":
    jobs = [c for c in CASES if a.force or not (OUT / f"{CS.case_id(c)}.csv").exists()]
    from multiprocessing import Pool
    with Pool(a.jobs) as p:
        for m in p.imap_unordered(work, jobs): print(m, flush=True)
