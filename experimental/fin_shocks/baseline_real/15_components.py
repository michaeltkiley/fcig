"""Step 15. Does the response rely on the index restriction? (FS-A93; review of 19 Nov 2026, item 2.)  Real version, 12 lags, monthly equations from 1996 and from 1973.
   python3 15_components.py [--draws 500] [--jobs 4]
One daily component system for both cases: the 2-year yield, the three weighted components of the FCI (10-year yield, equity valuation, dollar) and the funds rate (lib/model.py,
fci = "cmpR" / "cmp" with the funds-rate variant; each component's daily equation has its own, the yield's and the funds rate's averages, each rate's the two rates'). The window impact
moves each component by its response to policy news, so the three add to the FCI's move. The two cases differ only in the monthly equations:
  cmpR (restricted): the sum of the three components (the FCI built from the components) as one regressor per lag;
  cmp  (all free)  : the three components as separate regressors.
Both use the same bootstrap draws (seeded by the case without the FCI key), so their difference is paired. The author asked for the all-free test only (no equities-free case).
Outputs: results/real_cmpR_upi_<start>_all_out.csv, results/real_cmp_upi_<start>_all_out.csv (+ _paths), output/draws/..._L12.npz;
results/components_diff.csv (paired differences, all free less restricted, and each less the baseline); results/components_tradeoff.csv (Phillips multiplier and its set);
results/components_wald.csv (all three coefficients equal at every lag, in each monthly equation: Wald HC1, chi-square and block-bootstrap p-values)."""
import os, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np, pandas as pd
from scipy import stats
import cases as CS
from lib import model as M
from lib.paths import RESULTS, OUT

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4); a = ap.parse_args()
L = 12; STARTS = ("1996-01", "1973-01"); FORM = "real"
CASES = [dict(form=FORM, fci=f, macro="u,pi", start=st, end=None, t2020="out", trend="none") for st in STARTS for f in ("cmpR", "cmp")]

BASE = [dict(form=FORM, fci=FORM, macro="u,pi", start=st, end=None, t2020="out", trend="none") for st in STARTS]     # the baselines with the FCI: draws only (output/draws is not kept in the repository)

def work(c):
    t0 = time.time(); i = CS.case_id(c); sp = CS.spec(c); M.use_variant("")
    est = next(M.estimate(c["form"], c["fci"], c["macro"], c["start"], c["end"], c["t2020"], c["trend"], a.draws, (L,)))
    if c["fci"] == FORM:                                                                    # baseline: check it reproduces step 3's stored responses, then keep the draws only
        old = pd.read_csv(RESULTS / f"{i}.csv"); new = pd.DataFrame(M.summary_rows(sp, est)); old = old[old.lags == L].reset_index(drop=True)
        assert np.allclose(old[["r12", "r24", "lo24", "hi24"]].values, new[["r12", "r24", "lo24", "hi24"]].values, atol=1e-4), i
        np.savez_compressed(OUT / "draws" / f"{i}_L{L}.npz", s0=est["s0"], sd=est["sd"], f0=est["f0"], fd=est["fd"], names=est["names"]); return f"{i} (baseline, draws; reproduces step 3) in {time.time() - t0:.0f}s"
    pd.DataFrame(M.summary_rows(sp, est)).to_csv(RESULTS / f"{i}.csv", index=False, float_format="%.4f")
    M.path_rows(sp, est).to_csv(RESULTS / f"{i}_paths.csv", index=False, float_format="%.4f")
    np.savez_compressed(OUT / "draws" / f"{i}_L{L}.npz", s0=est["s0"], sd=est["sd"], f0=est["f0"], fd=est["fd"], names=est["names"])
    return f"{i} done in {time.time() - t0:.0f}s"

