from common import *
B = pd.read_csv(RES / "weights_boot.csv")
base_w = pd.read_csv(RES / "market_weights.csv", index_col=0).weight.values
lo, hi = np.percentile(B[["w_ten", "w_eq", "w_usd"]], 5, axis=0), np.percentile(B[["w_ten", "w_eq", "w_usd"]], 95, axis=0)
dates = RAW.Date.values
rows = []
for i in range(len(RAW)):
    d = RAW.Date.iloc[i]
    if i + 1 >= 60:   # compute from the 60th to show; flagged
        w, psi, load, sd = est(RAW.iloc[:i + 1])
        rows.append(dict(window="expanding", date=d, n=i + 1, w_ten=w[0], w_eq=w[1], w_usd=w[2], psi_ten=psi[0], psi_eq=psi[1], psi_usd=psi[2], load=load, ns_sd=sd))
    start = d - pd.DateOffset(years=20)
    if d >= pd.Timestamp("2016-01-01"):
        sub = RAW[(RAW.Date > start) & (RAW.Date <= d)]
        w, psi, load, sd = est(sub)
        rows.append(dict(window="rolling20", date=d, n=len(sub), w_ten=w[0], w_eq=w[1], w_usd=w[2], psi_ten=psi[0], psi_eq=psi[1], psi_usd=psi[2], load=load, ns_sd=sd))
P = pd.DataFrame(rows); P.to_csv(OUT / "weight_paths.csv", index=False)
# bootstrap at grid
grid = [pd.Timestamp(f"{y}-12-31") for y in range(2006, 2026)] + [RAW.Date.max()]
rng = np.random.default_rng(SEED); R = 500; br = []
for g in grid:
    for wt in ("expanding", "rolling20"):
        if wt == "rolling20" and g < pd.Timestamp("2016-01-01"): continue
        sub = RAW[RAW.Date <= g] if wt == "expanding" else RAW[(RAW.Date > g - pd.DateOffset(years=20)) & (RAW.Date <= g)]
        sub = sub.reset_index(drop=True)
        if len(sub) < MIN_N: continue
        pt = est(sub)
        draws = []
        for _ in range(R):
            b = sub.iloc[rng.integers(0, len(sub), len(sub))].reset_index(drop=True)
            w, psi, load, sd = est(b); draws.append(np.r_[w, load])
        draws = np.array(draws)
        r = dict(window=wt, date=g, n=len(sub), reps=R)
        for k, nm in enumerate(("ten", "eq", "usd", "load")):
            r[f"{nm}_pt"] = pt[0][k] if k < 3 else pt[2]
            r[f"{nm}_lo"], r[f"{nm}_hi"] = np.percentile(draws[:, k], [5, 95])
        br.append(r)
BB = pd.DataFrame(br)
for k, nm in enumerate(("ten", "eq", "usd")):
    BB[f"{nm}_in_base"] = (BB[f"{nm}_pt"] >= lo[k]) & (BB[f"{nm}_pt"] <= hi[k])
    BB[f"{nm}_base_in_own"] = (base_w[k] >= BB[f"{nm}_lo"]) & (base_w[k] <= BB[f"{nm}_hi"])
    BB[f"{nm}_width_ratio"] = (BB[f"{nm}_hi"] - BB[f"{nm}_lo"]) / (hi[k] - lo[k])
BB.to_csv(OUT / "weight_path_bands.csv", index=False)
# verdict table
P["period"] = np.where(P.date > "2010-12-31", "post2010", "pre2011")
for k, nm in enumerate(("ten", "eq", "usd")):
    P[f"{nm}_in"] = (P[f"w_{nm}"] >= lo[k]) & (P[f"w_{nm}"] <= hi[k])
P.to_csv(OUT / "weight_paths.csv", index=False)
V = []
for wt in ("expanding", "rolling20"):
    q = P[(P.window == wt) & (P.n >= MIN_N)]
    for per, g in q.groupby("period"):
        V.append(dict(window=wt, period=per, n_dates=len(g), **{f"{nm}_share_in_base_band": g[f"{nm}_in"].mean() for nm in ("ten", "eq", "usd")},
                      **{f"{nm}_min": g[f"w_{nm}"].min() for nm in ("ten", "eq", "usd")}, **{f"{nm}_max": g[f"w_{nm}"].max() for nm in ("ten", "eq", "usd")}))
V = pd.DataFrame(V); V.to_csv(OUT / "weight_verdict.csv", index=False)
pd.set_option("display.width", 250)
print("baseline w", base_w.round(3), "band lo", lo.round(3), "hi", hi.round(3))
print(V.round(3).to_string())
print(BB[["window","date","n","ten_pt","ten_lo","ten_hi","eq_pt","eq_lo","eq_hi","usd_pt","usd_lo","usd_hi","load_pt","load_lo","load_hi"]].round(3).to_string())
print(BB[["window","date","ten_width_ratio","eq_width_ratio","usd_width_ratio","ten_base_in_own","eq_base_in_own","usd_base_in_own"]].round(2).to_string())
print(B.describe(percentiles=[.01,.05,.5,.95,.99]).round(2).T)
print("share of boot draws with w_ten<0 or >2:", ((B.w_ten<0)|(B.w_ten>2)).mean())
