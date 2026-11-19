"""Exploration for review items 23 and 24 (19 Nov 2026; outside the replication package; FS-A113). Core baseline cases only, bias-corrected intervals, 12 lags, 500 draws.
Item 23, other r* in the step relative to r* (real rates and FCI less r*; the place LW r* enters): Laubach-Williams two-sided (LW2), Holston-Laubach-Williams one-sided (HLW;
  the New York Fed publishes HLW one-sided only), Lubik-Matthes (LM; the Richmond Fed publishes one median series). Each without and with the FCI, monthly equations from 1996 and 1973.
  LW one-sided is the package's case (form "rstar"), rebuilt here by the same route and checked.
Item 24, other weights for the FCI in the real version: FRB/US (B) and Goldman Sachs (G) calibrations of the companion paper, in Note B's units (output/four_weights_nb.csv:
  rescaled so that the window loading on policy news is 1). Real index with those weights (monthly), the daily index with the same weights, window move from the windows.
  With the FCI only (the rates-only case is the baseline's); compared with it draw by draw (same draws).
Data (explore_review/data): Laubach_Williams_current_estimates.xlsx, Holston_Laubach_Williams_current_estimates.xlsx (New York Fed), lubik_matthes_natural_rate_interest.xlsx
  (Richmond Fed), downloaded 19 Nov 2026.
   python3 run_items_23_24.py [--draws 500] [--jobs 4]       (from any folder)"""
import os, sys, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline_real"
sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from lib import model as M, noteA, daily as DD
from lib.daily import interp_monthly, POL
from lib.paths import OUT

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4); a = ap.parse_args()
RES = HERE / "results"; RES.mkdir(exist_ok=True)
D0 = M.D0

# ---------------------------------------------------------------- r* measures, quarterly -> monthly as LW (noteA.mid_quarter)
def q(dates, vals):
    s = pd.Series(np.asarray(vals, float), index=pd.PeriodIndex(pd.to_datetime(dates), freq="Q")).dropna(); return noteA.mid_quarter(s).reindex(D0.index)
lw = pd.read_excel(HERE / "data" / "Laubach_Williams_current_estimates.xlsx", "data", header=None).iloc[6:]; lw = lw[pd.to_datetime(lw[0], errors="coerce").notna()]
hlw = pd.read_excel(HERE / "data" / "Holston_Laubach_Williams_current_estimates.xlsx", "HLW Estimates", header=None).iloc[6:]; hlw = hlw[pd.to_datetime(hlw[0], errors="coerce").notna()]
lm = pd.read_excel(HERE / "data" / "lubik_matthes_natural_rate_interest.xlsx", "LM_RealRate")
D0["rstar LW1chk"] = q(lw[0], lw[2]); D0["rstar LW2"] = q(lw[0], lw[7]); D0["rstar HLW"] = q(hlw[0], hlw[10]); D0["rstar LM"] = q(lm.Date, lm.Median)
assert np.nanmax(np.abs((D0["rstar LW1chk"] - D0["rstar LW"]).loc["1973-01":"2026-06"])) < 1e-3, "LW one-sided not reproduced from the New York Fed file"
w = pd.read_csv(OUT / "market_weights.csv", index_col=0).weight.values
chk = noteA.market_index(noteA.index_inputs(D0, "rstar", "rstar LW"), w).loc[noteA.START:noteA.END]
assert np.allclose(chk.values, M.IDXM["rstar"].reindex(chk.index).values, atol=1e-3), "LW index not reproduced"
for key, col in (("lw2", "rstar LW2"), ("hlw", "rstar HLW"), ("lm", "rstar LM")):
    M.IDXM[key] = noteA.market_index(noteA.index_inputs(D0, "rstar", col), w).loc[noteA.START:noteA.END].where(D0[col].notna())
    M.FCI[key] = M._daily_fci(M.IDXM[key])
    for R in (M.RATE, M.RATE2): R[key] = POL - interp_monthly(M._e2 + D0[col])
    for R in (M.RATEM, M.RATEM2): R[key] = M.Y2M - M._e2m - D0[col]
pd.DataFrame({k: D0[c] for k, c in (("LW one-sided", "rstar LW"), ("LW two-sided", "rstar LW2"), ("HLW one-sided", "rstar HLW"), ("Lubik-Matthes", "rstar LM"))}).loc["1965-01":].to_csv(RES / "rstar_measures.csv", float_format="%.4f")

# ---------------------------------------------------------------- item 24: real index with the FRB/US (B) and GS (G) weights
WC = pd.read_csv(OUT / "four_weights_nb.csv", index_col=0)
for k in ("B", "G"):
    key = f"cal{k}r"; wk = WC.loc[k, ["y10", "equities", "dollar"]].values
    M.IDXM[key] = noteA.market_index(noteA.index_inputs(D0, "real", "rstar LW"), wk).loc[noteA.START:noteA.END]
    M.FCI[key] = M._daily_fci(M.IDXM[key], DD.DAILY[f"idx_cal{k}"].reindex(DD.CALW).ffill(limit=3))
    DD.EV[f"idx_win_{key}"] = DD.EV[f"idx_win_cal{k}"]                                     # same window move (real = nominal in the window)

JOBS = [(f, fc, s) for f in ("lw2", "hlw", "lm") for s in ("1996-01", "1973-01") for fc in (0, f)] + [("real", f"cal{k}r", s) for k in ("B", "G") for s in ("1996-01", "1973-01")]
def work(job):
    f, fc, s = job; M.use_variant(""); t0 = time.time()
    est = next(M.estimate(f, fc, "u,pi", s, None, "out", "none", a.draws, (12,)))
    np.savez_compressed(RES / f"{f}_{fc}_{s}.npz", s0=est["s0"], sd=est["sd"]); return job, est["s0"], est["sd"], time.time() - t0

if __name__ == "__main__":
    from multiprocessing import Pool
    with Pool(a.jobs) as pool: out = pool.map(work, JOBS)
    R = {j: (s0, sd) for j, s0, sd, _ in out}
    def ld(form, fc, s):
        if (form, fc, s) in R: return R[(form, fc, s)]
        z = np.load(OUT / "draws" / f"{form}_{fc}_upi_{s}_all_out_L12.npz"); return z["s0"], z["sd"]
    rows = []
    for (f, fc, s) in [(f, fc, s) for f in ("rstar", "lw2", "hlw", "lm") for s in ("1996-01", "1973-01") for fc in (0, f)] + [("real", fc, s) for fc in ("real", "calBr", "calGr") for s in ("1996-01", "1973-01")] + [("real", 0, s) for s in ("1996-01", "1973-01")]:
        s0, sd = ld(f, fc, s); s0n, sdn = ld(f, 0, s)
        for j, v in enumerate(("u", "P")):
            for h in (12, 24):
                lo, hi = M.IV.ci(sd[:, h, j], s0[h, j]); r = dict(form=f, fci=str(fc), start=s, var=v, h=h, r=s0[h, j], lo=lo, hi=hi)
                if fc != 0: d0 = s0[h, j] - s0n[h, j]; dl, dh = M.IV.ci(sd[:, h, j] - sdn[:, h, j], d0); r.update(fci_effect=d0, eff_lo=dl, eff_hi=dh)
                rows.append(r)
    T = pd.DataFrame(rows); T.to_csv(RES / "items_23_24.csv", index=False, float_format="%.4f")
    print(T.round(2).to_string(index=False))
