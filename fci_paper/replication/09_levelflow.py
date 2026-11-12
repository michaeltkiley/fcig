"""Step 9. Does the level or the 12-month change (flow) of an index carry the information about the economy a year ahead?
Series (14): market, GS, FRB/US, FCI-G (1-year lookback) at nominal, real and r* steps; NFCI and ANFCI as published.
Level x_t; flow x_t - x_{t-12}. Outcomes at 12 months: change in the unemployment gap, payroll growth. Origins 1976-03 to 2025-10, 2020-21 windows dropped.
 (a) mean: HAC(18) t-statistics of level and flow alone and jointly, adjusted-R2 gains over own lags; recursive out-of-sample (from 1995, training ends 12 months
     before the origin) RMSE ratio to own lags with a Diebold-Mariano t. 2 outcomes x 14 series x 5 statistics = 140 statistics, read as a pattern, not one by one.
 (b) granger: one-step unemployment equation, 12 lags of u and of x; the 12 lags of x written as the level (coefficient = sum of the lags) and 11 differences;
     F tests of all 12 lags, the sum, the 11 differences (classical and HAC).
 (c) quantile: in-sample quantile regressions (tau 0.1, 0.5, 0.9) of payroll growth on own lags, level and flow jointly; 90% intervals from a moving-block bootstrap of
     rows (block 24, REPS draws, seed in config). Primary: tau = 0.1 (42 coefficient intervals = 14 series x level/flow x ... read as a pattern). The out-of-sample tail
     is not estimated: the evaluation sample has too few recessions (counted in 09_sample.csv; scalar levelflow_oos_recessions).
 (d) logit: any recession month in t+1..t+12 on level and flow, HAC(18), descriptive.
Writes results/09_mean.csv, 09_granger.csv, 09_quantile.csv, 09_recession_logit.csv, 09_sample.csv, scalars_09_levelflow.csv."""
import os, warnings
from multiprocessing import Pool
import numpy as np, pandas as pd, statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg
from lib.config import RES, REPS, SEED
from lib.report import Scalars
from lib import levelflow_common as C

warnings.filterwarnings("ignore")
H = 12; TAUS = (0.1, 0.5, 0.9); BLOCK = 24
S = Scalars("09_levelflow")


def load_indexes():
    out = {}
    for step in ("nominal", "real", "rstar"):
        I = C.read_res(f"indexes_{step}.csv")
        for k, lab in (("market", "Market"), ("gs", "GS"), ("frbus", "FRB/US"), ("fcig_1yr", "FCI-G")):
            out[f"{lab}|{step}"] = I[k]
        if step == "rstar":
            out["NFCI|given"] = I["nfci"]; out["ANFCI|given"] = I["anfci"]
    return out


def design(x, yname):
    y, ctl = C.outcomes(H)[yname]
    D = pd.concat([y.rename("y"), ctl, x.rename("lvl"), (x - x.shift(12)).rename("flw")], axis=1).loc[C.START:C.LAST]
    D = D[[not any(C.covid(t + k) for k in range(-12, 13)) for t in D.index]].dropna()
    return C.standardise(D, ("lvl", "flw"))


def ols(D, cols):
    return sm.OLS(D.y, sm.add_constant(D[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": 18})


def dm_t(d, lags=12):
    return sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lags}).tvalues[0]


def oos(D, own, specs):
    errs = {k: [] for k in specs}
    for t in pd.period_range(C.FIRST_OOS, "2025-10", freq="M"):
        if t not in D.index: continue
        tr = D.loc[:t - H]
        if len(tr) < 100: continue
        for k, cols in specs.items():
            c = own + cols
            b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[c].values], tr.y.values, rcond=None)[0]
            errs[k].append(D.loc[t, "y"] - b @ np.r_[1, D.loc[t, c].values.astype(float)])
    return {k: np.array(v) for k, v in errs.items()}


IDX = load_indexes()

# (a) mean
rows = []
for yn, own in (("du", ["u", "du12"]), ("pay", ["g12", "g3"])):
    for lab, x in IDX.items():
        D = design(x, yn)
        r0 = ols(D, own); rL = ols(D, own + ["lvl"]); rF = ols(D, own + ["flw"]); rB = ols(D, own + ["lvl", "flw"])
        row = {"outcome": yn, "series": lab, "n": len(D), "first": str(D.index[0]), "last": str(D.index[-1]),
               "b_lvl_alone": rL.params["lvl"], "t_lvl_alone": rL.tvalues["lvl"], "gain_lvl": rL.rsquared_adj - r0.rsquared_adj,
               "b_flw_alone": rF.params["flw"], "t_flw_alone": rF.tvalues["flw"], "gain_flw": rF.rsquared_adj - r0.rsquared_adj,
               "b_lvl_both": rB.params["lvl"], "t_lvl_both": rB.tvalues["lvl"], "b_flw_both": rB.params["flw"], "t_flw_both": rB.tvalues["flw"],
               "gain_both": rB.rsquared_adj - r0.rsquared_adj, "sd_y": D.y.std()}
        e = oos(D, own, {"own": [], "lvl": ["lvl"], "flw": ["flw"], "both": ["lvl", "flw"]})
        for k in ("lvl", "flw", "both"):
            row[f"rmse_{k}"] = float(np.sqrt((e[k] ** 2).mean() / (e["own"] ** 2).mean())); row[f"dm_{k}"] = float(dm_t(e[k] ** 2 - e["own"] ** 2))
        row["n_oos"] = len(e["own"]); rows.append(row)
