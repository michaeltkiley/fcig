"""Step 00. Regenerate the FRB/US inputs of the package from the Board's public package, with the current vintage.

Downloads pyfrbus and LONGBASE (raw/frbus, gitignored; creates raw/frbus_venv with Python 3.11 if this interpreter cannot import pyfrbus), then reruns the experiments of
experimental/ms_fci/frbus_paths.py exactly (steady-state baseline from 2040Q1, VAR expectations, fiscal settings as in the Board's demos, 32 quarters):
  data/frbus_hike_paths.csv  GDP and spillovers of a persistent +1 pp funds-rate hike with full transmission (the yardstick)
  data/frbus_paths.csv       GDP per unit of persistent and temporary shifts of rshort, rg10, rme, rbbbp, req, fpxr, phouse, two expectation designs
The fresh files are written to results/00_frbus_paths.csv and 00_frbus_hike_paths.csv. When the pipeline is run normally the data/ copies are replaced (the previous ones are kept once
as data/*_oldvintage.csv); under the sync check (FCI_RESULTS set) the data/ copies are left alone and compared with the fresh run instead.
Records the LONGBASE date and sha256 in results/scalars_00_frbus.csv (strings in results/00_frbus_vintage.csv).
Usage: python3 00_frbus.py   (about 2 minutes)"""
import os, sys, time, shutil
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib.frbus_env import ensure_runtime
ensure_runtime()
import numpy as np, pandas as pd
from lib.frbus_env import longbase_info
from lib.frbus_common import Model, FIXED, PASS
from lib.config import RES, DATA

t0 = time.time(); H = 32
M = Model(H); fr, base, start = M.frbus, M.base, M.start
q = slice(start, start + H - 1)
f0, f1 = M.run(["rff"], ["rff"], 1.0); gF = M.gdp(f1, f0, H)
hike = pd.DataFrame({"quarter": np.arange(1, H + 1), "gdp": gF, "rff": (f1.loc[q, "rff"] - f0.loc[q, "rff"]).values, "rtb": (f1.loc[q, "rtb"] - f0.loc[q, "rtb"]).values,
                     "rg10": (f1.loc[q, "rg10"] - f0.loc[q, "rg10"]).values,
                     "mortgage spread": ((f1.loc[q, "rme"] - f1.loc[q, "rg10"]) - (f0.loc[q, "rme"] - f0.loc[q, "rg10"])).values, "rbbbp": (f1.loc[q, "rbbbp"] - f0.loc[q, "rbbbp"]).values,
                     "stocks %": 100 * np.log(f1.loc[q, "wpsn"] / f0.loc[q, "wpsn"]).values, "dollar %": 100 * np.log(f1.loc[q, "fpxr"] / f0.loc[q, "fpxr"]).values,
                     "house prices %": 100 * np.log(f1.loc[q, "phouse"] / f0.loc[q, "phouse"]).values})
hike.to_csv(RES / "00_frbus_hike_paths.csv", float_format="%.5f", index=False)
EXP = [("rshort", ["rff", "rtb"], 1.0, False, FIXED), ("rg10", ["rg5", "rg10", "rg30"], 1.0, False, [v for v in FIXED if v not in PASS]), ("rme", ["rme"], 1.0, False, FIXED),
       ("rbbbp", ["rbbbp"], 1.0, False, FIXED), ("req", ["req"], 1.0, False, [v for v in FIXED if v != "wpsn"]), ("fpxr", ["fpxr"], 0.10, True, FIXED),
       ("phouse", ["phouse"], 0.10, True, FIXED + ["phouse"])]
rows = []
for design in ("zfree", "zfixed"):
    for name, vars_, shift, mult, exo in EXP:
        exo = list(exo) + (M.Zv if design == "zfixed" else []); unit = None
        for shape in ("persistent", "temporary"):
            s0, s1 = M.run(exo, vars_, shift, mult, temporary=(shape == "temporary")); g = M.gdp(s1, s0, H)
            if unit is None:
                unit = (-100 * np.log(s1.loc[start, "wpsn"] / s0.loc[start, "wpsn"])) if name == "req" else (100 * np.log(1 + shift) if mult else shift)
            sign = -1.0 if name == "req" else 1.0
            for i in range(H):
                rows.append(dict(design=design, experiment=name, shape=shape, quarter=i + 1, gdp_per_unit=sign * g[i] / unit, ffr_eq=sign * g[i] / unit / gF[i]))
out = pd.DataFrame(rows); out.to_csv(RES / "00_frbus_paths.csv", float_format="%.6f", index=False)
d, h = longbase_info()
pd.DataFrame([dict(longbase_file_date=d, longbase_sha256=h)]).to_csv(RES / "00_frbus_vintage.csv", index=False)
pd.Series({"hike_gdp_q4": gF[3], "hike_gdp_q8": gF[7]}).rename_axis("name").rename("value").to_csv(RES / "scalars_00_frbus.csv")

# compare with the stored inputs
old_p, old_h = pd.read_csv(DATA / "frbus_paths.csv"), pd.read_csv(DATA / "frbus_hike_paths.csv")
def rel(a, b): return np.abs(a - b) / np.maximum(np.abs(b), 1e-9)
cmp = []
for (dsg, e, sh), g in out.groupby(["design", "experiment", "shape"]):
    o = old_p[(old_p.design == dsg) & (old_p.experiment == e) & (old_p["shape"] == sh)].sort_values("quarter")
    for qq in (4, 8):
        a, b = float(g[g.quarter == qq].gdp_per_unit.iloc[0]), float(o[o.quarter == qq].gdp_per_unit.iloc[0])
        cmp.append(dict(design=dsg, experiment=e, shape=sh, quarter=qq, new=a, old=b, rel_diff=abs(a - b) / max(abs(b), 1e-9)))
for qq in (4, 8):
    a, b = float(hike[hike.quarter == qq].gdp.iloc[0]), float(old_h[old_h.quarter == qq].gdp.iloc[0]); cmp.append(dict(design="", experiment="hike", shape="persistent", quarter=qq, new=a, old=b, rel_diff=abs(a - b) / abs(b)))
C = pd.DataFrame(cmp); C.to_csv(RES / "00_frbus_vs_stored.csv", index=False)
print(C[C["shape"] == "persistent"][C.design != "zfixed"].round(5).to_string())
print("max rel diff (persistent, zfree) q4/q8:", C[(C["shape"] == "persistent") & (C.design != "zfixed")].groupby("quarter").rel_diff.agg(["max", "mean"]).round(4).to_dict())
if os.environ.get("FCI_RESULTS"):                      # sync check: do not touch data/; the check compares results/00_* with the stored ones
    print("sync mode: data/ left alone")
else:
    for nm in ("frbus_paths.csv", "frbus_hike_paths.csv"):
        old = DATA / nm; keep = DATA / nm.replace(".csv", "_oldvintage.csv")
        if not keep.exists():
            shutil.copy(old, keep)
    shutil.copy(RES / "00_frbus_paths.csv", DATA / "frbus_paths.csv"); shutil.copy(RES / "00_frbus_hike_paths.csv", DATA / "frbus_hike_paths.csv")
    print("data/frbus_paths.csv and data/frbus_hike_paths.csv replaced (old vintage kept as *_oldvintage.csv)")
print("runtime %.0f s" % (time.time() - t0))
