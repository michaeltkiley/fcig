"""(c) R2 of NFCI/ANFCI on the market-weights variables (10y yield, CAPE, real dollar) and plus Baa-10y spread; levels (1976-03 on) and 12m changes; correlations with market level/flow.
NFCI contributions file (raw/nfci_contributions.xlsx) is not in the repository: skipped. Sample: months with all variables."""
import numpy as np, pandas as pd, statsmodels.api as sm
from common import *
X, D = M(); D = D.copy(); D["spread"] = D.baa - D.y10
V = pd.concat([X[["mkt", "mkt_flw", "nfci", "anfci"]], D[["y10", "cape", "usd_real", "spread"]]], axis=1).loc["1976-03":"2026-09"].dropna()
# drop covid window? levels regression: keep all (descriptive)
rows = []
def r2(y, cols, data):
    m = sm.OLS(data[y], sm.add_constant(data[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": 12}); return m.rsquared, m
L = V.copy(); C = V.copy()
for c in ("mkt", "nfci", "anfci", "y10", "cape", "usd_real", "spread"): C[c] = V[c] - V[c].shift(12)
C = C.dropna()
for basis, data in (("level", L), ("change12", C)):
    for y in ("nfci", "anfci", "mkt" if basis == "level" else "mkt_flw"):
        for nm, cols in (("3 vars", ["y10", "cape", "usd_real"]), ("3 vars + spread", ["y10", "cape", "usd_real", "spread"]), ("spread only", ["spread"])):
            if y.startswith("mkt") and "spread" in nm and nm != "3 vars + spread": pass
            R2, m = r2(y, cols, data)
            rows.append(dict(basis=basis, y=y, regressors=nm, n=len(data), R2=R2, **{f"b_{c}": m.params[c] for c in cols}, **{f"t_{c}": m.tvalues[c] for c in cols}))
Rr = pd.DataFrame(rows); Rr.to_csv(OUT / "nfci_on_variables.csv", index=False); print(Rr.round(2).to_string())
cor = pd.DataFrame({"level": L[["mkt", "nfci", "anfci", "spread", "y10", "cape", "usd_real"]].corr()["nfci"], "change12": C[["mkt", "nfci", "anfci", "spread", "y10", "cape", "usd_real"]].corr()["nfci"]})
cor["corr_with_anfci_level"] = L[["mkt", "nfci", "anfci", "spread", "y10", "cape", "usd_real"]].corr()["anfci"]
cor.to_csv(OUT / "correlations.csv"); print(cor.round(2)); print("corr mkt_flw vs nfci level", V.mkt_flw.corr(V.nfci), "vs nfci flow", C.mkt_flw.corr(C.nfci), "vs spread change", C.mkt_flw.corr(C.spread))
