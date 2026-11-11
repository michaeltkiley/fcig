"""Step 16. Do the market weights drift? Weights re-estimated on expanding and 20-year rolling windows of announcements, the pseudo-real-time index, the VAR response with it,
and the drift of the scale of the policy-news factor (the unit). Ported from followup3/weights_drift/ (01_paths.py, 02_index.py, 03_figure.py).
PRE-SPECIFIED DESIGN (descriptive; no formal tests, so no multiple-testing adjustment; the verdict counts are 3 weights x 2 window types x 2 periods):
 weights : as 02_weights.py (GLS on the policy-news factor, factor recomputed by SVD and 2-year scaling inside each window), updated at every announcement;
           expanding from the 60th announcement (rows with n < 80 are kept in 16_weight_paths.csv but not scored), rolling window of 20 years with first window ending 2016-01.
 bands   : announcement-resampling bootstrap (REPS draws, seed config.SEED, one generator across dates) at year ends 2006..2025 and the last announcement, per window type;
           baseline band = 5-95 percentiles of results/weights_boot.csv.
 verdict : (i) share of dates after 2010 with the point estimate inside the baseline band, per weight; (ii) flow correlations with the baseline above 0.9; (iii) width of own bands vs baseline.
 index   : pseudo-real-time market index (nominal, real, r*-gap steps): month-t weights = latest expanding estimate with announcements through month t (earliest estimate before that),
           inputs demeaned over the full sample (not real time). Forward impetus with the baseline Phi and with Phi re-estimated by the 12-lag VAR on the pseudo-real-time index; 12-month change.
           Also with the first estimate at the 100th announcement (check).
 unit    : scale of the raw factor (2-year pp per unit) and responses per 1 pp of 2-year news over the same windows.
Reads results/market_weights.csv, weights_boot.csv, indexes_*.csv, flow_*_p12.csv, var_paths_*_p12.csv.
Writes results/16_weight_paths.csv, 16_weight_bands.csv, 16_weight_verdict.csv, 16_index_sensitivity.csv, 16_index_series.csv, 16_var_response.csv,
16_weight_path.csv (tidy figure data for 07_report.py) and scalars_16_weights_drift.csv."""
import numpy as np, pandas as pd
from lib import data, cases, var, indexes as I
from lib.drift_est import est, MIN_N
from lib.config import RES, REPS, SEED
from lib.report import Scalars

S = Scalars("16_weights_drift")
RAW = I.events_raw()
B = pd.read_csv(RES / "weights_boot.csv")
base_w = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
WN = ("ten", "eq", "usd")
lo = np.percentile(B[["w_ten", "w_eq", "w_usd"]], 5, axis=0); hi = np.percentile(B[["w_ten", "w_eq", "w_usd"]], 95, axis=0)

# ---- weight paths
rows = []
for i in range(len(RAW)):
    d = RAW.Date.iloc[i]
    if i + 1 >= 60:
        w, psi, load, sd = est(RAW.iloc[:i + 1])
        rows.append(dict(window="expanding", date=d, n=i + 1, w_ten=w[0], w_eq=w[1], w_usd=w[2], psi_ten=psi[0], psi_eq=psi[1], psi_usd=psi[2], load=load, ns_sd=sd))
    if d >= pd.Timestamp("2016-01-01"):
        sub = RAW[(RAW.Date > d - pd.DateOffset(years=20)) & (RAW.Date <= d)]
        w, psi, load, sd = est(sub)
        rows.append(dict(window="rolling20", date=d, n=len(sub), w_ten=w[0], w_eq=w[1], w_usd=w[2], psi_ten=psi[0], psi_eq=psi[1], psi_usd=psi[2], load=load, ns_sd=sd))
P = pd.DataFrame(rows)
P["period"] = np.where(P.date > "2010-12-31", "post2010", "pre2011")
for k, nm in enumerate(WN):
    P[f"{nm}_in"] = (P[f"w_{nm}"] >= lo[k]) & (P[f"w_{nm}"] <= hi[k])
P.to_csv(RES / "16_weight_paths.csv", index=False)

# ---- bootstrap bands at year ends
grid = [pd.Timestamp(f"{y}-12-31") for y in range(2006, 2026)] + [RAW.Date.max()]
rng = np.random.default_rng(SEED); br = []
for g in grid:
    for wt in ("expanding", "rolling20"):
        if wt == "rolling20" and g < pd.Timestamp("2016-01-01"):
            continue
        sub = RAW[RAW.Date <= g] if wt == "expanding" else RAW[(RAW.Date > g - pd.DateOffset(years=20)) & (RAW.Date <= g)]
        sub = sub.reset_index(drop=True)
        if len(sub) < MIN_N:
            continue
        pt = est(sub)
        draws = []
        for _ in range(REPS):
            b = sub.iloc[rng.integers(0, len(sub), len(sub))].reset_index(drop=True)
            w, psi, load, sd = est(b); draws.append(np.r_[w, load])
        draws = np.array(draws)
        r = dict(window=wt, date=g, n=len(sub), reps=REPS)
        for k, nm in enumerate(WN + ("load",)):
            r[f"{nm}_pt"] = pt[0][k] if k < 3 else pt[2]
            r[f"{nm}_lo"], r[f"{nm}_hi"] = np.percentile(draws[:, k], [5, 95])
        br.append(r)
