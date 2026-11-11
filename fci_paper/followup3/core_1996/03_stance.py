"""(iii) stance: index given the funds-rate gap, all rows. Writes out/stance.csv"""
from common import *
rows = []
for row in ROWS:
    for yn in ("du", "pay"):
        ow = own(yn)
        for step in STEPS:
            for key, lab in SERIES:
                if ROWS[row].get("w2019") and key != "market": continue
                for form in ("flow", "mixed"):
                    D = design(yn, step, key, form, row)
                    r0 = hac_ols(D, ow); r1 = hac_ols(D, ow + ["ff"]); r2 = hac_ols(D, ow + ["idx"]); r3 = hac_ols(D, ow + ["ff", "idx"])
                    F = oos(D, {"M1": ow + ["ff"], "M3": ow + ["ff", "idx"]}, row)
                    e1 = F.y - F.M1; e3 = F.y - F.M3
                    d = e1 ** 2 - e3 ** 2; cw = d + (F.M1 - F.M3) ** 2
                    rows.append(dict(row=row, outcome=yn, step=step, series=key, form=form, n=len(D), gain_idx_given_ff=r3.rsquared_adj - r1.rsquared_adj,
                                     gain_ff_given_idx=r3.rsquared_adj - r2.rsquared_adj, t_idx_both=r3.tvalues["idx"], t_ff_both=r3.tvalues["ff"],
                                     first_oos=str(F.index[0]), n_oos=len(F), n_rec_oos=n_recessions(F.index), rmse_ratio=float(np.sqrt((e3 ** 2).mean() / (e1 ** 2).mean())),
                                     cw=mean_t(cw.values), dm=mean_t(d.values)))
    print(row, flush=True)
pd.DataFrame(rows).to_csv(OUT / "stance.csv", index=False)
