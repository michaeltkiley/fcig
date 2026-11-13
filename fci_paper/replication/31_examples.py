"""Step 31. The worked examples of the introduction and Section 2 (FP-A54 item 7, FP-A55, FP-A56).
(a) Two announcements read by the four calibrations (common scale, as step 26): 28 January 2004 (the statement dropped 'considerable period'; the three asset prices moved
    roughly in the usual proportions) and 3 January 2001 (an intermeeting cut; stocks rose sharply while the dollar rose). Window moves (USMPD), each calibration's reading and the
    contribution of each asset (weight x move).
(b) The 1980 and 2023 annual averages of the 10-year yield, expected inflation, r* and the index readings at the nominal, real and r* steps (futures-based weights).
Writes results/31_examples.csv and scalars_31_examples.csv."""
import numpy as np, pandas as pd
from lib import data, cases, indexes as I
from lib.agree_core import MV, load_frbus, b_persist, ns_arr
from lib.config import RES, START, END
from lib.report import Scalars

S = Scalars("31_examples")
raw = I.events_raw(); u2 = raw.UST2Y.values; Y3 = raw[["UST10Y", "SP500", "DXY"]].values
def fitg(f, Yv):
    fc = f - f.mean(); Yc = Yv - Yv.mean(0); psi = (fc @ Yc) / (fc @ fc); Rr = Yc - np.outer(fc, psi)
    Sg = Rr.T @ Rr / (len(f) - 2); w = np.linalg.solve(Sg, psi); return w / (psi @ w), psi
f = ns_arr(raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values, u2); wF, pF = fitg(f, Y3); wY, _ = fitg(u2, Y3)
R_, Gq = load_frbus(); b = b_persist(R_, Gq, 4)
g = np.array([I.GS_W["y10"], I.GS_W["equities"], I.GS_W["dollar_gs"]])
W = {"F": wF, "Y": wY / (wY @ pF), "B": b / (b @ pF), "G": g / (g @ pF)}
for j, a in enumerate(("ten", "eq", "usd")):
    S.add(f"psi_{a}", pF[j])
rows = []
for tag, d in (("jan2004", "2004-01-28"), ("jan2001", "2001-01-03")):
    i = int(np.where(raw.Date == pd.Timestamp(d))[0][0]); x = Y3[i]
    S.add(f"{tag}_d2y", 100 * u2[i]); S.add(f"{tag}_d10y", 100 * x[0]); S.add(f"{tag}_deq", x[1]); S.add(f"{tag}_dusd", x[2]); S.add(f"{tag}_ns", f[i])
    rd = {k: float(w @ x) for k, w in W.items()}
    for k, w in W.items():
        S.add(f"{tag}_{k}", rd[k])
        for j, a in enumerate(("ten", "eq", "usd")):
            S.add(f"{tag}_{k}_c_{a}", float(w[j] * x[j])); rows.append(dict(case=tag, calibration=k, asset=a, move=x[j], weight=w[j], contribution=w[j] * x[j]))
    S.add(f"{tag}_min", min(rd.values())); S.add(f"{tag}_max", max(rd.values()))
    # the usual response scaled to this announcement's news, and the departure from it
    for j, a in enumerate(("ten", "eq", "usd")):
        S.add(f"{tag}_usual_{a}", float(pF[j] * f[i]))
D0 = data.load()
for c in ("nominal", "real", "rstar"):
    X = cases.inputs(D0, c)[MV]; Xd = X - X.loc[START:END].mean(); R = Xd @ wF
    for y in ("1980", "2023"):
        S.add(f"lv_{c}_{y}", float(R.loc[y].mean())); S.add(f"lv_{c}_{y}_y10", float(X.y10.loc[y].mean()))
        for j, v in enumerate(MV):
            S.add(f"lv_{c}_{y}_c_{v}", float((Xd[v] * wF[j]).loc[y].mean()))
    S.add(f"lv_{c}_diff", float(R.loc["2023"].mean() - R.loc["1980"].mean()))
for y in ("1980", "2023"):
    for v, nm in (("y10", "y10"), ("einf_10y", "einf"), ("rstar LW", "rstar"), ("cape", "cape")):
        S.add(f"yr_{y}_{nm}", float(D0[v].loc[y].mean()))
pd.DataFrame(rows).to_csv(RES / "31_examples.csv", index=False, float_format="%.6g"); S.save()
print(pd.Series(S.items).to_string())
