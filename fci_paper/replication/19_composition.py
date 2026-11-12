"""Step 19. Does the composition of a financial movement matter for the outlook? (author's new direction, followup4/ASSESSMENT.md, empirical work item 3.)

DEFINITIONS (re-derived here; no dependence on step 18)
 x = (10-year yield, equity valuation, real broad dollar) at the r* step (lib/cases.py: yield less expected inflation less r*; equities = earnings-yield gap converted to CAPE log points).
 psi = event-window responses to a 1-unit policy surprise (results/market_weights.csv, column response); w_M = market weights (w_M'psi = 1);
 b = FRB/US weights, four quarters, funds-rate-equivalent units (results/frbus_weights.csv); w_B = b / (b'psi), so w_B'psi = 1 (b'psi is the 0.97 of the paper's Table 3).
 dM = w_M' dx, dB = w_B' dx, D = (w_B - w_M)'dx = dB - dM, dx the 12-month change of x, the SAME months as the market-index change (dM equals the step-03 market index 12-month change).
 Both dM and D are in 2-year-yield-equivalent points; D = 0 for any combination psi*s that a conventional surprise generates.

PRE-SPECIFIED PRIMARY TEST (exactly one, fixed before any estimate was looked at)
 y = unemployment gap(t+12) - unemployment gap(t); regressors: own lags (u, 12-month change of u, as in step 08), dM, D; main sample (origins 1976-03..2026-09, windows touching 2020-01..2021-03 dropped);
 H0: coefficient on D = 0, two-sided, HAC (Newey-West, 18 lags) t-test at the 10 percent level. Reported with the 90% HAC interval, a moving-block bootstrap (24 months, rows jointly, REPS draws) interval,
 and an interval over the weight-estimate draws (results/weights_boot.csv: w_M, psi redrawn, b fixed; dM and D recomputed). "Also with the funds-rate gap" = adding the 12-month change of the r*-step funds-rate gap (step 08 flow form).
 Model-facing check (not a second primary): four-quarter-ahead real GDP growth, quarterly alignment (origin = last month of a quarter), same regressors, HAC 6 quarterly lags, 8-quarter blocks.
EVERYTHING ELSE IS DESCRIPTIVE (no multiple-testing adjustment; counts below, in the CHECK file and in scalars):
 specifications per block: own, market flow, market+D, FRB/US-weight flow, equities alone, dollar alone, 10-year alone, three free (each without and with the funds-rate gap);
 blocks: 2 outcomes x 3 samples (main; origins from 1996-01; excluding 2008-01..2015-12 windows). Proportionality tests (free coefficients proportional to w_M, to w_B): HAC Wald chi2(2) and bootstrap p, per block.
 Recursive out-of-sample (step 08 machinery: expanding window, training ends 12 months before the origin, to 2025-09): Clark-West for adding D to the market flow, the free three to the market flow, each alone to own lags.
 SPF: forecast error (realized unemployment rate four quarters ahead, quarterly average, minus the SPF median, UNEMP6) on dM and D at the SPF information date (last complete month before the deadline month); GDP too.
 Episodes: 1998-01..2001-12, 2004-06..2006-06, 2022-03..2024-12 (and 2005-01..2006-12 for the contrast); mean readings, implied outlook contribution, model errors.
Writes results/19_*.csv and scalars_19_composition.csv."""
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
from lib import data, cases
from lib.config import RES, REPS
from lib.report import Scalars
from lib import comp_core as C, comp_spf as SP
from lib.stance_core import own, mean_t, oos, n_recessions, LAST_ORIGIN, ffg, M, Y, CTL, keep

S = Scalars("19_composition")
X, X12, dM, D, dB, chk, W = C.changes()
S.add("comp_check_dM_vs_step03", chk); S.add("comp_bpsi", W["bpsi"])
for v, a, b_, c_ in zip(C.VARS, W["wM"], W["wB"], W["b"]):
    S.add(f"comp_wM_{v}", a); S.add(f"comp_wB_{v}", b_); S.add(f"comp_b_{v}", c_)
regs = {"dM": dM, "D": D, "dB": dB, "dy10": X12.y10, "deq": X12.equities, "dusd": X12.dollar}
FF = ffg("rstar").diff(12)
SPECS = {"own": [], "mkt": ["dM"], "comp": ["dM", "D"], "frbus": ["dB"], "eq": ["deq"], "usd": ["dusd"], "y10": ["dy10"], "free": ["dy10", "deq", "dusd"]}
FREE = SPECS["free"]
TAGN = 0


def block_frame(yn, sname):
    s = C.SAMPLES[sname]
    return C.gdp_frame(regs, FF, s["start"], s["excl"]) if yn == "gdp" else C.frame(yn, regs, FF, s["start"], s["excl"])


def own_cols(yn): return ["g4", "g1"] if yn == "gdp" else own("du")