M = pd.DataFrame(rows); M.to_csv(RES / "09_mean.csv", index=False)
for yn in ("du", "pay"):
    for lab in ("Market|rstar", "GS|rstar", "FRB/US|rstar", "Market|nominal", "Market|real", "FCI-G|rstar", "NFCI|given", "ANFCI|given"):
        r = M[(M.outcome == yn) & (M.series == lab)].iloc[0]; key = lab.replace("|", "_").replace("/", "").replace("-", "").lower()
        for c in ("t_lvl_both", "t_flw_both", "gain_lvl", "gain_flw", "rmse_flw", "rmse_lvl", "dm_flw"):
            S.add(f"levelflow_{yn}_{key}_{c}", r[c])
fm = M[(M.outcome == "du") & M.series.str.split("|").str[0].isin(["Market", "GS", "FRB/US"])]
S.add("levelflow_du_flow_t_min", fm.t_flw_both.abs().min()); S.add("levelflow_du_flow_t_max", fm.t_flw_both.abs().max())
S.add("levelflow_du_level_t_max", fm.t_lvl_both.abs().max())
S.add("levelflow_du_flow_gain_min", fm.gain_flw.min()); S.add("levelflow_du_flow_gain_max", fm.gain_flw.max())
S.add("levelflow_du_level_gain_min", fm.gain_lvl.min()); S.add("levelflow_du_level_gain_max", fm.gain_lvl.max())
S.add("levelflow_du_rmse_flow_min", fm.rmse_flw.min()); S.add("levelflow_du_rmse_flow_max", fm.rmse_flw.max())
S.add("levelflow_du_dm_flow_absmax", fm.dm_flw.abs().max())
pm = M[(M.outcome == "pay") & M.series.str.split("|").str[0].isin(["Market", "GS", "FRB/US"])]
S.add("levelflow_pay_flow_t_min", pm.t_flw_both.abs().min()); S.add("levelflow_pay_flow_t_max", pm.t_flw_both.abs().max())