BB = pd.DataFrame(br)
for k, nm in enumerate(WN):
    BB[f"{nm}_in_base"] = (BB[f"{nm}_pt"] >= lo[k]) & (BB[f"{nm}_pt"] <= hi[k])
    BB[f"{nm}_base_in_own"] = (base_w[k] >= BB[f"{nm}_lo"]) & (base_w[k] <= BB[f"{nm}_hi"])
    BB[f"{nm}_width_ratio"] = (BB[f"{nm}_hi"] - BB[f"{nm}_lo"]) / (hi[k] - lo[k])
BB.to_csv(RES / "16_weight_bands.csv", index=False)

# ---- verdict table
V = []
for wt in ("expanding", "rolling20"):
    q = P[(P.window == wt) & (P.n >= MIN_N)]
    for per, g in q.groupby("period"):
        V.append(dict(window=wt, period=per, n_dates=len(g), **{f"{nm}_share_in_base_band": g[f"{nm}_in"].mean() for nm in WN},
                      **{f"{nm}_n_out": int((~g[f"{nm}_in"]).sum()) for nm in WN},
                      **{f"{nm}_min": g[f"w_{nm}"].min() for nm in WN}, **{f"{nm}_max": g[f"w_{nm}"].max() for nm in WN}))
V = pd.DataFrame(V); V.to_csv(RES / "16_weight_verdict.csv", index=False)

S.add("n_announcements", len(RAW)); S.add("min_n", MIN_N)
for k, nm in enumerate(WN):
    S.add(f"base_lo_{nm}", lo[k]); S.add(f"base_hi_{nm}", hi[k]); S.add(f"base_w_{nm}", base_w[k])
for wt, tag in (("expanding", "exp"), ("rolling20", "roll")):
    q = P[(P.window == wt) & (P.n >= MIN_N)]
    qq = q[q.period == "post2010"]
    S.add(f"{tag}_n_dates", len(q)); S.add(f"{tag}_n_dates_post2010", len(qq))
    for nm in WN:
        S.add(f"{tag}_post2010_n_out_{nm}", int((~qq[f"{nm}_in"]).sum()))
        S.add(f"{tag}_post2010_min_{nm}", qq[f"w_{nm}"].min()); S.add(f"{tag}_post2010_max_{nm}", qq[f"w_{nm}"].max())
        out = qq[~qq[f"{nm}_in"]]
        S.add(f"{tag}_first_out_{nm}", out.date.min().strftime("%Y-%m") if len(out) else "none")
        S.add(f"{tag}_last_out_{nm}", out.date.max().strftime("%Y-%m") if len(out) else "none")
    S.add(f"{tag}_last_w_ten", q.sort_values("date").w_ten.iloc[-1])
    S.add(f"{tag}_last_w_eq", q.sort_values("date").w_eq.iloc[-1]); S.add(f"{tag}_last_w_usd", q.sort_values("date").w_usd.iloc[-1])
S.add("exp_pre2011_first_w_ten", P[(P.window == "expanding") & (P.n >= MIN_N)].sort_values("date").w_ten.iloc[0])
e0910 = P[(P.window == "expanding") & (P.date >= "2009-01-01") & (P.date <= "2010-12-31")]
S.add("exp_2009_10_min_w_ten", e0910.w_ten.min()); S.add("exp_2009_10_max_w_ten", e0910.w_ten.max())
for wt, tag in (("expanding", "exp"), ("rolling20", "roll")):
    b = BB[BB.window == wt]
    for nm in WN:
        S.add(f"{tag}_width_ratio_min_{nm}", b[f"{nm}_width_ratio"].min()); S.add(f"{tag}_width_ratio_max_{nm}", b[f"{nm}_width_ratio"].max())
        S.add(f"{tag}_n_base_in_own_{nm}", int(b[f"{nm}_base_in_own"].sum())); S.add(f"{tag}_n_grid_{nm}", len(b))
        S.add(f"{tag}_own_lo_last_{nm}", b[f"{nm}_lo"].iloc[-1]); S.add(f"{tag}_own_hi_last_{nm}", b[f"{nm}_hi"].iloc[-1])
