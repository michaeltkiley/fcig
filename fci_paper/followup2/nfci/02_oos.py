"""(b) recursive OOS encompassing from 1995. Mean outcomes (du, pay at 6/12/24; GDP 2/4/8q) and 12m recession (logit, Brier)."""
import numpy as np, pandas as pd, statsmodels.api as sm
from common import *
X, D = M(); rows = []

def tstat(d, lags):
    return sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lags}).tvalues[0]

def run(F, own, h, lags, first, step_name):
    """F: standardised on full sample (standardisation is a monotone rescale of regressors: fit invariant, so no look-ahead)."""
    spec = {"own": own, "M": own + ["mkt_flw"], "N": own + ["nfci"], "A": own + ["anfci"], "MN": own + ["mkt_flw", "nfci"], "MA": own + ["mkt_flw", "anfci"]}
    P = {k: [] for k in spec}; yy = []; idx = []
    for t in F.index:
        if t < pd.Period(first, freq=F.index.freq): continue
        tr = F.loc[:t - h]
        if len(tr) < 100 and step_name == "m" or len(tr) < 40: continue
        idx.append(t); yy.append(F.loc[t, "y"])
        for k, c in spec.items():
            b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[c].values], tr.y.values, rcond=None)[0]
            P[k].append(b @ np.r_[1, F.loc[t, c].values.astype(float)])
    P = {k: np.array(v) for k, v in P.items()}; y = np.array(yy)
    e = {k: y - v for k, v in P.items()}
    out = {"n_oos": len(y)}
    for k in ("M", "N", "A", "MN", "MA"): out[f"rmse_{k}_vs_own"] = np.sqrt((e[k] ** 2).mean() / (e["own"] ** 2).mean())
    out["rmse_M_vs_N"] = np.sqrt((e["M"] ** 2).mean() / (e["N"] ** 2).mean())
    for a, big, small in (("N", "MN", "N"), ("M", "MN", "M"), ("A", "MA", "A"), ("M2", "MA", "M")):
        # Clark-West: big nests small. adj = e_s^2 - (e_b^2 - (f_s - f_b)^2)
        d = e[small] ** 2 - (e[big] ** 2 - (P[small] - P[big]) ** 2)
        out[f"cw_{big}_vs_{small}"] = tstat(d, lags)
    for nm, single, other in (("combo_MN", "N", "M"), ("combo_MA", "A", "M")):
        fc = 0.5 * (P["M"] + P["N" if "MN" in nm else "A"]); ec = y - fc
        for s, lab in (("M", "M"), ("N" if "MN" in nm else "A", "idx")):
            d = e[s] ** 2 - ec ** 2
            out[f"{nm}_mse_gain_vs_{lab}"] = 1 - (ec ** 2).mean() / (e[s] ** 2).mean(); out[f"{nm}_dm_vs_{lab}"] = tstat(d, lags)
        # encompassing (Harvey-Leybourne-Newbold): y - fN = lam (fM - fN)
        fN = P["N" if "MN" in nm else "A"]; m = sm.OLS(y - fN, P["M"] - fN).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
        out[f"{nm}_lam_mkt_weight"] = m.params[0]; out[f"{nm}_lam_t"] = m.tvalues[0]
        # Granger-Ramanathan (no constant, weights unconstrained, in-OOS descriptive only)
        gr = np.linalg.lstsq(np.c_[P["M"], fN], y, rcond=None)[0]; out[f"{nm}_GR_w_mkt"] = gr[0]; out[f"{nm}_GR_w_idx"] = gr[1]
    return out

for outc, hs in (("du", (6, 12, 24)), ("pay", (6, 12, 24)), ("gdp", (2, 4, 8))):
    for h in hs:
        xc = ["mkt_flw", "nfci", "anfci"]
        F, own = design_gdp(h, xc, X, D) if outc == "gdp" else design(h, outc, xc, X, D)
        if outc == "gdp": F = F.copy()
        lags = max(12, h + 6) if outc != "gdp" else max(4, h + 2)
        r = run(F, own, h, lags, "1995-01" if outc != "gdp" else "1995Q1", "m" if outc != "gdp" else "q")
        rows.append(dict(outcome=outc, h=h, **r)); print(outc, h, {k: round(v, 2) for k, v in r.items() if k in ("n_oos", "rmse_M_vs_own", "rmse_N_vs_own", "rmse_MN_vs_own", "cw_MN_vs_N", "cw_MN_vs_M", "combo_MN_dm_vs_idx", "combo_MN_lam_mkt_weight", "combo_MN_lam_t")}, flush=True)
pd.DataFrame(rows).to_csv(OUT / "oos_encompassing.csv", index=False)

# recession: logit OOS Brier (12m); training uses only origins whose 12m outcome window ended by the origin
F = design_rec(["mkt_flw", "nfci", "anfci"], X, D); spec = {"M": ["mkt_flw"], "N": ["nfci"], "A": ["anfci"], "MN": ["mkt_flw", "nfci"], "MA": ["mkt_flw", "anfci"]}
P = {k: [] for k in list(spec) + ["base"]}; y = []
for t in F.index:
    if t < pd.Period(FIRST_OOS, "M"): continue
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
pd.DataFrame([rr]).to_csv(OUT / "oos_recession.csv", index=False); print(rr)
