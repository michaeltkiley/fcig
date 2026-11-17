"""Is the failure of invertibility a feature of Note B's own model? Monte Carlo with Note B's estimated r*-gap model with the FCI as the true process (baseline/lib/simulate.py,
1996-2026, the actual announcement days, surprises drawn from the observed ones; in this process the policy shock IS the window surprise). On each simulated sample, Route 2 is
applied exactly as to the data (12-lag VAR in u, inflation, yield, FCI; window column; shock recovered from u_t), in end-of-month values and in monthly averages.
   python3 05_sim_invertibility.py [--sims 200]
Writes results/sim_invertibility.csv (one row per simulation and data version) and prints medians next to the data's values."""
import argparse, inspect, zlib
import numpy as np, pandas as pd
import lib_r2 as R
from lib import simulate as SIM

ap = argparse.ArgumentParser(); ap.add_argument("--sims", type=int, default=200); a = ap.parse_args()
OUT = R.Path(__file__).resolve().parent / "results"

src = inspect.getsource(SIM.DGP.simulate).replace("return m, fe, z", "return m, fe, z, fb")      # also return the monthly averages
ns = {}; exec(compile("import numpy as np\nfrom lib.simulate import *\n" + inspect.cleandoc("\n" + src), "sim", "exec"), vars(SIM), ns)
dg = SIM.DGP(); rng = np.random.default_rng(zlib.crc32(b"r2sim")); m, fe, z, fb = ns["simulate"](dg, a.sims, rng)
b_eom = np.r_[0, 0, dg.eom]; b_avg = np.r_[0, 0, dg.f0[0]]
rows = []
for s in range(a.sims):
    for kind, F, b in (("eom", fe[s], b_eom), ("avg", fb[s], b_avg)):
        Z = np.concatenate([m[s], F], axis=1); nm = Z.shape[0] - 12; L = 12
        X = np.column_stack([np.ones(nm)] + [Z[12 - l:12 - l + nm] for l in range(1, L + 1)]); Y = Z[12:]
        C = np.linalg.lstsq(X, Y, rcond=None)[0]; U = Y - X @ C; S = U.T @ U / (nm - X.shape[1]); T = R.ma(C, 4, L, 60)
        w = np.linalg.solve(S, b); d = float(b @ w); e = U @ w / d; zz = z[s]
        Zx = np.column_stack([np.ones(nm), U]); res = zz - Zx @ np.linalg.lstsq(Zx, zz, rcond=None)[0]; r2 = 1 - res @ res / ((zz - zz.mean()) @ (zz - zz.mean()))
        r = T @ b; up = R.fevd(T, S, r, 1 / d, (24,))[24]; lo = R.fevd(T, S, r, float((zz ** 2).mean()), (24,))[24]
        rows.append(dict(sim=s, kind=kind, r2_z_u=r2, corr_e_z=np.corrcoef(e, zz)[0, 1], sd_e=np.sqrt(1 / d), sd_z=np.sqrt((zz ** 2).mean()),
                         var_ratio=(1 / d) / (zz ** 2).mean(), fevd_u24_upper=up[0], fevd_u24_lower=lo[0], fevd_pi24_upper=up[1], fevd_pi24_lower=lo[1]))
D = pd.DataFrame(rows); D.to_csv(OUT / "sim_invertibility.csv", index=False, float_format="%.5f")
print(D.groupby("kind").quantile([0.05, 0.5, 0.95]).drop(columns="sim").round(4).to_string())
