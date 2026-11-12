"""Step 25. How often would the two calibrations have given different assessments? Common draws, weights inference (FP-A41, stage 2).

QUESTIONS (fixed before any number was read)
 (1) MONTHLY AGREEMENT. For every month m from 1996-01 to the data end, the market-implied reading M(m) = w_M'dx(m) and the spending-equivalent reading B(m) = w_B'dx(m), where dx is the
     12-month change of the three market variables at the r* step (as in step 21 part E) and both readings are in the market unit (a policy move raising the two-year yield 1 pp). Threshold t (0.10 and 0.25 points):
       agree        M and B have the same sign
       near_zero    opposite signs and min(|M|, |B|) < t          (the calibrations differ only around zero)
       opposing     opposite signs and both |M|, |B| >= t         (materially opposing readings)
       big_gap      |B - M| >= t, regardless of sign
     Shares of all months, of months in 1998-01..2001-12 and 2022-03..2024-12, per policy-news definition (21_signal.py: baseline, two_year, to_2019, no_lower_bound), with 5th-95th percentile
     intervals over announcement-bootstrap draws (weights uncertainty; the 12-month changes are held fixed).
 (2) PROPORTIONALITY (cross-multiplied). Does the dollar-over-equity ratio of the spending weights equal that of the market weights?  c = wB_usd*wM_eq - wB_eq*wM_usd  (zero iff proportional); same draws for both.
     Reported per definition with the paired difference to the baseline. The contrast in points (dollar part less equity part for the same illustrative movements) is repeated with the same draws.
 (3) MORE DRAWS. REPS25 draws (env FCI_REPS_25, default 5000). The first 500 draws are those of 02_weights.py / 21_signal.py (same generator and order; asserted).
Writes results/25_*.csv and scalars_25_months.csv."""
import os, time
import numpy as np, pandas as pd
from lib import data, cases, indexes as I
from lib.agree_core import MV, load_frbus, b_persist, ns_arr
from lib.config import RES, SEED, END
from lib.report import Scalars

T0 = time.time(); S = Scalars("25_months")
REPS25 = int(os.environ.get("FCI_REPS_25", 5000))
EQ, USD = -5.0, 3.9
raw = I.events_raw(); n = len(raw)
X5 = raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values; u2 = raw.UST2Y.values; Y3 = raw[["UST10Y", "SP500", "DXY"]].values; dates = raw.Date
MASK = {"baseline": np.ones(n, bool), "two_year": np.ones(n, bool), "to_2019": (dates < "2020-01-01").values,
        "no_lower_bound": ((dates < "2008-12-01") | (dates >= "2015-12-01")).values}
KIND = {"baseline": "ns", "two_year": "ust2y", "to_2019": "ns", "no_lower_bound": "ns"}
DEFS = list(MASK)

def fitg(f, Y):
    fc = f - f.mean(); Yc = Y - Y.mean(0); psi = (fc @ Yc) / (fc @ fc); Rr = Yc - np.outer(fc, psi)
    Sg = Rr.T @ Rr / (len(f) - 2); w = np.linalg.solve(Sg, psi); return w / (psi @ w), psi
def est(rows, kind):
    return fitg(ns_arr(X5[rows], u2[rows]) if kind == "ns" else u2[rows], Y3[rows])

R_, G = load_frbus(); b = b_persist(R_, G, 4)
POINT = {d: est(np.where(MASK[d])[0], KIND[d]) for d in DEFS}
mw = pd.read_csv(RES / "market_weights.csv", index_col=0); assert np.allclose(POINT["baseline"][0], mw.weight.values, atol=1e-8)
rng = np.random.default_rng(SEED)
IX = np.array([rng.integers(0, n, n) for _ in range(REPS25)]); R = len(IX)
BW = {d: np.empty((R, 3)) for d in DEFS}; BP = {d: np.empty((R, 3)) for d in DEFS}
for r in range(R):
    for d in DEFS:
        rows = IX[r][MASK[d][IX[r]]]; BW[d][r], BP[d][r] = est(rows, KIND[d])
Bd = pd.read_csv(RES / "weights_boot.csv"); k0 = min(len(Bd), R)
assert np.abs(BW["baseline"][:k0] - Bd[["w_ten", "w_eq", "w_usd"]].values[:k0]).max() < 1e-6      # first draws are the stored draws
S.add("reps", R)
ci = lambda a, lo=5, hi=95: (float(np.nanpercentile(a, lo)), float(np.nanpercentile(a, hi)))

