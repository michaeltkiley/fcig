"""Exploration (18 Nov 2026, outside the replication package): Note B's two baselines with two alternative r* measures in place of Laubach-Williams.
The alternative r* enters every place LW r* enters (the 'identical case'): the r*-gap 2-year yield (2-year - 2-year expected inflation - r*, daily and monthly),
and the r*-gap market index (10-year - 10-year expected inflation - r*; equities as E/P - r*; real dollar), Note B's weights unchanged.
  ma8: r* = trailing 8-year (96-month) average of the REAL 2-year yield (monthly average 2-year less 2-year expected inflation, the series of the real step).
  nma8: the trailing 8-year average of the nominal 2-year replaces expected inflation and r* together (FS-A20's form; see below).
  fwd: r* = 1-year forward rate 9 years ahead (Gurkaynak-Sack-Wright SVEN1F09, monthly average) less 10-year expected inflation (Note A's series).
Cases: baselines B (monthly equations from 1996) and B73 (from 1973), r*-gap with and without the FCI, 2020 dropped, no trend, 3/6/12 lags, 500 draws.
Run from this folder:  python3 run_rstar_alt.py [--draws 500] [--jobs 4]
Writes results/<case>.csv and results/<case>_paths.csv (same layout as baseline/results), rstar_measures.csv, summary.csv, summary.md, fig_rstar.pdf."""
import os, sys, argparse, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"
sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from lib import model as M, noteA
from lib.daily import interp_monthly, POL

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--jobs", type=int, default=4)
ap.add_argument("--force", action="store_true"); a = ap.parse_args()
RES = HERE / "results"; RES.mkdir(exist_ok=True)

# ---------------------------------------------------------------- the r* measures (monthly)
D0 = M.D0
real2 = (M.Y2M - M._e2m).reindex(D0.index)                                  # monthly real 2-year (Note B's real step; Livingston-based expectations before 1982)
ma8 = real2.rolling(96, min_periods=96).mean()
g = pd.read_csv(HERE / "gsw_sven1f09.csv", parse_dates=["Date"]).set_index("Date").SVEN1F09
fwd = g.groupby(g.index.to_period("M")).mean().reindex(D0.index) - D0.einf_10y
D0["rstar MA8"] = ma8; D0["rstar FWD"] = fwd
# nma8 (FS-A20's form): the trailing 8-year average of the NOMINAL 2-year replaces expected inflation and r* together.
#   2-year: 2-year - MA8(2-year). Index: 10-year - MA8(2-year); equities: nominal earnings yield (E/P + e10) - MA8(2-year) = E/P - (MA8 - e10).
#   In index_inputs this is r* = MA8 - e10 (it subtracts e10 and r*); in the rate it is r* = MA8 - e2.
nma8 = M.Y2M.reindex(D0.index).rolling(96, min_periods=96).mean()
D0["rstar NMA8"] = nma8 - D0.einf_10y
# ma5 / nma5 (18 Nov, author): LAGGED 5-year average, months t-60..t-1 (excludes the current month); real 2-year in the r* slot (ma5), nominal 2-year replacing e + r* (nma5).
#   Available from 1966-07 (2-year from 1961-06), so the 1973 sample with 12 lags is fully covered.
ma5 = real2.shift(1).rolling(60, min_periods=60).mean()
nma5 = M.Y2M.reindex(D0.index).shift(1).rolling(60, min_periods=60).mean()
D0["rstar MA5"] = ma5; D0["rstar NMA5"] = nma5 - D0.einf_10y
# spf (18 Nov, author; 1996 baseline only): SPF median BILL10 - CPI10 (first-quarter surveys, 1992-2026), placed in February (survey month),
#   linearly interpolated between surveys and held after the last (as LW is placed mid-quarter and interpolated). Undefined before 1992-02.
def _spf(name, col):
    d = pd.read_excel(HERE / "survey_data" / f"Median_{name}_Level.xlsx").dropna(subset=[col]).query("QUARTER == 1")
    return pd.Series(d[col].values, index=pd.PeriodIndex([f"{y}-02" for y in d.YEAR], freq="M"))
_q = (_spf("BILL10", "BILL10") - _spf("CPI10", "CPI10"))
spf = _q.reindex(pd.period_range(_q.index[0], D0.index[-1], freq="M")).interpolate(limit_area="inside").ffill().reindex(D0.index)
D0["rstar SPF"] = spf
RS = pd.DataFrame({"LW": D0["rstar LW"], "Kiley": D0["rstar Kiley"], "MA8 (real 2-year)": ma8, "Forward 9-10y less e10": fwd, "MA8 nominal 2-year (replaces e + r*)": nma8, "MA5 real 2-year, lagged": ma5, "MA5 nominal 2-year, lagged (replaces e + r*)": nma5, "SPF BILL10 - CPI10": spf, "e2 (2-year expected inflation)": M._e2m.reindex(D0.index)})
RS.loc["1965-01":].to_csv(HERE / "rstar_measures.csv", float_format="%.4f")

