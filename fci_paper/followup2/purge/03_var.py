"""(c, d) Two-variable VAR (u first, 12 lags) with the unpurged and purged index: Phi(6, 12, 24) with 90% block-bootstrap intervals (500 draws, 12-month blocks, lib/var.py),
Granger p, the forward impetus and its correlation with the unpurged forward impetus (same sample). 30 specifications (2 indexes x 3 steps x 5 version/sample). Writes out/var.csv, out/var_paths_*.csv, out/fi_*.csv"""
from common import *
from lib import var
from lib.config import REPS
P = load_purged(); u = data.load().u_gap
rows, FI = [], {}
for kind in VARS:
    for s in STEPS:
        for v, start in (("unpurged", "1973-01"), ("full", "1973-01"), ("unpurged", "1983-01"), ("full", "1983-01"), ("recursive", "1983-01")):
            m = P[(kind, s, v)]
            r, Dd, dum = var.fit(u, m, 12, start, "2026-09")
            Phi, own = var.response(r)
            gc = r.test_causality("u", ["M"], kind="f")
            ph, _ = var.bootstrap(Dd, dum, 12, 36, REPS)
            lo, hi = var.bands(ph, 0.90)
            fi = var.forward_impetus(m, Phi)
            FI[(kind, s, v, start)] = fi
            rows.append({"kind": kind, "step": s, "version": v, "start": start, "n": len(Dd), "granger_F": gc.test_statistic, "granger_p": gc.pvalue,
                         "phi6": Phi[6], "phi12": Phi[12], "phi12_lo90": lo[12], "phi12_hi90": hi[12], "phi24": Phi[24], "phi24_lo90": lo[24], "phi24_hi90": hi[24],
                         "n_sig_h": int((lo[1:] > 0).sum()), "own12": own[12], "sd_M": m.loc[start:].std(), "sd_flow": m.diff(12).loc[start:].std()})
            print(kind, s, v, start, f"Phi12 {Phi[12]:.2f} [{lo[12]:.2f},{hi[12]:.2f}] F {gc.test_statistic:.2f} p {gc.pvalue:.3f}", flush=True)
            pd.DataFrame({"h": range(37), "phi": Phi, "lo90": lo, "hi90": hi}).to_csv(OUT / f"var_paths_{kind}_{s}_{v}_{start[:4]}.csv", index=False)
V = pd.DataFrame(rows)
# forward-impetus correlations with the unpurged FI on the same sample start
for i, r in V.iterrows():
    base = FI[(r.kind, r.step, "unpurged", r.start)]; this = FI[(r.kind, r.step, r.version, r.start)]
    sl = slice("1984-01", None)
    V.loc[i, "corr_fi_unpurged"] = base.loc[sl].corr(this.loc[sl])
V.to_csv(OUT / "var.csv", index=False)
pd.DataFrame({"|".join(k): v for k, v in FI.items()}).to_csv(OUT / "forward_impetus.csv", float_format="%.5f")
