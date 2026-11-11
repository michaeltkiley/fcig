"""Supplement (added after the main results, flagged as such): which part of the market index carries the increment over the funds-rate gap?
Market index r* step split into rates (10-year gap), equities, dollar (results/groups_rstar.csv; the index is their sum). Mixed form (FFG level, component 12-month change),
3 outcomes x 3 components = 9 descriptive cells; M3 = own + FFG + component vs M1 = own + FFG; in-sample gain in adjusted R2, HAC-18 t, recursive CW from 1995."""
from common import *
G = pcols(REP / "results" / "groups_rstar.csv"); f = ffg("rstar"); rows = []
for c in ("rates", "equities", "dollar", "equities+dollar"):
    x = G[["market|equities", "market|dollar"]].sum(axis=1) if c == "equities+dollar" else G[f"market|{c}"]
    for yn in OUTCOMES:
        D = design(yn, f, x, "mixed"); ow = own(yn); F = oos(D, ow); F = F[F.index >= pd.Period(FIRST_OOS, "M")]
        r1 = hac_ols(D, ow + ["ff"], 18); r3 = hac_ols(D, ow + ["ff", "idx"], 18)
        e1, e3 = F.y - F.M1, F.y - F.M3
        rows.append(dict(component=c, outcome=yn, n=len(D), gain=r3.rsquared_adj - r1.rsquared_adj, t=r3.tvalues["idx"], rmse=float(np.sqrt((e3**2).mean() / (e1**2).mean())), cw=mean_t((e1**2 - e3**2 + (F.M1 - F.M3)**2).values)))
R = pd.DataFrame(rows); R.to_csv(OUT / "components.csv", index=False); print(R.round(3).to_string())
