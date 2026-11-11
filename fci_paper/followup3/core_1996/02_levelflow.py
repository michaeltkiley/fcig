"""(ii) level versus flow, all rows. du and payrolls; own lags + level + flow; HAC 18. Writes out/levelflow.csv"""
from common import *
rows = []
for row in ROWS:
    for yn in ("du", "pay"):
        for step in STEPS:
            for key, lab in SERIES:
                if ROWS[row].get("w2019") and key != "market": continue
                D = design(yn, step, key, "lf", row); ow = own(yn)
                r0 = hac_ols(D, ow); rB = hac_ols(D, ow + ["lvl", "flw"]); rF = hac_ols(D, ow + ["flw"])
                rows.append(dict(row=row, outcome=yn, step=step, series=key, n=len(D), t_flw=rB.tvalues["flw"], t_lvl=rB.tvalues["lvl"], b_flw=rB.params["flw"],
                                 t_flw_alone=rF.tvalues["flw"], gain_flw=rF.rsquared_adj - r0.rsquared_adj, gain_both=rB.rsquared_adj - r0.rsquared_adj))
    print(row, flush=True)
pd.DataFrame(rows).to_csv(OUT / "levelflow.csv", index=False)
