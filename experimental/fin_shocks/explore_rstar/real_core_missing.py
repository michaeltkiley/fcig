"""The two core robustness tests of Note B's Section 5 that the package runs only for the r*-gap version, run for the real version with the FCI (author, 18 Nov 2026: real as the baseline?):
excess bond premium as a third monthly variable (R3a) and the Bauer-Swanson surprise (R5a); from 1996 and from 1973; the package's specification otherwise (12 lags, 2020 dropped, 500 draws).
Writes results/realcore_<test>_<start>.csv."""
import os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import pandas as pd
from lib import model as M, daily as DD
RES = HERE / "results"; RES.mkdir(exist_ok=True)
JOBS = [(t, s) for t in ("ebp", "bs") for s in ("1996-01", "1973-01")]
def work(j):
    t, s = j; t0 = time.time(); shock = "bs" if t == "bs" else "ns"; macro = "u,pi,ebp" if t == "ebp" else "u,pi"; DD.use_surprise(shock); M.use_variant("")
    sp = dict(form="real", fci="real", macro=macro, start=s, end="", t2020="out", trend="none", shock=shock)
    est = next(M.estimate("real", "real", macro, s, None, "out", "none", 500, lags=(12,)))
    pd.DataFrame(M.summary_rows(sp, est)).to_csv(RES / f"realcore_{t}_{s}.csv", index=False, float_format="%.4f"); return f"{j} {time.time() - t0:.0f}s"
if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(4) as p:
        for m in p.imap_unordered(work, [j for j in JOBS if not (RES / f"realcore_{j[0]}_{j[1]}.csv").exists()]): print(m, flush=True)
