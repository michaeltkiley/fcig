"""Step 16. Calendar position alone (FS-A97; review of 19 Nov 2026, item 13). Real version, monthly equations from 1996, 12 lags, without and with the FCI.
   python3 16_timing.py [--draws 500] [--jobs 4]
The main model with its estimated equations, window impact and bootstrap draws unchanged; only the assumed day of each announcement within its month changes:
  actual: the data's positions (six bins, as lib/model.irf; reproduces step 3);  first: every announcement on the first trading day of its month;
  mid: every announcement at the middle of its month (day n/2 of n trading days).
n is the share-weighted mean number of trading days in the announcement months (of the draw). Same seeds as step 3, so the three are paired draw by draw.
Output: results/timing_only.csv (responses at 12/24/36 m with 90% intervals) and results/timing_only_diff.csv (paired differences: actual less first, mid less first, actual less mid)."""
import os, argparse
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np, pandas as pd
from lib import model as M
from lib.paths import RESULTS

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4); a = ap.parse_args()
def _n(pos): return int(round(sum(w * n0 for _, n0, w in pos) / sum(w for *_, w in pos)))
TIMINGS = {"actual": None, "first": lambda pos: [(0, _n(pos), 1.0)], "mid": lambda pos: [(_n(pos) // 2, _n(pos), 1.0)]}
JOBS = [(t, fci) for t in TIMINGS for fci in (0, "real")]

def work(job):
    t, fci = job; M.use_variant(""); M.POS_OVERRIDE[0] = TIMINGS[t]
    est = next(M.estimate("real", fci, "u,pi", "1996-01", None, "out", "none", a.draws, (12,)))
    return t, fci, est["s0"], est["sd"]

if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(a.jobs) as pool: out = pool.map(work, JOBS)
    R = {(t, f): (s0, sd) for t, f, s0, sd in out}; rows, drows = [], []
    for (t, f), (s0, sd) in R.items():
        for j, v in enumerate(("u", "P")):
            rows.append(dict(timing=t, fci=f, var=v, **{f"r{h}": s0[h, j] for h in M.HORIZ}, **{f"lo{h}": np.percentile(sd[:, h, j], 5) for h in M.HORIZ}, **{f"hi{h}": np.percentile(sd[:, h, j], 95) for h in M.HORIZ},
                             **{f"lo95_{h}": np.percentile(sd[:, h, j], 2.5) for h in M.HORIZ}, **{f"hi95_{h}": np.percentile(sd[:, h, j], 97.5) for h in M.HORIZ}))
    for f in (0, "real"):
        for x, y in (("actual", "first"), ("mid", "first"), ("actual", "mid")):
            (sx, dx), (sy, dy) = R[(x, f)], R[(y, f)]
            for j, v in enumerate(("u", "P")):
                for h in M.HORIZ:
                    d = dx[:, h, j] - dy[:, h, j]; drows.append(dict(fci=f, contrast=f"{x}-{y}", var=v, h=h, diff=sx[h, j] - sy[h, j], lo=np.percentile(d, 5), hi=np.percentile(d, 95)))
    # check: the actual timing reproduces step 3
    for f in (0, "real"):
        old = pd.read_csv(RESULTS / f"real_{f}_upi_1996-01_all_out.csv").query("lags == 12").set_index("var")
        for j, v in enumerate(("u", "P")): assert abs(old.loc[v].r24 - R[("actual", f)][0][24, j]) < 1e-4 and abs(old.loc[v].lo24 - np.percentile(R[("actual", f)][1][:, 24, j], 5)) < 1e-4
    T = pd.DataFrame(rows); T.to_csv(RESULTS / "timing_only.csv", index=False, float_format="%.4f"); D = pd.DataFrame(drows); D.to_csv(RESULTS / "timing_only_diff.csv", index=False, float_format="%.4f")
    print(T[["timing", "fci", "var", "r12", "r24", "lo24", "hi24"]].round(2).to_string(index=False)); print(D[D.h == 24].round(2).to_string(index=False))
