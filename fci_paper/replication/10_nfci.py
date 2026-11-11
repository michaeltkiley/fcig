"""Step 10. The market index and the NFCI/ANFCI: complement or substitute?
Market flow = 12-month change of the r*-gap market index (results/indexes_rstar.csv); NFCI and ANFCI = monthly means of the published weekly levels.
Outcomes: change in the unemployment gap and payroll growth at 6, 12, 24 months; GDP growth over 2, 4, 8 quarters; any NBER recession month in t+1..t+12 (logit).
Own lags as in step 9. Regressors standardised. Origins from 1976-03, windows touching 2020-01..2021-03 dropped. Pre-specified design:
 (a) joint: own + market flow + NFCI, own + market flow + ANFCI, and each alone: 5 specs x (9 mean horizons + recession) ; HAC with max(12, h+6) lags
     (quarterly: max(4, h+2)); 90% interval from a moving-block bootstrap of rows (block = HAC lags, REPS draws). 20 joint models, 40 joint coefficients: read as a pattern.
 (b) NFCI/ANFCI level versus flow (own 12-month change), same outcomes (unemployment and payrolls).
 (c) recursive out-of-sample from 1995 (1995Q1), training ends h before the origin: market, NFCI, ANFCI, joint and equal-weight combination; Clark-West (nested),
     Diebold-Mariano on the combination, encompassing regression of (y - f_NFCI) on (f_mkt - f_NFCI); 12-month recession logit with Brier scores. About 40 tests.
 (d) decomposition: R2 of NFCI, ANFCI (and the market index/flow) on the 10-year yield, CAPE and real dollar, with and without the Baa-10y spread, in levels and 12-month changes.
Writes results/10_joint_lp.csv, 10_level_vs_flow.csv, 10_oos_encompassing.csv, 10_oos_recession.csv, 10_nfci_on_variables.csv, 10_correlations.csv, scalars_10_nfci.csv."""
import warnings
import numpy as np, pandas as pd, statsmodels.api as sm
from lib.config import RES, REPS, SEED
from lib.report import Scalars
from lib import levelflow_common as C

warnings.filterwarnings("ignore")
S = Scalars("10_nfci")
I = C.read_res("indexes_rstar.csv"); D0 = C.read_res("data_monthly.csv")
X = pd.DataFrame({"mkt": I["market"], "nfci": C.weekly_to_month("NFCI"), "anfci": C.weekly_to_month("ANFCI")})
X["mkt_flw"] = X.mkt - X.mkt.shift(12)
rng = np.random.default_rng(SEED)


def design(h, outcome, xcols, X=X):
    y, own = C.outcomes(h)[outcome]
    F = pd.concat([y.rename("y"), own, X[xcols]], axis=1).loc[C.START:C.LAST]
    F = F[[not any(C.covid(t + k) for k in range(-12, h + 1)) for t in F.index]].dropna()
    return C.standardise(F, xcols), list(own.columns)


def design_rec(xcols, X=X):
    F = X[xcols].loc[C.START:C.LAST].copy(); F["y"] = C.recession_future(F.index)
    F = F[[not any(C.covid(t + k) for k in range(-12, 13)) for t in F.index]].dropna()
    return C.standardise(F, xcols)


def design_gdp(hq, xcols, X=X):
    g = np.log(C.fred("GDPC1")) * 100; g.index = g.index.to_period("Q")
    y = g.shift(-hq) - g; own = (g - g.shift(4)).rename("g4")
    Xq = X[xcols][X.index.month.isin([3, 6, 9, 12])].copy(); Xq.index = Xq.index.asfreq("Q")
    F = pd.concat([y.rename("y"), own, Xq], axis=1).loc["1976Q1":"2026Q2"]
    F = F[[not any(((q + k).year == 2020) or ((q + k).year == 2021 and (q + k).quarter == 1) for k in range(-4, hq + 1)) for q in F.index]].dropna()
    return C.standardise(F, xcols), ["g4"]


def get(outc, h, xc):
    return design_gdp(h, xc) if outc == "gdp" else design(h, outc, xc)


def lags_for(outc, h):
    return max(4, h + 2) if outc == "gdp" else max(12, h + 6)


