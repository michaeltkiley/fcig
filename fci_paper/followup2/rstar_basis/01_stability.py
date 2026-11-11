"""A1: stability of the 12-month projection (index level / flow) across subperiods and rolling 20-year windows, by basis."""
from common import *
from scipy import stats
rng = np.random.default_rng(20261111)
SER = all_series(); SD = {k: v.loc["1973-01":"2026-09"].std() for k, v in SER.items()}
# sd of the flow over its own full sample for scaling
def scaled(k, kind):
    D = design(SER[k], kind); D["x"] = D.x / D.x.std(); return D
def fit(D, L=18):
    X = np.c_[np.ones(len(D)), D.u, D.du12, D.x]; b, e = ols(D.y.values, X); V = hac(X, e, L); return b, V, e, X

rows, roll = [], []
DES = {(k, kind): scaled(k, kind) for k in SER for kind in ("level", "flow")}
for (k, kind), D in DES.items():
    b, V, *_ = fit(D)
    row = {"family": k[0], "step": k[1], "kind": kind, "n_full": len(D), "slope_full": b[3], "se_full": np.sqrt(V[3, 3])}
    for p, (a, z) in SUBS.items():
        d = D.loc[a:z]
        if len(d) < 30: row[f"slope_{p}"] = np.nan; continue
        bb, VV, *_ = fit(d)
        row[f"n_{p}"] = len(d); row[f"slope_{p}"] = bb[3]; row[f"se_{p}"] = np.sqrt(VV[3, 3])
    # joint interaction models on P1-P3
    d = pd.concat([D.loc[SUBS[p][0]:SUBS[p][1]].assign(g=i) for i, p in enumerate(MAIN)])
    G = [(d.g == i).values.astype(float) for i in range(3)]
    Xs = np.column_stack([g[:, None] * np.c_[np.ones(len(d)), d.u, d.du12, d.x] for g in G])      # separate coefficients, 12 columns
    bs, es = ols(d.y.values, Xs); Vs = hac(Xs, es, 18)
    R1 = np.zeros((2, 12)); R1[0, 3], R1[0, 7] = 1, -1; R1[1, 7], R1[1, 11] = 1, -1                  # index slope equal
    Wc, pc = wald(bs, Vs, R1)
    R2 = np.zeros((8, 12))
    for j in range(4): R2[j, j], R2[j, 4 + j] = 1, -1; R2[4 + j, 4 + j], R2[4 + j, 8 + j] = 1, -1       # all coefficients equal
    Wa, pa = wald(bs, Vs, R2)
    row.update(wald_slope=Wc, p_slope=pc, wald_all=Wa, p_all=pa)
    sl = np.array([row[f"slope_{p}"] for p in MAIN]); row["disp_sd"] = sl.std(ddof=1); row["range"] = sl.max() - sl.min()
    row["sign_flip"] = bool(np.any(np.sign(sl) != np.sign(sl[0])))
    # sup-F for a single break in the index slope, bootstrap p
    n = len(D); X = np.c_[np.ones(n), D.u, D.du12, D.x]; y = D.y.values
    br = list(range(int(.15 * n), int(.85 * n) + 1, 3))
    def supF(y):
        b0, e0 = ols(y, X); s0 = e0 @ e0; best = 0
        for t in br:
            z = np.r_[np.zeros(t), X[t:, 3]]; X1 = np.c_[X, z]; b1, e1 = ols(y, X1); F = (s0 - e1 @ e1) / (e1 @ e1 / (n - 5)); best = max(best, F)
        return best
    F0 = supF(y); b0, e0 = ols(y, X); fit0 = X @ b0
    Fb = np.array([supF(fit0 + e0[blocks(n, 24, rng)]) for _ in range(499)])
    row.update(supF=F0, supF_p=float((Fb >= F0).mean()), supF_crit90=np.percentile(Fb, 90), supF_crit95=np.percentile(Fb, 95))
    rows.append(row); print(k, kind, round(row["wald_slope"], 2), round(row["p_slope"], 3), round(F0, 2), row["supF_p"], flush=True)
