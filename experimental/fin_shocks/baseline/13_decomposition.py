"""Step 13. How much do policy shocks explain? Route 1 (measured surprises) and Route 2 (policy-direction shocks, daily from 1990 with the monthly splice before), propagated through
Note B's r*-gap model from 1996 and from 1973 (2020 dropped), with and without the FCI; two treatments of March-December 2020 (infer = main, absorb = robustness). Also the appendix
diagnostics: the monthly invertibility table and its Monte Carlo. Specification in lib/decomp.py. Reads output/draws of step 3 (bands).
   python3 13_decomposition.py [--draws 500] [--sims 200]
Output: results/decomp_shares.csv (variance shares), results/decomp_bands.csv (5-95% bands of the shares), results/decomp_overlap.csv (splice), results/decomp_hd_<tag>.csv
(historical contributions, monthly), results/decomp_diagnostics.csv, results/decomp_sim.csv; output/decomp/ (daily shocks and the band draws of the historical decomposition)."""
import os, argparse
os.environ.setdefault("OMP_NUM_THREADS", "1")
import pandas as pd
from lib import decomp as DC
from lib.paths import RESULTS, OUT

ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); ap.add_argument("--sims", type=int, default=200); a = ap.parse_args()
(OUT / "decomp").mkdir(exist_ok=True)
shares, bands, ov = [], [], []
for fci in ("rstar", 0):
    r = DC.run(fci, B=a.draws, save_hd=OUT / "decomp"); shares += r["shares"]; bands += r["bands"]; ov.append(r["overlap"])
    for tag, d in r["hd"].items(): d.to_csv(RESULTS / f"decomp_hd_{tag}.csv", index=False, float_format="%.5f")
    for mode, d in r["daily"].items(): d.to_csv(OUT / "decomp" / f"daily_shocks_rstar_{fci}_{mode}.csv", index=False, float_format="%.6f")
    print("decomposition", fci, "done", flush=True)
for fci in ("rstar", 0):                                                             # robustness (D9): pre-1990 monthly shocks unscaled (point estimates)
    shares += [dict(r, mode=r["mode"] + "_unscaled") for r in DC.run(fci, modes=("infer",), bands=False, scale_pre=False)["shares"] if r["era"] == "1974-1989"]
pd.DataFrame(shares).to_csv(RESULTS / "decomp_shares.csv", index=False, float_format="%.5f"); pd.DataFrame(bands).to_csv(RESULTS / "decomp_bands.csv", index=False, float_format="%.5f")
pd.DataFrame(ov).to_csv(RESULTS / "decomp_overlap.csv", index=False, float_format="%.4f")
diag = [DC.diagnostics(DC.monthly_var(s, f, st, L)) for s in ("nom", "real", "rstar") for f in (0, s) for st in ("1973-01", "1996-01") for L in (12,)]
pd.DataFrame(diag).to_csv(RESULTS / "decomp_diagnostics.csv", index=False, float_format="%.4f")
sim = DC.sim_invertibility(a.sims); sim.to_csv(RESULTS / "decomp_sim.csv", index=False, float_format="%.5f")
print(pd.DataFrame(ov).round(3).to_string(index=False)); print(sim.drop(columns="sim").quantile([0.05, 0.5, 0.95]).round(3).to_string())
