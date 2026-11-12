"""(a) joint local projections and (d) level vs flow for NFCI/ANFCI."""
import numpy as np, pandas as pd, statsmodels.api as sm
from common import *
rng = np.random.default_rng(1); X, D = M(); rows = []

def fit(F, own, xc, lags):
    m = sm.OLS(F.y, sm.add_constant(F[own + xc])).fit(cov_type="HAC", cov_kwds={"maxlags": lags}); return m
def boot(F, own, xc, block, B=999):
    cols = own + xc; A = np.c_[np.ones(len(F)), F[cols].values]; y = F.y.values; n = len(y); nb = int(np.ceil(n / block)); out = []
    for _ in range(B):
        st = rng.integers(0, n - block + 1, nb); ix = np.concatenate([np.arange(s, s + block) for s in st])[:n]
        out.append(np.linalg.lstsq(A[ix], y[ix], rcond=None)[0][1 + len(own):])
    return np.percentile(out, [5, 95], axis=0)

specs = {"joint_nfci": ["mkt_flw", "nfci"], "joint_anfci": ["mkt_flw", "anfci"],
         "mkt_flw_alone": ["mkt_flw"], "nfci_alone": ["nfci"], "anfci_alone": ["anfci"]}
for spec, xc in specs.items():
    for outc, hs in (("du", (6, 12, 24)), ("pay", (6, 12, 24)), ("gdp", (2, 4, 8))):
        for h in hs:
            F, own = design_gdp(h, xc, X, D) if outc == "gdp" else design(h, outc, xc, X, D)
            hm = h * (3 if outc == "gdp" else 1); lags = max(12, hm + 6) if outc != "gdp" else max(12, hm + 6)
            lag_use = lags if outc != "gdp" else max(4, h + 2)  # quarterly: h+2 lags
            m0 = sm.OLS(F.y, sm.add_constant(F[own])).fit()
            m = fit(F, own, xc, lag_use); bi = boot(F, own, xc, lag_use)
            for j, c in enumerate(xc):
                rows.append(dict(spec=spec, outcome=outc, h=h, var=c, n=len(F), first=str(F.index[0]), last=str(F.index[-1]), b=m.params[c], t_hac=m.tvalues[c],
                                 lo90=bi[0, j], hi90=bi[1, j], gain_adjR2=m.rsquared_adj - m0.rsquared_adj, hac_lags=lag_use))
    # recession logit
    F = design_rec(xc, X, D)
    m = sm.Logit(F.y, sm.add_constant(F[xc])).fit(disp=0, cov_type="HAC", cov_kwds={"maxlags": 18}); m0 = sm.Logit(F.y, np.ones(len(F))).fit(disp=0)
    for c in xc: rows.append(dict(spec=spec, outcome="rec12", h=12, var=c, n=len(F), first=str(F.index[0]), last=str(F.index[-1]), b=m.params[c], t_hac=m.tvalues[c], gain_adjR2=m.prsquared, hac_lags=18))
R = pd.DataFrame(rows); R.to_csv(OUT / "joint_lp.csv", index=False)
print(R[R.spec.str.startswith("joint")].round(2).to_string())

# (d) level vs flow of NFCI / ANFCI
X2 = X.copy()
for v in ("nfci", "anfci"): X2[v + "_flw"] = X2[v] - X2[v].shift(12)
rows = []
for v in ("nfci", "anfci"):
    for outc, hs in (("du", (6, 12, 24)), ("pay", (6, 12, 24))):
        for h in hs:
            F, own = design(h, outc, [v, v + "_flw"], X2, D)
            m = fit(F, own, [v, v + "_flw"], max(12, h + 6)); m0 = sm.OLS(F.y, sm.add_constant(F[own])).fit()
            mL = fit(F, own, [v], max(12, h + 6)); mF = fit(F, own, [v + "_flw"], max(12, h + 6))
            rows.append(dict(index=v, outcome=outc, h=h, n=len(F), t_lvl_both=m.tvalues[v], t_flw_both=m.tvalues[v + "_flw"], t_lvl_alone=mL.tvalues[v], t_flw_alone=mF.tvalues[v + "_flw"],
                             gain_lvl=mL.rsquared_adj - m0.rsquared_adj, gain_flw=mF.rsquared_adj - m0.rsquared_adj))
    F = design_rec([v, v + "_flw"], X2, D)
    for nm, cols in (("both", [v, v + "_flw"]),):
        m = sm.Logit(F.y, sm.add_constant(F[cols])).fit(disp=0, cov_type="HAC", cov_kwds={"maxlags": 18})
        rows.append(dict(index=v, outcome="rec12", h=12, n=len(F), t_lvl_both=m.tvalues[v], t_flw_both=m.tvalues[v + "_flw"]))
pd.DataFrame(rows).to_csv(OUT / "nfci_level_vs_flow.csv", index=False); print(pd.DataFrame(rows).round(2).to_string())
