"""Step 8. Does an index measure stance beyond the funds-rate gap? (ported from followup2/stance; no FOMC-window surprises, only the already-estimated market weights.)

DESIGN (pre-specified before any estimate was looked at)
 question : does the index add to the funds-rate gap (FFG) in explaining the economy 12 months ahead?
 FFG      : nominal step FEDFUNDS; real step less 1-year expected inflation; r* step less r* (Laubach-Williams; Kiley in the episode check); same series as the indexes.
 indexes  : Market, GS, FRB/US at the nominal, real and r* steps (results/indexes_<step>.csv).
 forms    : level (FFG_t, index_t); flow (12-month changes of both); mixed (FFG level, index 12-month change).
 outcomes : h = 12 change of the unemployment gap (du); 12-month payroll growth (pay); 12-month core PCE inflation (pi), each with own lags.
 models   : M0 own lags; M1 + FFG; M2 + index; M3 + FFG + index; regressors standardised on the common sample.
 sample   : origins 1976-03 to 2025-09; origins whose window t-12..t+12 touches 2020-01..2021-03 dropped.
 in sample: HAC 18 lags (12 in sub-periods). Out of sample: recursive from 1995-01, training ends 12 months before the origin; RMSE ratio, Diebold-Mariano, Clark-West (nested), HAC 12.
 periods  : full; pre2009 (1995-2008, out of sample only); zlb 2009-01..2015-12; post 2022-01..2026-09.
 PRIMARY  : Market, r* step, 3 outcomes x 3 forms, full-sample Clark-West M1 -> M3 (index given FFG): 9 one-sided tests, Holm-adjusted (Holm family = these 9).
 DESCRIPTIVE (shared data, no adjustment): every other cell (3 outcomes x 3 steps x 3 indexes x 3 forms x 4 periods), correlations, components, episodes, today's reading.
 episodes : index (r* step) minus FFG, both demeaned over 1973-2026; 2004-06 (2004-06..2006-06), 2022-24 (2022-03..2024-12) and 2022-03..2023-12; 90% interval over the weight bootstrap draws
            (results/weights_boot.csv, first REPS draws) and r* Kiley versus LW; rank among rolling means of the same length (1976-2026).
 components: rates (10-year gap), equities, dollar, equities+dollar, mixed form (supplement added after the main results).
 today    : last month's index (r* step) minus FFG, both demeaned over 1973-2026; weights-bootstrap interval; Kiley r*.
Writes results/08_<table>.csv and scalars_08_stance.csv."""
import numpy as np, pandas as pd
from scipy import stats
from lib import data, cases, indexes as I
from lib.config import RES, REPS, REPS_W
from lib.report import Scalars
from lib.stance_core import *

S = Scalars("08_stance")
INDEXES = {"market": "Market", "gs": "GS", "frbus": "FRB/US"}
FORMS = ["level", "flow", "mixed"]; OUTCOMES = ["du", "pay", "pi"]; FIRST_OOS = "1995-01"
PERIODS = {"full": ("1995-01", "2026-09"), "pre2009": ("1995-01", "2008-12"), "zlb": ("2009-01", "2015-12"), "post": ("2022-01", "2026-09")}
pct = lambda a, q: float(np.percentile(a, q))

# ---- correlations of the funds-rate gap with each index
CP = {"full 1976-2026": ("1976-03", "2026-09"), "pre-2009 1976-2008": ("1976-03", "2008-12"), "2004-06": ("2004-06", "2006-06"), "zlb 2009-15": ("2009-01", "2015-12"), "post 2022-26": ("2022-04", "2026-09")}
rows = []
for s in STEPS:
    f = ffg(s)
    for k in INDEXES:
        x = index(s, k)
        for pn, (a, b) in CP.items():
            r = {"step": s, "index": k, "period": pn}
            for form, (ff, xx) in {"level": (f, x), "flow": (f.diff(12), x.diff(12))}.items():
                z = pd.concat([ff, xx], axis=1).loc[a:b].dropna(); r[f"corr_{form}"] = z.corr().iloc[0, 1]; r["n"] = len(z)
            r["sd_ffg"] = f.loc[a:b].std(); rows.append(r)
C = pd.DataFrame(rows); C.to_csv(RES / "08_corr.csv", index=False)
TAG = {"full 1976-2026": "full", "pre-2009 1976-2008": "pre2009", "2004-06": "p0406", "zlb 2009-15": "zlb", "post 2022-26": "post"}
for pn in CP:
    c = C[(C.step == "rstar") & (C["index"] == "market") & (C.period == pn)].iloc[0]
    S.add(f"corr_mkt_rstar_level_{TAG[pn]}", c.corr_level); S.add(f"corr_mkt_rstar_flow_{TAG[pn]}", c.corr_flow)

