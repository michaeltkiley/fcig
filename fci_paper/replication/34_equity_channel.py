"""Step 34. The equity channel: how much of a policy move each asset carries, in the announcement windows and in FRB/US (new version, stage 6; FP-A67).

(1) Windows: the share of a one-point policy move carried by the 10-year yield, equities and the dollar, w_a psi_a (the shares sum to one), for the market
    weights (with 90 percent intervals from the announcement bootstrap, results/weights_boot.csv) and for the FRB/US and GS weights on the same three assets
    on the common scale (results/32_weights_common.csv).
(2) FRB/US: each index's reading of a persistent 1 pp funds-rate hike in FRB/US, split by variable, at quarters 1, 4 and 8 (results/33_hike_readings.csv):
    the share of the reading carried by equities, rates (funds rate, 10-year, spreads) and the dollar.
(3) Variance: equities' share of each level index's variance (step 32).
Writes results/34_equity_channel.csv and scalars_34_equity_channel.csv."""
import numpy as np, pandas as pd
from lib.config import RES
from lib.report import Scalars

S = Scalars("34_equity_channel")
mw = pd.read_csv(RES / "market_weights.csv", index_col=0)
psi = mw.response.values
WC = pd.read_csv(RES / "32_weights_common.csv", index_col=0)
B = pd.read_csv(RES / "weights_boot.csv")
rows = []
AS = ["ten", "eq", "usd"]
for k in ("market", "gs", "frbus"):
    sh = WC[k].values * psi / (WC[k].values @ psi)
    for j, a in enumerate(AS):
        r = dict(part="window", index=k, asset=a, horizon="window", share=sh[j])
        if k == "market":
            d = B[f"w_{a}"] * B[f"psi_{a}"]; r["lo"], r["hi"] = np.percentile(d, [5, 95])
        rows.append(r); S.add(f"win_{k}_{a}", sh[j])
HR = pd.read_csv(RES / "33_hike_readings.csv")
GRP = {"policy": "rates", "y10": "rates", "mortgage_spread": "rates", "bbb_spread": "rates", "equities": "eq", "dollar": "usd", "dollar_gs": "usd"}
for k in ("market", "gs", "frbus"):
    comp = [c for c in HR.columns if c.startswith(k + "_") and c != f"{k}_reading"]
    for q in (1, 4, 8):
        r0 = HR[HR.quarter == q].iloc[0]; tot = r0[f"{k}_reading"]
        g = {}
        for c in comp:
            v = c[len(k) + 1:]; g[GRP[v]] = g.get(GRP[v], 0.0) + r0[c]
        for grp, val in g.items():
            rows.append(dict(part="frbus_hike", index=k, asset=grp, horizon=f"q{q}", share=val / tot, contribution=val, reading=tot))
            S.add(f"hike_{k}_{grp}_q{q}", val / tot)
        S.add(f"hike_{k}_reading_q{q}", tot)
V = pd.read_csv(RES / "32_variance_by_asset.csv")
for _, r in V.iterrows():
    rows.append(dict(part="variance", index=r["index"], asset={"equities": "eq", "dollar": "usd", "rates": "rates"}[r.group], horizon=r.basis, share=r.share))
T = pd.DataFrame(rows); T.to_csv(RES / "34_equity_channel.csv", index=False, float_format="%.4f")
print(T[T.asset == "eq"].round(2).to_string(index=False))
S.save()
