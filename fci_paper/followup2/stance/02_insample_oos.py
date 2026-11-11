"""In-sample (adjusted R2, HAC t) and recursive out-of-sample comparisons for every outcome x step x index x form, by period."""
from common import *
from scipy import stats
ins, oo = [], []
for yn in OUTCOMES:
    ow = own(yn)
    for s in STEPS:
        f = ffg(s)
        for k, lab in INDEXES.items():
            x = index(s, k)
            for form in FORMS:
                D = design(yn, f, x, form)
                F = oos(D, ow)
                for pn, (a, b) in PERIODS.items():
                    # ---- in sample: period origins (full uses the whole sample; sub-periods origins within the window)
                    if pn == "full": S = D; lags = 18
                    elif pn == "pre2009": continue
                    else: S = D.loc[a:b]; lags = 12
                    if len(S) >= 30:
                        r0 = hac_ols(S, ow, lags); r1 = hac_ols(S, ow + ["ff"], lags); r2 = hac_ols(S, ow + ["idx"], lags); r3 = hac_ols(S, ow + ["ff", "idx"], lags)
                        ins.append(dict(outcome=yn, step=s, index=k, form=form, period=pn, n=len(S), r2a_ff=r1.rsquared_adj - r0.rsquared_adj, r2a_idx=r2.rsquared_adj - r0.rsquared_adj,
                                        r2a_both=r3.rsquared_adj - r0.rsquared_adj, gain_idx_given_ff=r3.rsquared_adj - r1.rsquared_adj, gain_ff_given_idx=r3.rsquared_adj - r2.rsquared_adj,
                                        t_ff_alone=r1.tvalues["ff"], t_idx_alone=r2.tvalues["idx"], t_ff_both=r3.tvalues["ff"], t_idx_both=r3.tvalues["idx"],
                                        b_ff_both=r3.params["ff"], b_idx_both=r3.params["idx"]))
                    # ---- out of sample
                    G = F.loc[a:b] if True else F
                    G = F[(F.index >= pd.Period(a, "M")) & (F.index <= pd.Period(b, "M"))]
                    if len(G) < 20: continue
                    e = {m: G.y - G[m] for m in ("M0", "M1", "M2", "M3")}
                    row = dict(outcome=yn, step=s, index=k, form=form, period=pn, n_oos=len(G))
                    for small, large, nm in (("M0", "M1", "ff_vs_own"), ("M0", "M2", "idx_vs_own"), ("M1", "M3", "idx_given_ff"), ("M2", "M3", "ff_given_idx")):
                        d = e[small] ** 2 - e[large] ** 2
                        cw = d + (G[small] - G[large]) ** 2
                        row[f"rmse_{nm}"] = float(np.sqrt((e[large] ** 2).mean() / (e[small] ** 2).mean()))
                        row[f"dm_{nm}"] = mean_t(d.values); row[f"cw_{nm}"] = mean_t(cw.values)
                    oo.append(row)
    print(yn, "done", flush=True)
pd.DataFrame(ins).to_csv(OUT / "insample.csv", index=False); pd.DataFrame(oo).to_csv(OUT / "oos.csv", index=False)
# primary family: Market, r*, full sample, CW idx_given_ff, one-sided p (normal), Holm
O = pd.DataFrame(oo); Pm = O[(O["index"] == "market") & (O.step == "rstar") & (O.period == "full")].copy()
Pm["p"] = 1 - stats.norm.cdf(Pm.cw_idx_given_ff); o = Pm.p.sort_values().index; m = len(Pm)
Pm["p_holm"] = np.nan; run = 0
for i, ix in enumerate(o): run = max(run, min(1, (m - i) * Pm.p[ix])); Pm.loc[ix, "p_holm"] = run
Pm[["outcome", "form", "n_oos", "rmse_idx_given_ff", "dm_idx_given_ff", "cw_idx_given_ff", "p", "p_holm"]].to_csv(OUT / "primary.csv", index=False)
print(Pm[["outcome", "form", "rmse_idx_given_ff", "cw_idx_given_ff", "p", "p_holm"]].round(3).to_string())