# ---- (1) monthly classification
Xr = cases.inputs(data.load(), "rstar")[MV]
Z = Xr.diff(12).loc["1996-01":END].dropna(); idx = Z.index; Zv = Z.values
inper = lambda a, e: np.array([(p >= pd.Period(a, "M")) and (p <= pd.Period(e, "M")) for p in idx])
SETS = {"all": np.ones(len(idx), bool), "1998-2001": inper("1998-01", "2001-12"), "2022-24": inper("2022-03", "2024-12")}
def classify(wM, wB, t):
    m, f = Zv @ wM, Zv @ wB; opp = np.sign(m) != np.sign(f)
    return dict(agree=~opp, near_zero=opp & (np.minimum(abs(m), abs(f)) < t), opposing=opp & (np.minimum(abs(m), abs(f)) >= t), big_gap=abs(f - m) >= t)
rows = []
for d in DEFS:
    wM0, psi0 = POINT[d]; wB0 = b / (b @ psi0)
    for t in (0.10, 0.25):
        c0 = classify(wM0, wB0, t)
        draws = [classify(BW[d][r], b / (b @ BP[d][r]), t) for r in range(R)]
        for sname, msk in SETS.items():
            for k in c0:
                v = c0[k][msk].mean(); l, u = ci([x[k][msk].mean() for x in draws])
                rows.append(dict(definition=d, threshold=t, period=sname, category=k, share=v, lo=l, hi=u, n_months=int(msk.sum()), n_count=int(c0[k][msk].sum())))
                if d == "baseline": S.add(f"mo_{sname}_t{int(round(t*100))}_{k}", v); S.add(f"mo_{sname}_t{int(round(t*100))}_{k}_n", int(c0[k][msk].sum()))
pd.DataFrame(rows).to_csv(RES / "25_monthly_classes.csv", index=False, float_format="%.6g")
# magnitudes by month, for a figure and for the reader (baseline)
wM0, psi0 = POINT["baseline"]; wB0 = b / (b @ psi0)
mon = pd.DataFrame({"month": idx.astype(str), "market": Zv @ wM0, "frbus": Zv @ wB0}); mon["D"] = mon.frbus - mon.market
mon.to_csv(RES / "25_monthly_readings.csv", index=False, float_format="%.6g")
for sname, msk in SETS.items():
    S.add(f"mo_{sname}_max_abs_gap", float(np.abs(mon.D.values[msk]).max())); S.add(f"mo_{sname}_mean_abs_gap", float(np.abs(mon.D.values[msk]).mean()))
# magnitude of readings when the calibrations oppose or agree
S.add("mo_all_share_market_abs_gt_025", float((np.abs(mon.market) >= 0.25).mean()))
# among months with a material market reading (|M| >= 0.25): share where B has the same sign and where |B-M| < 0.25
mm = np.abs(mon.market.values) >= 0.25
S.add("mo_all_material_n", int(mm.sum())); S.add("mo_all_material_same_sign", float((np.sign(mon.market.values[mm]) == np.sign(mon.frbus.values[mm])).mean()))
S.add("mo_all_material_gap_lt_025", float((np.abs(mon.D.values[mm]) < 0.25).mean()))

# ---- (2) proportionality and contrast, per definition, common draws
def quant(w, psi):
    wB = b / (b @ psi); c = wB[2] * w[1] - wB[1] * w[2]
    contrast = (wB[2] * USD - wB[1] * EQ) - (w[2] * USD - w[1] * EQ)        # dollar part less equity part, FRB/US less market, in points
    ror = (wB[2] * USD / (wB[1] * EQ)) / (w[2] * USD / (w[1] * EQ))
    return dict(cross=c, contrast_diff=contrast, ror=ror, bpsi=b @ psi)
Q0 = {d: quant(*POINT[d]) for d in DEFS}; QB = {d: [quant(BW[d][r], BP[d][r]) for r in range(R)] for d in DEFS}
prow = []
for d in DEFS:
    for k in Q0[d]:
        a = np.array([x[k] for x in QB[d]]); l, u = ci(np.where(np.isfinite(a), a, np.nan))
        row = dict(definition=d, quantity=k, point=Q0[d][k], lo=l, hi=u, share_draws_positive=float((a > 0).mean()), diff_vs_baseline=np.nan, diff_lo=np.nan, diff_hi=np.nan, share_diff_positive=np.nan)
        if d != "baseline":
            dd = a - np.array([x[k] for x in QB["baseline"]]); dl, du = ci(dd); row.update(diff_vs_baseline=Q0[d][k] - Q0["baseline"][k], diff_lo=dl, diff_hi=du, share_diff_positive=float((dd > 0).mean()))
        prow.append(row); S.add(f"pr_{d}_{k}", Q0[d][k]); S.add(f"pr_{d}_{k}_lo", l); S.add(f"pr_{d}_{k}_hi", u)
pd.DataFrame(prow).to_csv(RES / "25_proportionality.csv", index=False, float_format="%.6g")
S.save(); print(f"done, {R} draws, {time.time() - T0:.0f}s")