T = pd.DataFrame(rows); T.to_csv(OUT / "stability_subperiods.csv", index=False)

# rolling 20-year windows
for (k, kind), D in DES.items():
    for end in pd.period_range("1996-01", "2025-09", freq="12M" if False else "M")[::12]:
        a = end - 239; d = D.loc[a:end]
        if len(d) < 120: continue
        b, V, *_ = fit(d); roll.append({"family": k[0], "step": k[1], "kind": kind, "window_end": str(end), "n": len(d), "slope": b[3], "se": np.sqrt(V[3, 3])})
R = pd.DataFrame(roll); R.to_csv(OUT / "stability_rolling.csv", index=False)
S = R.groupby(["family", "step", "kind"]).agg(sd=("slope", "std"), mn=("slope", "min"), mx=("slope", "max"), n_win=("slope", "size"), frac_lo90_gt0=("slope", lambda s: np.nan)).reset_index()
R["sig"] = R.slope / R.se > 1.645
S["frac_sig_pos"] = R.groupby(["family", "step", "kind"]).sig.mean().values
S.drop(columns="frac_lo90_gt0").to_csv(OUT / "stability_rolling_summary.csv", index=False)

# dispersion bootstrap: within-period moving blocks (24 months), same draws across all series
def disp_boot(reps=300):
    out = []
    for r in range(reps):
        row = {}
        idxs = {p: blocks(len(DES[(("Market", "nominal"), "flow")].loc[SUBS[p][0]:SUBS[p][1]]), 24, rng) for p in MAIN}   # nominal and others share the sample (same rows)
        for (k, kind), D in DES.items():
            sl = []
            for p in MAIN:
                d = D.loc[SUBS[p][0]:SUBS[p][1]]
                if len(d) != len(idxs[p]): idxs[p] = blocks(len(d), 24, rng)
                d = d.iloc[idxs[p]]; X = np.c_[np.ones(len(d)), d.u, d.du12, d.x]; sl.append(ols(d.y.values, X)[0][3])
            row[f"{k[0]}|{k[1]}|{kind}"] = np.std(sl, ddof=1)
        out.append(row)
    return pd.DataFrame(out)
B = disp_boot(); B.to_csv(OUT / "dispersion_boot.csv", index=False)
res = []
for kind in ("flow", "level"):
    for fam in FAM:
        for s in STEPS:
            c = f"{fam}|{s}|{kind}"; pt = T[(T.family == fam) & (T.step == s) & (T.kind == kind)].disp_sd.iloc[0]
            res.append({"family": fam, "step": s, "kind": kind, "disp_sd": pt, "lo90": B[c].quantile(.05), "hi90": B[c].quantile(.95)})
        for s in ("real", "rstar"):
            d = B[f"{fam}|{s}|{kind}"] - B[f"{fam}|nominal|{kind}"]
            res.append({"family": fam, "step": f"{s} minus nominal", "kind": kind, "disp_sd": T[(T.family == fam) & (T.step == s) & (T.kind == kind)].disp_sd.iloc[0] - T[(T.family == fam) & (T.step == "nominal") & (T.kind == kind)].disp_sd.iloc[0], "lo90": d.quantile(.05), "hi90": d.quantile(.95)})
        d = B[f"{fam}|rstar|{kind}"] - B[f"{fam}|real|{kind}"]
        res.append({"family": fam, "step": "rstar minus real", "kind": kind, "disp_sd": T[(T.family == fam) & (T.step == "rstar") & (T.kind == kind)].disp_sd.iloc[0] - T[(T.family == fam) & (T.step == "real") & (T.kind == kind)].disp_sd.iloc[0], "lo90": d.quantile(.05), "hi90": d.quantile(.95)})
pd.DataFrame(res).to_csv(OUT / "dispersion.csv", index=False)
