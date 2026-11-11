"""Fuller bootstrap for the baseline cases (12 lags): each draw also re-estimates the daily block on a moving-block resample of its rows (66-day blocks), in addition to resampling
announcements and monthly residuals (same announcement draws as step 3). Point estimates are those of step 3; only the intervals change.
   python3 10_fuller_bootstrap.py [--draws 500]       Output: results/fullboot.csv (case, var, h, point, 90% interval of the main bootstrap and of the fuller bootstrap)."""
import os, argparse
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, pandas as pd
import cases as CS
from lib import model as M, daily as DD
from lib.paths import RESULTS

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); a = ap.parse_args()
DD.use_surprise("ns"); rows = []
for c in CS.PANELS[0]["cases"]:
    e = M.estimate_full(c["form"], c["fci"], c["macro"], c["start"], c["end"], c["t2020"], c["trend"], a.draws, 12)
    base = pd.read_csv(RESULTS / f"{CS.case_id(c)}.csv"); base = base[base.lags == 12]
    for j, v in enumerate(("u", "P")):
        b = base[base["var"] == v].iloc[0]
        for h in (12, 24, 36):
            rows.append(dict(form=c["form"], fci=str(c["fci"]), var=v, h=h, point=e["s0"][h, j], lo_fuller=np.percentile(e["sd"][:, h, j], 5), hi_fuller=np.percentile(e["sd"][:, h, j], 95), lo_main=b[f"lo{h}"], hi_main=b[f"hi{h}"], point_main=b[f"r{h}"]))
    print(c["form"], c["fci"], "done", flush=True)
pd.DataFrame(rows).to_csv(RESULTS / "fullboot.csv", index=False, float_format="%.4f")
