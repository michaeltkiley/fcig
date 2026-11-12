"""Step 3. Every index at every step of the construction: nominal, real, r* (baseline, Laubach-Williams) and r* (Kiley, check).
Writes results/indexes_<case>.csv (levels in their units, demeaned over 1973-2026), groups_<case>.csv (contributions by group), market_variants.csv
(the r* market index under the alternative weights of step 2) and index_boot.csv (index summaries for each bootstrap draw of the weights)."""
import numpy as np, pandas as pd
from lib import data, cases, indexes as I, compare as K
from lib.config import RES, START, END

D = data.load()
conv = pd.read_csv(RES / "conversions.csv", index_col=0).to_2y
w = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
GROUP = {"policy": "rates", "y10": "rates", "mortgage_spread": "rates", "bbb_spread": "rates", "equities": "equities", "dollar": "dollar", "dollar_gs": "dollar", "house": "other"}
XS = {}
for case, rs in (("nominal", None), ("real", None), ("rstar", "rstar LW"), ("rstar_kiley", "rstar Kiley")):
    X = cases.inputs(D, "rstar" if rs else case, rstar=rs or "rstar LW")
    XS[case] = X
    mkt, cm = I.market(X, w)
    gs, cg = I.gs(X, conv["GS"])
    ep, cf, gi = I.frbus(X, house=False)
    eph, cfh, gih = I.frbus(X, house=True)
    f1, _ = I.fcig(X, 4); f3, _ = I.fcig(X, 12)
    out = pd.DataFrame({"market": mkt, "gs": gs, "frbus": ep, "frbus_hp": eph, "frbus_gi": gi, "frbus_gi_hp": gih, "fcig_1yr": f1, "fcig_3yr": f3})
    for nm in ("NFCI", "ANFCI"):
        s = pd.read_csv(data.DATA / f"{nm}.csv"); s = pd.Series(s.iloc[:, 1].values, index=pd.to_datetime(s.iloc[:, 0]))
        s = s.groupby(s.index.to_period("M")).last()
        out[nm.lower()] = (s - s.loc[START:END].mean()) * conv[nm]
    out.loc[START:END].to_csv(RES / f"indexes_{case}.csv", float_format="%.5f")
    G = {}
    for lab, C in (("market", cm), ("gs", cg), ("frbus_hp", cfh)):
        g = C.T.groupby(lambda c: GROUP[c]).sum().T
        for k in g:
            G[f"{lab}|{k}"] = g[k]
    pd.DataFrame(G).loc[START:END].to_csv(RES / f"groups_{case}.csv", float_format="%.5f")
    print(f"{case:12s} latest: " + ", ".join(f"{c} {v:+.2f}" for c, v in out.loc[END].items()))

# Market index under alternative weights (r* baseline inputs)
V = pd.read_csv(RES / "weights_variants.csv").set_index("variant")
Xd = cases.demean(XS["rstar"][I.MARKET_VARS])
pd.DataFrame({k: Xd @ V.loc[k, ["w_ten", "w_eq", "w_usd"]].values for k in V.index}).loc[START:END].to_csv(RES / "market_variants.csv", float_format="%.5f")

# Bootstrap of the weights: what the sampling error of the policy-news regressions does to the index (each step)
Bt = pd.read_csv(RES / "weights_boot.csv")[["w_ten", "w_eq", "w_usd"]].values
rows = []
base = {c: pd.read_csv(RES / f"indexes_{c}.csv", index_col=0) for c in ("nominal", "real", "rstar")}
for b in Bt:
    r = {}
    for c in ("nominal", "real", "rstar"):
        I0 = base[c].copy(); I0.index = pd.PeriodIndex(I0.index, freq="M")
        I0 = I0.loc["1974-01":]
        m = (cases.demean(XS[c][I.MARKET_VARS]) @ b).loc["1974-01":]
        z = pd.concat([m.rename("market"), I0[["gs", "frbus", "frbus_hp"]]], axis=1)
        z90 = z.loc["1990-01":] - z.loc["1990-01":].mean()
        r[f"{c}_corr_gs"] = m.corr(I0.gs); r[f"{c}_corr_frbus"] = m.corr(I0.frbus)
        r[f"{c}_corr_gs_chg"] = m.diff(12).corr(I0.gs.diff(12)); r[f"{c}_corr_frbus_chg"] = m.diff(12).corr(I0.frbus.diff(12))
        r[f"{c}_range_long"] = K.spread(z).mean(); r[f"{c}_range_ninety"] = K.spread(z90).mean()
        r[f"{c}_latest"] = m.iloc[-1]; r[f"{c}_corr_base"] = m.corr(I0.market)
        r[f"{c}_latest_gap_gs"] = m.iloc[-1] - I0.gs.iloc[-1]; r[f"{c}_latest_gap_frbus"] = m.iloc[-1] - I0.frbus.iloc[-1]
    rows.append(r)
pd.DataFrame(rows).to_csv(RES / "index_boot.csv", index=False)
print(pd.DataFrame(rows).describe().round(2).loc[["mean", "std", "min", "max"]].T.filter(like="rstar", axis=0))