def fit(F, own, xc, lags):
    return sm.OLS(F.y, sm.add_constant(F[own + xc])).fit(cov_type="HAC", cov_kwds={"maxlags": lags})


def boot(F, own, xc, block):
    A = np.c_[np.ones(len(F)), F[own + xc].values]; y = F.y.values; n = len(y); nb = int(np.ceil(n / block)); out = []
    for _ in range(REPS):
        st = rng.integers(0, n - block + 1, nb); ix = np.concatenate([np.arange(s, s + block) for s in st])[:n]
        out.append(np.linalg.lstsq(A[ix], y[ix], rcond=None)[0][1 + len(own):])
    return np.percentile(out, [5, 95], axis=0)


def tstat(d, lags):
    return sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lags}).tvalues[0]


# (a) joint local projections
rows = []
specs = {"joint_nfci": ["mkt_flw", "nfci"], "joint_anfci": ["mkt_flw", "anfci"], "mkt_flw_alone": ["mkt_flw"], "nfci_alone": ["nfci"], "anfci_alone": ["anfci"]}
for spec, xc in specs.items():
    for outc, hs in (("du", (6, 12, 24)), ("pay", (6, 12, 24)), ("gdp", (2, 4, 8))):
        for h in hs:
            F, own = get(outc, h, xc); lg = lags_for(outc, h)
            m0 = sm.OLS(F.y, sm.add_constant(F[own])).fit(); m = fit(F, own, xc, lg); bi = boot(F, own, xc, lg)
            for j, c in enumerate(xc):
                rows.append(dict(spec=spec, outcome=outc, h=h, var=c, n=len(F), first=str(F.index[0]), last=str(F.index[-1]), b=m.params[c], t_hac=m.tvalues[c],
                                 lo90=bi[0, j], hi90=bi[1, j], gain_adjR2=m.rsquared_adj - m0.rsquared_adj, hac_lags=lg))
    F = design_rec(xc)
    m = sm.Logit(F.y, sm.add_constant(F[xc])).fit(disp=0, cov_type="HAC", cov_kwds={"maxlags": 18})
    for c in xc:
        rows.append(dict(spec=spec, outcome="rec12", h=12, var=c, n=len(F), first=str(F.index[0]), last=str(F.index[-1]), b=m.params[c], t_hac=m.tvalues[c], gain_adjR2=m.prsquared, hac_lags=18))
R = pd.DataFrame(rows); R.to_csv(RES / "10_joint_lp.csv", index=False)
for _, r in R[R.spec.str.startswith("joint")].iterrows():
    for c in ("b", "t_hac", "lo90", "hi90"):
        if pd.notna(r[c]): S.add(f"nfci_{r.spec[6:]}_{r.outcome}_h{r.h}_{r['var']}_{c}", r[c])

# (b) level versus flow for NFCI / ANFCI
X2 = X.copy()
for v in ("nfci", "anfci"): X2[v + "_flw"] = X2[v] - X2[v].shift(12)
rows = []
for v in ("nfci", "anfci"):
    for outc in ("du", "pay"):
        for h in (6, 12, 24):
            F, own = design(h, outc, [v, v + "_flw"], X2); lg = lags_for(outc, h)
            m = fit(F, own, [v, v + "_flw"], lg); m0 = sm.OLS(F.y, sm.add_constant(F[own])).fit()
            mL = fit(F, own, [v], lg); mF = fit(F, own, [v + "_flw"], lg)
            rows.append(dict(index=v, outcome=outc, h=h, n=len(F), t_lvl_both=m.tvalues[v], t_flw_both=m.tvalues[v + "_flw"], t_lvl_alone=mL.tvalues[v], t_flw_alone=mF.tvalues[v + "_flw"],
                             gain_lvl=mL.rsquared_adj - m0.rsquared_adj, gain_flw=mF.rsquared_adj - m0.rsquared_adj))
    F = design_rec([v, v + "_flw"], X2)
    m = sm.Logit(F.y, sm.add_constant(F[[v, v + "_flw"]])).fit(disp=0, cov_type="HAC", cov_kwds={"maxlags": 18})
    rows.append(dict(index=v, outcome="rec12", h=12, n=len(F), t_lvl_both=m.tvalues[v], t_flw_both=m.tvalues[v + "_flw"]))
