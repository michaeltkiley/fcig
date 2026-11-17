"""Part A7: Brennan-Jacobson-Matthes-Walker's sample with Note B's exact approach and data (D-A20).
Their VAR: economic data January 1973 to February 2020, shocks 1995-2019. Here: Note B's model unchanged (u gap, core PCE inflation; 2-year yield and FCI in the daily block and
as lagged monthly averages; window-impact identification with the NS surprise; 12 lags; 500 block-bootstrap draws), with the monthly equations from January 1973 and every equation
ending December 2019 (Note B's code ends samples at a year end; their two extra months, January-February 2020, are pre-COVID), and the announcements restricted to 1996-2019
(ours start in January 1996; theirs in 1995). Versions: announcements through 2019 (main) and all 252 announcements (Note B's R1e definition) for the r*-gap pair as a check.
Also from 1996 on the same end, for comparison. Note B's code is not changed: event_index is restricted in this process only.
   python3 A7_bjmw.py [--draws 500] [--jobs 4]  -> results_bjmw/<id>.csv, _paths.csv"""
import os, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, pandas as pd
import lib_r2 as R
import cases as CS
from lib import daily as DD

OUT = R.Path(__file__).resolve().parent / "results_bjmw"; OUT.mkdir(exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4); ap.add_argument("--only-all", action="store_true"); a = ap.parse_args()
_ev_all = DD.event_index
def event_index_2019(): i = _ev_all(); return i[DD.EV.Date.values[i] <= np.datetime64("2019-12-31")]
CASES = [dict(form=f, fci=x, start=s, ann="1996-2019") for s in ("1973-01", "1996-01") for f in ("rstar", "real", "nom") for x in (f, 0)] + \
        [dict(form="rstar", fci=x, start="1973-01", ann="all") for x in ("rstar", 0)]

def work(c):
    t0 = time.time()
    f = event_index_2019 if c["ann"] == "1996-2019" else _ev_all; R.M.event_index = f; DD.event_index = f      # set in every task (pool workers are reused)
    spec = dict(form=c["form"], fci=c["fci"], macro="u,pi", start=c["start"], end=2019, t2020="in", trend="none")
    i = CS.case_id(spec) + ("" if c["ann"] == "all" else "_ann2019"); sp = {**CS.spec(spec), "announcements": c["ann"]}; rows, paths = [], []
    for est in R.M.estimate(spec["form"], spec["fci"], "u,pi", spec["start"], 2019, "in", "none", a.draws, (12,)):
        rows += R.M.summary_rows(sp, est); paths.append(R.M.path_rows(sp, est))
    pd.DataFrame(rows).to_csv(OUT / f"{i}.csv", index=False, float_format="%.4f"); pd.concat(paths).to_csv(OUT / f"{i}_paths.csv", index=False, float_format="%.4f")
    return f"{i} done in {time.time() - t0:.0f}s ({len(R.M.event_index())} announcements)"

if __name__ == "__main__":
    import sys
    only_all = "--only-all" in sys.argv
    from multiprocessing import Pool
    with Pool(a.jobs) as p:
        for m in p.imap_unordered(work, [c for c in CASES if not only_all or c["ann"] == "all"]): print(m, flush=True)