b = BB[(BB.window == "expanding") & (BB.date < "2016-12-31")]
S.add("exp_own_band_includes_zero_ten_until", b[b.ten_lo <= 0].date.max().strftime("%Y") if (b.ten_lo <= 0).any() else "none")
S.add("boot_sd_w_ten", B.w_ten.std()); S.add("boot_sd_w_eq", B.w_eq.std()); S.add("boot_sd_w_usd", B.w_usd.std())
S.add("boot_share_w_ten_outside_0_2", ((B.w_ten < 0) | (B.w_ten > 2)).mean())

# ---- unit: scale of the raw factor and responses
E = P[(P.window == "expanding") & (P.n >= MIN_N)].sort_values("date")
Rl = P[P.window == "rolling20"].sort_values("date")
def at(df, d, col):
    return df[df.date <= d][col].iloc[-1]
for y in (2006, 2009, 2014, 2019):
    S.add(f"load_exp_{y}", at(E, pd.Timestamp(f"{y}-12-31"), "load"))
S.add("load_exp_last", E.load.iloc[-1]); S.add("load_roll_min", Rl.load.min()); S.add("load_roll_max", Rl.load.max())
S.add("load_exp_pct_change_2006_last", 100 * (E.load.iloc[-1] / at(E, pd.Timestamp("2006-12-31"), "load") - 1))
for nm in WN:
    S.add(f"psi_exp_{nm}_2005", E[E.date <= "2005-12-31"][f"psi_{nm}"].iloc[-1] if (E.date <= "2005-12-31").any() else np.nan)
    S.add(f"psi_exp_{nm}_2006", at(E, pd.Timestamp("2006-12-31"), f"psi_{nm}")); S.add(f"psi_exp_{nm}_last", E[f"psi_{nm}"].iloc[-1])
    S.add(f"psi_exp_{nm}_min", E[f"psi_{nm}"].min()); S.add(f"psi_exp_{nm}_max", E[f"psi_{nm}"].max())
bl = BB[(BB.window == "expanding")]
S.add("load_inside_bands_all_dates", int(((bl.load_pt >= bl.load_lo) & (bl.load_pt <= bl.load_hi)).all()))

# ---- pseudo-real-time index
D = data.load(); u = D.u_gap
Wm = pd.DataFrame(E[["w_ten", "w_eq", "w_usd"]].values, index=E.date.dt.to_period("M"), columns=I.MARKET_VARS).groupby(level=0).last()
E100 = P[(P.window == "expanding") & (P.n >= 100)].sort_values("date")
W100 = pd.DataFrame(E100[["w_ten", "w_eq", "w_usd"]].values, index=E100.date.dt.to_period("M"), columns=I.MARKET_VARS).groupby(level=0).last()
def monthly(W, idx):
    return W.reindex(W.index.union(idx)).sort_index().ffill().bfill().loc[idx]
