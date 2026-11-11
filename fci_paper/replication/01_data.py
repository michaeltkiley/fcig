"""Step 1. Monthly data set (January 1973 to September 2026, monthly averages): results/data_monthly.csv, and the numbers about inflation expectations and r*."""
from lib import data
from lib.report import Scalars

D = data.build()
D.to_csv(data.OUT / "data_monthly.csv", float_format="%.5f")
print(f"monthly data {D.index[0]}..{D.index[-1]}, {D.shape[1]} series")
S = Scalars("data")
for k, s, a, b in (("einf_1981", "einf_1y", "1981-01", "1981-12"), ("einf_1974", "einf_1y", "1974-01", "1974-12"), ("rstar_lw_70s", "rstar LW", "1973-01", "1979-12"),
                   ("rstar_lw_pre", "rstar LW", "1990-01", "2007-12"), ("rstar_lw_post", "rstar LW", "2009-01", "2016-12"), ("rstar_ki_post", "rstar Kiley", "2009-01", "2016-12"),
                   ("rstar_ki_pre", "rstar Kiley", "1990-01", "2007-12")):
    S.add(k, D[s].loc[a:b].mean())
S.add("einf_latest", D.einf_1y.iloc[-1]); S.add("rstar_lw_latest", D["rstar LW"].iloc[-1]); S.add("rstar_ki_latest", D["rstar Kiley"].iloc[-1])
S.add("usd_nom_1973", D.usd_nominal.loc["1973-01"]); S.add("usd_nom_latest", D.usd_nominal.iloc[-1])
S.save()