# ---- in sample and out of sample, every cell
ins, oo = [], []
for yn in OUTCOMES:
    ow = own(yn)
    for s in STEPS:
        f = ffg(s)
        for k in INDEXES:
            x = index(s, k)
            for form in FORMS:
                D = design(yn, f, x, form)
                F = oos(D, {"M0": ow, "M1": ow + ["ff"], "M2": ow + ["idx"], "M3": ow + ["ff", "idx"]}, FIRST_OOS, 100, LAST_ORIGIN)
                for pn, (a, b) in PERIODS.items():
                    if pn != "pre2009":
                        Sm = D if pn == "full" else D.loc[a:b]; lags = 18 if pn == "full" else 12
                        if len(Sm) >= 30:
                            r0, r1, r2, r3 = (hac_ols(Sm, ow + c, lags) for c in ([], ["ff"], ["idx"], ["ff", "idx"]))
                            ins.append(dict(outcome=yn, step=s, index=k, form=form, period=pn, n=len(Sm), r2a_ff=r1.rsquared_adj - r0.rsquared_adj, r2a_idx=r2.rsquared_adj - r0.rsquared_adj,
                                            r2a_both=r3.rsquared_adj - r0.rsquared_adj, gain_idx_given_ff=r3.rsquared_adj - r1.rsquared_adj, gain_ff_given_idx=r3.rsquared_adj - r2.rsquared_adj,
                                            t_ff_alone=r1.tvalues["ff"], t_idx_alone=r2.tvalues["idx"], t_ff_both=r3.tvalues["ff"], t_idx_both=r3.tvalues["idx"],
                                            b_ff_both=r3.params["ff"], b_idx_both=r3.params["idx"]))
                    G = F[(F.index >= pd.Period(a, "M")) & (F.index <= pd.Period(b, "M"))]
                    if len(G) < 20: continue
                    e = {m: G.y - G[m] for m in ("M0", "M1", "M2", "M3")}
                    row = dict(outcome=yn, step=s, index=k, form=form, period=pn, n_oos=len(G))
                    for small, large, nm in (("M0", "M1", "ff_vs_own"), ("M0", "M2", "idx_vs_own"), ("M1", "M3", "idx_given_ff"), ("M2", "M3", "ff_given_idx")):
                        d = e[small] ** 2 - e[large] ** 2; cw = d + (G[small] - G[large]) ** 2
                        row[f"rmse_{nm}"] = float(np.sqrt((e[large] ** 2).mean() / (e[small] ** 2).mean()))
                        row[f"dm_{nm}"] = mean_t(d.values); row[f"cw_{nm}"] = mean_t(cw.values)
                    oo.append(row)
INS = pd.DataFrame(ins); OOS = pd.DataFrame(oo)
INS.to_csv(RES / "08_insample.csv", index=False); OOS.to_csv(RES / "08_oos.csv", index=False)

# ---- primary family and Holm
Pm = OOS[(OOS["index"] == "market") & (OOS.step == "rstar") & (OOS.period == "full")].copy().reset_index(drop=True)
Pm["p"] = 1 - stats.norm.cdf(Pm.cw_idx_given_ff); Pm["p_holm"] = holm(Pm.p)
Pi = INS[(INS["index"] == "market") & (INS.step == "rstar") & (INS.period == "full")]
Pm = Pm.merge(Pi[["outcome", "form", "gain_idx_given_ff", "gain_ff_given_idx", "t_idx_both", "t_ff_both", "r2a_ff", "r2a_idx", "t_ff_alone", "t_idx_alone"]], on=["outcome", "form"])
Pm = Pm[["outcome", "form", "n_oos", "gain_idx_given_ff", "gain_ff_given_idx", "t_idx_both", "t_ff_both", "r2a_ff", "r2a_idx", "t_ff_alone", "t_idx_alone",
         "rmse_idx_given_ff", "dm_idx_given_ff", "cw_idx_given_ff", "p", "p_holm"]]
