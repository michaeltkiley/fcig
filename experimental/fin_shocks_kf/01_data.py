"""Step 1. Build the inputs (kf/inputs.py) and check them against Note B's own files (read as data, not code):
macro against ../fin_shocks/baseline/output/macro_monthly.csv; the daily FCI's monthly averages against Note A's frozen monthly index; announcements used (252)."""
import numpy as np, pandas as pd
from kf.inputs import Inputs, window_impact, position_bins, OUT, ROOT

I = Inputs(); OUT.mkdir(exist_ok=True)
nb = pd.read_csv(ROOT.parent / "fin_shocks" / "baseline" / "output" / "macro_monthly.csv", index_col=0); nb.index = pd.PeriodIndex(nb.index, freq="M")
du = (I.mac.u - nb.u_gap).abs().max(); dp = (I.mac.pi - nb.pi_core).abs().max()
print(f"macro vs Note B: max |diff| u {du:.1e}, pi {dp:.1e} (Note B file rounded to 5 decimals)"); assert du < 1e-4 and dp < 1e-4
NAMES = {"nom": "nominal", "real": "real", "rstar": "rstar"}
for k in ("nom", "real", "rstar"):
    m = I.fci[k].loc["1996-01-01":"2026-09-30"]; m = m.groupby(m.index.to_period("M")).mean()
    a = pd.read_csv(f"data/frozen/indexes_{NAMES[k]}.csv", index_col=0).market; a.index = pd.PeriodIndex(a.index, freq="M")
    print(f"daily FCI {k}: monthly averages vs Note A's index, max |diff| 1996-2026 {(m - a.reindex(m.index)).abs().max():.1e}")
print(f"announcements used: {len(I.used)} ({I.ev.day.iloc[I.used].min():%Y-%m-%d} to {I.ev.day.iloc[I.used].max():%Y-%m-%d}); window impact [2-year, FCI] = {np.round(window_impact(I.ev, I.used), 4)}")
print("position bins (position, days in month, share):", [(a, b, round(c, 3)) for a, b, c in position_bins(I.ev, I.used)])
I.mac.to_csv(OUT / "macro.csv", float_format="%.6f")
for f in ("nom", "real", "rstar"): I.daily(f, f).to_csv(OUT / f"daily_{f}.csv", float_format="%.6f")