# ---------------------------------------------------------------- plug into the model exactly as LW / Kiley are
w = pd.read_csv(M.OUT / "market_weights.csv", index_col=0).weight.values
chk = noteA.market_index(noteA.index_inputs(D0, "rstar", "rstar LW"), w).loc[noteA.START:noteA.END]
assert np.allclose(chk.values, M.IDXM["rstar"].reindex(chk.index).values, atol=1e-3), "LW index not reproduced"
chk = noteA.market_index(noteA.index_inputs(D0, "rstar", "rstar Kiley"), w).loc[noteA.START:noteA.END]
assert np.allclose(chk.values, M.IDXM["kiley"].reindex(chk.index).values, atol=1e-3), "Kiley index not reproduced"
for key, col in (("ma8", "rstar MA8"), ("fwd", "rstar FWD"), ("ma5", "rstar MA5"), ("spf", "rstar SPF")):
    M.IDXM[key] = noteA.market_index(noteA.index_inputs(D0, "rstar", col), w).loc[noteA.START:noteA.END]
    M.IDXM[key] = M.IDXM[key].where(D0[col].reindex(M.IDXM[key].index).notna())     # undefined where r* is (market_index's sum would otherwise keep the other terms)
    M.FCI[key] = M._daily_fci(M.IDXM[key])
    for R in (M.RATE, M.RATE2): R[key] = POL - interp_monthly(M._e2 + D0[col])
    for R in (M.RATEM, M.RATEM2): R[key] = M.Y2M - M._e2m - D0[col]
M.IDXM["nma8"] = noteA.market_index(noteA.index_inputs(D0, "rstar", "rstar NMA8"), w).loc[noteA.START:noteA.END]
M.FCI["nma8"] = M._daily_fci(M.IDXM["nma8"])
for R in (M.RATE, M.RATE2): R["nma8"] = POL - interp_monthly(nma8)
for R in (M.RATEM, M.RATEM2): R["nma8"] = M.Y2M - nma8
M.IDXM["nma5"] = noteA.market_index(noteA.index_inputs(D0, "rstar", "rstar NMA5"), w).loc[noteA.START:noteA.END]
M.FCI["nma5"] = M._daily_fci(M.IDXM["nma5"])
for R in (M.RATE, M.RATE2): R["nma5"] = POL - interp_monthly(nma5)
for R in (M.RATEM, M.RATEM2): R["nma5"] = M.Y2M - nma5
# same check on the rate: rebuilding LW this way reproduces the stored rate
assert np.allclose((M.Y2M - M._e2m - D0["rstar LW"]).dropna(), M.RATEM["rstar"].dropna())

FORMS = ("rstar", "kiley", "ma8", "fwd"); LAB = {"rstar": "LW (baseline)", "kiley": "Kiley", "ma8": "MA8 real 2-year", "fwd": "Forward less e10"}
STARTS = ("1996-01", "1973-01")
def cid(form, fci, start): return f"{form}_{fci}_upi_{start}_all_out"
JOBS = [(f, fci, s) for f in ("ma8", "fwd", "nma8", "ma5", "nma5") for s in STARTS for fci in (0, f)] + [("spf", fci, "1996-01") for fci in (0, "spf")]

def work(job):
    f, fci, s = job; t0 = time.time(); rows, paths = [], []
    sp = dict(form=f, fci=fci, macro="u,pi", start=s, end="", t2020="out", trend="none", shock="ns")
    for est in M.estimate(f, fci, "u,pi", s, None, "out", "none", a.draws):
        rows += M.summary_rows(sp, est); paths.append(M.path_rows(sp, est))
    pd.DataFrame(rows).to_csv(RES / f"{cid(*job)}.csv", index=False, float_format="%.4f")
    pd.concat(paths).to_csv(RES / f"{cid(*job)}_paths.csv", index=False, float_format="%.4f")
    return f"{cid(*job)} done in {time.time() - t0:.0f}s"

if __name__ == "__main__":
    todo = [j for j in JOBS if a.force or not (RES / f"{cid(*j)}.csv").exists()]
    print(f"{len(todo)} cases to run", flush=True)
    if todo:
        from multiprocessing import Pool
        with Pool(min(a.jobs, len(todo))) as pool:
            for m in pool.imap_unordered(work, todo): print(m, flush=True)
