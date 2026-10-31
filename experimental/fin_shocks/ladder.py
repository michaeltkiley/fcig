"""Frequency ladder. How does the relevance of the high-frequency policy surprise (Nakamura-Steinsson factor, 30-minute windows, 253 events 1994-2026) fall as the outcome window grows?
Outcome: change from the close before the event to the close h trading days after the event day (h = 0 is the event-day close), for the 2-year yield (DGS2), the 10-year yield (DGS10) and the Goldman-style FCI (index points, higher = tighter; fcig_gs_daily.csv).
Regression y = a + b*ns, HC1 t, F = t^2, R2. Also: the same surprise summed within the month against the monthly change of the monthly-average 2-year (the relation a monthly VAR works with).
Output: ladder.log"""
import sys, numpy as np, pandas as pd, warnings
import statsmodels.api as sm
sys.path.insert(0, "../mp_var_fci")
from mpcommon import *
warnings.filterwarnings("ignore")
ev = events()
gs = pd.read_csv(HERE.parents[1] / "fcig_gs_daily.csv", parse_dates=["date"]).set_index("date").fci
S = {"2-year yield (pp)": fred("DGS2").dropna(), "10-year yield (pp)": fred("DGS10").dropna(), "GS-style FCI (index pts)": gs.dropna()}
H = [0, 1, 2, 5, 10, 21]
print("Relevance of the NS surprise by outcome window (event-day close before -> close h trading days after the event day); slope b, F (R2 %), n")
print(f"{'outcome':26s}" + "".join(f"   h={h:<2d}               " for h in H))
for nm, s in S.items():
    row = []
    for h in H:
        y, x = [], []
        for d, v in zip(ev.Date.dt.normalize(), ev.ns):
            i = s.index.searchsorted(d)
            if i < 1 or i + h >= len(s) or s.index[i] != d: continue
            y.append(s.iloc[i + h] - s.iloc[i - 1]); x.append(v)
        r = sm.OLS(np.array(y), sm.add_constant(np.array(x))).fit(cov_type="HC1")
        row.append(f"{r.params[1]:+6.2f} F{r.tvalues[1] ** 2:6.1f} ({100 * r.rsquared:4.1f}%) n{len(y)}")
    print(f"{nm:26s}" + "  ".join(row))
# monthly counterpart
Z = monthly_instruments(ev, ("ns",))["ns"]
g2 = fred("GS2"); g2 = g2.groupby(g2.index.to_period("M")).mean().reindex(M.index)
d = pd.concat([g2.diff(), Z, Z.shift(1)], axis=1, keys=["dy", "ns", "ns1"]).loc["1994-01":].dropna()
r = sm.OLS(d.dy.values, sm.add_constant(d[["ns", "ns1"]].values)).fit(cov_type="HC1")
print(f"\nMonthly: change in the monthly-average 2-year on the month's NS sum and last month's: b = {r.params[1]:+.2f} (t {r.tvalues[1]:+.1f}), {r.params[2]:+.2f} (t {r.tvalues[2]:+.1f}), R2 {100 * r.rsquared:.1f}%, n = {len(d)}")
