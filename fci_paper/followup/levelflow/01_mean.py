"""(a) Mean projections of the 12-month change of the unemployment gap and 12-month payroll growth on the level, the 12-month change (flow), and both,
with own lags. In-sample HAC(18) t-stats and adjusted R2 gain; recursive out-of-sample RMSE ratio to own lags with a paired Diebold-Mariano t.
Tests counted: 2 outcomes x 14 series x (t_level, t_flow in the joint spec, and 3 OOS DM) = 2*14*5 = 140 statistics; read as a pattern, not one by one."""
import numpy as np, pandas as pd, statsmodels.api as sm
from common import *

def ols(D, cols):
    X = sm.add_constant(D[cols]); return sm.OLS(D.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 18})

def oos(D, own, cols_list):
    errs = {k: [] for k in cols_list}; idx = []
    for t in pd.period_range(FIRST_OOS, "2025-10", freq="M"):
        if t not in D.index: continue
        tr = D.loc[:t - H]
        if len(tr) < 100: continue
        idx.append(t)
        for k, cols in cols_list.items():
            c = own + cols
            b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[c].values], tr.y.values, rcond=None)[0]
            errs[k].append(D.loc[t, "y"] - b @ np.r_[1, D.loc[t, c].values.astype(float)])
    return {k: np.array(v) for k, v in errs.items()}

rows = []
for yn, own in (("du", ["u", "du12"]), ("pay", ["g12", "g3"])):
    for lab, x in load_indexes().items():
        D = monthly_design(x, yn)
        r0 = ols(D, own); rL = ols(D, own + ["lvl"]); rF = ols(D, own + ["flw"]); rB = ols(D, own + ["lvl", "flw"])
        # Wald for joint, and level-given-flow / flow-given-level
        row = {"outcome": yn, "series": lab, "n": len(D), "first": str(D.index[0]), "last": str(D.index[-1]),
               "b_lvl_alone": rL.params["lvl"], "t_lvl_alone": rL.tvalues["lvl"], "gain_lvl": rL.rsquared_adj - r0.rsquared_adj,
               "b_flw_alone": rF.params["flw"], "t_flw_alone": rF.tvalues["flw"], "gain_flw": rF.rsquared_adj - r0.rsquared_adj,
               "b_lvl_both": rB.params["lvl"], "t_lvl_both": rB.tvalues["lvl"], "b_flw_both": rB.params["flw"], "t_flw_both": rB.tvalues["flw"],
               "gain_both": rB.rsquared_adj - r0.rsquared_adj, "sd_y": D.y.std()}
        e = oos(D, own, {"own": [], "lvl": ["lvl"], "flw": ["flw"], "both": ["lvl", "flw"]})
        for k in ("lvl", "flw", "both"):
            d = e[k] ** 2 - e["own"] ** 2
            dm = sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": 12}).tvalues[0]
            row[f"rmse_{k}"] = float(np.sqrt((e[k] ** 2).mean() / (e["own"] ** 2).mean())); row[f"dm_{k}"] = float(dm)
        row["n_oos"] = len(e["own"])
        rows.append(row); print(yn, lab, round(row["t_lvl_both"], 2), round(row["t_flw_both"], 2), round(row["rmse_flw"], 3), flush=True)
pd.DataFrame(rows).to_csv(OUT / "mean_results.csv", index=False)
