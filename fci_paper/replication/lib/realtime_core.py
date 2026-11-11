"""Helpers for step 17 (pseudo real time): stance regressions on vintage inputs.
Reads the package (results/data_monthly.csv, indexes_<step>.csv, market_weights.csv; data/PAYEMS.csv, PCEPILFE.csv, NROU.csv) and data/realtime/ (vintage_panel.csv,
nrou_vintages.csv, lw_realtime.csv). No network access. Nothing is written here; the step writes the results."""
import numpy as np, pandas as pd, statsmodels.api as sm
from . import data as RD, cases as RC, indexes as RI
from .config import DATA, RES

RT = DATA / "realtime"
H, START, FIRST_OOS, LAST = 12, "1976-03", "1995-01", "2026-09"
M = RD.load()


# ---------------------------------------------------------------- design (same as the stance analysis of the package's follow-up)
def covid(p): return p.year == 2020 or (p.year == 2021 and p.month <= 3)
def keep_mask(idx): return np.array([not any(covid(t + k) for k in range(-12, 13)) for t in idx])

def ffg(step, rstar=None):
    r = M["rstar LW"] if rstar is None else rstar
    return {"nominal": M.ffr, "real": M.ffr - M.einf_1y, "rstar": M.ffr - M.einf_1y - r}[step]

def index(step, key="market"): return RD.read(f"indexes_{step}.csv")[key]

def outcomes_revised():
    u = M.u_gap; pay = np.log(RD.fred("PAYEMS")) * 100; px = np.log(RD.fred("PCEPILFE")) * 100
    y = pd.DataFrame({"du": u.shift(-H) - u, "pay": pay.shift(-H) - pay, "pi": px.shift(-H) - px})
    ctl = {"du": pd.DataFrame({"u": u, "du12": u - u.shift(12)}),
           "pay": pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))}),
           "pi": pd.DataFrame({"p12": px - px.shift(12), "p3": 4 * (px - px.shift(3))})}
    return y, ctl

def design(Y, CTL, yname, f, x, form):
    """origins x [y, own lags, ff, idx]; regressors standardised on the sample returned; f, x are level series."""
    ff = f.diff(12) if form == "flow" else f
    ix = x.diff(12) if form in ("flow", "mixed") else x
    D = pd.concat([Y[yname].rename("y"), CTL[yname], ff.rename("ff"), ix.rename("idx")], axis=1).loc[START:LAST]
    return D[keep_mask(D.index)].dropna()

def stand(D, cols=("ff", "idx")):
    D = D.copy()
    for c in cols: D[c] = (D[c] - D[c].mean()) / D[c].std()
    return D

def own(CTL, yname): return list(CTL[yname].columns)
def hac_ols(D, cols, lags): return sm.OLS(D.y, sm.add_constant(D[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
def mean_t(d, lags=12):
    return float(sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lags}).tvalues[0])

def oos(D, ow):
    """Recursive forecasts (from 1995-01, training sample ends H months before the origin) for M0 own lags, M1 +ff, M2 +idx, M3 +ff +idx."""
    sets = {"M0": ow, "M1": ow + ["ff"], "M2": ow + ["idx"], "M3": ow + ["ff", "idx"]}; rows = {}
    for t in pd.period_range(FIRST_OOS, "2025-09", freq="M"):
        if t not in D.index: continue
        tr = D.loc[:t - H]
        if len(tr) < 100: continue
        r = {"y": D.loc[t, "y"]}
        for k, c in sets.items():
            b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[c].values], tr.y.values, rcond=None)[0]
            r[k] = float(b @ np.r_[1, D.loc[t, c].values.astype(float)])
        rows[t] = r
    return pd.DataFrame(rows).T

def hacstats(D, ow, lags, with_oos=True):
    r0 = hac_ols(D, ow, lags); r1 = hac_ols(D, ow + ["ff"], lags); r2 = hac_ols(D, ow + ["idx"], lags); r3 = hac_ols(D, ow + ["ff", "idx"], lags)
    s = dict(n=len(D), first=str(D.index[0]), last=str(D.index[-1]), gain_idx_alone=r2.rsquared_adj - r0.rsquared_adj, gain_ff_alone=r1.rsquared_adj - r0.rsquared_adj,
             gain_idx_given_ff=r3.rsquared_adj - r1.rsquared_adj, t_idx_alone=r2.tvalues["idx"], t_idx_both=r3.tvalues["idx"], b_idx_both=r3.params["idx"],
             t_ff_both=r3.tvalues["ff"], b_ff_both=r3.params["ff"])
    if with_oos:
        F = oos(D, ow)
        if len(F) >= 60:
            e = {m: F.y - F[m] for m in ("M0", "M1", "M3")}
            d = e["M1"] ** 2 - e["M3"] ** 2; cw = d + (F["M1"] - F["M3"]) ** 2
            s.update(n_oos=len(F), rmse_idx_given_ff=float(np.sqrt((e["M3"] ** 2).mean() / (e["M1"] ** 2).mean())), cw_idx_given_ff=mean_t(cw.values), dm_idx_given_ff=mean_t(d.values))
    return s


