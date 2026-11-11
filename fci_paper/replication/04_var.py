"""Step 4. The market index's flow: VAR of the unemployment gap and the market index. Main cases: each step of the construction, 12 lags (baseline) and 4 lags; variations:
estimation sample (from 1990, to 2019) and weights from other policy-news series or event samples. For each case: Granger test, response Phi(h) with block-bootstrap bands,
the index's own path, the forward impetus and its correlation with FCI-G (point and over bootstrap draws).
Writes results/var_specs.csv, var_paths_<case>.csv (bands), flow_<case>.csv (flows of the main cases), var_fi_draws.csv."""
import numpy as np, pandas as pd
from lib import data, var, compare as K
from lib.config import RES, REPS
from lib.report import Scalars

D = data.load(); u = D.u_gap
IDX = {c: data.read(f"indexes_{c}.csv") for c in ("nominal", "real", "rstar", "rstar_kiley")}
MV = data.read("market_variants.csv")
H = 36
SPECS = []                                    # (key, market series, FCI-G series, lags, start, end, step label)
for c in IDX:
    for p in (12, 4):
        SPECS.append((f"{c}_p{p}", IDX[c].market, IDX[c].fcig_1yr, p, "1973-01", "2026-09", c))
SPECS += [("rstar_p12_from1990", IDX["rstar"].market, IDX["rstar"].fcig_1yr, 12, "1990-01", "2026-09", "rstar"),
          ("rstar_p12_to2019", IDX["rstar"].market, IDX["rstar"].fcig_1yr, 12, "1973-01", "2019-12", "rstar"),
          ("rstar_p4_from1990", IDX["rstar"].market, IDX["rstar"].fcig_1yr, 4, "1990-01", "2026-09", "rstar"),
          ("rstar_p4_to2019", IDX["rstar"].market, IDX["rstar"].fcig_1yr, 4, "1973-01", "2019-12", "rstar")]
SPECS += [(f"rstar_p12_w_{k}", MV[k], IDX["rstar"].fcig_1yr, 12, "1973-01", "2026-09", "rstar") for k in ("two_year", "to_2019", "no_lower_bound")]
rows, fidraws = [], {}
for key, m, fcig, p, a, b, step in SPECS:
    r, Dd, dum = var.fit(u, m, p, a, b)
    Phi, own = var.response(r)
    gc = r.test_causality("u", ["M"], kind="f")
    ph, ow = var.bootstrap(Dd, dum, p, H, REPS)
    lo90, hi90 = var.bands(ph, 0.90); lo68, hi68 = var.bands(ph, 0.68)
    sig = [h for h in range(1, H + 1) if lo90[h] > 0]
    pd.DataFrame({"h": range(H + 1), "phi": Phi, "own": own, "lo68": lo68, "hi68": hi68, "lo90": lo90, "hi90": hi90}).to_csv(RES / f"var_paths_{key}.csv", index=False)
    mm = m.loc["1974-01":]
    fi = var.forward_impetus(m, Phi)
    fd = []
    for k in range(len(ph)):
        if ph[k, 12] > 0.05:
            fd.append(K.corr(var.forward_impetus(m, ph[k]), fcig))
    fidraws[key] = fd
    rows.append({"key": key, "step": step, "lags": p, "start": a, "end": b, "n": len(Dd), "granger_F": gc.test_statistic, "granger_p": gc.pvalue, "phi6": Phi[6], "phi12": Phi[12], "phi24": Phi[24],
                 "phi12_lo90": lo90[12], "phi12_hi90": hi90[12], "phi12_lo68": lo68[12], "phi12_hi68": hi68[12], "phi24_lo90": lo90[24], "phi24_hi90": hi90[24],
                 "own12": own[12], "own24": own[24], "sig_from": sig[0] if sig else np.nan, "sig_to": sig[-1] if sig else np.nan, "n_sig": len(sig),
                 "corr_fi_fcig": K.corr(fi, fcig), "corr_fi_fcig_lo90": np.percentile(fd, 5), "corr_fi_fcig_hi90": np.percentile(fd, 95)})
    if key in [f"{c}_p{p}" for c in IDX for p in (12, 4)]:
        fl = pd.DataFrame({"forward_impetus": fi, "current_pressure": var.current_pressure(m, Phi)})
        fl.to_csv(RES / f"flow_{key}.csv", float_format="%.5f")
    print(f"{key:28s} F {gc.test_statistic:5.2f} Phi12 {Phi[12]:.2f} [{lo90[12]:.2f},{hi90[12]:.2f}] sig {sig[0] if sig else '-'}-{sig[-1] if sig else '-'} corr FI-FCI-G {rows[-1]['corr_fi_fcig']:.2f}")
T = pd.DataFrame(rows)
T.to_csv(RES / "var_specs.csv", index=False)
pd.DataFrame({k: pd.Series(v) for k, v in fidraws.items()}).to_csv(RES / "var_fi_draws.csv", index=False)
