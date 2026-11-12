"""(a) correlations of purged and unpurged level and flow; (b) level-versus-flow local projections. Writes out/corr.csv, out/lp.csv.
Counts: LP = 2 outcomes x 2 indexes x 3 steps x 5 (version, sample) = 60 regressions, each with a level and a flow coefficient (120 t-statistics); descriptive, shared data."""
from common import *
import statsmodels.api as sm
P = load_purged()
chk = pd.read_csv(REP / "results" / "indexes_rstar.csv", index_col=0)
print("check unpurged market r* vs package:", np.abs(P[("market", "rstar", "unpurged")].values - chk.market.values).max())

# ---------- (a) correlations on the common sample 1984-01.. (flow needs 12 months after 1983-01)
rows = []
for kind in VARS:
    for s in STEPS:
        U = P[(kind, s, "unpurged")]
        for v in ("full", "recursive"):
            Q = P[(kind, s, v)]
            for lab, sl in (("1984+", slice("1984-01", None)), ("1973+", slice("1974-01", None))):
                if v == "recursive" and lab == "1973+": continue
                u_, q_ = U.loc[sl], Q.loc[sl]
                rows.append({"kind": kind, "step": s, "version": v, "sample": lab, "n": int(q_.dropna().size),
                             "corr_level": u_.corr(q_), "corr_flow": u_.diff(12).corr(q_.diff(12)),
                             "sd_level_ratio": q_.std() / u_.std(), "sd_flow_ratio": q_.diff(12).std() / u_.diff(12).std()})
C = pd.DataFrame(rows); C.to_csv(OUT / "corr.csv", index=False); print(C.round(2).to_string())

# ---------- (b) local projections
def monthly(name):
    d = pd.read_csv(HERE.parents[1] / "followup" / "data" / f"{name}.csv")
    return pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.PeriodIndex(pd.to_datetime(d.iloc[:, 0]), freq="M")).dropna()
covid = lambda p: p.year == 2020 or (p.year == 2021 and p.month <= 3)
u = data.load().u_gap; pay = np.log(monthly("PAYEMS")) * 100
Y = pd.DataFrame({"du": u.shift(-12) - u, "pay": pay.shift(-12) - pay})
CTL = {"du": pd.DataFrame({"u": u, "du12": u - u.shift(12)}), "pay": pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))})}
rec = monthly("USREC")
def design(x, yn, start):
    Dd = pd.concat([Y[yn].rename("y"), CTL[yn], x.rename("lvl"), (x - x.shift(12)).rename("flw")], axis=1).loc[start:"2026-09"]
    Dd = Dd[[not any(covid(t + k) for k in range(-12, 13)) for t in Dd.index]].dropna()
    for c in ("lvl", "flw"): Dd[c] = (Dd[c] - Dd[c].mean()) / Dd[c].std()
    return Dd
def ols(Dd, cols): return sm.OLS(Dd.y, sm.add_constant(Dd[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": 18})
rows = []
for yn, own in (("du", ["u", "du12"]), ("pay", ["g12", "g3"])):
    for kind in VARS:
        for s in STEPS:
            for v, start in (("unpurged", "1976-03"), ("full", "1976-03"), ("unpurged", "1983-03"), ("full", "1983-03"), ("recursive", "1983-03")):
                Dd = design(P[(kind, s, v)], yn, start)
                r0, rB, rF, rL = ols(Dd, own), ols(Dd, own + ["lvl", "flw"]), ols(Dd, own + ["flw"]), ols(Dd, own + ["lvl"])
                nrec = int(((rec.reindex(Dd.index).fillna(0) == 1) & (rec.reindex(Dd.index).fillna(0).diff() == 1)).sum())
                rows.append({"outcome": yn, "kind": kind, "step": s, "version": v, "start": start, "n": len(Dd),
                             "b_flw": rB.params["flw"], "t_flw": rB.tvalues["flw"], "b_lvl": rB.params["lvl"], "t_lvl": rB.tvalues["lvl"],
                             "gain_both": rB.rsquared_adj - sm.OLS(Dd.y, sm.add_constant(Dd[own])).fit().rsquared_adj,
                             "gain_flw_alone": rF.rsquared_adj - sm.OLS(Dd.y, sm.add_constant(Dd[own])).fit().rsquared_adj,
                             "t_flw_alone": rF.tvalues["flw"], "t_lvl_alone": rL.tvalues["lvl"]})
L = pd.DataFrame(rows); L.to_csv(OUT / "lp.csv", index=False)
print(L.round(2).to_string())
