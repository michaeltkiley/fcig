"""Step 38. How much of each MCFCI is a slow-moving trend: share of the variance of the monthly MCFCI (nominal, real, relative to r*) fitted by a
quadratic time trend, 1973-01 to the last month of the index (FP-A76; the author's measure of the slow-moving component, a spline being too flexible).
Writes results/38_trend_share.csv and scalars_38_trend_share.csv."""
import numpy as np, pandas as pd
from lib.config import RES
from lib.report import Scalars

S = Scalars("38_trend_share")
rows = []
for step in ("nominal", "real", "rstar"):
    s = pd.read_csv(RES / f"indexes_{step}.csv", index_col=0).market.dropna()
    t = np.arange(len(s)) / len(s); X = np.column_stack([np.ones_like(t), t, t * t])
    e = s.values - X @ np.linalg.lstsq(X, s.values, rcond=None)[0]
    r2 = 1 - e.var() / s.values.var()
    rows.append(dict(step=step, start=s.index[0], end=s.index[-1], months=len(s), r2_quadratic=r2, sd=s.std()))
    S.add(f"{step}_r2", r2)
    print(f"{step:8s} {s.index[0]} to {s.index[-1]}: quadratic trend R2 {r2:.3f}")
pd.DataFrame(rows).to_csv(RES / "38_trend_share.csv", index=False, float_format="%.4f")
S.save()
