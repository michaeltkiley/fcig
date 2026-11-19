"""Step 18. The bootstrap with the FCI weights re-estimated in each draw (FS-A107; review of 19 Nov 2026, item 22). Real baseline, monthly equations from 1996, 12 lags.
   python3 18_weights_boot.py [--draws 500] [--jobs 4]
The baseline bootstrap (lib/model.estimate, "j12r") holds the FCI weights at their estimates, so its intervals are conditional on the weights. Here each draw also
re-estimates the one-factor GLS weights (lib/noteA.gls_weights) on the announcements of the months drawn, rebuilds the daily and monthly real FCI with them
(the index is the sum of its weighted components, lib/model.CMPD / CMPM, rescaled by w_b / w), recomputes the FCI's window move per +1 pp on the 2-year yield,
and re-estimates the daily block and the monthly equations on the rebuilt data. The policy-news factor itself is held fixed.
Two runs on the same draws (same months, announcements and residual blocks), so they are paired:
  fixed: the weights at their estimates (the index built from its components; within 5e-5 of the baseline index, FS-A81);  reestimated: the weights of each draw.
Output: results/weights_boot.csv (responses at 12/24/36 m with 90% intervals, both runs) and results/weights_boot_draws.csv (the weights of each draw)."""
import os, argparse, zlib
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np, pandas as pd
from lib import model as M, daily as DD, noteA
from lib.paths import RESULTS

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4); a = ap.parse_args()
FORM, MV, START, L, K = "real", ["u", "pi"], "1996-01", 12, 2
M.use_variant("")
KEYS = M.CMPKEYS; W0 = np.array([M._wv[k] for k in KEYS]); EV = DD.EV; idx0 = DD.event_index()
D = EV[["UST10Y", "SP500", "DXY", "UST2Y", "ns"]].values

def set_weights(w):
    """Rebuild the real FCI (daily and monthly) with weights w (10-year, equities, dollar)."""
    sc = w / W0
    M.FCI[FORM] = sum(M.CMPD[FORM][k] * s for k, s in zip(KEYS, sc)); M.IDXM[FORM] = sum(M.CMPM[FORM][k] * s for k, s in zip(KEYS, sc))

def impact_b(w, ib):
    s = D[ib, 4]; x = s - s.mean(); sl = lambda y: float(np.sum((y - y.mean()) * x) / np.sum(x * x))
    return np.r_[1.0, sl(D[ib, :3] @ w) / sl(D[ib, 3]), M.B_FF]

def data(w):
    set_weights(w)
    Xd, Yd, dmon, ddate = M.har_rows(FORM, FORM, MV, None, "out", months=True, dates=True)
    X, Y, P = M.macro_data(FORM, FORM, MV, L, START, None, "out", "none", periods=True)
    return Xd, Yd, dmon, X, Y, P

def fit(Xd, Yd, X, Y):
    C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; return M.har_fit(Xd, Yd, FORM), C0, Y - X @ C0

# point data with the estimated weights, and the draws (months, announcements, residual blocks) exactly as lib/model.estimate builds them
w_hat = noteA.gls_weights(D[idx0, :3], D[idx0, 4])[0]
Xd0, Yd0, dmon0, X0, Y0, P0 = data(W0); Bd0, C00, res0 = fit(Xd0, Yd0, X0, Y0)
cal = pd.period_range("1996-01", "2026-09", freq="M"); evm = EV.d.iloc[idx0].dt.to_period("M").values
prow = {p: i for i, p in enumerate(P0)}; post = np.where(P0 >= pd.Period("1996-01", "M"))[0]
rng = np.random.default_rng(zlib.crc32(f"{FORM}|u,pi|{START}|None|out|{L}".encode()))
DRAWS = []
for b in range(a.draws):
    mo, rows = [], []
    while len(rows) < len(post):
        for r in M.block_rows(len(cal), rng, M.BLOCK_M):
            mo.append(cal[r]); rows += [prow[cal[r]]] if cal[r] in prow else []
    rows = rows[:len(post)]; ev_i = np.concatenate([idx0[evm == m] for m in mo]); DRAWS.append((mo, np.array(rows), ev_i if len(ev_i) >= 20 else idx0))

def one(job):
    b, mode = job; mo, rows, ib = DRAWS[b]
    w = W0 if mode == "fixed" else noteA.gls_weights(D[ib, :3], D[ib, 4])[0]
    Xd, Yd, dmon, X, Y, P = (Xd0, Yd0, dmon0, X0, Y0, P0) if mode == "fixed" else data(w)
    Bd_, C0, res = (Bd0, C00, res0) if mode == "fixed" else fit(Xd, Yd, X, Y)
    LI = M._lag_index(P, L); e = res[rows]
    Ys = M._recursive(X, C0, e, K, L, LI); Cb = np.linalg.lstsq(M._rebuild(X, K, L, LI, Ys), Ys, rcond=None)[0]
    dr = np.concatenate([np.where(dmon == m)[0] for m in mo]); Bd = M.har_fit(Xd[dr], Yd[dr], FORM)
    bvec = impact_b(w, ib); pb = DD.positions(ib); nd = Yd.shape[1]
    m = sum(wt * M.simulate(Bd, Cb, K, nd, L, bvec, k0, n0)[0] for k0, n0, wt in pb)
    return b, mode, M.to_level(m), w

if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(a.jobs) as pool: out = pool.map(one, [(b, md) for b in range(a.draws) for md in ("fixed", "reestimated")], chunksize=4)
    S = {md: np.array([o[2] for o in sorted([o for o in out if o[1] == md])]) for md in ("fixed", "reestimated")}
    Wd = np.array([o[3] for o in sorted([o for o in out if o[1] == "reestimated"])])
    pt = M.to_level(sum(wt * M.simulate(Bd0, C00, K, Yd0.shape[1], L, impact_b(W0, idx0), k0, n0)[0] for k0, n0, wt in DD.positions(idx0)))
    rows = []
    for md, sd in S.items():
        for j, v in enumerate(("u", "P")):
            rows.append(dict(run=md, var=v, **{f"r{h}": pt[h, j] for h in M.HORIZ}, **{f"lo{h}": np.percentile(sd[:, h, j], 5) for h in M.HORIZ}, **{f"hi{h}": np.percentile(sd[:, h, j], 95) for h in M.HORIZ},
                             **{f"sd{h}": sd[:, h, j].std() for h in M.HORIZ}))
    R = pd.DataFrame(rows); R.to_csv(RESULTS / "weights_boot.csv", index=False, float_format="%.4f")
    pd.DataFrame(Wd, columns=KEYS).to_csv(RESULTS / "weights_boot_draws.csv", index=False, float_format="%.5f")
    print("weights: estimate", np.round(w_hat, 4), "used", np.round(W0, 4), "draws 5-95:", np.round(np.percentile(Wd, 5, axis=0), 4), np.round(np.percentile(Wd, 95, axis=0), 4))
    print(R.round(3).to_string(index=False))
