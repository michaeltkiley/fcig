"""Part A3: separate the sample from the data type in the monthly VAR benchmarks: monthly averages and end-of-month values on the same samples (from 1991 and from 1996),
and monthly averages from 1973. 12 lags, 500 draws, cases as A2.   python3 A3_avg_vs_eom.py -> results_core/avg_vs_eom.csv"""
import itertools, sys
sys.argv = [sys.argv[0], "--draws", "500"]
import importlib.util, pandas as pd
from pathlib import Path
spec = importlib.util.spec_from_file_location("a2", Path(__file__).resolve().parent / "A2_monthly.py"); A2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(A2)
def job(args):
    step, wf, (kind, start) = args; return A2.case(step, step if wf else 0, kind, start, 12, 500)
if __name__ == "__main__":
    from multiprocessing import Pool
    jobs = list(itertools.product(("nom", "real", "rstar"), (False, True), (("avg", "1973-01"), ("avg", "1991-01"), ("eom", "1991-01"), ("avg", "1996-01"), ("eom", "1996-01"))))
    with Pool(4) as p: res = p.map(job, jobs)
    pd.DataFrame(sum(res, [])).to_csv(A2.OUT / "avg_vs_eom.csv", index=False, float_format="%.4f"); print("done", len(jobs))
