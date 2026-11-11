"""Build unpurged, full-sample-purged and recursively purged market and GS indexes at each step. Writes out/purged_indexes.csv, out/purge_r2.csv."""
from common import *
D, XS = all_inputs()
conv = pd.read_csv(REP / "results" / "conversions.csv", index_col=0).to_2y["GS"]
Z = regressors(D.u_gap, core_inflation())
assert not Z.isna().any().any()
res, r2rows = {}, []
for s in STEPS:
    X = XS[s].loc[START:END]
    for kind, cols in VARS.items():
        Xf, Xr = X[cols].copy(), X[cols].copy()
        for c in cols:
            Xf[c], r2 = purge_full(X[c], Z)
            Xr[c] = purge_recursive(X[c], Z)
            r2rows.append({"kind": kind, "step": s, "var": c, "r2_full": r2})
        res[f"{kind}|{s}|unpurged"] = build_index(X, kind, conv)
        res[f"{kind}|{s}|full"] = build_index(Xf, kind, conv)
        res[f"{kind}|{s}|recursive"] = build_index(Xr, kind, conv)
pd.DataFrame(res).to_csv(OUT / "purged_indexes.csv", float_format="%.5f")
R = pd.DataFrame(r2rows); R.to_csv(OUT / "purge_r2.csv", index=False)
print(R.round(2).to_string())
