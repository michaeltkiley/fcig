"""A2: VAR (u first, 12 lags) response of u at 12 months, Phi(12), by subperiod, with 12-month block bootstrap (300 draws); rolling 20-year windows (points)."""
from common import *
from lib import var
from lib.config import SEED
SER = all_series(); rows = []; rr = []
SUBV = {"V1_1973-89": ("1973-01", "1989-12"), "V2_1990-2007": ("1990-01", "2007-12"), "V3_2009-19": ("2009-01", "2019-12")}
for k, m in SER.items():
    for p, (a, z) in SUBV.items():
        r, D, dum = var.fit(U, m, 12, a, z); Phi, _ = var.response(r, 12)
        ph, _ = var.bootstrap(D, dum, 12, 12, 300, seed=SEED)
        rows.append({"family": k[0], "step": k[1], "period": p, "n": len(D), "phi12": Phi[12], "se": ph[:, 12].std(ddof=1), "lo90": np.percentile(ph[:, 12], 5), "hi90": np.percentile(ph[:, 12], 95)})
    print(k, flush=True)
    for end in pd.period_range("1992-12", "2026-09", freq="M")[::12]:
        a = end - 239
        if a < pd.Period("1973-01", "M"): continue
        r, D, dum = var.fit(U, m, 12, str(a), str(end)); Phi, _ = var.response(r, 12)
        rr.append({"family": k[0], "step": k[1], "window_end": str(end), "phi12": Phi[12]})
T = pd.DataFrame(rows)
def stats_(g):
    w = 1 / g.se ** 2; mu = (w * g.phi12).sum() / w.sum(); Q = (w * (g.phi12 - mu) ** 2).sum()
    from scipy import stats
    return pd.Series({"phi_V1": g.phi12.iloc[0], "phi_V2": g.phi12.iloc[1], "phi_V3": g.phi12.iloc[2], "Q_equal_chi2_2": Q, "p_equal": 1 - stats.chi2.cdf(Q, 2),
                      "sd_across": g.phi12.std(ddof=1), "cv": g.phi12.std(ddof=1) / abs(mu)})
S = T.groupby(["family", "step"]).apply(stats_).reset_index()
T.to_csv(OUT / "var_phi12_subperiods.csv", index=False); S.to_csv(OUT / "var_phi12_stability.csv", index=False)
R = pd.DataFrame(rr); R.to_csv(OUT / "var_phi12_rolling.csv", index=False)
R.groupby(["family", "step"]).phi12.agg(["std", "min", "max", "count"]).reset_index().to_csv(OUT / "var_phi12_rolling_summary.csv", index=False)