def lags_of(yn): return 6 if yn == "gdp" else 18


rows_spec, rows_coef, rows_prop, rows_prim, rows_dist = [], [], [], [], []
BOOT = {}
for yn in ("du", "gdp"):
    for sname in C.SAMPLES:
        Dd = block_frame(yn, sname); TAGN += 1
        idx = C.block_idx(len(Dd), REPS, TAGN, C.BLOCK // 3 if yn == "gdp" else C.BLOCK)
        ow = own_cols(yn)
        # distribution of dM, D and D orthogonal to dM in this sample
        Z = sm.add_constant(Dd[["dM"]]); Dres = sm.OLS(Dd.D, Z).fit().resid
        dD90_res = C.pct(Dres, 95) - C.pct(Dres, 5); dD90_unc = C.pct(Dd.D, 95) - C.pct(Dd.D, 5)
        rows_dist.append(dict(outcome=yn, sample=sname, n=len(Dd), sd_y=Dd.y.std(), sd_dM=Dd.dM.std(), sd_D=Dd.D.std(), sd_Dperp=Dres.std(), p5_Dperp=C.pct(Dres, 5), p95_Dperp=C.pct(Dres, 95),
                              p5_D=C.pct(Dd.D, 5), p95_D=C.pct(Dd.D, 95), corr_dM_D=Dd[["dM", "D"]].corr().iloc[0, 1], mean_dM=Dd.dM.mean(), mean_D=Dd.D.mean()))
        for ff in (False, True):
            base = ow + (["ff"] if ff else []); fl = "ff" if ff else "noff"
            r0 = C.hac(Dd, base, lags_of(yn))
            for sp, extra in SPECS.items():
                cols = base + extra
                r = C.hac(Dd, cols, lags_of(yn)); bc = C.boot_coefs(Dd, cols, idx); BOOT[(yn, sname, fl, sp)] = bc
                wj = np.nan
                if extra:
                    Rm = np.zeros((len(extra), len(r.params)));
                    for i, e in enumerate(extra): Rm[i, list(r.params.index).index(e)] = 1
                    wj = float(r.wald_test(Rm, use_f=False, scalar=True).pvalue)
                rows_spec.append(dict(outcome=yn, sample=sname, ff=fl, spec=sp, n=len(Dd), adj_r2=r.rsquared_adj, gain_adj_r2=r.rsquared_adj - r0.rsquared_adj, p_joint=wj))
                ci = r.conf_int(alpha=0.10)
                for e in extra:
                    j = list(r.params.index).index(e)
                    rows_coef.append(dict(outcome=yn, sample=sname, ff=fl, spec=sp, term=e, coef=r.params[e], se=r.bse[e], t=r.tvalues[e], p=r.pvalues[e], lo90=ci.loc[e, 0], hi90=ci.loc[e, 1],
                                          boot_lo90=C.pct(bc[:, j], 5), boot_hi90=C.pct(bc[:, j], 95), boot_sd=float(bc[:, j].std())))
                if sp == "free":
                    ii = [list(r.params.index).index(e) for e in FREE]; th = r.params.values[ii]; V = r.cov_params().values[np.ix_(ii, ii)]; bb = bc[:, ii]
                    for wn, w in (("w_M", W["wM"]), ("w_B", W["wB"])):
                        Wd, ph, pb = C.prop_test(th, V, w, bb)
                        lam = float(th @ w / (w @ w))
                        rows_prop.append(dict(outcome=yn, sample=sname, ff=fl, null=wn, wald=Wd, p_hac=ph, p_boot=pb, scale_lambda=lam, n=len(Dd)))
                    # free coefficients normalised so that theta'psi = 1 (comparable with w_M, w_B), bootstrap bands
                    tp = th / (th @ W["psi"]); tpb = bb / (bb @ W["psi"])[:, None]
                    for k, v in enumerate(FREE):
                        rows_coef.append(dict(outcome=yn, sample=sname, ff=fl, spec="free_norm_psi", term=v, coef=tp[k], boot_lo90=C.pct(tpb[:, k], 5), boot_hi90=C.pct(tpb[:, k], 95),
                                              boot_sd=float(tpb[:, k].std()), se=np.nan, t=np.nan, p=np.nan, lo90=np.nan, hi90=np.nan))
                if sp == "comp":
                    a, c = r.params["dM"], r.params["D"]; jc = list(r.params.index).index("D"); ja = list(r.params.index).index("dM")
                    rows_prim.append(dict(outcome=yn, sample=sname, ff=fl, n=len(Dd), a_dM=a, se_a=r.bse["dM"], c_D=c, se_c=r.bse["D"], t_c=r.tvalues["D"], p_c=r.pvalues["D"],
                                          lo90_c=ci.loc["D", 0], hi90_c=ci.loc["D", 1], boot_lo90_c=C.pct(bc[:, jc], 5), boot_hi90_c=C.pct(bc[:, jc], 95), p_boot_c=float(2 * min((bc[:, jc] > 0).mean(), (bc[:, jc] < 0).mean())),
                                          t_c_minus_a=float((c - a) / np.sqrt(r.cov_params().loc["D", "D"] + r.cov_params().loc["dM", "dM"] - 2 * r.cov_params().loc["D", "dM"])),
                                          gain_given_mkt=r.rsquared_adj - C.hac(Dd, base + ["dM"], lags_of(yn)).rsquared_adj,
                                          dD_p5_p95_resid=dD90_res, effect_p5_p95=c * dD90_res, effect_lo90=ci.loc["D", 0] * dD90_res, effect_hi90=ci.loc["D", 1] * dD90_res,
                                          effect_boot_lo90=C.pct(bc[:, jc], 5) * dD90_res, effect_boot_hi90=C.pct(bc[:, jc], 95) * dD90_res,
                                          dD_p5_p95_uncond=dD90_unc, effect_p5_p95_uncond=c * dD90_unc, effect_per_sd_Dperp=c * Dres.std(), sd_Dperp=Dres.std()))
        print(yn, sname, len(Dd), flush=True)
SPEC, COEF, PROP, PRIM, DIST = (pd.DataFrame(r) for r in (rows_spec, rows_coef, rows_prop, rows_prim, rows_dist))

# ---- weights-draw interval for the primary test (main sample, unemployment, without and with the funds-rate gap)
WB = pd.read_csv(RES / "weights_boot.csv")
Wd_ = WB[["w_ten", "w_eq", "w_usd"]].values[:REPS]; Psid = WB[["psi_ten", "psi_eq", "psi_usd"]].values[:REPS]
Dd = block_frame("du", "main"); ix = Dd.index; Xs = X12.reindex(ix); wd = {}
for ff in (False, True):
    cs, as_ = [], []
    for wm, ps in zip(Wd_, Psid):
        wb = W["b"] / (W["b"] @ ps); dm_ = Xs.values @ wm; d_ = Xs.values @ (wb - wm)
        cols = [np.ones(len(ix)), Dd[own("du")].values, dm_[:, None], d_[:, None]] + ([Dd[["ff"]].values] if ff else [])
        Xm = np.column_stack([np.ones(len(ix))] + [Dd[own("du")].values] + [dm_, d_] + ([Dd.ff.values] if ff else []))
        b = np.linalg.lstsq(Xm, Dd.y.values, rcond=None)[0]; k = 1 + len(own("du")); as_.append(b[k]); cs.append(b[k + 1])
    wd[ff] = (C.pct(cs, 5), C.pct(cs, 95), C.pct(as_, 5), C.pct(as_, 95), float(np.mean(np.array(cs) > 0)))
for ff in (False, True):
    m = (PRIM.outcome == "du") & (PRIM["sample"] == "main") & (PRIM.ff == ("ff" if ff else "noff"))
    for k, v in zip(("wdraw_lo90_c", "wdraw_hi90_c", "wdraw_lo90_a", "wdraw_hi90_a", "wdraw_share_c_pos"), wd[ff]): PRIM.loc[m, k] = v

# ---- scalars: primary and checks
for _, r in PRIM.iterrows():
    sfx = f"{r.outcome}_{r['sample'].replace('+', 'p').replace('-', '_')}_{r.ff}"
    for k in ("n", "a_dM", "c_D", "se_c", "t_c", "p_c", "lo90_c", "hi90_c", "boot_lo90_c", "boot_hi90_c", "p_boot_c", "t_c_minus_a", "gain_given_mkt", "effect_p5_p95", "effect_lo90", "effect_hi90",
              "effect_boot_lo90", "effect_boot_hi90", "dD_p5_p95_resid", "effect_per_sd_Dperp", "effect_p5_p95_uncond", "dD_p5_p95_uncond"):
        S.add(f"comp_{k}_{sfx}", r[k])
    for k in ("wdraw_lo90_c", "wdraw_hi90_c", "wdraw_lo90_a", "wdraw_hi90_a", "wdraw_share_c_pos"):
        if k in r and pd.notna(r[k]): S.add(f"comp_{k}_{sfx}", r[k])
for _, r in SPEC.iterrows():
    sfx = f"{r.outcome}_{r['sample'].replace('+', 'p').replace('-', '_')}_{r.ff}_{r.spec}"
    S.add(f"comp_gain_{sfx}", r.gain_adj_r2)
for _, r in COEF[COEF.spec.isin(["eq", "usd", "y10", "mkt", "frbus"])].iterrows():
    S.add(f"comp_t_{r.outcome}_{r['sample'].replace('+', 'p').replace('-', '_')}_{r.ff}_{r.spec}", r.t)
for _, r in PROP.iterrows():
    sfx = f"{r.outcome}_{r['sample'].replace('+', 'p').replace('-', '_')}_{r.ff}_{r.null}"
    S.add(f"comp_prop_p_hac_{sfx}", r.p_hac); S.add(f"comp_prop_p_boot_{sfx}", r.p_boot)

# ---- recursive out-of-sample
oo = []
for yn in ("du", "gdp"):
    for sname, s in C.SAMPLES.items():
        Dd = block_frame(yn, sname); ow = own_cols(yn); q = yn == "gdp"; nmin = s["nmin"] // 3 + 1 if q else s["nmin"]; L = 4 if q else 12
        for ff in (False, True):
            base = ow + (["ff"] if ff else [])
            sets = {k: base + v for k, v in SPECS.items() if k in ("own", "mkt", "comp", "free", "eq", "frbus")}
            F = oos(Dd, {("base" if k == "own" else k): v for k, v in sets.items()}, s["first_oos"], nmin, LAST_ORIGIN)
            F = F.astype(float)
            for small, large, lab in (("mkt", "comp", "add_D_to_market"), ("mkt", "free", "free_three_vs_market"), ("base", "mkt", "market_vs_own"), ("base", "eq", "equities_vs_own"),
                                      ("base", "frbus", "frbus_weights_vs_own"), ("base", "comp", "market_and_D_vs_own"), ("mkt", "eq", "equities_vs_market_nonnested"), ("mkt", "frbus", "frbus_weights_vs_market_nonnested")):
                st = C.cw_stats(F, small, large, L)
                oo.append(dict(outcome=yn, sample=sname, ff="ff" if ff else "noff", comparison=lab, n_oos=len(F), first=str(F.index[0]), last=str(F.index[-1]), n_recessions=n_recessions(F.index), **st))
OOS = pd.DataFrame(oo)
for _, r in OOS[OOS.comparison.isin(["add_D_to_market", "free_three_vs_market", "equities_vs_own", "market_vs_own"])].iterrows():
    sfx = f"{r.outcome}_{r['sample'].replace('+', 'p').replace('-', '_')}_{r.ff}_{r.comparison}"
    S.add(f"comp_oos_cw_{sfx}", r.cw_t); S.add(f"comp_oos_rmse_{sfx}", r.rmse_ratio); S.add(f"comp_oos_n_{sfx}", r.n_oos)
S.add("comp_oos_n_recessions_du_main", int(OOS[(OOS.outcome == "du") & (OOS["sample"] == "main")].n_recessions.iloc[0]))

# ---- episodes (main sample, unemployment, no funds-rate gap)
Dd = block_frame("du", "main"); ow = own("du")
fits = {k: C.hac(Dd, ow + v, 18) for k, v in SPECS.items() if k in ("own", "mkt", "comp", "frbus", "eq", "free")}
Fo = oos(Dd, {"own": ow, "mkt": ow + ["dM"], "frbus": ow + ["dB"], "comp": ow + ["dM", "D"], "eq": ow + ["deq"]}, "1995-01", 100, LAST_ORIGIN).astype(float)
rc = fits["comp"]; a, c = rc.params["dM"], rc.params["D"]; Vac = rc.cov_params().loc[["dM", "D"], ["dM", "D"]].values
bc = BOOT[("du", "main", "noff", "comp")]; jc = list(rc.params.index).index("D"); ja = list(rc.params.index).index("dM")
XL = cases.demean(cases.inputs(data.load(), "rstar")[C.VARS]).loc["1973-01":"2026-09"]
Mlev, Dlev = XL @ W["wM"], XL @ (W["wB"] - W["wM"])
EPS = {"1998-2001": ("1998-01", "2001-12", "e9801"), "2004-06": ("2004-06", "2006-06", "e0406"), "2022-24": ("2022-03", "2024-12", "e2224"), "2005-06": ("2005-01", "2006-12", "e0506")}
mdM, mD = Dd.dM.mean(), Dd.D.mean(); er, ef = [], []
sl = lambda s, a_, b_: s[(s.index >= pd.Period(a_, "M")) & (s.index <= pd.Period(b_, "M"))]
EPR = {}
for en, (a_, b_, tag) in EPS.items():
    dm_, d_ = sl(dM, a_, b_), sl(D, a_, b_); o = sl(Dd.y, a_, b_)
    EPR[en] = dict(dM=float(dm_.mean()), D=float(d_.mean()), dB=float(sl(dB, a_, b_).mean()), lev_M=float(sl(Mlev, a_, b_).mean()), lev_D=float(sl(Dlev, a_, b_).mean()))
    Dm, Mm = EPR[en]["D"] - mD, EPR[en]["dM"] - mdM; v = np.array([Mm, Dm]); se_t = float(np.sqrt(v @ Vac @ v))
    er.append(dict(episode=en, start=a_, end=b_, n_months=len(dm_), n_origins=len(o), mean_dM=EPR[en]["dM"], mean_D=EPR[en]["D"], mean_dB=EPR[en]["dB"], level_market=EPR[en]["lev_M"], level_D=EPR[en]["lev_D"],
                   sd_dM_sample=Dd.dM.std(), sd_D_sample=Dd.D.std(), contrib_dM=a * Mm, contrib_D=c * Dm, contrib_D_lo90=min(rc.conf_int(0.10).loc["D"] * Dm), contrib_D_hi90=max(rc.conf_int(0.10).loc["D"] * Dm),
                   contrib_D_boot_lo90=C.pct(bc[:, jc] * Dm, 5), contrib_D_boot_hi90=C.pct(bc[:, jc] * Dm, 95), contrib_total=a * Mm + c * Dm, contrib_total_lo90=a * Mm + c * Dm - 1.645 * se_t, contrib_total_hi90=a * Mm + c * Dm + 1.645 * se_t))
    if len(o):
        row = dict(episode=en, n_origins=len(o), mean_y=float(o.mean()))
        for k, r in fits.items():
            fit = r.fittedvalues.reindex(o.index); row[f"insample_fit_{k}"] = float(fit.mean()); row[f"insample_err_{k}"] = float((o - fit).mean())
        oi = o.index.intersection(Fo.index)
        row["n_oos"] = len(oi)
        if len(oi):
            for k in Fo.columns[1:]:
                row[f"oos_fc_{k}"] = float(Fo.loc[oi, k].mean()); row[f"oos_err_{k}"] = float((Fo.loc[oi, "y"] - Fo.loc[oi, k]).mean())
            dd = (Fo.loc[oi, "y"] - Fo.loc[oi, "mkt"]).abs() - (Fo.loc[oi, "y"] - Fo.loc[oi, "frbus"]).abs()
            row["oos_mean_abs_err_mkt_minus_frbus"] = float(dd.mean()); row["oos_mean_fc_mkt_minus_frbus"] = float((Fo.loc[oi, "mkt"] - Fo.loc[oi, "frbus"]).mean())
        ef.append(row)
# contrast: 1998-2001 vs 2005-06
dDc = EPR["1998-2001"]["D"] - EPR["2005-06"]["D"]; dMc = EPR["1998-2001"]["dM"] - EPR["2005-06"]["dM"]; v = np.array([dMc, dDc])
contr = dict(episode="1998-2001 minus 2005-06", mean_dM=dMc, mean_D=dDc, contrib_D=c * dDc, contrib_D_lo90=min(rc.conf_int(0.10).loc["D"] * dDc), contrib_D_hi90=max(rc.conf_int(0.10).loc["D"] * dDc),
             contrib_D_boot_lo90=C.pct(bc[:, jc] * dDc, 5), contrib_D_boot_hi90=C.pct(bc[:, jc] * dDc, 95), contrib_dM=a * dMc, contrib_total=a * dMc + c * dDc,
             contrib_total_lo90=a * dMc + c * dDc - 1.645 * np.sqrt(v @ Vac @ v), contrib_total_hi90=a * dMc + c * dDc + 1.645 * np.sqrt(v @ Vac @ v))
ER = pd.concat([pd.DataFrame(er), pd.DataFrame([contr])], ignore_index=True); EF = pd.DataFrame(ef)
for _, r in ER.iterrows():
    tag = {"1998-2001": "e9801", "2004-06": "e0406", "2022-24": "e2224", "2005-06": "e0506", "1998-2001 minus 2005-06": "e9801_vs_e0506"}[r.episode]
    for k in ER.columns:
        if k not in ("episode", "start", "end") and pd.notna(r[k]): S.add(f"comp_ep_{tag}_{k}", r[k])
for _, r in EF.iterrows():
    tag = {"1998-2001": "e9801", "2004-06": "e0406", "2022-24": "e2224", "2005-06": "e0506"}[r.episode]
    for k in EF.columns:
        if k != "episode" and pd.notna(r[k]): S.add(f"comp_epfit_{tag}_{k}", r[k])

# ---- SPF: forecast-error regressions
P = SP.panel(); P = P[P.survey != "1990Q2"].copy()          # 1990Q2 was not taken in real time (shares the 1990Q3 deadline)
P["m"] = pd.PeriodIndex(P.info_month, freq="M")
P["dM"] = dM.reindex(P.m).values; P["D"] = D.reindex(P.m).values; P["dB"] = dB.reindex(P.m).values
cv = lambda p: p.year == 2020 or (p.year == 2021 and p.month <= 3)
P["covid"] = [any(cv(m - 12 + k) for k in range(0, 27)) for m in P.m]         # 12-month change base through the target quarter
P["ex0815"] = [any(pd.Period("2008-01", "M") <= m - 12 + k <= pd.Period("2015-12", "M") for k in range(0, 27)) for m in P.m]
P["ex2001"] = [any(pd.Period("2001-01", "M") <= m - 12 + k <= pd.Period("2001-12", "M") for k in range(0, 27)) for m in P.m]
P["ex0809"] = [any(pd.Period("2008-01", "M") <= m - 12 + k <= pd.Period("2009-12", "M") for k in range(0, 27)) for m in P.m]
P["used"] = ~P.covid & P.u_err.notna() & P.dM.notna()
P.drop(columns=["m"]).to_csv(RES / "19_spf_panel.csv", index=False)
Pu = P[P.used].reset_index(drop=True); spr = []; Dres_all = sm.OLS(Pu.D, sm.add_constant(Pu.dM)).fit().resid; dD90_spf = C.pct(Dres_all, 95) - C.pct(Dres_all, 5)
for tname, ecol, extra_ctl in (("unemployment", "u_err", "u_fc_change"), ("gdp", "gdp_err", None)):
    Q = Pu[Pu[ecol].notna()].reset_index(drop=True)
    for lab, cols in (("both", ["dM", "D"]), ("market_only", ["dM"]), ("D_only", ["D"]), ("both_plus_spf_change", ["dM", "D", extra_ctl] if extra_ctl else None), ("both_ex2008-15", ["dM", "D"])):
        if cols is None: continue
        Q_ = Q[~Q.ex0815].reset_index(drop=True) if lab == "both_ex2008-15" else Q
        TAGN += 1; idx = C.block_idx(len(Q_), REPS, TAGN, 8)
        Z = sm.add_constant(Q_[cols]); r = sm.OLS(Q_[ecol], Z).fit(cov_type="HAC", cov_kwds={"maxlags": 4}); ci = r.conf_int(alpha=0.10)
        Xb = Z.values; yb = Q_[ecol].values; bcs = np.array([np.linalg.lstsq(Xb[i], yb[i], rcond=None)[0] for i in idx])
        for j, e in enumerate(cols):
            spr.append(dict(target=tname, spec=lab, term=e, n=len(Q_), first=Q_.survey.iloc[0], last=Q_.survey.iloc[-1], coef=r.params[e], se=r.bse[e], t=r.tvalues[e], p=r.pvalues[e], lo90=ci.loc[e, 0], hi90=ci.loc[e, 1],
                            boot_lo90=C.pct(bcs[:, j + 1], 5), boot_hi90=C.pct(bcs[:, j + 1], 95), adj_r2=r.rsquared_adj, mean_err=float(Q_[ecol].mean()), sd_err=float(Q_[ecol].std()),
                            effect_p5_p95=(r.params[e] * dD90_spf if e == "D" else np.nan)))
SPR = pd.DataFrame(spr)
for _, r in SPR.iterrows():
    if r.spec in ("both", "market_only", "D_only", "both_ex2008-15"):
        for k in ("coef", "se", "t", "p", "lo90", "hi90", "boot_lo90", "boot_hi90", "n", "adj_r2", "effect_p5_p95"):
            if pd.notna(r[k]): S.add(f"comp_spf_{r.target}_{r.spec.replace('-', '_')}_{r.term}_{k}", r[k])
S.add("comp_spf_first", Pu.survey.iloc[0]); S.add("comp_spf_last_unemp", Pu[Pu.u_err.notna()].survey.iloc[-1]); S.add("comp_spf_dD_p5_p95", dD90_spf)
S.add("comp_spf_mean_err_unemp", float(Pu.u_err.mean())); S.add("comp_spf_sd_err_unemp", float(Pu.u_err.std()))

# ---- EXTENSION 1: the two restrictions tested directly in the primary regression (added after review; every output above is unchanged, new outputs only)
# y = ... + beta*dM + gamma*D, D = dB - dM computed once on the same 12-month changes, so dB = dM + D.
#  Market reading right: the outlook depends on dM only, so gamma = 0.
#  FRB/US reading right: the outlook depends on dB = dM + D, so y = k*(dM + D) and beta = gamma, i.e. gamma - beta = 0.
# Intervals: HAC (18 lags; 6 quarterly for GDP) with the joint covariance of (beta, gamma); moving-block bootstrap with the SAME draws as Table comp (BOOT).
# Two restrictions in each of 12 blocks (2 outcomes x 3 samples x without/with the funds-rate gap): descriptive, unadjusted; the single pre-specified primary test is unchanged.
S2 = Scalars("19_composition_ext")
rr = []
RLAB = {"beta": "coefficient on dM (market-index change)", "gamma": "market reading sufficient: gamma = 0", "gamma_minus_beta": "FRB/US reading sufficient: gamma = beta (y depends on dM + D)"}
for yn in ("du", "gdp"):
    for sname in C.SAMPLES:
        Dd = block_frame(yn, sname)
        for ff in (False, True):
            base = own_cols(yn) + (["ff"] if ff else []); fl = "ff" if ff else "noff"
            r = C.hac(Dd, base + ["dM", "D"], lags_of(yn)); V = r.cov_params(); bc = BOOT[(yn, sname, fl, "comp")]
            jb, jg = list(r.params.index).index("dM"), list(r.params.index).index("D")
            bb, gg = bc[:, jb], bc[:, jg]
            corr = float(V.loc["dM", "D"] / np.sqrt(V.loc["dM", "dM"] * V.loc["D", "D"]))
            for term, est, se, bd in (("beta", r.params["dM"], r.bse["dM"], bb), ("gamma", r.params["D"], r.bse["D"], gg),
                                      ("gamma_minus_beta", r.params["D"] - r.params["dM"], float(np.sqrt(V.loc["D", "D"] + V.loc["dM", "dM"] - 2 * V.loc["D", "dM"])), gg - bb)):
                t = est / se; p = float(2 * (1 - stats.norm.cdf(abs(t)))); lo, hi = est - 1.645 * se, est + 1.645 * se
                blo, bhi = C.pct(bd, 5), C.pct(bd, 95)
                rr.append(dict(outcome=yn, sample=sname, ff=fl, n=len(Dd), term=term, tests=RLAB[term], coef=est, se=se, t=t, p=p, lo90=lo, hi90=hi, boot_lo90=blo, boot_hi90=bhi, boot_sd=float(bd.std()),
                               p_boot=float(2 * min((bd > 0).mean(), (bd < 0).mean())), reject_hac90=int(lo > 0 or hi < 0), reject_boot90=int(blo > 0 or bhi < 0), corr_beta_gamma_hac=corr))
RST = pd.DataFrame(rr)
RST.to_csv(RES / "19_restrictions.csv", index=False)
for _, r in RST.iterrows():
    sfx = f"{r.term}_{r.outcome}_{r['sample'].replace('+', 'p').replace('-', '_')}_{r.ff}"
    for k in ("coef", "se", "t", "p", "lo90", "hi90", "boot_lo90", "boot_hi90", "p_boot", "reject_hac90", "reject_boot90"): S2.add(f"comp_restr_{k}_{sfx}", r[k])
S2.add("comp_restr_n_tests", len(RST[RST.term != "beta"]))
for term in ("gamma", "gamma_minus_beta"):
    m = RST[RST.term == term]
    S2.add(f"comp_restr_n_reject_hac90_{term}", int(m.reject_hac90.sum())); S2.add(f"comp_restr_n_reject_boot90_{term}", int(m.reject_boot90.sum())); S2.add(f"comp_restr_n_blocks_{term}", len(m))

# ---- EXTENSION 2: SPF decomposition. Same surveys and information dates as the SPF test above (Pu: COVID windows dropped, dM available, outcome available).
# (a) forecast component = SPF median four quarters ahead minus the last observed value (unemployment: UNEMP1, the previous-quarter value known at the deadline; GDP: the forecast growth 100 ln(RGDP6/RGDP2)),
# (b) realized = realized minus the same base, (c) error = realized minus forecast (the existing u_err / gdp_err). (b) = (a) + (c) is an identity, so the OLS coefficients add; checked below.
# Regressors dM, D (as above); OLS, HAC 4 lags, 8-survey blocks with ONE set of draws per sample shared by (a), (b), (c), so bootstrap draws add too.
Pu["u_real_chg"] = Pu.u_real - Pu.u_last; Pu["u_fc_chg"] = Pu.u_fc - Pu.u_last
COMP = {"unemployment": (("forecast", "u_fc_chg"), ("realized", "u_real_chg"), ("error", "u_err")), "gdp": (("forecast", "gdp_fc"), ("realized", "gdp_real"), ("error", "gdp_err"))}
sd_, idn = [], {}
for tname, comps in COMP.items():
    Q0 = Pu[Pu[comps[2][1]].notna() & Pu[comps[0][1]].notna() & Pu[comps[1][1]].notna()].reset_index(drop=True)
    for si, (sname, Q_) in enumerate((("all", Q0), ("ex2008-15", Q0[~Q0.ex0815].reset_index(drop=True)), ("ex2001", Q0[~Q0.ex2001].reset_index(drop=True)), ("ex2008-09", Q0[~Q0.ex0809].reset_index(drop=True)), ("ex2001-and-2008-09", Q0[~Q0.ex2001 & ~Q0.ex0809].reset_index(drop=True)))):
        idx = C.block_idx(len(Q_), REPS, 100 + 10 * (tname == "gdp") + si, 8)
        Dr = sm.OLS(Q_.D, sm.add_constant(Q_.dM)).fit().resid; rng_D = C.pct(Dr, 95) - C.pct(Dr, 5); rng_M = C.pct(Q_.dM, 95) - C.pct(Q_.dM, 5)
        Z = sm.add_constant(Q_[["dM", "D"]]); Xb = Z.values; res = {}
        for cn, col in comps: 
            r = sm.OLS(Q_[col], Z).fit(cov_type="HAC", cov_kwds={"maxlags": 4}); res[cn] = (r, np.array([np.linalg.lstsq(Xb[i], Q_[col].values[i], rcond=None)[0] for i in idx]), Q_[col])
        idn[(tname, sname)] = (max(float(np.abs(res["realized"][0].params - res["forecast"][0].params - res["error"][0].params).max()), 0.0),
                               float(np.abs(res["realized"][1] - res["forecast"][1] - res["error"][1]).max()), len(Q_))
        for cn, (r, bcs, yv) in res.items():
            ci = r.conf_int(alpha=0.10)
            for j, term in ((1, "dM"), (2, "D")):
                e = r.params.iloc[j]; rg = rng_M if term == "dM" else rng_D
                sd_.append(dict(target=tname, sample=sname, component=cn, term=term, n=len(Q_), first=Q_.survey.iloc[0], last=Q_.survey.iloc[-1], coef=e, se=r.bse.iloc[j], t=r.tvalues.iloc[j], p=r.pvalues.iloc[j],
                                lo90=ci.iloc[j, 0], hi90=ci.iloc[j, 1], boot_lo90=C.pct(bcs[:, j], 5), boot_hi90=C.pct(bcs[:, j], 95), mean_y=float(yv.mean()), sd_y=float(yv.std()), adj_r2=r.rsquared_adj,
                                range_p5_p95=rg, range_is="dM unconditional" if term == "dM" else "D orthogonal to dM", effect_p5_p95=e * rg, effect_lo90=ci.iloc[j, 0] * rg, effect_hi90=ci.iloc[j, 1] * rg,
                                effect_boot_lo90=C.pct(bcs[:, j], 5) * rg, effect_boot_hi90=C.pct(bcs[:, j], 95) * rg, identity_max_abs_diff_coef=idn[(tname, sname)][0], identity_max_abs_diff_boot=idn[(tname, sname)][1]))
SD = pd.DataFrame(sd_); SD.to_csv(RES / "19_spf_decomp.csv", index=False)
for _, r in SD.iterrows():
    sfx = f"{r.target}_{r['sample'].replace('-', '_')}_{r.component}_{r.term}"
    for k in ("coef", "se", "t", "p", "lo90", "hi90", "boot_lo90", "boot_hi90", "n", "effect_p5_p95", "effect_lo90", "effect_hi90", "effect_boot_lo90", "effect_boot_hi90", "range_p5_p95"): S2.add(f"comp_spfd_{k}_{sfx}", r[k])
for (tname, sname), (d1, d2, n_) in idn.items():
    S2.add(f"comp_spfd_identity_max_diff_coef_{tname}_{sname.replace('-', '_')}", d1); S2.add(f"comp_spfd_identity_max_diff_boot_{tname}_{sname.replace('-', '_')}", d2)
S2.save()

# ---- tests counted
S.add("comp_n_primary_tests", 1)
S.add("comp_n_specs_insample", len(SPEC)); S.add("comp_n_coef_tests_insample", int((COEF.spec != "free_norm_psi").sum())); S.add("comp_n_prop_tests", len(PROP)); S.add("comp_n_oos_comparisons", len(OOS)); S.add("comp_n_spf_coefs", len(SPR))
S.add("comp_n_boot_reps", REPS)
for n_, f_ in (("spec", SPEC), ("coef", COEF), ("prop", PROP), ("prim", PRIM), ("oos", OOS), ("episodes", ER), ("episode_fit", EF), ("spf", SPR), ("dist", DIST)):
    f_.to_csv(RES / f"19_{n_}.csv", index=False)
S.save()
pd.set_option("display.width", 250)
print(PRIM[["outcome", "sample", "ff", "n", "a_dM", "c_D", "t_c", "lo90_c", "hi90_c", "boot_lo90_c", "boot_hi90_c", "effect_p5_p95", "effect_lo90", "effect_hi90", "wdraw_lo90_c", "wdraw_hi90_c"]].round(3).to_string())
print(SPEC[(SPEC.ff == "noff")].round(3).to_string()); print(PROP.round(3).to_string()); print(OOS[OOS.comparison.isin(["add_D_to_market", "free_three_vs_market", "equities_vs_own"])].round(3).to_string())
print(ER.round(3).T.to_string()); print(EF.round(3).T.to_string()); print(SPR.round(3).to_string()); print(DIST.round(3).to_string())
print(RST.round(3).to_string()); print(SD.round(3).to_string()); print(idn)