# (b) Granger: sum of lags versus differences
res = []
u = C.u_gap()
for lab, x in IDX.items():
    cols = {"y": u.shift(-1)}
    for l in range(12): cols[f"u{l}"] = u.shift(l); cols[f"x{l}"] = x.shift(l)
    J = pd.DataFrame(cols).loc["1974-03":"2026-08"]
    J = J[[not (C.covid(t) or C.covid(t + 1) or any(C.covid(t - l) for l in range(12))) for t in J.index]].dropna()
    R = pd.DataFrame({"y": J.y}); R[[f"u{l}" for l in range(12)]] = J[[f"u{l}" for l in range(12)]]
    R["xsum"] = J.x0
    for k in range(11): R[f"dx{k}"] = J[f"x{k}"] - J[f"x{k+1}"]
    X = sm.add_constant(R.drop(columns="y")); m = sm.OLS(R.y, X).fit(); mh = sm.OLS(R.y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    xs = [c for c in X.columns if c.startswith("xsum") or c.startswith("dx")]

    def F(cl):
        A = np.zeros((len(cl), len(X.columns)))
        for i, c in enumerate(cl): A[i, list(X.columns).index(c)] = 1
        f = m.f_test(A); w = mh.wald_test(A, scalar=True, use_f=True)
        return float(f.fvalue), float(f.pvalue), float(w.statistic), float(w.pvalue)
    Fall = F(xs); Fsum = F(["xsum"]); Fdif = F([c for c in xs if c.startswith("dx")])
    X0 = sm.add_constant(J.drop(columns="y")); m0 = sm.OLS(J.y, X0).fit()
    A0 = np.zeros((12, X0.shape[1]))
    for l in range(12): A0[l, list(X0.columns).index(f"x{l}")] = 1
    sd = x.loc["1974-03":"2026-08"].std()
    res.append({"series": lab, "n": len(J), "F_all12": Fall[0], "p_all12": Fall[1], "check_p_orig": float(m0.f_test(A0).pvalue), "p_all12_HAC": Fall[3],
                "F_sum": Fsum[0], "p_sum": Fsum[1], "p_sum_HAC": Fsum[3], "sum_coef_per_sd": float(m.params["xsum"] * sd), "t_sum_HAC": float(mh.tvalues["xsum"]),
                "F_diff11": Fdif[0], "p_diff11": Fdif[1], "p_diff11_HAC": Fdif[3]})
G = pd.DataFrame(res); G.to_csv(RES / "09_granger.csv", index=False)
for _, r in G.iterrows():
    key = r.series.replace("|", "_").replace("/", "").replace("-", "").lower()
    for c in ("p_all12", "p_sum", "p_diff11"): S.add(f"levelflow_granger_{key}_{c}", r[c])
S.add("levelflow_granger_max_check_diff", float((G.p_all12 - G.check_p_orig).abs().max()))

# (c) quantile regressions of payroll growth, in sample
def qfit(y, X, tau): return QuantReg(y, X).fit(q=tau, max_iter=2000).params


def bootstrap(D, cols, tau, rng):
    n = len(D); yv = D.y.values; Xv = np.c_[np.ones(n), D[cols].values]; k = int(np.ceil(n / BLOCK)); out = []
    for _ in range(REPS):
        st = rng.integers(0, n - BLOCK + 1, k); ix = np.concatenate([np.arange(s, s + BLOCK) for s in st])[:n]
        try: out.append(qfit(yv[ix], Xv[ix], tau))
        except Exception: pass
    return np.array(out)


def qjob(lab):
    D = design(IDX[lab], "pay"); c = ["g12", "g3", "lvl", "flw"]; rng = np.random.default_rng(SEED); out = []
    for tau in TAUS:
        p = qfit(D.y.values, np.c_[np.ones(len(D)), D[c].values], tau); bs = bootstrap(D, c, tau, rng)
        row = {"series": lab, "tau": tau, "n": len(D), "first": str(D.index[0]), "last": str(D.index[-1]), "draws": len(bs)}
        for nm in ("lvl", "flw"):
            j = 1 + c.index(nm); row[f"b_{nm}"] = p[j]; row[f"lo_{nm}"] = np.percentile(bs[:, j], 5); row[f"hi_{nm}"] = np.percentile(bs[:, j], 95)
        out.append(row)
    return out


with Pool(min(4, os.cpu_count() or 1)) as pool:       # one job per series with its own seeded generator: identical results to a serial run
    qrows = [r for rr in pool.map(qjob, list(IDX)) for r in rr]
Q = pd.DataFrame(qrows); Q.to_csv(RES / "09_quantile.csv", index=False)
for _, r in Q[Q.tau == 0.1].iterrows():
    key = r.series.replace("|", "_").replace("/", "").replace("-", "").lower()
    for nm in ("lvl", "flw"):
        for c in ("b", "lo", "hi"): S.add(f"levelflow_q10_{key}_{c}_{nm}", r[f"{c}_{nm}"])
q1 = Q[(Q.tau == 0.1) & Q.series.str.split("|").str[0].isin(["Market", "GS", "FRB/US"])]
S.add("levelflow_q10_flow_excl_zero_count", int((q1.hi_flw < 0).sum())); S.add("levelflow_q10_flow_series_count", len(q1))

# (d) sample counts and descriptive recession logit
rec = C.monthly("USREC").reindex(pd.period_range("1970-01", "2026-10", freq="M")).fillna(0)
starts = [str(p) for p in rec.index[rec.diff().fillna(0) == 1]]
D = design(IDX["Market|rstar"], "pay"); fut = C.recession_future(D.index); oo = D.loc[C.FIRST_OOS:]
cnt = [("monthly sample", str(D.index[0]), str(D.index[-1]), len(D)),
       ("origins with a recession month in t+1..t+12", "", "", int(fut.sum())),
       ("recession episodes starting in sample", "", "", len([s for s in starts if "1976-03" <= s <= "2018-12"])),
       ("OOS origins", str(oo.index[0]), str(oo.index[-1]), len(oo)),
       ("OOS origins with a recession in next 12m", "", "", int(fut.loc[oo.index].sum())),
       ("OOS recession episodes", "", "", len([s for s in starts if "1995-01" <= s <= "2018-12"]))]
pd.DataFrame(cnt, columns=["item", "first", "last", "n"]).to_csv(RES / "09_sample.csv", index=False)
for k, v in zip(("sample_n", "recession_origins", "recessions_in_sample", "oos_n", "oos_recession_origins", "oos_recessions"), [c[3] for c in cnt]):
    S.add(f"levelflow_{k}", v)
lg = []
for lab, x in IDX.items():
    D = design(x, "pay"); y = C.recession_future(D.index); r = {}
    for k, cols in (("lvl", ["lvl"]), ("flw", ["flw"]), ("both", ["lvl", "flw"])):
        m = sm.Logit(y, sm.add_constant(D[cols])).fit(disp=0, cov_type="HAC", cov_kwds={"maxlags": 18})
        for c in cols: r[f"z_{c}_{k}"] = m.tvalues[c]
        r[f"pr2_{k}"] = m.prsquared
    lg.append({"series": lab, "n": len(D), "event_months": int(y.sum()), **r})
pd.DataFrame(lg).to_csv(RES / "09_recession_logit.csv", index=False)
S.save()
