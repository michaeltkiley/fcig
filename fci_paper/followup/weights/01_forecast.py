"""Recursive out-of-sample forecasts of five outcomes at 6, 12, 24 months from weight sets on a common basis.
Design (pre-specified, see RESULT.md): steps r*-gap (primary) and real (secondary); forms level and 12-month change; sets MKT, FRBUS3, PC1, EQ, ACT (three variables)
and the full indexes as given (GS, FRB/US, NFCI, ANFCI; and, as given flows, FCI-G 1-year and FRB/US growth impetus, in the change form only).
Each forecast: y(t+h) on a constant, the outcome's own current value, and one index (recession: constant and index). Origins 1995-01 on, expanding window.
Writes results/oos_cells.csv (one row per step-form-outcome-h-set) and results/oos_pairs.csv (paired contrasts with the market weights)."""
import sys; sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, pandas as pd
import common as c

D = c.load_monthly()
mw = pd.read_csv(c.RES_IN / "market_weights.csv", index_col=0).weight.reindex(c.VARS).values
fw = pd.read_csv(c.RES_IN / "frbus_weights.csv", index_col=0).frbus_weight.reindex(c.VARS).values
J = pd.period_range(c.SAMPLE0, "2026-09", freq="M")
origins = list(pd.period_range(c.FIRST, "2026-09", freq="M"))
rows, pairs, ERR = [], [], {}
for case in ("rstar", "real"):
    S, I, Z = c.fixed_sets(D, case, mw, fw)
    chk = np.abs((Z @ mw - I.market).dropna()).max(); assert chk < 1e-4, chk       # the three-variable market index is the package's market index
    for form in ("level", "change"):
        fixed = {k: c.to_form(v, form) for k, v in S.items()}
        if form == "change": fixed["FCIG"] = I.fcig_1yr; fixed["FRBUS_gi"] = I.frbus_gi_hp          # flows as given
        Zo = c.to_form(Z * c.ORIENT, form)
        for h in c.HORIZONS:
            O = c.outcomes(D, h)
            for oc, (y, own, valid) in O.items():
                R = c.recursive_forecasts(J, y, own, valid, fixed, Zo, h, origins, c.OUTCOMES[oc])
                a = R["actual"]; lag = c.HACLAG(h); e = {k: a - R[k] for k in R if k not in ("actual", "t", "wts")}
                mse0 = (e["base"] ** 2).mean()
                for k in e: ERR[f"{case}|{form}|{oc}|{h}|{k}"] = e[k]
                ERR[f"{case}|{form}|{oc}|{h}|t"] = np.array([p.ordinal for p in R["t"]])
                for k in e:
                    if k == "base": continue
                    rows.append(dict(step=case, form=form, outcome=oc, h=h, set=k, n=len(a), mse_ratio_base=(e[k] ** 2).mean() / mse0,
                                     cw_t=c.cw(e["base"], e[k], R["base"], R[k], lag)))
                    if k != "MKT":
                        d = e[k] ** 2 - e["MKT"] ** 2
                        pairs.append(dict(step=case, form=form, outcome=oc, h=h, set=k, n=len(a), mse_ratio_mkt=(e[k] ** 2).mean() / (e["MKT"] ** 2).mean(), dm_t=c.dm(d, lag)))
        print(case, form, "done", flush=True)
pd.DataFrame(rows).to_csv(c.OUT / "oos_cells.csv", index=False); pd.DataFrame(pairs).to_csv(c.OUT / "oos_pairs.csv", index=False)
np.savez_compressed(c.OUT / "oos_errors.npz", **ERR)
