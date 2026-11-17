"""Bootstrap for Route 2 (12 lags, 2020 in): moving blocks of 12 months of VAR residuals (pre-1996 and post-1996 rows drawn separately, as in Note B; post-1996 blocks carry
their months' policy news, so the proxy column P1 is re-estimated in each draw), the VAR rebuilt recursively from the data's initial lags and re-estimated. The window column
(WE) is held at its point value (DECOMP_QA D-A7). Each draw recomputes Sigma, the recovered shock, the variance shares, the diagnostics, and the historical decomposition of
the actual data under the draw's parameters.
   python3 02_boot.py [--draws 500]
Writes results/boot_summary.csv (percentiles) and results/boot_hd_<case>.npz for the main cases."""
import argparse, itertools, zlib
import numpy as np, pandas as pd
import lib_r2 as R

OUT = R.Path(__file__).resolve().parent / "results"
ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); a = ap.parse_args()
HD_KEEP = {("rstar", "rstar", "avg", "WE"), ("rstar", "rstar", "eom", "WE"), ("nom", 0, "avg", "WE"), ("nom", 0, "eom", "WE"),
           ("rstar", "rstar", "avg", "P1"), ("rstar", 0, "avg", "WE")}
POST = pd.Period("1996-01", "M")

def blocks(idx, n, rng, length=12):
    nb = -(-n // length); st = rng.integers(0, len(idx) - length + 1, nb)
    return np.concatenate([idx[s:s + length] for s in st])[:n]

def draw_case(step, fci, kind, start, ident, B):
    c = R.run(step, fci, kind, start, 12, ident, "in")
    X, Y, per, C, U, K, L = c["X"], c["Y"], c["per"], c["C"], c["U"], c["K"], c["L"]
    n = len(per); z_all = R.ZFULL.reindex(per).fillna(0.0).values
    pre = np.where(per < POST)[0]; post = np.where(per >= POST)[0]
    rng = np.random.default_rng(zlib.crc32(f"r2|{step}|{fci}|{kind}|{start}".encode()))     # same draws for WE and P1
    out = dict(fevd_u24=[], fevd_u36=[], fevd_pi24=[], fevd_pol12=[], fevd_idx12=[], sd_e=[], corr=[], r2=[], u24=[], P24=[], hd=[])
    for _ in range(B):
        rows = np.concatenate([blocks(pre, len(pre), rng) if len(pre) else np.array([], int), blocks(post, len(post), rng)])
        Ud = U[rows]; zd = z_all[rows]
        Ys = np.zeros_like(Y); Xs = X.copy()
        for t in range(n):                                   # recursive rebuild; lags before the sample from the data
            for l in range(L):
                if t - l - 1 >= 0: Xs[t, 1 + K * l:1 + K * (l + 1)] = Ys[t - l - 1]
            Ys[t] = Xs[t] @ C + Ud[t]
        Cb = np.linalg.lstsq(Xs, Ys, rcond=None)[0]; Ub = Ys - Xs @ Cb; Sb = Ub.T @ Ub / (n - X.shape[1])
        if ident == "P1":
            ok = np.arange(n) >= len(pre); zc = zd[ok] - zd[ok].mean(); g = (Ub[ok] - Ub[ok].mean(0)).T @ zc / (zc @ zc); b = g / g[2] * c["bwe"][2]
            corr_z = zd[ok]
        else: b = c["b"]
        Tb = R.ma(Cb, K, L, n)
        rb = Tb @ b
        # diagnostics on the drawn sample (shock recovered from the draw's innovations, compared with the drawn policy news)
        eb = Ub @ np.linalg.solve(Sb, b) / float(b @ np.linalg.solve(Sb, b)); okp = np.arange(n) >= len(pre)
        out["corr"].append(np.corrcoef(eb[okp], zd[okp])[0, 1])
        Zx = np.column_stack([np.ones(okp.sum()), Ub[okp]]); zz = zd[okp]; res = zz - Zx @ np.linalg.lstsq(Zx, zz, rcond=None)[0]
        out["r2"].append(1 - res @ res / ((zz - zz.mean()) @ (zz - zz.mean())))
        s2 = 1.0 / float(b @ np.linalg.solve(Sb, b)); out["sd_e"].append(np.sqrt(s2))
        f = R.fevd(Tb, Sb, rb, s2, (12, 24, 36))
        out["fevd_u24"].append(f[24][0]); out["fevd_u36"].append(f[36][0]); out["fevd_pi24"].append(f[24][1]); out["fevd_pol12"].append(f[12][2])
        out["fevd_idx12"].append(f[12][3] if K > 3 else np.nan)
        out["u24"].append(rb[24, 0]); out["P24"].append(np.cumsum(rb[:, 1])[24] / 12)
        if (step, fci, kind, ident) in HD_KEEP:            # historical decomposition of the actual data under the draw's parameters
            Ua = Y - X @ Cb; ea = Ua @ np.linalg.solve(Sb, b) / float(b @ np.linalg.solve(Sb, b))
            out["hd"].append(R.hd(rb, ea).astype(np.float32))
    if out["hd"]: np.savez_compressed(OUT / f"boot_hd_{step}_{fci}_{kind}_{ident}.npz", hd=np.array(out["hd"]), months=per.astype(str).values)
    rows = []
    for k, v in out.items():
        if k == "hd": continue
        v = np.array(v, float)
        rows.append(dict(step=step, fci=fci, kind=kind, start=start, ident=ident, stat=k, point=np.nan, p5=np.nanpercentile(v, 5), p16=np.nanpercentile(v, 16),
                         p50=np.nanpercentile(v, 50), p84=np.nanpercentile(v, 84), p95=np.nanpercentile(v, 95)))
    return rows

def _job(args):
    step, wf, (kind, start), ident = args; fci = step if wf else 0
    return draw_case(step, fci, kind, start, ident, a.draws)

if __name__ == "__main__":
    import os
    from multiprocessing import Pool
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    jobs = list(itertools.product(("nom", "real", "rstar"), (False, True), (("avg", "1973-01"), ("eom", "1990-01")), ("WE", "P1")))
    with Pool(4) as p: res = p.map(_job, jobs)
    pd.DataFrame(sum(res, [])).to_csv(OUT / "boot_summary.csv", index=False, float_format="%.4f")
    print("done", len(jobs))
