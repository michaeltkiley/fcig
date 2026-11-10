"""Step 4. Implied policy trade-off (Phillips multiplier, Barnichon-Mesters 2021) from the draws of step 3.
kappa_H = P_H / U_H: the core PCE price level at month H (percent) per percentage-point year of cumulative unemployment-gap response; the sacrifice ratio is -1/kappa_H.
Confidence set: {kappa : the 90% interval of P_H - kappa U_H contains zero} on a grid (Anderson-Rubin style, because U_H can be near zero); unbounded sets reach the grid edge.
Paired difference (r*-gap with FCI minus nominal with FCI) uses the same announcement draws; draws with either cumulative unemployment response below 0.05 pp-years are dropped.
Output: results/tradeoff.csv, results/tradeoff_diff.csv"""
import numpy as np, pandas as pd
import cases as CS
from lib import model as M
from lib.paths import RESULTS, OUT

def load(c, L):
    z = np.load(OUT / "draws" / f"{CS.case_id(c)}_L{L}.npz"); return dict(lags=L, s0=z["s0"], sd=z["sd"])

rows = []
for c in CS.unique_cases():
    for L in M.LAGS: rows += M.multiplier_rows(CS.spec(c), load(c, L))
pd.DataFrame(rows).to_csv(RESULTS / "tradeoff.csv", index=False, float_format="%.4f")

base = {(c["form"], c["fci"]): c for c in CS.PANELS[0]["cases"]}; diff = []
for L in M.LAGS:
    a, b = load(base[("rstar", "rstar")], L), load(base[("nom", "nom")], L)
    Ua, Ub = np.cumsum(a["sd"][:, :, 0], axis=1) / 12, np.cumsum(b["sd"][:, :, 0], axis=1) / 12
    for h in M.HORIZ:
        ok = (Ua[:, h] > 0.05) & (Ub[:, h] > 0.05); dk = a["sd"][ok, h, 1] / Ua[ok, h] - b["sd"][ok, h, 1] / Ub[ok, h]
        ka = a["s0"][h, 1] / (np.cumsum(a["s0"][:, 0])[h] / 12); kb = b["s0"][h, 1] / (np.cumsum(b["s0"][:, 0])[h] / 12)
        diff.append(dict(lags=L, H=h, kappa_diff=ka - kb, lo=np.percentile(dk, 5), hi=np.percentile(dk, 95), share=float(ok.mean())))
pd.DataFrame(diff).to_csv(RESULTS / "tradeoff_diff.csv", index=False, float_format="%.4f")
print(pd.DataFrame(rows).query("H == 24 and lags == 12")[["form", "fci", "start", "end", "t2020", "trend", "kappa", "k_lo", "k_hi", "bounded"]].round(2).to_string(index=False))