L = pd.DataFrame(rows); L.to_csv(RES / "10_level_vs_flow.csv", index=False)
for _, r in L.iterrows():
    S.add(f"nfci_lf_{r['index']}_{r.outcome}_h{r.h}_t_level", r.t_lvl_both); S.add(f"nfci_lf_{r['index']}_{r.outcome}_h{r.h}_t_flow", r.t_flw_both)

# (c) recursive out-of-sample
def run(F, own, h, lags, first, monthly):
    spec = {"own": own, "M": own + ["mkt_flw"], "N": own + ["nfci"], "A": own + ["anfci"], "MN": own + ["mkt_flw", "nfci"], "MA": own + ["mkt_flw", "anfci"]}
    P = {k: [] for k in spec}; yy = []
    for t in F.index:
        if t < pd.Period(first, freq=F.index.freq): continue
        tr = F.loc[:t - h]
        if len(tr) < (100 if monthly else 40): continue
        yy.append(F.loc[t, "y"])
        for k, c in spec.items():
            b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[c].values], tr.y.values, rcond=None)[0]
            P[k].append(b @ np.r_[1, F.loc[t, c].values.astype(float)])
    P = {k: np.array(v) for k, v in P.items()}; y = np.array(yy); e = {k: y - v for k, v in P.items()}
    out = {"n_oos": len(y)}
    for k in ("M", "N", "A", "MN", "MA"): out[f"rmse_{k}_vs_own"] = np.sqrt((e[k] ** 2).mean() / (e["own"] ** 2).mean())
    out["rmse_M_vs_N"] = np.sqrt((e["M"] ** 2).mean() / (e["N"] ** 2).mean())
    for big, small in (("MN", "N"), ("MN", "M"), ("MA", "A"), ("MA", "M")):
        out[f"cw_{big}_vs_{small}"] = tstat(e[small] ** 2 - (e[big] ** 2 - (P[small] - P[big]) ** 2), lags)
    for nm, idx in (("combo_MN", "N"), ("combo_MA", "A")):
        ec = y - 0.5 * (P["M"] + P[idx])
        for s, lab in (("M", "M"), (idx, "idx")):
            out[f"{nm}_mse_gain_vs_{lab}"] = 1 - (ec ** 2).mean() / (e[s] ** 2).mean(); out[f"{nm}_dm_vs_{lab}"] = tstat(e[s] ** 2 - ec ** 2, lags)
        m = sm.OLS(y - P[idx], P["M"] - P[idx]).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
        out[f"{nm}_lam_mkt_weight"] = m.params[0]; out[f"{nm}_lam_t"] = m.tvalues[0]
        gr = np.linalg.lstsq(np.c_[P["M"], P[idx]], y, rcond=None)[0]; out[f"{nm}_GR_w_mkt"] = gr[0]; out[f"{nm}_GR_w_idx"] = gr[1]
    return out


rows = []
for outc, hs in (("du", (6, 12, 24)), ("pay", (6, 12, 24)), ("gdp", (2, 4, 8))):
    for h in hs:
        F, own = get(outc, h, ["mkt_flw", "nfci", "anfci"])
        r = run(F, own, h, lags_for(outc, h), "1995Q1" if outc == "gdp" else C.FIRST_OOS, outc != "gdp")
        rows.append(dict(outcome=outc, h=h, **r))
O = pd.DataFrame(rows); O.to_csv(RES / "10_oos_encompassing.csv", index=False)
for _, r in O.iterrows():
    for c in O.columns[2:]: S.add(f"nfci_oos_{r.outcome}_h{r.h}_{c}", r[c])

