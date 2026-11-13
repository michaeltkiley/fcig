"""Step 30. The r* step and FCI* (FP-A54 item 9, FP-A55).
Question (fixed before the formal run; an exploratory run of the same correlations for the futures-based index is recorded in FP-A55): does measuring yields and valuations
relative to r* move the readings toward the gap between financial conditions and their neutral level as estimated by Caballero, Caravello and Simsek (FCI-G less FCI*)?
For each of the four calibrations (common scale, as step 26) and three versions of the inputs (real; r* step with r* held at its 1973-2026 mean; r* step, the paper's series), the
quarterly mean of the level reading and its 4-quarter change are correlated with FCI-G, FCI* and the gap FCI-G less FCI*, 1990Q2-2024Q4. The FCI* series is one-sided.
Writes results/30_fcistar.csv and scalars_30_fcistar.csv."""
import numpy as np, pandas as pd
from lib import data, cases, indexes as I
from lib.agree_core import MV, load_frbus, b_persist, ns_arr
from lib.config import RES, DATA, START, END
from lib.report import Scalars

S = Scalars("30_fcistar")
raw = I.events_raw(); u2 = raw.UST2Y.values; Y3 = raw[["UST10Y", "SP500", "DXY"]].values
def fitg(f, Yv):
    fc = f - f.mean(); Yc = Yv - Yv.mean(0); psi = (fc @ Yc) / (fc @ fc); Rr = Yc - np.outer(fc, psi)
    Sg = Rr.T @ Rr / (len(f) - 2); w = np.linalg.solve(Sg, psi); return w / (psi @ w), psi
wF, pF = fitg(ns_arr(raw[["MP1", "MP2", "ED2", "ED3", "ED4"]].values, u2), Y3); wY, _ = fitg(u2, Y3)
R_, Gq = load_frbus(); b = b_persist(R_, Gq, 4)
g = np.array([I.GS_W["y10"], I.GS_W["equities"], I.GS_W["dollar_gs"]])
W = {"F": wF, "Y": wY / (wY @ pF), "B": b / (b @ pF), "G": g / (g @ pF)}
D0 = data.load()
INP = {"real": cases.inputs(D0, "real")[MV], "rstar_fixed": cases.inputs(D0.assign(**{"rstar fixed": float(D0["rstar LW"].loc[START:END].mean())}), "rstar", rstar="rstar fixed")[MV],
       "rstar": cases.inputs(D0, "rstar")[MV]}
F = pd.read_excel(DATA / "fcistar_results.xlsx"); F.index = pd.PeriodIndex(F.Date.dt.to_period("Q"))
T = pd.DataFrame({"fcig": F.FCI, "fcistar": F.fci_star, "gap": F.FCI - F.fci_star})
q = lambda s: s.groupby(s.index.asfreq("Q")).mean()
rows = []
for inp, X in INP.items():
    Xd = X - X.loc[START:END].mean()
    for k, w in W.items():
        J = T.join(q(Xd @ w).rename("r")).dropna()
        for form, Z in (("level", J), ("d4", J.diff(4).dropna())):
            row = dict(inputs=inp, calibration=k, form=form, n=len(Z), first=str(Z.index.min()), last=str(Z.index.max()),
                       **{f"corr_{c}": float(Z.r.corr(Z[c])) for c in ("fcig", "fcistar", "gap")})
            rows.append(row)
            for c in ("fcig", "fcistar", "gap"):
                S.add(f"{inp}_{k}_{form}_{c}", row[f"corr_{c}"])
J = T.join(q(D0["rstar LW"]).rename("rstar")).dropna()
S.add("corr_rstar_fcistar_level", float(J.rstar.corr(J.fcistar))); S.add("corr_rstar_fcistar_d4", float(J.diff(4).rstar.corr(J.diff(4).fcistar)))
S.add("n_q", len(J)); S.add("first_q", str(J.index.min())); S.add("last_q", str(J.index.max()))
R = pd.DataFrame(rows); R.to_csv(RES / "30_fcistar.csv", index=False, float_format="%.6g"); S.save()
print(R.pivot_table(index=["form", "calibration"], columns="inputs", values="corr_gap").round(2).to_string())
print(R.pivot_table(index=["form", "calibration"], columns="inputs", values="corr_fcig").round(2).to_string())
print("corr r*, FCI*: level", round(J.rstar.corr(J.fcistar), 2), "d4", round(J.diff(4).rstar.corr(J.diff(4).fcistar), 2))
