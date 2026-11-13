"""Step 2. Stage 1: Note B's panel B by the state-space model (kf/noteb.py) and the comparison with Note B's stored results.
Cases: nominal, real, r*-gap 2-year yield, each without and with the FCI of the same step; 3, 6, 12 lags; 1996-2026; 500 draws of the block bootstrap.
Writes results/stage1_<form>_<fci>.csv (Note B's summary format), results/stage1_<form>_<fci>_paths.csv, results/stage1_vs_noteb.csv, results/stage1_checks.csv."""
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ.setdefault(_v, "1")      # one BLAS thread per worker (4 workers)
from multiprocessing import Pool
import numpy as np, pandas as pd
from kf import noteb as N
from kf.inputs import RES, ROOT

B = int(sys.argv[1]) if len(sys.argv) > 1 else 500
CASES = [(f, k) for f in ("nom", "real", "rstar") for k in (0, f)]
LAGS = (3, 6, 12); HZ = (12, 24, 36)
NB = ROOT.parent / "fin_shocks" / "baseline" / "results"


def run(job):
    form, fci, L = job; r = N.estimate(form, fci, L, B); pc = lambda a, q: np.percentile(a, q, axis=0)
    summ = []; paths = []
    for j, v in enumerate(("u", "P")):
        s0, sd = r["s0"][:, j], r["sd"][:, :, j]
        summ.append(dict(form=form, fci=fci, lags=L, var=v, nobs=r["nobs"], draws=B, **{f"r{h}": s0[h] for h in HZ},
                         **{f"lo{h}": pc(sd, 5)[h] for h in HZ}, **{f"hi{h}": pc(sd, 95)[h] for h in HZ},
                         **{f"lo68_{h}": pc(sd, 16)[h] for h in HZ}, **{f"hi68_{h}": pc(sd, 84)[h] for h in HZ}))
        paths.append(pd.DataFrame(dict(form=form, fci=fci, lags=L, kind="macro", var=v, h=np.arange(N.H + 1), r=s0, lo=pc(sd, 5), hi=pc(sd, 95))))
    for j, v in enumerate(["pol", "idx"][:r["f0"].shape[1]]):
        paths.append(pd.DataFrame(dict(form=form, fci=fci, lags=L, kind="fin", var=v, h=np.arange(N.H + 1), r=r["f0"][:, j], lo=pc(r["fd"][:, :, j], 5), hi=pc(r["fd"][:, :, j], 95))))
    c = r["checks"]; chk = dict(form=form, fci=fci, lags=L, ndays=r["ndays"], nmonths=r["nobs"], em_vs_ols_monthly=c["em_vs_ols_m"], em_vs_ols_daily=c["em_vs_ols_d"],
                                loglik_kalman=c["kf_ll"], loglik_closed_form=c["closed_ll"], loglik_start=c["em_path"][0], loglik_em_step1=c["em_path"][1])
    return pd.DataFrame(summ), pd.concat(paths), chk


if __name__ == "__main__":
    RES.mkdir(exist_ok=True)
    jobs = [(f, k, L) for f, k in CASES for L in LAGS]
    with Pool(4) as p: out = p.map(run, jobs)
    S = pd.concat([o[0] for o in out]); Pth = pd.concat([o[1] for o in out]); C = pd.DataFrame([o[2] for o in out])
    for f, k in CASES:
        S[(S.form == f) & (S.fci == k)].to_csv(RES / f"stage1_{f}_{k}.csv", index=False, float_format="%.4f")
        Pth[(Pth.form == f) & (Pth.fci == k)].to_csv(RES / f"stage1_{f}_{k}_paths.csv", index=False, float_format="%.6f")
    C.to_csv(RES / "stage1_checks.csv", index=False)
    # comparison with Note B
    rows = []
    for f, k in CASES:
        nb = pd.read_csv(NB / f"{f}_{k}_upi_1996-01_all_in.csv"); nbp = pd.read_csv(NB / f"{f}_{k}_upi_1996-01_all_in_paths.csv")
        for L in LAGS:
            for v in ("u", "P"):
                a = S[(S.form == f) & (S.fci == k) & (S.lags == L) & (S["var"] == v)].iloc[0]; b = nb[(nb.lags == L) & (nb["var"] == v)].iloc[0]
                pa = Pth[(Pth.form == f) & (Pth.fci == k) & (Pth.lags == L) & (Pth.kind == "macro") & (Pth["var"] == v)].set_index("h")
                pb = nbp[(nbp.lags == L) & (nbp.kind == "macro") & (nbp["var"] == v)].set_index("h")
                rows.append(dict(form=f, fci=k, lags=L, var=v, path_point_maxdiff=float((pa.r - pb.r).abs().max()), path_lo_maxdiff=float((pa.lo - pb.lo).abs().max()),
                                 path_hi_maxdiff=float((pa.hi - pb.hi).abs().max()), **{f"{q}{h}_kf": a[f"{q}{h}"] for q in ("r", "lo", "hi") for h in HZ},
                                 **{f"{q}{h}_noteb": b[f"{q}{h}"] for q in ("r", "lo", "hi") for h in HZ}))
    R = pd.DataFrame(rows); R.to_csv(RES / "stage1_vs_noteb.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 200)
    print(C[["form", "fci", "lags", "em_vs_ols_monthly", "em_vs_ols_daily", "loglik_kalman", "loglik_closed_form"]].to_string(index=False))
    print(R[["form", "fci", "lags", "var", "path_point_maxdiff", "path_lo_maxdiff", "path_hi_maxdiff"]].to_string(index=False))
    print(f"largest path differences, all cases: point {R.path_point_maxdiff.max():.1e}, 5th pct {R.path_lo_maxdiff.max():.1e}, 95th pct {R.path_hi_maxdiff.max():.1e} (Note B paths stored to 4 decimals)")
