"""Step 11. Is the index's content only activity reflected back? Index inputs purged of the unemployment gap and 12-month core PCE inflation (Hatzius et al. 2010 style).

PRE-SPECIFIED DESIGN (ported unchanged from followup2/purge)
 purge   : each input x_t, in the form it takes at the step (nominal, real, r*-gap with LW r*), regressed on a constant, u_t..u_{t-12} (unemployment gap) and
           pi_t..pi_{t-12} (12-month core PCE inflation, 100 ln(P_t/P_{t-12})). Residuals replace the inputs; the index is rebuilt with unchanged weights
           (market: results/market_weights.csv on y10, equities, dollar; GS: published weights x conversion to 2-year units).
 versions: unpurged; full (one regression on 1973-01..2026-09); recursive (expanding window 1973-01..t, first residual 1983-01, coefficients re-estimated monthly).
 (a) correlations of purged with unpurged level and 12-month change, 1984+ (and 1974+ for the full purge); R2 of each input on the purge regressors.
 (b) LPs: 12-month change in the unemployment gap and 12-month payroll growth on the standardised level and 12-month flow jointly, with own lags; HAC(18);
     Covid rule (any t-12..t+12 in 2020-01..2021-03 dropped). Origins from 1976-03 (unpurged, full) and 1983-03 (all three versions, same sample).
 (c) VAR (lib/var.py: u first, 12 lags, 2020 dummies), 90% moving-block bootstrap (REPS draws, 12-month blocks) of Phi(12) and Phi(24) at 1973-01 (unpurged, full)
     and 1983-01 (all three); Granger p; forward impetus and its correlation with the unpurged forward impetus.
 Counts: 2 indexes x 3 steps x 5 (version, sample) = 30 VARs; LPs 2 outcomes x 30 = 60 regressions (120 coefficients). Descriptive: shared data, no multiple-testing adjustment.
 Primary: market r*-gap, unemployment-gap outcome (flow t-statistic and Phi(12) interval, purged versus unpurged on the same sample).
Writes results/11_purged_indexes.csv, 11_r2.csv, 11_corr.csv, 11_lp.csv, 11_var.csv, 11_var_paths.csv, scalars_11_purge.csv."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from lib import data, var
from lib.config import RES, REPS, SEED, START, END
from lib.report import Scalars
from lib.purge_util import monthly, covid
from lib import purge_purge as P

from lib.purge_util import single_thread_blas
single_thread_blas()
S = Scalars("11_purge")
D, XS = P.all_inputs()
conv = pd.read_csv(RES / "conversions.csv", index_col=0).to_2y["GS"]
mw = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
Z = P.regressors(D.u_gap, P.core_inflation())
assert not Z.isna().any().any()

# ---- build
IDX, r2rows = {}, []
for s in P.STEPS:
    X = XS[s].loc[START:END]
    for kind, cols in P.VARS.items():
        Xf, Xr = X[cols].copy(), X[cols].copy()
        for c in cols:
            Xf[c], r2 = P.purge_full(X[c], Z); Xr[c] = P.purge_recursive(X[c], Z)
            r2rows.append({"kind": kind, "step": s, "var": c, "r2_full": r2}); S.add(f"r2_{kind}_{s}_{c}", r2)
        IDX[(kind, s, "unpurged")] = P.build_index(X, kind, conv, mw)
        IDX[(kind, s, "full")] = P.build_index(Xf, kind, conv, mw)
        IDX[(kind, s, "recursive")] = P.build_index(Xr, kind, conv, mw)
pd.DataFrame({"|".join(k): v for k, v in IDX.items()}).to_csv(RES / "11_purged_indexes.csv", float_format="%.5f")
pd.DataFrame(r2rows).to_csv(RES / "11_r2.csv", index=False)
chk = pd.read_csv(RES / "indexes_rstar.csv", index_col=0)
S.add("check_unpurged_vs_step3", float(np.abs(IDX[("market", "rstar", "unpurged")].values - chk.market.values).max()))

# ---- (a) correlations
rows = []
for kind in P.VARS:
    for s in P.STEPS:
        U = IDX[(kind, s, "unpurged")]
        for v in ("full", "recursive"):
            Q = IDX[(kind, s, v)]
            for lab, sl in (("1984+", slice("1984-01", None)), ("1973+", slice("1974-01", None))):
                if v == "recursive" and lab == "1973+":
                    continue
                u_, q_ = U.loc[sl], Q.loc[sl]
                r = {"kind": kind, "step": s, "version": v, "sample": lab, "n": int(q_.dropna().size), "corr_level": u_.corr(q_), "corr_flow": u_.diff(12).corr(q_.diff(12)),
                     "sd_level_ratio": q_.std() / u_.std(), "sd_flow_ratio": q_.diff(12).std() / u_.diff(12).std()}
                rows.append(r)
                if lab == "1984+":
                    S.add(f"corr_level_{kind}_{s}_{v}", r["corr_level"]); S.add(f"corr_flow_{kind}_{s}_{v}", r["corr_flow"])
C = pd.DataFrame(rows); C.to_csv(RES / "11_corr.csv", index=False)
for v in ("full", "recursive"):
    c1 = C[(C.version == v) & (C["sample"] == "1984+")]
    for k in ("level", "flow"):
        S.add(f"corr_{k}_{v}_min", c1[f"corr_{k}"].min()); S.add(f"corr_{k}_{v}_max", c1[f"corr_{k}"].max())

# ---- (b) local projections
u = D.u_gap; pay = np.log(monthly("PAYEMS")) * 100
Y = pd.DataFrame({"du": u.shift(-12) - u, "pay": pay.shift(-12) - pay})
CTL = {"du": pd.DataFrame({"u": u, "du12": u - u.shift(12)}), "pay": pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))})}
rec = monthly("USREC")


def design(x, yn, start):
    Dd = pd.concat([Y[yn].rename("y"), CTL[yn], x.rename("lvl"), (x - x.shift(12)).rename("flw")], axis=1).loc[start:END]
    Dd = Dd[[not any(covid(t + k) for k in range(-12, 13)) for t in Dd.index]].dropna()
    for c in ("lvl", "flw"):
        Dd[c] = (Dd[c] - Dd[c].mean()) / Dd[c].std()
    return Dd


def fit(Dd, cols):
    return sm.OLS(Dd.y, sm.add_constant(Dd[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": 18})


VS = (("unpurged", "1976-03"), ("full", "1976-03"), ("unpurged", "1983-03"), ("full", "1983-03"), ("recursive", "1983-03"))
rows = []
for yn, own in (("du", ["u", "du12"]), ("pay", ["g12", "g3"])):
    for kind in P.VARS:
        for s in P.STEPS:
            for v, start in VS:
                Dd = design(IDX[(kind, s, v)], yn, start)
                rB, rF, rL = fit(Dd, own + ["lvl", "flw"]), fit(Dd, own + ["flw"]), fit(Dd, own + ["lvl"])
                a0 = sm.OLS(Dd.y, sm.add_constant(Dd[own])).fit().rsquared_adj
                rr = rec.reindex(Dd.index).fillna(0)
                row = {"outcome": yn, "kind": kind, "step": s, "version": v, "start": start, "n": len(Dd), "n_recessions": int(((rr == 1) & (rr.diff() == 1)).sum()),
                       "b_flw": rB.params["flw"], "t_flw": rB.tvalues["flw"], "b_lvl": rB.params["lvl"], "t_lvl": rB.tvalues["lvl"],
                       "gain_both": rB.rsquared_adj - a0, "gain_flw_alone": rF.rsquared_adj - a0, "t_flw_alone": rF.tvalues["flw"], "t_lvl_alone": rL.tvalues["lvl"]}
                rows.append(row)
                tag = f"{yn}_{kind}_{s}_{v}_{start[:4]}"
                S.add(f"lp_tflw_{tag}", row["t_flw"]); S.add(f"lp_bflw_{tag}", row["b_flw"]); S.add(f"lp_tlvl_{tag}", row["t_lvl"])
L = pd.DataFrame(rows); L.to_csv(RES / "11_lp.csv", index=False)
S.add("lp_n_1976", int(L[L.start == "1976-03"].n.iloc[0])); S.add("lp_n_1983", int(L[(L.start == "1983-03") & (L.version == "full")].n.iloc[0]))
S.add("lp_n_1983_recursive", int(L[(L.start == "1983-03") & (L.version == "recursive")].n.iloc[0]))

# ---- (c) VAR
rows, FI, paths = [], {}, []
for kind in P.VARS:
    for s in P.STEPS:
        for v, start in (("unpurged", "1973-01"), ("full", "1973-01"), ("unpurged", "1983-01"), ("full", "1983-01"), ("recursive", "1983-01")):
            m = IDX[(kind, s, v)]
            r, Dd, dum = var.fit(u, m, 12, start, END)
            Phi, own = var.response(r)
            gc = r.test_causality("u", ["M"], kind="f")
            ph = P.bootstrap_fast(Dd, dum, 12, 36, REPS)
            lo, hi = var.bands(ph, 0.90)
            FI[(kind, s, v, start)] = var.forward_impetus(m, Phi)
            row = {"kind": kind, "step": s, "version": v, "start": start, "n": len(Dd), "granger_F": gc.test_statistic, "granger_p": gc.pvalue,
                   "phi6": Phi[6], "phi12": Phi[12], "phi12_lo90": lo[12], "phi12_hi90": hi[12], "phi24": Phi[24], "phi24_lo90": lo[24], "phi24_hi90": hi[24],
                   "n_sig_h": int((lo[1:] > 0).sum()), "own12": own[12], "sd_M": m.loc[start:].std(), "sd_flow": m.diff(12).loc[start:].std()}
            rows.append(row)
            tag = f"{kind}_{s}_{v}_{start[:4]}"
            for k in ("phi12", "phi12_lo90", "phi12_hi90", "phi24", "granger_p"):
                S.add(f"var_{k}_{tag}", row[k])
            paths.append(pd.DataFrame({"kind": kind, "step": s, "version": v, "start": start, "h": range(37), "phi": Phi, "lo90": lo, "hi90": hi}))
            print(tag, f"Phi12 {Phi[12]:.2f} [{lo[12]:.2f},{hi[12]:.2f}] p {gc.pvalue:.3f}", flush=True)
V = pd.DataFrame(rows)
for i, r in V.iterrows():
    base, this = FI[(r.kind, r.step, "unpurged", r.start)], FI[(r.kind, r.step, r.version, r.start)]
    sl = slice("1984-01", None)
    V.loc[i, "corr_fi_unpurged"] = base.loc[sl].corr(this.loc[sl])
    S.add(f"var_corr_fi_{r.kind}_{r.step}_{r.version}_{r.start[:4]}", V.loc[i, "corr_fi_unpurged"])
V.to_csv(RES / "11_var.csv", index=False); pd.concat(paths).to_csv(RES / "11_var_paths.csv", index=False)
S.add("var_n_specs", len(V)); S.add("var_n_interval_excludes_zero", int((V.phi12_lo90 > 0).sum())); S.add("var_n_granger_p_below_01_rstar", int(((V.step == "rstar") & (V.granger_p < 0.01)).sum()))
for kind in P.VARS:
    for st in ("1973", "1983"):
        a = V[(V.kind == kind) & (V.step == "rstar") & (V.start == f"{st}-01")].set_index("version")
        for v in ("full", "recursive"):
            if v in a.index:
                S.add(f"var_phi12_fall_pct_{kind}_rstar_{v}_{st}", 100 * (1 - a.loc[v, "phi12"] / a.loc["unpurged", "phi12"]))
S.save()
