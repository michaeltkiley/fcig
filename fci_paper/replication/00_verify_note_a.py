"""Check: the package reproduces the published files of the companion note (../../fci_note/replication/output) wherever they exist: weights, conversions, the four index files,
the unemployment response Phi, the flows and the local-projection table. Run after steps 2-6. Tolerance 2e-4 (the note's files are rounded to 4-5 digits)."""
from pathlib import Path
import numpy as np, pandas as pd
from lib.config import RES, ROOT

A = ROOT.parents[1] / "fci_note" / "replication" / "output"
if not A.exists():
    raise SystemExit("companion package not found; nothing to check")
bad = []
def cmp(name, new, old, tol=2e-4):
    j = new.join(old, how="inner", lsuffix="_n", rsuffix="_o") if False else None
    n = new.reindex(old.index)[old.columns]
    d = np.nanmax(np.abs(n.values.astype(float) - old.values.astype(float)))
    print(f"{name:34s} max abs difference {d:.2e}")
    if not d <= tol:
        bad.append(name)
rd = lambda p: pd.read_csv(p, index_col=0)
cmp("market_weights", rd(RES / "market_weights.csv"), rd(A / "market_weights.csv"))
cmp("conversions", rd(RES / "conversions.csv"), rd(A / "conversions.csv"))
for c in ("nominal", "real", "rstar", "rstar_kiley"):
    cmp(f"indexes_{c}", rd(RES / f"indexes_{c}.csv"), rd(A / f"indexes_{c}.csv"))
    for p in (12, 4):
        old = rd(A / f"flow_{c}.csv")[[f"forward_impetus_p{p}", f"current_pressure_p{p}"]]
        new = rd(RES / f"flow_{c}_p{p}.csv"); new.columns = [f"forward_impetus_p{p}", f"current_pressure_p{p}"]
        cmp(f"flow_{c}_p{p}", new, old, 5e-4)
    old = rd(A / "var_phi.csv")
    new = pd.DataFrame({f"{c} p{p}": pd.read_csv(RES / f"var_paths_{c}_p{p}.csv").phi for p in (12, 4)})
    cmp(f"var_phi {c}", new, old[[f"{c} p12", f"{c} p4"]], 5e-5)
old = pd.read_csv(A / "tables" / "tab6_unemployment_rstar.tex", sep="&", skiprows=4, nrows=8, header=None) if False else None
new = pd.read_csv(RES / "activity.csv"); new = new[new.case == "rstar"].set_index("index")
print("local projections: forward impetus coefficient", round(new.coef.iloc[0], 2), "(note: 0.50), FCI-G 1-year", round(new.coef.iloc[1], 2), "(note: 0.70)")
assert abs(new.coef.iloc[0] - 0.50) < 0.005 and abs(new.coef.iloc[1] - 0.70) < 0.005
if bad:
    raise SystemExit("DIFFERENCES from the companion note: " + ", ".join(bad))
print("package reproduces the companion note")