EP = {"2004-06": ("2004-01", "2006-12"), "2009-15": ("2009-01", "2015-12"), "2022-26": ("2022-01", "2026-09")}
T, series, VR = [], {}, []
for case, rs in (("nominal", None), ("real", None), ("rstar", "rstar LW")):
    X = cases.inputs(D, "rstar" if rs else case, rstar=rs or "rstar LW")
    Xd = cases.demean(X[I.MARKET_VARS])
    base = pd.read_csv(RES / f"indexes_{case}.csv", index_col=0).market; base.index = pd.PeriodIndex(base.index, freq="M")
    fl = pd.read_csv(RES / f"flow_{case}_p12.csv", index_col=0); fl.index = pd.PeriodIndex(fl.index, freq="M")
    vp = pd.read_csv(RES / f"var_paths_{case}_p12.csv"); ph = vp.phi.values
    for tag, W in (("exp80", Wm), ("exp100", W100)):
        m = (Xd * monthly(W, Xd.index)).sum(axis=1).loc["1973-01":"2026-09"]
        fi_b = var.forward_impetus(m, ph)
        r, Dd, dum = var.fit(u, m, 12); Phi, _ = var.response(r)
        fi_r = var.forward_impetus(m, Phi) if Phi[12] > 0 else pd.Series(np.nan, index=m.index)
        d12, b12 = m.diff(12), base.diff(12)
        c1 = lambda a, b: pd.concat([a, b], axis=1).loc["1996-01":].dropna().corr().iloc[0, 1]
        c2 = lambda a, b: pd.concat([a, b], axis=1).loc["2006-01":].dropna().corr().iloc[0, 1]
        row = dict(case=case, weights=tag, phi12_rev=Phi[12], phi12_base=ph[12], phi6_rev=Phi[6], phi24_rev=Phi[24], phi6_base=ph[6], phi24_base=ph[24],
                   corr_level_1996=c1(m, base), corr_level_2006=c2(m, base), corr_d12_1996=c1(d12, b12), corr_d12_2006=c2(d12, b12),
                   corr_fi_basePhi_1996=c1(fi_b, fl.forward_impetus), corr_fi_basePhi_2006=c2(fi_b, fl.forward_impetus),
                   corr_fi_ownPhi_1996=c1(fi_r, fl.forward_impetus), corr_fi_ownPhi_2006=c2(fi_r, fl.forward_impetus),
                   latest=m.iloc[-1], latest_base=base.iloc[-1], latest_gap=m.iloc[-1] - base.iloc[-1],
                   fi_latest=fi_b.iloc[-1], fi_latest_base=fl.forward_impetus.iloc[-1], fi_latest_ownPhi=fi_r.iloc[-1])
        for k, (a, b) in EP.items():
            row[f"gap_level_{k}"] = (m - base).loc[a:b].mean(); row[f"gap_fi_{k}"] = (fi_b - fl.forward_impetus).loc[a:b].mean()
            row[f"base_sd_level_{k}"] = base.loc[a:b].std(); row[f"gap_level_absmax_{k}"] = (m - base).loc[a:b].abs().max()
        T.append(row)
        series[f"{case}_{tag}"] = m; series[f"{case}_{tag}_fi"] = fi_b
        for h in range(0, 37):
            VR.append(dict(case=case, weights=tag, h=h, phi_rt=Phi[h], phi_base=ph[h]))
        if tag == "exp80":
            for kk in ("level_1996", "level_2006", "d12_1996", "d12_2006", "fi_basePhi_1996", "fi_basePhi_2006", "fi_ownPhi_1996"):
                S.add(f"corr_{kk}_{case}", row[f"corr_{kk}"])
            S.add(f"phi12_rt_{case}", Phi[12]); S.add(f"phi12_base_{case}", ph[12])
            S.add(f"fi_latest_rt_{case}", row["fi_latest"]); S.add(f"fi_latest_base_{case}", row["fi_latest_base"]); S.add(f"latest_gap_{case}", row["latest_gap"])
            S.add(f"max_abs_gap_fi_{case}", max(abs(row[f"gap_fi_{k}"]) for k in EP))
            for k in EP:
                S.add(f"gap_level_{k.replace('-', '_')}_{case}", row[f"gap_level_{k}"])
        else:
            S.add(f"corr_fi_basePhi_1996_exp100_{case}", row["corr_fi_basePhi_1996"]); S.add(f"phi12_rt_exp100_{case}", Phi[12])
    series[f"{case}_base"] = base; series[f"{case}_base_fi"] = fl.forward_impetus
T = pd.DataFrame(T); T.to_csv(RES / "16_index_sensitivity.csv", index=False)
pd.DataFrame(series).to_csv(RES / "16_index_series.csv", float_format="%.5f")
pd.DataFrame(VR).to_csv(RES / "16_var_response.csv", index=False)
for c in ("level", "d12", "fi_basePhi"):
    t = T[T.weights == "exp80"]
    S.add(f"corr_{c}_min", t[f"corr_{c}_1996"].min()); S.add(f"corr_{c}_max", t[f"corr_{c}_1996"].max())

# ---- tidy figure data: path (expanding, rolling), own bootstrap bars, baseline band and weights
fig = []
SER = {"ten": ("w_ten", "Weight on the 10-year yield"), "eq": ("w_eq", "Weight on equity valuation (CAPE)"), "usd": ("w_usd", "Weight on the real dollar"),
       "load": ("load", "Scale of the policy-news factor (2-year pp per unit of raw factor)")}
for k, (nm, (col, lab)) in enumerate(SER.items()):
    for wt in ("expanding", "rolling20"):
        for r in P[(P.window == wt) & (P.n >= MIN_N)].itertuples():
            fig.append(dict(kind="path", series=nm, label=lab, window=wt, date=r.date, value=getattr(r, col), lo=np.nan, hi=np.nan))
        for r in BB[BB.window == wt].itertuples():
            fig.append(dict(kind="bootstrap", series=nm, label=lab, window=wt, date=r.date, value=getattr(r, f"{nm}_pt"), lo=getattr(r, f"{nm}_lo"), hi=getattr(r, f"{nm}_hi")))
    if k < 3:
        fig.append(dict(kind="baseline", series=nm, label=lab, window="full_sample", date=pd.NaT, value=base_w[k], lo=lo[k], hi=hi[k]))
pd.DataFrame(fig).to_csv(RES / "16_weight_path.csv", index=False)
S.save()
print(V.round(3).to_string()); print(T[T.weights == "exp80"].round(2).T.to_string())