F = design_rec(["mkt_flw", "nfci", "anfci"]); spec = {"M": ["mkt_flw"], "N": ["nfci"], "A": ["anfci"], "MN": ["mkt_flw", "nfci"], "MA": ["mkt_flw", "anfci"]}
P = {k: [] for k in list(spec) + ["base"]}; y = []
for t in F.index:
    if t < pd.Period(C.FIRST_OOS, "M"): continue
    tr = F.loc[:t - 12]; y.append(F.loc[t, "y"])
    for k, c in spec.items():
        try:
            m = sm.Logit(tr.y, sm.add_constant(tr[c])).fit(disp=0, maxiter=200); P[k].append(float(m.predict(np.r_[1, F.loc[t, c].values.astype(float)][None, :])[0]))
        except Exception: P[k].append(tr.y.mean())
    P["base"].append(tr.y.mean())
y = np.array(y); P = {k: np.array(v) for k, v in P.items()}; B = {k: (v - y) ** 2 for k, v in P.items()}
rr = {"n_oos": len(y), "months_recession_in_next12": int(y.sum())}
for k in spec: rr[f"brier_{k}_vs_base"] = B[k].mean() / B["base"].mean()
fc = 0.5 * (P["M"] + P["N"]); rr["brier_combo_MN_vs_base"] = ((fc - y) ** 2).mean() / B["base"].mean()
for s in ("M", "N"): rr[f"dm_combo_MN_vs_{s}"] = tstat(B[s] - (fc - y) ** 2, 18)
rr["dm_MN_joint_vs_N"] = tstat(B["N"] - B["MN"], 18); rr["dm_MN_joint_vs_M"] = tstat(B["M"] - B["MN"], 18)
pd.DataFrame([rr]).to_csv(RES / "10_oos_recession.csv", index=False)
for k, v in rr.items(): S.add(f"nfci_oosrec_{k}", v)

# (d) what the NFCI is
Dm = D0.copy(); Dm["spread"] = Dm.baa - Dm.y10
V = pd.concat([X[["mkt", "mkt_flw", "nfci", "anfci"]], Dm[["y10", "cape", "usd_real", "spread"]]], axis=1).loc["1976-03":"2026-09"].dropna()
Cc = V.copy()
for c in ("mkt", "nfci", "anfci", "y10", "cape", "usd_real", "spread"): Cc[c] = V[c] - V[c].shift(12)
Cc = Cc.dropna(); rows = []
for basis, data in (("level", V), ("change12", Cc)):
    for y_ in ("nfci", "anfci", "mkt" if basis == "level" else "mkt_flw"):
        for nm, cols in (("3 vars", ["y10", "cape", "usd_real"]), ("3 vars + spread", ["y10", "cape", "usd_real", "spread"]), ("spread only", ["spread"])):
            m = sm.OLS(data[y_], sm.add_constant(data[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
            rows.append(dict(basis=basis, y=y_, regressors=nm, n=len(data), R2=m.rsquared, **{f"b_{c}": m.params[c] for c in cols}, **{f"t_{c}": m.tvalues[c] for c in cols}))
Rr = pd.DataFrame(rows); Rr.to_csv(RES / "10_nfci_on_variables.csv", index=False)
for _, r in Rr.iterrows():
    k = f"nfci_decomp_{r.basis}_{r.y}_{r.regressors.replace(' + ', '_plus_').replace(' ', '_')}"
    S.add(k + "_R2", r.R2)
    if pd.notna(r.get("t_spread")): S.add(k + "_t_spread", r.t_spread)
V2 = V[["mkt", "nfci", "anfci", "y10", "cape", "usd_real"]].copy(); V2["spread"] = V.spread; C2 = Cc[["mkt", "nfci", "anfci", "spread", "y10", "cape", "usd_real"]]
V2 = V2[["mkt", "nfci", "anfci", "spread", "y10", "cape", "usd_real"]]
cor = pd.DataFrame({"level": V2.corr()["nfci"], "change12": C2.corr()["nfci"], "corr_with_anfci_level": V2.corr()["anfci"]})
cor.to_csv(RES / "10_correlations.csv")
S.add("nfci_corr_mkt_level_nfci", V2.corr().loc["mkt", "nfci"]); S.add("nfci_corr_mktflow_nfci_level", V.mkt_flw.corr(V.nfci))
S.add("nfci_corr_mktflow_nfci_flow", Cc.mkt_flw.corr(Cc.nfci)); S.add("nfci_corr_mktflow_spread_flow", Cc.mkt_flw.corr(Cc.spread))
S.save()
