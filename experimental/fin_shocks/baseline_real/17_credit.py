"""Step 17. Credit and the FCI, matched (FS-A98; review of 19 Nov 2026, item 14). Real version, 12 lags, monthly equations from 1996 and from 1973, March-December 2020 dropped.
   python3 17_credit.py [--draws 500] [--jobs 4]
Each credit specification without and with the FCI, all on the bootstrap months of the baseline (seed_macro = "u,pi"), so every comparison is paired:
  base: the baseline (u, pi);  ebp: the excess bond premium as a third monthly variable;  ip: industrial production as a third monthly variable;  ebpip: both (robustness test R2);
  baa: the daily Baa-10-year spread in the daily block (without the FCI: fci = "baa0", the 2-year yield, the spread and the funds rate; with: fci = "baa"); months before the daily
  Baa data (1986) use Moody's monthly Baa less GS10.
Output: results/credit_cases.csv (responses at 12/24/36 m with 90% intervals) and results/credit_diff.csv (the effect of adding the FCI in each specification, and that effect less the baseline's)."""
import os, argparse
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np, pandas as pd
from lib import model as M
from lib.paths import RESULTS

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4); a = ap.parse_args()
SPECS = {"base": ("u,pi", 0, "real"), "ebp": ("u,pi,ebp", 0, "real"), "ip": ("u,pi,ip", 0, "real"), "ebpip": ("u,pi,ebp,ip", 0, "real"), "baa": ("u,pi", "baa0", "baa")}
STARTS = ("1996-01", "1973-01")
JOBS = [(k, st, w) for k in SPECS for st in STARTS for w in ("no", "yes")]

def work(job):
    k, st, w = job; macro, f0, f1 = SPECS[k]; M.use_variant("")
    est = next(M.estimate("real", f0 if w == "no" else f1, macro, st, None, "out", "none", a.draws, (12,), seed_macro="u,pi"))
    return job, est["s0"][:, :2], est["sd"][:, :, :2], est["nobs"]          # unemployment gap and price level (the first two macro variables)

if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(a.jobs) as pool: out = pool.map(work, JOBS)
    R = {j: (s0, sd, n) for j, s0, sd, n in out}; rows, drows = [], []
    for (k, st, w), (s0, sd, n) in R.items():
        for j, v in enumerate(("u", "P")):
            rows.append(dict(spec=k, start=st, fci=w, var=v, nobs=n, **{f"r{h}": s0[h, j] for h in M.HORIZ}, **{f"lo{h}": M.IV.ci(sd[:, h, j], s0[h, j])[0] for h in M.HORIZ},
                             **{f"hi{h}": M.IV.ci(sd[:, h, j], s0[h, j])[1] for h in M.HORIZ}))
    for st in STARTS:
        inc = {k: (R[(k, st, "yes")][0] - R[(k, st, "no")][0], R[(k, st, "yes")][1] - R[(k, st, "no")][1]) for k in SPECS}
        for k in SPECS:
            for j, v in enumerate(("u", "P")):
                for h in M.HORIZ:
                    x, xd = inc[k][0][h, j], inc[k][1][:, h, j]; y, yd = inc["base"][0][h, j], inc["base"][1][:, h, j]
                    drows.append(dict(spec=k, start=st, var=v, h=h, fci_effect=x, lo=M.IV.ci(xd, x)[0], hi=M.IV.ci(xd, x)[1],
                                      vs_base=x - y, vs_lo=M.IV.ci(xd - yd, x - y)[0], vs_hi=M.IV.ci(xd - yd, x - y)[1]))
    base_old = pd.read_csv(RESULTS / "real_real_upi_1996-01_all_out.csv").query("lags == 12").set_index("var")
    assert abs(base_old.loc["u"].r24 - R[("base", "1996-01", "yes")][0][24, 0]) < 1e-4 and abs(base_old.loc["u"].lo24 - M.IV.ci(R[("base", "1996-01", "yes")][1][:, 24, 0], R[("base", "1996-01", "yes")][0][24, 0])[0]) < 1e-4    # the baseline reproduces step 3
    C = pd.DataFrame(rows); C.to_csv(RESULTS / "credit_cases.csv", index=False, float_format="%.4f"); D = pd.DataFrame(drows); D.to_csv(RESULTS / "credit_diff.csv", index=False, float_format="%.4f")
    print(C[C["var"] == "u"][["spec", "start", "fci", "nobs", "r12", "r24", "lo24", "hi24"]].round(2).to_string(index=False))
    print(C[C["var"] == "P"][["spec", "start", "fci", "r24", "lo24", "hi24"]].round(2).to_string(index=False))
    print(D[D.h == 24].round(2).to_string(index=False))