if __name__ == "__main__":
    (OUT / "draws").mkdir(exist_ok=True)
    if a.jobs > 1:
        from multiprocessing import Pool
        with Pool(a.jobs) as pool:
            for m in pool.imap_unordered(work, CASES + [b for b in BASE if not (OUT / 'draws' / f'{CS.case_id(b)}_L{L}.npz').exists()]): print(m, flush=True)
    else:
        for c in CASES + BASE: print(work(c), flush=True)

    # ---- paired differences (all free less restricted; each less the baseline with the FCI, whose draws come from step 3)
    def load(fci, st): z = np.load(OUT / "draws" / f"{CS.case_id(dict(form=FORM, fci=fci, macro='u,pi', start=st, end=None, t2020='out', trend='none'))}_L{L}.npz"); return z["s0"], z["sd"]
    rows = []
    for st in STARTS:
        for lab, x, y in (("free-restricted", "cmp", "cmpR"), ("restricted-baseline", "cmpR", FORM), ("free-baseline", "cmp", FORM)):
            try: (sx, dx), (sy, dy) = load(x, st), load(y, st)
            except FileNotFoundError: print(f"draws missing for {y} {st}: run 03_estimate.py --missing-draws --panel {'B' if st == '1996-01' else 'B73'}"); continue
            for j, v in enumerate(("u", "P")):
                for h in M.HORIZ:
                    d = dx[:, h, j] - dy[:, h, j]
                    rows.append(dict(start=st, contrast=lab, var=v, h=h, diff=sx[h, j] - sy[h, j], lo=M.IV.ci(d, sx[h, j] - sy[h, j])[0], hi=M.IV.ci(d, sx[h, j] - sy[h, j])[1], lo95=M.IV.ci(d, sx[h, j] - sy[h, j], 2.5, 97.5)[0], hi95=M.IV.ci(d, sx[h, j] - sy[h, j], 2.5, 97.5)[1]))
    D = pd.DataFrame(rows); D.to_csv(RESULTS / "components_diff.csv", index=False, float_format="%.4f")

    # ---- Phillips multiplier and its set (as step 5)
    T = []
    for c in CASES:
        s0, sd = load(c["fci"], c["start"]); T += M.multiplier_rows(CS.spec(c), dict(lags=L, s0=s0, sd=sd))
    pd.DataFrame(T).to_csv(RESULTS / "components_tradeoff.csv", index=False, float_format="%.4f")

    # ---- Wald test: the three component coefficients equal at every lag (as step 9's "all" test, with the funds rate in the monthly equations)
    def wald(X, y, R):
        n, k = X.shape; XX = np.linalg.inv(X.T @ X); b = XX @ X.T @ y; r = y - X @ b; V = XX @ (X.T * (r ** 2)) @ X @ XX * n / (n - k); Rb = R @ b
        return float(Rb @ np.linalg.solve(R @ V @ R.T, Rb))
    M.use_variant(""); rng = np.random.default_rng(15); W = []
    for st in STARTS:
        X, Y = M.macro_data(FORM, "cmp", ["u", "pi"], L, st, None, "out", "none"); Xr, _ = M.macro_data(FORM, FORM, ["u", "pi"], L, st, None, "out", "none")
        n, k = X.shape; K = 2; nd = 5                                                       # monthly regressors per lag: yield, 10-year, equities, dollar, funds rate
        R = np.zeros((2 * L, k))
        for l in range(L):
            o = 1 + K * L + l * nd; R[2 * l, o + 1], R[2 * l, o + 2] = 1, -1; R[2 * l + 1, o + 2], R[2 * l + 1, o + 3] = 1, -1
        for j, name in enumerate(("u", "pi")):
            y = Y[:, j]; w = wald(X, y, R); fit = Xr @ np.linalg.lstsq(Xr, y, rcond=None)[0]; res = y - fit
            wb = np.array([wald(X, fit + res[M.block_rows(n, rng, M.BLOCK_M)], R) for _ in range(999)])
            ssr = lambda Z: float(np.sum((y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]) ** 2)); lr = n * np.log(ssr(Xr) / ssr(X)); q = X.shape[1] - Xr.shape[1]
            W.append(dict(start=st, eq=name, restrictions=2 * L, nobs=n, wald=w, p=1 - stats.chi2.cdf(w, 2 * L), p_boot=(1 + np.sum(wb >= w)) / 1000,
                          lr=lr, d_aic=2 * q - lr, d_bic=q * np.log(n) - lr))           # information criteria, free less restricted (Gaussian): positive = the restriction preferred
    W = pd.DataFrame(W); W.to_csv(RESULTS / "components_wald.csv", index=False, float_format="%.4f")
    print(D[D.h.isin([12, 24])].round(2).to_string(index=False)); print(W.round(3).to_string(index=False))
    print(pd.DataFrame(T).query("H == 24")[["fci", "start", "kappa", "k_lo", "k_hi"]].round(2).to_string(index=False))
