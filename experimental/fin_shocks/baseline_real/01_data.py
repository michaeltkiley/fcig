"""Step 1. Monthly data of Note B from raw inputs in data/: Note A's inputs (output/data_monthly.csv) and the macro variables of the monthly system
(output/macro_monthly.csv): unemployment gap (pp), core PCE inflation (annualised, 1200 x log difference of monthly-average PCEPILFE), excess bond premium."""
import numpy as np, pandas as pd
from lib import noteA
from lib.paths import DATA, OUT

D = noteA.build(); D.to_csv(OUT / "data_monthly.csv", float_format="%.5f")
pce = pd.read_csv(DATA / "PCEPILFE.csv"); pce = pd.Series(pce.iloc[:, 1].values.astype(float), index=pd.to_datetime(pce.iloc[:, 0]))
P = pce.groupby(pce.index.to_period("M")).mean()
eb = pd.read_csv(DATA / "ebp.csv"); eb.index = pd.PeriodIndex(pd.to_datetime(eb.date), freq="M")
idx = pd.period_range(noteA.START, noteA.END, freq="M")
M = pd.DataFrame({"u_gap": D.u_gap, "pi_core": 1200 * np.log(P).diff(), "ebp": eb.ebp}).reindex(idx)
M.index.name = "month"; M.to_csv(OUT / "macro_monthly.csv", float_format="%.5f")
print(f"data_monthly {D.index[0]}..{D.index[-1]}, {D.shape[1]} series; macro_monthly {M.index[0]}..{M.index[-1]}")
