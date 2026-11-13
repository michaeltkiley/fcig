"""Step 29. How much of the excess bond premium do the three asset prices carry? (FP-A54, item 8)
Monthly, 1973-01 to the sample end: OLS of the Gilchrist-Zakrajsek excess bond premium (and the GZ spread) on the three r*-step asset series of the paper
(10-year yield less expected inflation less r*, equity valuation, real dollar), in levels and in 12-month changes (the history comparison uses 12-month changes); R2 and the
R2 of each asset alone. Also from 1996. Data: data/ebp.csv, Federal Reserve Board FEDS Notes file ebp_csv.csv, downloaded 13 Nov 2026.
Writes results/29_credit.csv and scalars_29_credit.csv."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from lib import data, cases
from lib.agree_core import MV
from lib.config import RES, DATA, START, END
from lib.report import Scalars

S = Scalars("29_credit")
e = pd.read_csv(DATA / "ebp.csv", parse_dates=["date"]); e.index = e.date.dt.to_period("M")
X = cases.inputs(data.load(), "rstar")[MV]
rows = []
for y in ("ebp", "gz_spread"):
    for form in ("level", "d12"):
        for start in (START, "1996-01"):
            Z = X.join(e[y]).loc[:END]
            Z = Z.diff(12) if form == "d12" else Z
            Z = Z.loc[start:].dropna()
            r = sm.OLS(Z[y], sm.add_constant(Z[MV])).fit()
            row = dict(dep=y, form=form, start=start, n=len(Z), r2=r.rsquared, **{f"r2_{v}": sm.OLS(Z[y], sm.add_constant(Z[[v]])).fit().rsquared for v in MV},
                       **{f"b_{v}": r.params[v] for v in MV})
            rows.append(row); tag = f"{y}_{form}_{start[:4]}"
            for k in ("r2", "r2_y10", "r2_equities", "r2_dollar", "n"):
                S.add(f"{tag}_{k}", row[k])
T = pd.DataFrame(rows); T.to_csv(RES / "29_credit.csv", index=False, float_format="%.6g"); S.save()
print(T.round(3).to_string())
