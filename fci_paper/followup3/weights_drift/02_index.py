from common import *
D = data.load(); u = D.u_gap
P = pd.read_csv(OUT / "weight_paths.csv", parse_dates=["date"])
E = P[(P.window == "expanding") & (P.n >= MIN_N)].sort_values("date")
Wm = pd.DataFrame(E[["w_ten", "w_eq", "w_usd"]].values, index=E.date.dt.to_period("M"), columns=I.MARKET_VARS).groupby(level=0).last()
# also check variant: first estimate at the 100th announcement
E100 = P[(P.window == "expanding") & (P.n >= 100)].sort_values("date")
W100 = pd.DataFrame(E100[["w_ten", "w_eq", "w_usd"]].values, index=E100.date.dt.to_period("M"), columns=I.MARKET_VARS).groupby(level=0).last()
w0 = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
def monthly(W, idx):
    return W.reindex(W.index.union(idx)).sort_index().ffill().bfill().loc[idx]
rows, series = [], {}
EP = {"2004-06": ("2004-01", "2006-12"), "2009-15": ("2009-01", "2015-12"), "2022-26": ("2022-01", "2026-09")}
for case, rs in (("nominal", None), ("real", None), ("rstar", "rstar LW")):
    X = cases.inputs(D, "rstar" if rs else case, rstar=rs or "rstar LW")
    Xd = cases.demean(X[I.MARKET_VARS])
    base = pd.read_csv(RES / f"indexes_{case}.csv", index_col=0).market; base.index = pd.PeriodIndex(base.index, freq="M")
    fl = pd.read_csv(RES / f"flow_{case}_p12.csv", index_col=0); fl.index = pd.PeriodIndex(fl.index, freq="M")
    # baseline Phi
    ph = pd.read_csv(RES / f"var_paths_{case}_p12.csv").phi.values
    for tag, W in (("exp80", Wm), ("exp100", W100)):
        Wt = monthly(W, Xd.index)
        m = (Xd * Wt).sum(axis=1).loc["1973-01":"2026-09"]
        fi_b = var.forward_impetus(m, ph)                         # baseline Phi
        r, Dd, dum = var.fit(u, m, 12); Phi, _ = var.response(r)
        fi_r = var.forward_impetus(m, Phi) if Phi[12] > 0 else pd.Series(np.nan, index=m.index)
        d12, b12 = m.diff(12), base.diff(12)
        ok = lambda a, b: pd.concat([a, b], axis=1).loc["1996-01":].dropna().corr().iloc[0, 1]
        ok2 = lambda a, b: pd.concat([a, b], axis=1).loc["2006-01":].dropna().corr().iloc[0, 1]
        row = dict(case=case, weights=tag, phi12_rev=Phi[12], phi12_base=ph[12],
                   corr_level_1996=ok(m, base), corr_level_2006=ok2(m, base), corr_d12_1996=ok(d12, b12), corr_d12_2006=ok2(d12, b12),
                   corr_fi_basePhi_1996=ok(fi_b, fl.forward_impetus), corr_fi_basePhi_2006=ok2(fi_b, fl.forward_impetus),
                   corr_fi_ownPhi_1996=ok(fi_r, fl.forward_impetus), corr_fi_ownPhi_2006=ok2(fi_r, fl.forward_impetus),
                   latest=m.iloc[-1], latest_base=base.iloc[-1], latest_gap=m.iloc[-1] - base.iloc[-1],
                   fi_latest=fi_b.iloc[-1], fi_latest_base=fl.forward_impetus.iloc[-1],
                   fi_latest_ownPhi=fi_r.iloc[-1])
        for k, (a, b) in EP.items():
            row[f"gap_level_{k}"] = (m - base).loc[a:b].mean(); row[f"gap_fi_{k}"] = (fi_b - fl.forward_impetus).loc[a:b].mean()
            row[f"base_sd_level_{k}"] = base.loc[a:b].std(); row[f"gap_level_absmax_{k}"] = (m - base).loc[a:b].abs().max()
        rows.append(row)
        series[f"{case}_{tag}"] = m; series[f"{case}_{tag}_fi"] = fi_b
    series[f"{case}_base"] = base; series[f"{case}_base_fi"] = fl.forward_impetus
T = pd.DataFrame(rows); T.to_csv(OUT / "index_sensitivity.csv", index=False)
pd.DataFrame(series).to_csv(OUT / "index_series.csv", float_format="%.5f")
pd.set_option("display.width", 250, "display.max_columns", 50)
print(T.round(2).T.to_string())
print("sd of level/fi (baseline) by case over 1996+:", {c: (round(series[f'{c}_base'].loc['1996':].std(), 2), round(series[f'{c}_base_fi'].loc['1996':].std(), 2)) for c in ('nominal','real','rstar')})
print(Wm.iloc[[0, 24, 60, -1]])
