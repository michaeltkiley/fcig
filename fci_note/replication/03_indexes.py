"""Step 3. Every index at every step of the construction: nominal, real, r* (baseline, Laubach-Williams) and r* (Kiley, check).
Output: output/indexes_<case>.csv (levels in their units, demeaned 1973-2026) and output/groups_<case>.csv (contributions by group)."""
import pandas as pd
from fci import data, cases, indexes as I

D = data.load()
conv = pd.read_csv(data.OUT / "conversions.csv", index_col=0).to_2y
w = pd.read_csv(data.OUT / "market_weights.csv", index_col=0).weight.values
GROUP = {"policy": "rates", "y10": "rates", "mortgage_spread": "rates", "bbb_spread": "rates", "equities": "equities", "dollar": "dollar", "dollar_gs": "dollar", "house": "other"}

for case, rs in (("nominal", None), ("real", None), ("rstar", "rstar LW"), ("rstar_kiley", "rstar Kiley")):
    X = cases.inputs(D, "rstar" if rs else case, rstar=rs or "rstar LW")
    mkt, cm = I.market(X, w)
    gs, cg = I.gs(X, conv["GS"])
    ep, cf, gi = I.frbus(X, house=False)
    eph, cfh, gih = I.frbus(X, house=True)
    f1, _ = I.fcig(X, 4); f3, _ = I.fcig(X, 12)
    out = pd.DataFrame({"market": mkt, "gs": gs, "frbus": ep, "frbus_hp": eph, "frbus_gi": gi, "frbus_gi_hp": gih, "fcig_1yr": f1, "fcig_3yr": f3})
    for nm in ("NFCI", "ANFCI"):
        s = pd.read_csv(data.DATA / f"{nm}.csv"); s = pd.Series(s.iloc[:, 1].values, index=pd.to_datetime(s.iloc[:, 0]))
        s = s.groupby(s.index.to_period("M")).last()
        out[nm.lower()] = (s - s.loc[data.START:data.END].mean()) * conv[nm]
    out.loc[data.START:data.END].to_csv(data.OUT / f"indexes_{case}.csv", float_format="%.4f")
    G = {}
    for lab, C in (("market", cm), ("gs", cg), ("frbus_hp", cfh)):
        g = C.T.groupby(lambda c: GROUP[c]).sum().T
        for k in g:
            G[f"{lab}|{k}"] = g[k]
    pd.DataFrame(G).loc[data.START:data.END].to_csv(data.OUT / f"groups_{case}.csv", float_format="%.4f")
    print(f"{case:12s} latest: " + ", ".join(f"{c} {v:+.2f}" for c, v in out.loc[data.END].items()))