# ---------------------------------------------------------------- vintage inputs
def nrou_panel():
    """CBO natural rate as known at each origin t (vintage t+2, else t+3; 12-month outcome from vintage t+14, else t+15); vintages exist from March 2011."""
    N = pd.read_csv(RT / "nrou_vintages.csv", parse_dates=["vintage_date", "observation_date"])
    V = {v: g.set_index("observation_date").NROU.dropna() for v, g in N.groupby("vintage_date")}
    def mid_q(q):
        q = q.copy(); q.index = q.index.to_period("Q")
        m = pd.Series(q.values, index=[p.asfreq("M", "s") + 1 for p in q.index]); full = pd.period_range(m.index[0], m.index[-1], freq="M")
        return m.reindex(full).interpolate(limit_area="inside")
    def get(t, offs, fn):
        for o in offs:
            v = (t + o).to_timestamp()
            if v not in V: continue
            r = fn(mid_q(V[v]))
            if all(pd.notna(x) for x in r.values()): return r
        return {}
    rows = []
    for t in pd.period_range("1976-03", "2025-09", freq="M"):
        r = {"t": str(t)}
        r.update(get(t, (2, 3), lambda m: {"n_k": m.get(t), "n12_k": m.get(t - 12)}))
        r.update(get(t, (14, 15), lambda m: {"n_t_f": m.get(t), "n_h_f": m.get(t + 12)}))
        rows.append(r)
    return pd.DataFrame(rows).set_index("t")

def panel():
    P = pd.read_csv(RT / "vintage_panel.csv", index_col=0).join(nrou_panel()); P.index = pd.PeriodIndex(P.index, freq="M"); return P

def nrou_expost(t):
    n = pd.read_csv(DATA / "NROU.csv"); n = pd.Series(n.iloc[:, 1].values, index=pd.PeriodIndex(pd.to_datetime(n.iloc[:, 0]), freq="Q"))
    return pd.Series(RD.mid_quarter(n).reindex(t).values, index=t)

def versions(P):
    """name -> (Y, CTL) for outcomes du, pay, pi. rev = revised data; rt1 = vintage u, payrolls, core PCE with ex-post NROU; rt2 = rt1 plus vintage CBO NROU (origins from 2011)."""
    t = P.index; out = {"rev": outcomes_revised()}
    def build(gap_k, gap12_k, gap_t_f, gap_h_f):
        Y = pd.DataFrame({"du": gap_h_f - gap_t_f, "pay": P.p_h_f - P.p_t_f, "pi": P.c_h_f - P.c_t_f}, index=t)
        ctl = {"du": pd.DataFrame({"u": gap_k, "du12": gap_k - gap12_k}),
               "pay": pd.DataFrame({"g12": P.p_k - P.p12_k, "g3": 4 * (P.p_k - P.p3_k)}),
               "pi": pd.DataFrame({"p12": P.c_k - P.c12_k, "p3": 4 * (P.c_k - P.c3_k)})}
        return Y, ctl
    nt, nt12, nh = nrou_expost(t), nrou_expost(t - 12), nrou_expost(t + 12)
    out["rt1"] = build(P.u_k - nt.values, P.u12_k - nt12.values, P.u_t_f - nt.values, P.u_h_f - nh.values)
    out["rt2"] = build(P.u_k - P.n_k, P.u12_k - P.n12_k, P.u_t_f - P.n_t_f, P.u_h_f - P.n_h_f)
    return out

def rstar_rt():
    """Monthly real-time Laubach-Williams r*: final-point estimate of the latest vintage released by the end of the month (step function from 2005-07);
    no vintage was published between Aug 2020 and May 2023, so Sep 2020 to Apr 2023 are missing."""
    R = pd.read_csv(RT / "lw_realtime.csv", parse_dates=["release"]).sort_values("release")
    s = pd.Series(np.nan, index=pd.period_range("2005-01", "2026-09", freq="M"))
    for m in s.index:
        a = R[R.release <= m.to_timestamp(how="end")]
        if len(a): s[m] = a.rstar_rt.iloc[-1]
    s.loc["2020-09":"2023-04"] = np.nan
    return s

def rt_index_rstar():
    """Market index at the r* step with real-time r* (weights unchanged); also the largest gap to the package's series when the full-sample r* is used (should be 0)."""
    D = RD.load(); w = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
    chk = RI.market(RC.inputs(D, "rstar", rstar="rstar LW"), w)[0].loc["1973-01":"2026-09"]
    gap = float((chk - index("rstar")).abs().max())
    D = D.copy(); D["rstar RT"] = rstar_rt()
    return RI.market(RC.inputs(D, "rstar", rstar="rstar RT"), w)[0].where(D["rstar RT"].notna()), gap