Pm.to_csv(RES / "08_primary.csv", index=False)
S.add("stance_n_primary", len(Pm)); S.add("stance_n_primary_p10", int((Pm.p < 0.10).sum())); S.add("stance_n_primary_holm10", int((Pm.p_holm < 0.10).sum()))
for _, r in Pm.iterrows():
    n = f"stance_{r.outcome}_{r.form}"
    for c, v in (("gain", r.gain_idx_given_ff), ("gain_ff", r.gain_ff_given_idx), ("t", r.t_idx_both), ("t_ff", r.t_ff_both), ("cw", r.cw_idx_given_ff), ("rmse", r.rmse_idx_given_ff), ("p", r.p), ("pholm", r.p_holm),
                 ("r2_ff", r.r2a_ff), ("r2_idx", r.r2a_idx), ("t_ffalone", r.t_ff_alone), ("t_idxalone", r.t_idx_alone)):
        S.add(f"{n}_{c}", v)
S.add("stance_n_oos", int(Pm.n_oos.iloc[0]))
# other indexes and steps, unemployment, flow and mixed, full sample
for k in ("market", "gs", "frbus"):
    for s in STEPS:
        for form in ("flow", "mixed"):
            i = INS[(INS["index"] == k) & (INS.step == s) & (INS.period == "full") & (INS.outcome == "du") & (INS.form == form)].iloc[0]
            o = OOS[(OOS["index"] == k) & (OOS.step == s) & (OOS.period == "full") & (OOS.outcome == "du") & (OOS.form == form)].iloc[0]
            if not (k == "market" and s == "rstar"):
                S.add(f"stance_du_{form}_{k}_{s}_gain", i.gain_idx_given_ff); S.add(f"stance_du_{form}_{k}_{s}_t", i.t_idx_both)
                S.add(f"stance_du_{form}_{k}_{s}_cw", o.cw_idx_given_ff); S.add(f"stance_du_{form}_{k}_{s}_rmse", o.rmse_idx_given_ff)
# periods, Market r*, unemployment
for pn in ("zlb", "post", "pre2009"):
    for form in ("level", "flow", "mixed"):
        for yn in OUTCOMES:
            o = OOS[(OOS["index"] == "market") & (OOS.step == "rstar") & (OOS.period == pn) & (OOS.outcome == yn) & (OOS.form == form)]
            if len(o):
                o = o.iloc[0]; S.add(f"stance_{pn}_{yn}_{form}_cw", o.cw_idx_given_ff); S.add(f"stance_{pn}_{yn}_{form}_rmse", o.rmse_idx_given_ff); S.add(f"stance_{pn}_{yn}_{form}_n_oos", int(o.n_oos))
                S.add(f"stance_{pn}_{yn}_{form}_cw_ff", o.cw_ff_vs_own); S.add(f"stance_{pn}_{yn}_{form}_rmse_ff", o.rmse_ff_vs_own)
            i = INS[(INS["index"] == "market") & (INS.step == "rstar") & (INS.period == pn) & (INS.outcome == yn) & (INS.form == form)]
            if len(i):
                i = i.iloc[0]; S.add(f"stance_{pn}_{yn}_{form}_gain", i.gain_idx_given_ff); S.add(f"stance_{pn}_{yn}_{form}_t", i.t_idx_both); S.add(f"stance_{pn}_{yn}_{form}_n", int(i.n))

