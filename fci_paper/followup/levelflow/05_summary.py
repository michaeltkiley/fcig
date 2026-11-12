"""Summaries: Holm / Benjamini-Hochberg over the primary family (payroll growth, tau=0.1, OOS pinball DM, 14 series x 3 specs = 42 one-sided tests of 'better than own lags'),
counts by pattern, and compact tables to out/summary_*.csv."""
import numpy as np, pandas as pd
from scipy import stats
from common import *
pd.set_option("display.width", 250)
q = pd.read_csv(OUT / "quantile_results.csv")
P = q[(q.freq == "M") & (q.tau == 0.1)].melt(id_vars=["series"], value_vars=["dm_lvl", "dm_flw", "dm_both"], var_name="spec", value_name="dm")
P["p_one"] = stats.norm.cdf(P.dm)
P = P.sort_values("p_one").reset_index(drop=True); m = len(P)
P["holm"] = np.minimum(1, np.maximum.accumulate((m - np.arange(m)) * P.p_one))
bh = (P.p_one * m / (np.arange(m) + 1))[::-1].cummin()[::-1]; P["bh"] = np.minimum(1, bh)
P.to_csv(OUT / "summary_primary_family.csv", index=False)
print(P.head(8).round(3).to_string()); print("min holm", P.holm.min(), "n p_one<0.05:", (P.p_one < .05).sum(), "of", m)
for fr, tag in (("M", "pay"), ("Q", "gdp")):
    t = q[q.freq == fr]
    print(tag); print(t[["series", "tau", "n", "n_oos", "b_lvl", "lo_lvl", "hi_lvl", "b_flw", "lo_flw", "hi_flw", "qs_lvl", "qs_flw", "qs_both", "dm_lvl", "dm_flw", "dm_both"]].round(2).to_string())
