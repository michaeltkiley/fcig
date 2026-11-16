"""Experiment (16 Nov 2026, user): find the funds-rate path that, in FRB/US, moves the FRB/US index along the VAR's own path for the FRB/US index
(FCI ordered first, r* step), and read the GDP effect off FRB/US; compare with the VAR's output-gap response.
Linear superposition of the persistent 1 pp hike (FRB/US, VAR expectations, full transmission; data/frbus_hike_paths.csv): a funds-rate path = steps a_s at quarter s.
FRB/US index reading of the hike at quarter q: F(q) = sum_v w_v dX_v(q), w = the index weights (Phi_v(4) / G(4), lib.indexes), dX from the hike file
(rff, rg10, mortgage spread, BBB spread, stocks %, dollar %). Solve sum_s a_s F(q - s) = x_q (VAR path, q = 0..12, FRB/US quarter 1 = VAR quarter 0),
then GDP(h) = sum_s a_s G(h - s). Approximations [inference]: the r*-step index is read off nominal model changes (expected inflation and r* in the model ignored);
stocks % stands for the CAPE log change."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent; PKG = HERE.parents[1] / "fci_paper" / "replication"; sys.path.insert(0, str(PKG))
from lib import indexes as I  # noqa: E402

P, G = I.frbus_paths(); cols = [c for c in I.FRBUS_VARS if c != "house"]
w = I.phi_at(P[cols], 4) / G[4]
hk = pd.read_csv(PKG / "data" / "frbus_hike_paths.csv").sort_values("quarter")
dX = pd.DataFrame({"policy": hk.rff, "y10": hk.rg10, "mortgage_spread": hk["mortgage spread"], "bbb_spread": hk.rbbbp,
                   "equities": hk["stocks %"], "dollar": hk["dollar %"]}).values
F = dX @ w[cols].values                        # F[k] = index reading k quarters after the hike starts (k = 0 is FRB/US quarter 1)
Gk = hk.gdp.values                             # Gk[k] = GDP at FRB/US quarter k + 1
R = pd.read_csv(HERE / "results" / "irf_full_indexes.csv")
rows = []
for dummies in [True, False]:
    # full own path needed: rerun the VAR point estimate quickly from qvar_full's functions
    import importlib.util
    spec = importlib.util.spec_from_file_location("qf", HERE / "qvar_full.py")
    src = (HERE / "qvar_full.py").read_text().split("rows = []")[0]; ns = {"__file__": str(HERE / "qvar_full.py")}; exec(src, ns)
    ix = pd.read_csv(PKG / "results" / "indexes_rstar.csv", index_col=0); ix.index = pd.PeriodIndex(ix.index, freq="M")
    q = ix["frbus"].dropna(); q = q.groupby(q.index.asfreq("Q")).mean()
    df = pd.concat([ns["gap"].rename("gap"), q.rename("fci")], axis=1).loc[ns["START"]:ns["END_Q"]].dropna()
    Z = df.values; dums = np.column_stack([(df.index == d).astype(float) for d in ns["DUM"]]) if dummies else None
    B, U, S = ns["ols"](Z, dums); path = ns["irf"](B, S, "fci")
    x = path[:, 1]; n = len(x); a = np.zeros(n)
    for t in range(n):
        a[t] = (x[t] - sum(a[s] * F[t - s] for s in range(t))) / F[0]
    gdp = np.array([sum(a[s] * Gk[h - s] for s in range(h + 1)) for h in range(n)])
    ffr = np.cumsum(a)
    for h in range(n):
        rows.append(dict(dummies_2020=dummies, quarter=h, fci_var=x[h], ffr_path=ffr[h], frbus_gdp=gdp[h], var_gap=path[h, 0]))
out = pd.DataFrame(rows); out.to_csv(HERE / "results" / "frbus_match.csv", index=False, float_format="%.4f")
print("F(k), index reading of a persistent 1 pp hike:", np.round(F[:13], 2))
print(out.to_string(index=False, float_format=lambda v: f"{v:+.2f}"))
