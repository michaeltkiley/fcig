"""Part A2: Note B's monthly VAR benchmarks (Table 4: proxy VAR P1 and window-impact VAR WE; Table 2: recursive Cholesky VAR) from 1973 in monthly averages (main, D-A2)
and from 1990 in end-of-month values (check), next to the paper's end-of-month 1996 versions. Same systems as baseline/lib/monthly.py: (u gap, core PCE inflation, 2-year yield [, FCI])
in each step, 3/6/12 lags, no trend, 2020 in.
  P1  impact column from the first stage on the month's sum of policy news (instrument months 1996-2026); 90% Anderson-Rubin sets (MO.ar_set, HC1), as in the paper.
  WE  impact column (0, 0, r_i, r_F): Note B's model's response of the month's average (avg) or end-of-month value (eom) of the yield and FCI, per +1 pp window surprise.
  CH  recursive VAR, yield ordered last (without the FCI only; paper's standard method), per +1 pp innovation in the yield measure.
Units: WE per +1 pp in the window. P1 is reported per +1 pp in the window too: the first-stage column is scaled so that its yield entry equals WE's (end of month: within 5% of
the paper's unit, +1 pp on the end-of-month yield; monthly averages: a window move of 1 pp raises the month's average by 0.47-0.49, so the paper's per-yield unit would double the numbers).
Bootstrap (WE, CH): 500 draws, moving blocks of 12 months, pre-1996 and post-1996 rows drawn separately, the VAR rebuilt recursively; WE's FCI entry rescaled by the window ratio
of the drawn months' announcements (as lib/monthly.py).
   python3 A2_monthly.py [--draws 500]  -> results_core/monthly_benchmarks.csv"""
import argparse, itertools, zlib, os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, pandas as pd
import lib_r2 as R
from lib.daily import EV, event_index

MO, M = R.MO, R.M
OUT = R.Path(__file__).resolve().parent / "results_core"; OUT.mkdir(exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); a = ap.parse_args()
TARGETS = MO.TARGETS
idx0 = event_index(); ev = EV.iloc[idx0]; evm = ev.Date.dt.to_period("M").values
POST = pd.Period("1996-01", "M")

def blocks(idx, n, rng, length=12):
    nb = -(-n // length); st = rng.integers(0, len(idx) - length + 1, nb); return np.concatenate([idx[s:s + length] for s in st])[:n]

def case(step, fci, kind, start, L, B):
    D = R.data(step, fci, kind, start); K = D.shape[1]
    X, Y, per, keep = R.design(D, L, "in"); C, U, S = R.fit(X, Y, keep); T = MO.ma(C, K, L)
    win = R.window_column(step, fci, kind)[2:2 + (K - 2)]; b_we = np.r_[0, 0, win]; b0 = M.impact(fci, idx0)
    ok = (per >= R.Z_FIRST) & (per <= R.Z_LAST); z = R.ZFULL.reindex(per[ok]).fillna(0.0).values; r = U[ok]
    g = np.array([MO.first_stage(r[:, j], z)[0] for j in range(K)]); F = MO.first_stage(r[:, 2], z)[1]; s_p1 = g / g[2]
    info = dict(step=step, fci=fci, kind=kind, start=str(per[0]), L=L, nobs=len(per), F=F, win_pol=win[0], win_fci=(win[1] if K == 4 else np.nan),
                p1_imp_u=s_p1[0], p1_imp_pi=s_p1[1], p1_imp_fci=(s_p1[3] if K == 4 else np.nan))
    rows = []
    for v, h in TARGETS:                                     # P1: per +1 pp in the yield measure, then rescaled to the window unit by win[0]
        c = MO.row_of(T, v, h); lo, hi, unb = MO.ar_set(r @ c, r[:, 2], z)
        rows.append(dict(**info, ident="P1", var=v, h=h, r=float(c @ s_p1) * win[0], lo=lo * win[0], hi=hi * win[0], unbounded=int(unb)))
    chol = np.linalg.cholesky(S)[:, 2]; s_ch = chol / chol[2] if K == 3 else None
    pre = np.where(per < POST)[0]; post = np.where(per >= POST)[0]
    rng = np.random.default_rng(zlib.crc32(f"A2|{step}|{kind}|{start}|{L}".encode()))      # FCI not in the tag: pairs share draws
    dr = {("WE", t): [] for t in TARGETS}; dr.update({("CH", t): [] for t in TARGETS})
    for _ in range(B):
        rows_b = np.concatenate([blocks(pre, len(pre), rng) if len(pre) else np.array([], int), blocks(post, len(post), rng)])
        Ud = U[rows_b]; Ys = np.zeros_like(Y); Xs = X.copy()
        for t in range(len(per)):
            for l in range(L):
                if t - l - 1 >= 0: Xs[t, 1 + K * l:1 + K * (l + 1)] = Ys[t - l - 1]
            Ys[t] = Xs[t] @ C + Ud[t]
        Cb = np.linalg.lstsq(Xs, Ys, rcond=None)[0]; Tb = MO.ma(Cb, K, L)
        mo_b = per[rows_b[rows_b >= len(pre)]]; ib = idx0[np.isin(evm, mo_b.values)] if len(mo_b) else idx0
        ib = ib if len(ib) >= 20 else idx0; ratio = M.impact(fci, ib) / b0; sb = np.r_[0, 0, win * ratio[:K - 2]]
        if K == 3:
            Ub = Ys - Xs @ Cb; Sb = Ub.T @ Ub / (len(per) - X.shape[1]); cb = np.linalg.cholesky(Sb)[:, 2]; cb = cb / cb[2]
        for t in TARGETS:
            dr[("WE", t)].append(MO.row_of(Tb, *t) @ sb)
            if K == 3: dr[("CH", t)].append(MO.row_of(Tb, *t) @ cb)
    for t in TARGETS:
        rows.append(dict(**info, ident="WE", var=t[0], h=t[1], r=float(MO.row_of(T, *t) @ b_we), lo=np.percentile(dr[("WE", t)], 5), hi=np.percentile(dr[("WE", t)], 95), unbounded=0))
        if K == 3: rows.append(dict(**info, ident="CH", var=t[0], h=t[1], r=float(MO.row_of(T, *t) @ s_ch), lo=np.percentile(dr[("CH", t)], 5), hi=np.percentile(dr[("CH", t)], 95), unbounded=0))
    return rows

def job(args):
    step, wf, (kind, start), L = args; return case(step, step if wf else 0, kind, start, L, a.draws)

if __name__ == "__main__":
    from multiprocessing import Pool
    jobs = list(itertools.product(("nom", "real", "rstar"), (False, True), (("avg", "1973-01"), ("eom", "1990-01"), ("eom", "1996-01")), (3, 6, 12)))
    with Pool(2) as p: res = p.map(job, jobs)
    pd.DataFrame(sum(res, [])).to_csv(OUT / "monthly_benchmarks.csv", index=False, float_format="%.4f"); print("done", len(jobs))