# ---- episodes: index minus funds-rate gap, intervals over the weight draws and Kiley r*
D0 = data.load(); W = pd.read_csv(RES / "weights_boot.csv")[["w_ten", "w_eq", "w_usd"]].values[:REPS_W]
w0 = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
EP = {"conundrum 2004-06..2006-06": ("2004-06", "2006-06", "e0406"), "tightening 2022-03..2024-12": ("2022-03", "2024-12", "e2224"), "2022-03..2023-12": ("2022-03", "2023-12", "e2223")}
rows = []
for rs, lab, sfx in (("rstar LW", "LW", ""), ("rstar Kiley", "Kiley", "_kiley")):
    X = cases.demean(cases.inputs(D0, "rstar", rstar=rs)[I.MARKET_VARS]).loc["1973-01":"2026-09"]
    f = ffg("rstar", rs).loc["1973-01":"2026-09"]; f = f - f.mean(); sf = f.std()
    base = X @ w0; draws = X.values @ W.T; sx = draws.std(0)
    for en, (a, b, tag) in EP.items():
        sl = (X.index >= pd.Period(a, "M")) & (X.index <= pd.Period(b, "M")); fm = float(f[sl].mean()); im = draws[sl].mean(0)
        r = dict(rstar=lab, episode=en, series="market", n_months=int(sl.sum()), ffg=fm, index_point=float(base[sl].mean()), index_lo=pct(im, 5), index_hi=pct(im, 95),
                 diff_point=float(base[sl].mean() - fm), diff_lo=pct(im - fm, 5), diff_hi=pct(im - fm, 95),
                 zdiff_point=float(base[sl].mean() / base.std() - fm / sf), zdiff_lo=pct(im / sx - fm / sf, 5), zdiff_hi=pct(im / sx - fm / sf, 95), share_draws_diff_neg=float(((im - fm) < 0).mean()))
        rows.append(r)
        S.add(f"ep_{tag}_diff{sfx}", r["diff_point"]); S.add(f"ep_{tag}_lo{sfx}", r["diff_lo"]); S.add(f"ep_{tag}_hi{sfx}", r["diff_hi"]); S.add(f"ep_{tag}_ffg{sfx}", fm)
        S.add(f"ep_{tag}_index{sfx}", r["index_point"]); S.add(f"ep_{tag}_share_neg{sfx}", r["share_draws_diff_neg"]); S.add(f"ep_{tag}_zdiff{sfx}", r["zdiff_point"]); S.add(f"ep_{tag}_n{sfx}", r["n_months"])
    for k in ("gs", "frbus"):
        ix = index("rstar" if lab == "LW" else "rstar_kiley", k).loc["1973-01":"2026-09"]
        for en, (a, b, tag) in EP.items():
            sl = (ix.index >= pd.Period(a, "M")) & (ix.index <= pd.Period(b, "M"))
            d = float(ix[sl].mean() - f[sl].mean())
            rows.append(dict(rstar=lab, episode=en, series=k, n_months=int(sl.sum()), ffg=float(f[sl].mean()), index_point=float(ix[sl].mean()), diff_point=d))
            S.add(f"ep_{tag}_diff_{k}{sfx}", d)
E = pd.DataFrame(rows); E.to_csv(RES / "08_episodes.csv", index=False)

# monthly series for the figure: market index minus FFG (LW), weights-bootstrap band
X = cases.demean(cases.inputs(D0, "rstar")[I.MARKET_VARS]).loc["1990-01":"2026-09"]; f = ffg("rstar").loc["1973-01":"2026-09"]; f = (f - f.mean()).loc["1990-01":]
dr = X.values @ W.T
pd.DataFrame({"market": X @ w0, "ffg": f, "diff": X @ w0 - f, "diff_lo": np.percentile(dr - f.values[:, None], 5, axis=1), "diff_hi": np.percentile(dr - f.values[:, None], 95, axis=1)}).to_csv(RES / "08_diff_series.csv")

# rank of the episodes among rolling means of the same length
x = index("rstar", "market").loc["1976-01":"2026-09"]; f = ffg("rstar").loc[x.index]
d = (x - x.mean()) - (f - f.mean()); sd_all = d.std(); rows = []
for en, (a, b), tag in (("conundrum", ("2004-06", "2006-06"), "e0406"), ("tightening", ("2022-03", "2024-12"), "e2224")):
    n = len(d.loc[a:b]); rm = d.rolling(n).mean().dropna(); v = d.loc[a:b].mean()
    rows.append(dict(episode=en, n=n, mean_diff=v, sd_monthly_diff=sd_all, pct_rank=float((rm < v).mean()), min_rolling=rm.min(), median_rolling=rm.median(), p05=rm.quantile(.05), p95=rm.quantile(.95)))
    S.add(f"ep_{tag}_pct_rank", rows[-1]["pct_rank"]); S.add(f"ep_{tag}_sd_monthly", sd_all)
pd.DataFrame(rows).to_csv(RES / "08_episode_rank.csv", index=False)

# ---- bootstrap of the in-sample increment over weight draws (Market, r*, full sample)
Xf = cases.demean(cases.inputs(D0, "rstar")[I.MARKET_VARS]); f = ffg("rstar"); res = []
for b in W:
    x = (Xf @ b).loc["1973-01":"2026-09"]
    for yn in OUTCOMES:
        for form in FORMS:
            Sm = design(yn, f, x, form); ow = own(yn)
            r1 = hac_ols(Sm, ow + ["ff"], 18); r3 = hac_ols(Sm, ow + ["ff", "idx"], 18)
            res.append(dict(outcome=yn, form=form, t_idx_both=r3.tvalues["idx"], gain=r3.rsquared_adj - r1.rsquared_adj))
