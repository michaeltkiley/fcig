"""Step 3b. Rebuild every case's interval columns from its saved bootstrap draws (FS-A108), without re-estimating.
   python3 03b_intervals.py        (CI=pct for the plain percentile intervals of the earlier convention)
For each case of cases.py with output/draws/<id>_L<lags>.npz for every lag length: results/<id>.csv and results/<id>_paths.csv are rewritten with the intervals of
lib/intervals (bias-corrected percentile by default). Point estimates and the number of observations are taken from the existing results file and checked against
the draws file. Run step 3 with --missing-draws first."""
import numpy as np, pandas as pd
import cases as CS
from lib import model as M, daily as DD
from lib.paths import RESULTS, OUT

n_ok, missing = 0, []
for c in CS.unique_cases():
    i = CS.case_id(c); f = {L: OUT / "draws" / f"{i}_L{L}.npz" for L in M.LAGS}
    if not all(p.exists() for p in f.values()): missing.append(i); continue
    DD.use_surprise(c.get("shock", "ns")); M.use_variant(c.get("ext", ""))
    old = pd.read_csv(RESULTS / f"{i}.csv"); sp = CS.spec(c); rows, paths = [], []
    fn = list(M.daily_frame(c["form"], c["fci"]).columns) if M.VARIANT["ff"] else None
    for L in M.LAGS:
        z = np.load(f[L], allow_pickle=True); o = old[old.lags == L]
        est = dict(lags=L, names=[str(x) for x in z["names"]], s0=z["s0"], sd=z["sd"], f0=z["f0"], fd=z["fd"], nobs=int(o.nobs.iloc[0]), fnames=fn)
        for j, n in enumerate(est["names"]):
            r = o[o["var"] == n].iloc[0]; assert abs(r.r24 - z["s0"][24, j]) < 1e-4, (i, L, n)          # the draws belong to the stored point estimates
        rows += M.summary_rows(sp, est); paths.append(M.path_rows(sp, est))
    pd.DataFrame(rows).to_csv(RESULTS / f"{i}.csv", index=False, float_format="%.4f"); pd.concat(paths).to_csv(RESULTS / f"{i}_paths.csv", index=False, float_format="%.4f"); n_ok += 1
print(f"{n_ok} cases rewritten ({M.IV.METHOD}); missing draws: {len(missing)}", *missing[:10], sep="\n  ")
