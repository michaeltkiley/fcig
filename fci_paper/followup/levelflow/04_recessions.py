"""Sample sizes and recessions (USREC, NBER) in each estimation / evaluation sample, and a descriptive logit: any recession month in t+1..t+12 on level and flow
(in-sample only, HAC 18, standardised; the number of independent episodes is what limits it)."""
import numpy as np, pandas as pd, statsmodels.api as sm
from common import *
rec = monthly("USREC").reindex(pd.period_range("1970-01", "2026-10", freq="M")).fillna(0)
ep = (rec.diff().fillna(0) == 1)
starts = [str(p) for p in rec.index[ep]]
rows = []
D = monthly_design(load_indexes()["Market|rstar"], "pay")  # baseline sample (common to all series)
fut = pd.Series([rec.loc[t + 1:t + 12].max() for t in D.index], index=D.index)
rows.append({"item": "monthly sample (payroll/unemployment projections)", "first": str(D.index[0]), "last": str(D.index[-1]), "n": len(D)})
rows.append({"item": "origins with a recession month in t+1..t+12", "n": int(fut.sum())})
rows.append({"item": "recession episodes starting in the sample window", "n": ",".join(s for s in starts if "1976-03" <= s <= "2018-12")})
oo = D.loc["1995-01":]
rows.append({"item": "OOS origins 1995-01 on", "n": len(oo), "first": str(oo.index[0]), "last": str(oo.index[-1])})
rows.append({"item": "OOS origins with a recession in next 12m", "n": int(fut.loc[oo.index].sum())})
rows.append({"item": "OOS recession episodes (2001, 2007-09; 2020 dropped with covid window)", "n": ",".join(s for s in starts if "1995-01" <= s <= "2018-12")})
Q = quarterly_design(load_indexes()["Market|rstar"]); rows.append({"item": "quarterly sample (GDP)", "first": str(Q.index[0]), "last": str(Q.index[-1]), "n": len(Q)})
pd.DataFrame(rows).to_csv(OUT / "sample_counts.csv", index=False); print(pd.DataFrame(rows).to_string())
lg = []
for lab, x in load_indexes().items():
    D = monthly_design(x, "pay"); y = pd.Series([rec.loc[t + 1:t + 12].max() for t in D.index], index=D.index)
    r = {}
    for k, cols in (("lvl", ["lvl"]), ("flw", ["flw"]), ("both", ["lvl", "flw"])):
        m = sm.Logit(y, sm.add_constant(D[cols])).fit(disp=0, cov_type="HAC", cov_kwds={"maxlags": 18})
        for c in cols: r[f"z_{c}_{k}"] = m.tvalues[c]
        r[f"pr2_{k}"] = m.prsquared
    lg.append({"series": lab, "n": len(D), "events_months": int(y.sum()), **r}); 
pd.DataFrame(lg).to_csv(OUT / "recession_logit.csv", index=False); print(pd.DataFrame(lg).round(2).to_string())