R = pd.DataFrame(res).groupby(["outcome", "form"]).agg(t_med=("t_idx_both", "median"), t_lo=("t_idx_both", lambda a: pct(a, 5)), t_hi=("t_idx_both", lambda a: pct(a, 95)),
                                                    gain_med=("gain", "median"), gain_lo=("gain", lambda a: pct(a, 5)), gain_hi=("gain", lambda a: pct(a, 95))).reset_index()
R.to_csv(RES / "08_boot_insample.csv", index=False)
for _, r in R.iterrows():
    for c in ("t_med", "t_lo", "t_hi", "gain_med", "gain_lo", "gain_hi"): S.add(f"stance_boot_{r.outcome}_{r.form}_{c}", r[c])

# ---- components of the market index (supplement), mixed form
G = pcols(RES / "groups_rstar.csv"); f = ffg("rstar"); rows = []
for c in ("rates", "equities", "dollar", "equities+dollar"):
    x = G[["market|equities", "market|dollar"]].sum(axis=1) if c == "equities+dollar" else G[f"market|{c}"]
    for yn in OUTCOMES:
        Dd = design(yn, f, x, "mixed"); ow = own(yn); F = oos(Dd, {"M1": ow + ["ff"], "M3": ow + ["ff", "idx"]}, FIRST_OOS, 100, LAST_ORIGIN)
        r1 = hac_ols(Dd, ow + ["ff"], 18); r3 = hac_ols(Dd, ow + ["ff", "idx"], 18); e1, e3 = F.y - F.M1, F.y - F.M3
        rows.append(dict(component=c, outcome=yn, n=len(Dd), gain=r3.rsquared_adj - r1.rsquared_adj, t=r3.tvalues["idx"], rmse=float(np.sqrt((e3 ** 2).mean() / (e1 ** 2).mean())),
                         cw=mean_t((e1 ** 2 - e3 ** 2 + (F.M1 - F.M3) ** 2).values)))
        for m_, v in (("gain", rows[-1]["gain"]), ("t", rows[-1]["t"]), ("rmse", rows[-1]["rmse"]), ("cw", rows[-1]["cw"])):
            S.add(f"comp_{c.replace('+', '_')}_{yn}_{m_}", v)
pd.DataFrame(rows).to_csv(RES / "08_components.csv", index=False)

# ---- today's reading relative to the funds-rate gap (r* step; zero = 1973-2026 mean; index in 2-year-yield equivalents, gap in funds-rate points)
rows = []; last = M.index[-1]
for rs, lab, step in (("rstar LW", "LW", "rstar"), ("rstar Kiley", "Kiley", "rstar_kiley")):
    X = cases.demean(cases.inputs(D0, "rstar", rstar=rs)[I.MARKET_VARS]).loc["1973-01":"2026-09"]
    fg = ffg("rstar", rs).loc["1973-01":"2026-09"]; fm_all = fg.mean(); fl = float(fg.iloc[-1] - fm_all)
    base = X @ w0; draws = X.values[-1] @ W.T
    rows.append(dict(rstar=lab, month=str(last), series="market", index=float(base.iloc[-1]), index_lo=pct(draws, 5), index_hi=pct(draws, 95), ffg=fl,
                     diff=float(base.iloc[-1]) - fl, diff_lo=pct(draws - fl, 5), diff_hi=pct(draws - fl, 95), share_draws_diff_neg=float(((draws - fl) < 0).mean()),
                     zindex=float(base.iloc[-1] / base.std()), zffg=fl / fg.std()))
    for k in ("gs", "frbus"):
        ix = index(step, k).loc["1973-01":"2026-09"]
        rows.append(dict(rstar=lab, month=str(last), series=k, index=float(ix.iloc[-1]), ffg=fl, diff=float(ix.iloc[-1]) - fl, zindex=float(ix.iloc[-1] / ix.std()), zffg=fl / fg.std()))
T = pd.DataFrame(rows); T.to_csv(RES / "08_today.csv", index=False)
for _, r in T.iterrows():
    sfx = "" if r.rstar == "LW" else "_kiley"
    S.add(f"today_{r.series}_diff{sfx}", r["diff"]); S.add(f"today_{r.series}_index{sfx}", r["index"]); S.add(f"today_ffg{sfx}", r["ffg"])
    if r.series == "market": S.add(f"today_market_diff_lo{sfx}", r.diff_lo); S.add(f"today_market_diff_hi{sfx}", r.diff_hi); S.add(f"today_market_share_neg{sfx}", r.share_draws_diff_neg)
S.add("today_month", str(last))
S.save()
print(Pm.round(3).to_string()); print(E.round(2).to_string()); print(T.round(2).to_string())
