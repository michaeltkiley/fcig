"""Step 6. What the indexes say about unemployment a year ahead (Box, Table 6, Figure 6): local projections u(t+12) on u(t) and the current index reading,
1976-2026, with recursive out-of-sample forecasts from 1995; FCI-G response profile by horizon (4 lags of u and of the index)."""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from fci import data, lp, report

D = data.load(); u = D.u_gap
N = report.Numbers("unemp")
pub = pd.read_csv(data.DATA / "fed_monthly_1yr.csv", parse_dates=["date"]).set_index("date").iloc[:, 0]; pub.index = pub.index.to_period("M")
rows = []
for case, lab in (("rstar", "r*"), ("real", "real")):
    I = data.read(f"indexes_{case}.csv"); F = data.read(f"flow_{case}.csv")
    X = {"Market index forward impetus": F.forward_impetus_p12, "FCI-G, 1-year lookback": I.fcig_1yr, "FCI-G, 3-year lookback": I.fcig_3yr,
         "FRB/US growth impetus": I.frbus_gi_hp, "Market index (level)": I.market, "Market index current pressure": F.current_pressure_p12,
         "GS (level)": I.gs, "FRB/US index (level)": I.frbus}
    for nm, x in X.items():
        b, se, dr2 = lp.fit(u, x)
        ratio, dm = lp.oos(u, x)
        sub = {k: lp.oos(u, x, first=a, last=z)[0] for k, (a, z) in {"1995-07": ("1995-01", "2007-12"), "2008-19": ("2008-01", "2019-12"), "2021-25": ("2021-01", "2025-09")}.items()}
        rows.append({"Case": lab, "Index": nm, "Coef. (s.e.)": f"{b:.2f} ({se:.2f})", "Gain adj. R2": dr2, "OOS ratio": ratio, **sub, "DM t": dm})
T = pd.DataFrame(rows).set_index(["Case", "Index"])
print(T.round(3).to_string())
report.table("tab6_unemployment_rstar", T.xs("r*"), fmt="{:.2f}")
report.table("tab6b_unemployment_real", T.xs("real"), fmt="{:.2f}")
r = T.xs("r*")
N.add("LpFiRatio", r.loc["Market index forward impetus", "OOS ratio"]); N.add("LpFcigRatio", r.loc["FCI-G, 1-year lookback", "OOS ratio"])
N.add("LpFiGain", r.loc["Market index forward impetus", "Gain adj. R2"]); N.add("LpFcigGain", r.loc["FCI-G, 1-year lookback", "Gain adj. R2"])
N.add("LpLevelGain", r.loc["Market index (level)", "Gain adj. R2"]); N.add("LpLevelRatio", r.loc["Market index (level)", "OOS ratio"])
N.add("LpDMBest", r["DM t"].min())

# FCI-G scale: response of u(t+h) to a reading held over the 4 lag months (sum of coefficients), h = 0..24
prof = {}
for nm, x, st in (("FCI-G (r* version), 1974-2026", data.read("indexes_rstar.csv").fcig_1yr, "1974-03"),
                  ("FCI-G (nominal replication), 1974-2026", data.read("indexes_nominal.csv").fcig_1yr, "1974-03"),
                  ("Published FCI-G, 1990-2026", pub, "1990-01")):
    prof[nm] = pd.DataFrame([lp.fit(u, x, h=h, L=4, start=st)[:2] for h in range(25)], columns=["b", "se"])
fig, ax = plt.subplots(figsize=(7, 3.8))
for (nm, P), col in zip(prof.items(), [report.COLORS["market"], report.COLORS["grey"], report.COLORS["fcig"]]):
    ax.plot(P.index, P.b, color=col, lw=1.5, label=nm); ax.fill_between(P.index, P.b - 1.645 * P.se, P.b + 1.645 * P.se, color=col, alpha=0.12, lw=0)
ax.plot([0, 12], [0, 0.5], color="#999999", ls="--", lw=1, label="FCI-G's own claim (0.5 by month 12, Okun's law)")
ax.set_xlabel("months ahead")
report.axes(ax, "unemployment gap, pp, per +1 reading")
report.figure("fig6_fcig_scale", fig)
for nm, k in zip(prof, ("Rstar", "Nom", "Pub")):
    N.add(f"FcigScale{k}", prof[nm].b[12]); N.add(f"FcigScaleSe{k}", prof[nm].se[12])
N.write()
