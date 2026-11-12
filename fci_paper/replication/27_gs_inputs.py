"""Step 27. Do the transformations produce the closeness? The four portfolios of step 26 applied to alternative input sets (FP-A46; the author's first priority).

INPUT SETS (all four portfolios on the SAME series in each set; weights unchanged; common normalization w'psi_F = 1 as in step 26):
  rstar      the paper's series: 10-year yield less expected inflation less r*; equities = earnings-yield gap to r* converted to CAPE log points; real broad dollar (100 ln)
  real_cape  10-year yield less expected inflation; equities = 100 ln CAPE (prices over a 10-year average of earnings, the documented GS equity concept); real broad dollar
  gs_inputs  the nearest publicly reproducible GS inputs: nominal 10-year yield; 100 ln CAPE; nominal broad dollar (100 ln)
QUESTIONS (fixed before any number was read): for each set, the six pairwise mean absolute distances of the 12-month-change readings (1996-01..data end, bp), the share of months with the same sign
under all four, materially opposing months (any pair; and F-B only) at 10 and 25 bp, the episode averages (2008-09, 1998-2001, 2022-24); paired draws for F-G less the nearest other pair.
Announcement bootstrap as in step 26 (REPS_W draws; F, Y, psi_F redrawn; B, G fixed). Writes results/27_*.csv and scalars_27_gs_inputs.csv."""
import numpy as np, pandas as pd
from lib import data, cases, indexes as I
from lib.agree_core import load_frbus, b_persist, ns_arr
from lib.config import RES, SEED, END, REPS_W
from lib.report import Scalars

S = Scalars("27_gs_inputs")
raw = I.events_raw(); n = len(raw)
X5 = raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values; u2 = raw.UST2Y.values; Y3 = raw[["UST10Y", "SP500", "DXY"]].values
def fitg(f, Yv):
    fc = f - f.mean(); Yc = Yv - Yv.mean(0); psi = (fc @ Yc) / (fc @ fc); Rr = Yc - np.outer(fc, psi)
    Sg = Rr.T @ Rr / (len(f) - 2); w = np.linalg.solve(Sg, psi); return w / (psi @ w), psi
def est(rows):
    wF, pF = fitg(ns_arr(X5[rows], u2[rows]), Y3[rows]); wY, pY = fitg(u2[rows], Y3[rows]); return wF, pF, wY, pY
R_, Gq = load_frbus(); b = b_persist(R_, Gq, 4)
g = np.array([I.GS_W["y10"], I.GS_W["equities"], I.GS_W["dollar_gs"]])
NAMES = ["F", "Y", "B", "G"]; PAIRS = [(a, c) for i, a in enumerate(NAMES) for c in NAMES[i + 1:]]
def portfolios(wF, pF, wY, pY): return {"F": wF, "Y": wY / (wY @ pF), "B": b / (b @ pF), "G": g / (g @ pF)}
P0 = portfolios(*est(np.arange(n)))
rng = np.random.default_rng(SEED); IX = np.array([rng.integers(0, n, n) for _ in range(REPS_W)]); DR = [portfolios(*est(ix)) for ix in IX]
ci = lambda a: (float(np.nanpercentile(a, 5)), float(np.nanpercentile(a, 95)))

D0 = data.load()
SETS = {"rstar": cases.inputs(D0, "rstar")[["y10", "equities", "dollar"]],
        "real_cape": cases.inputs(D0, "real")[["y10", "equities", "dollar"]],
        "gs_inputs": cases.inputs(D0, "nominal")[["y10", "equities", "dollar_gs"]]}
EP = {"2008-09": ("2008-01", "2009-12"), "1998-2001": ("1998-01", "2001-12"), "2022-24": ("2022-03", "2024-12")}
rows, erows = [], []
for sname, X in SETS.items():
    Z = X.diff(12).loc["1996-01":END].dropna(); idx = Z.index; Zv = Z.values
    def summ(P):
        Rd = {k: Zv @ P[k] for k in NAMES}; out = {f"mad_{a}{c}": np.abs(Rd[a] - Rd[c]).mean() for a, c in PAIRS}
        out["mean_abs_F"] = np.abs(Rd["F"]).mean(); M = np.column_stack([Rd[k] for k in NAMES])
        out["all_same_sign"] = float((np.abs(np.sign(M).sum(1)) == 4).mean())
        for t in (0.10, 0.25):
            out[f"any_opp_t{int(t*100)}"] = float((((M >= t).any(1)) & ((M <= -t).any(1))).mean())
            out[f"FB_opp_t{int(t*100)}"] = float(((np.sign(Rd["F"]) != np.sign(Rd["B"])) & (np.minimum(np.abs(Rd["F"]), np.abs(Rd["B"])) >= t)).mean())
        others = [out[f"mad_{a}{c}"] for a, c in PAIRS if (a, c) != ("F", "G")]
        out["FG_minus_nearest"] = out["mad_FG"] - min(others)
        return out, M
    O0, M0 = summ(P0); OD = [summ(P)[0] for P in DR]
    for k, v in O0.items():
        l, u = ci([o[k] for o in OD]); rows.append(dict(inputs=sname, stat=k, point=v, lo=l, hi=u)); S.add(f"{sname}_{k}", v); S.add(f"{sname}_{k}_lo", l); S.add(f"{sname}_{k}_hi", u)
    for ep, (a, e) in EP.items():
        msk = np.array([(p >= pd.Period(a, "M")) and (p <= pd.Period(e, "M")) for p in idx])
        for j, k in enumerate(NAMES):
            v = float(M0[msk, j].mean()); erows.append(dict(inputs=sname, episode=ep, portfolio=k, mean=v)); S.add(f"{sname}_ep_{ep}_{k}", v)
    S.add(f"{sname}_n_months", len(Zv))
pd.DataFrame(rows).to_csv(RES / "27_gs_inputs.csv", index=False, float_format="%.6g")
pd.DataFrame(erows).to_csv(RES / "27_episodes.csv", index=False, float_format="%.6g")
S.save()
T = pd.DataFrame(rows); print(T[T.stat.str.startswith("mad_") | T.stat.isin(["all_same_sign", "any_opp_t25", "any_opp_t10", "FB_opp_t25", "FB_opp_t10", "FG_minus_nearest", "mean_abs_F"])].pivot(index="stat", columns="inputs", values="point").round(3))
print(T[T.stat == "FG_minus_nearest"].round(3)); print(pd.DataFrame(erows).pivot_table(index=["episode", "inputs"], columns="portfolio", values="mean").round(2))
