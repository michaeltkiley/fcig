"""Step 6. What the indexes say about unemployment a year ahead: local projections u(t+12) on u(t) and the current index reading, 1976-2026, with recursive out-of-sample
forecasts from 1995; the response of unemployment to FCI-G by horizon (4 lags of u and of the index).
Writes results/activity.csv, fcig_scale.csv and scalars_activity.csv."""
import numpy as np, pandas as pd
from lib import data, lp
from lib.report import Scalars

S = Scalars("activity")
D = data.load(); u = D.u_gap
pub = pd.read_csv(data.DATA / "fed_monthly_1yr.csv", parse_dates=["date"]).set_index("date").iloc[:, 0]; pub.index = pub.index.to_period("M")
rows = []
for case in ("rstar", "real", "nominal"):
    I = data.read(f"indexes_{case}.csv"); F = data.read(f"flow_{case}_p12.csv")
    X = {"Market index forward impetus": F.forward_impetus, "FCI-G, 1-year lookback": I.fcig_1yr, "FCI-G, 3-year lookback": I.fcig_3yr, "FRB/US growth impetus": I.frbus_gi_hp,
         "Market index (level)": I.market, "Market index current pressure": F.current_pressure, "GS (level)": I.gs, "FRB/US index (level)": I.frbus}
    for nm, x in X.items():
        b, se, dr2 = lp.fit(u, x)
        ratio, dm = lp.oos(u, x)
        sub = {k: lp.oos(u, x, first=a, last=z)[0] for k, (a, z) in {"r_1995_2007": ("1995-01", "2007-12"), "r_2008_2019": ("2008-01", "2019-12"), "r_2021_2025": ("2021-01", "2025-09")}.items()}
        rows.append({"case": case, "index": nm, "coef": b, "se": se, "gain": dr2, "oos_ratio": ratio, **sub, "dm_t": dm})
T = pd.DataFrame(rows)
T.to_csv(data.OUT / "activity.csv", index=False)
print(T[T.case == "rstar"].round(2).to_string())

prof = {}
for nm, x, st in (("rstar", data.read("indexes_rstar.csv").fcig_1yr, "1974-03"), ("nominal", data.read("indexes_nominal.csv").fcig_1yr, "1974-03"), ("published", pub, "1990-01")):
    prof[nm] = pd.DataFrame([lp.fit(u, x, h=h, L=4, start=st)[:2] for h in range(25)], columns=["b", "se"])
    S.add(f"fcig_scale_{nm}", prof[nm].b[12]); S.add(f"fcig_scale_se_{nm}", prof[nm].se[12])
pd.concat(prof, axis=1).to_csv(data.OUT / "fcig_scale.csv")
S.save()
