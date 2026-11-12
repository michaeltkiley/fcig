"""Step 22 (weights by persistence). FRB/US weight vectors b (10-year yield, equity valuation, real dollar; funds-rate points per unit, GDP at four quarters) under the persistence assumptions
of the paper's sensitivity envelope: persistent paths and a common decaying path with half-lives of 8, 4 and 2 quarters for all three variables (priced from the temporary-shock responses
by linearity, exactly as step 18's matched paths: lib/agree_core.b_path), with b'psi (FRB/US reading of the usual announcement response) and the normalized weights. Verified against
step 18's matched-path results. Writes results/22_weights_by_persistence.csv and scalars_22_weights_persist.csv."""
import numpy as np, pandas as pd
from lib.agree_core import load_frbus, b_path, b_persist, MV
from lib.config import RES
from lib.report import Scalars

S = Scalars("22_weights_persist")
mw = pd.read_csv(RES / "market_weights.csv", index_col=0); psi = mw.response.values; wM = mw.weight.values
R, G = load_frbus(); names = ("ten", "eq", "usd"); rows = []
for h in (2, 4, 8):
    for lab, hl in (("persistent", np.inf), ("hl8", 8.0), ("hl4", 4.0), ("hl2", 2.0)):
        bv = b_persist(R, G, h) if np.isinf(hl) else b_path(R, G, h, (hl,) * 3)
        bp = float(bv @ psi); wb = bv / bp
        rec = dict(h=h, path=lab, half_life=hl, bpsi=bp, ratio_usd_eq=float(bv[2] * 3.9 / (bv[1] * -5.0)), ratio_of_ratios=float((bv[2] * 3.9 / (bv[1] * -5.0)) / (wM[2] * 3.9 / (wM[1] * -5.0))))
        for k, n in enumerate(names): rec[f"b_{n}"] = float(bv[k]); rec[f"wB_{n}"] = float(wb[k])
        rows.append(rec)
T = pd.DataFrame(rows); T.to_csv(RES / "22_weights_by_persistence.csv", index=False, float_format="%.6f")
# verification against step 18 (matched paths, point estimates), when step 18's results exist in this results directory
mp = pd.read_csv(RES / "18_matched_paths.csv") if (RES / "18_matched_paths.csv").exists() else None
maxd = np.nan
if mp is not None:
    d = []
    for _, r in T[T.h == 4].iterrows():
        sel = mp[(mp.h == 4) & (mp.path == r.path)]
        for q, key in (("bpsi", "bpsi"), ("b_ten", "b_ten"), ("b_eq", "b_eq"), ("b_usd", "b_usd"), ("ratio_usd_eq", "ratio_usd_eq"), ("ratio_of_ratios", "ratio_of_ratios")):
            d.append(abs(float(sel[sel.quantity == q].point.iloc[0]) - r[key]))
    maxd = max(d[i] for i, (_, r) in enumerate([(i, r) for _, r in T[T.h == 4].iterrows() for i in range(6)]) if r.path != "persistent")
    maxp = max(d[i] for i, (_, r) in enumerate([(i, r) for _, r in T[T.h == 4].iterrows() for i in range(6)]) if r.path == "persistent")
    # decaying paths agree exactly; 'persistent' here is the direct persistent run (as the package uses it), step 18's matched path uses the cumulated temporary responses (linearity)
    assert maxd < 1e-5 and maxp < 2e-3, f"22_weights_persist disagrees with step 18 matched paths by {maxd}, {maxp}"
    S.add("max_abs_diff_persistent_vs_cumulated_temporary", maxp)
S.add("max_abs_diff_vs_step18", maxd)
for _, r in T.iterrows():
    for k in ("bpsi", "b_ten", "b_eq", "b_usd", "ratio_usd_eq", "ratio_of_ratios"):
        S.add(f"h{int(r.h)}_{r.path}_{k}", r[k])
S.save(); print(T.round(4).to_string()); print("max diff vs step 18:", maxd)
