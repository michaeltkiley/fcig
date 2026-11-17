"""Part A4: Note B's model with industrial production added as a third monthly variable (u gap, core PCE inflation, IP = 100 x log INDPRO, as the legacy robustness
in fin_shocks/legacy/midas_core.py). IP enters exactly like the other monthly variables: in the monthly equations (own and cross lags, lagged monthly averages of the yield
and FCI) and, this month and last, in the daily block's regressors. Three versions, without and with the FCI, monthly equations from 1973 and from 1996, 12 lags, 500 draws.
Data: experimental/mp_var_fci/data/INDPRO.csv (FRED INDPRO, monthly, 1950-01 to 2026-09; vintage not recorded).
Note B's code is not changed: the column is added to model.MAC in this process only.
   python3 A4_ip.py [--draws 500] [--jobs 4]  -> results_ip/<id>.csv, <id>_paths.csv, results_ip/draws/ (not committed)"""
import os, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, pandas as pd
import lib_r2 as R
import cases as CS          # Note B case naming

HERE = R.Path(__file__).resolve().parent; OUT = HERE / "results_ip"; (OUT / "draws").mkdir(parents=True, exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4); a = ap.parse_args()
ip = pd.read_csv(HERE.parents[1] / "mp_var_fci" / "data" / "INDPRO.csv"); ip = pd.Series(100 * np.log(ip.INDPRO.values), index=pd.PeriodIndex(pd.to_datetime(ip.observation_date), freq="M"))
R.M.MAC["ip"] = ip.reindex(R.M.MAC.index)
CASES = [dict(form=f, fci=x, macro="u,pi,ip", start=s, end=None, t2020="in", trend="none") for s in ("1973-01", "1996-01") for f in ("rstar", "real", "nom") for x in (f, 0)]

def work(c):
    t0 = time.time(); i = CS.case_id(c); sp = CS.spec(c); rows, paths = [], []
    for est in R.M.estimate(c["form"], c["fci"], c["macro"], c["start"], c["end"], c["t2020"], c["trend"], a.draws, (12,)):
        rows += R.M.summary_rows(sp, est); paths.append(R.M.path_rows(sp, est))
        np.savez_compressed(OUT / "draws" / f"{i}_L12.npz", s0=est["s0"], sd=est["sd"], names=est["names"])
    pd.DataFrame(rows).to_csv(OUT / f"{i}.csv", index=False, float_format="%.4f"); pd.concat(paths).to_csv(OUT / f"{i}_paths.csv", index=False, float_format="%.4f")
    return f"{i} done in {time.time() - t0:.0f}s"

if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(a.jobs) as p:
        for m in p.imap_unordered(work, CASES): print(m, flush=True)
