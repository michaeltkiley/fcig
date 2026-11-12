"""(iv) the r* ladder for the unemployment outcome: own lags + index flow; step differences in-sample (R2) and OOS (MSE) with paired moving-block bootstrap. Writes out/ladder.csv
Samples: a (1976+), a_pre96 (origins before 1996-01), a_post96 (origins 1996-01 on, same fitted model as a: coefficients from the full sample; here refit within the subsample),
b (1996+ refit), c, e."""
from common import *
rng = np.random.default_rng(20261111); B = 1000; BL = 24

def blocks(n):
    nb = -(-n // BL)
    return [np.concatenate([np.arange(s, s + BL) for s in rng.integers(0, n - BL + 1, nb)])[:n] for _ in range(B)]

def r2(y, X):
    Z = np.c_[np.ones(len(y)), X]; b = np.linalg.lstsq(Z, y, rcond=None)[0]; e = y - Z @ b
    return 1 - (e @ e) / (((y - y.mean()) ** 2).sum())

def boot_ci(stat_fn, n, draws):
    s = np.array([stat_fn(ix) for ix in draws]); return np.percentile(s, 5), np.percentile(s, 95)

rows = []
PAIRS = [("real", "nominal"), ("rstar", "real"), ("rstar", "nominal")]   # (later, earlier)
SAMPLES = [("a", "a", None, None), ("a_pre96", "a", None, "1995-12"), ("a_post96", "a", "1996-01", None), ("b", "b", None, None), ("c", "c", None, None), ("e", "e", None, None)]
for lab, row, lo, hi in SAMPLES:
    for key, nm in SERIES:
        ow = own("du"); D = {s: design("du", s, key, "flow", row) for s in STEPS}
        idx = D["nominal"].index
        for s in STEPS: assert (D[s].index == idx).all()
        sel = np.ones(len(idx), bool)
        if lo: sel &= idx >= pd.Period(lo, "M")
        if hi: sel &= idx <= pd.Period(hi, "M")
        # in-sample: refit within the subsample
        Ds = {s: D[s][sel].copy() for s in STEPS}
        for s in STEPS: Ds[s]["idx"] = (Ds[s].idx - Ds[s].idx.mean()) / Ds[s].idx.std()
        y = Ds["nominal"].y.values; C = Ds["nominal"][ow].values
        X = {s: np.c_[C, Ds[s].idx.values] for s in STEPS}
        draws = blocks(len(y))
        # OOS (recursive) on the full design, evaluated over origins in the subsample
        F = {s: oos(D[s], {"M": ow + ["idx"]}, row) for s in STEPS}
        for later, earlier in PAIRS:
            diff = r2(y, X[later]) - r2(y, X[earlier])
            l, h = boot_ci(lambda ix: r2(y[ix], X[later][ix]) - r2(y[ix], X[earlier][ix]), len(y), draws)
            Fl, Fe = F[later], F[earlier]
            m = np.ones(len(Fl), bool)
            if lo: m &= Fl.index >= pd.Period(lo, "M")
            if hi: m &= Fl.index <= pd.Period(hi, "M")
            Fl, Fe = Fl[m], Fe[m]
            row_ = dict(sample=lab, series=key, later=later, earlier=earlier, n=len(y), r2_later=r2(y, X[later]), r2_earlier=r2(y, X[earlier]), dr2=diff, dr2_lo90=l, dr2_hi90=h)
            if len(Fl) >= 40:
                d = (Fe.y - Fe.M) ** 2 - (Fl.y - Fl.M) ** 2
                dv = d.values; n = len(dv); nb = -(-n // BL)
                bs = [dv[np.concatenate([np.arange(s, s + BL) for s in rng.integers(0, max(n - BL, 1), nb)])[:n]].mean() for _ in range(B)]
                row_.update(first_oos=str(Fl.index[0]), last_oos=str(Fl.index[-1]), n_oos=len(Fl), n_rec_oos=n_recessions(Fl.index), rmse_ratio=float(np.sqrt(((Fl.y - Fl.M) ** 2).mean() / ((Fe.y - Fe.M) ** 2).mean())),
                            dm_t=mean_t(dv), dmse=float(dv.mean()), dmse_lo90=float(np.percentile(bs, 5)), dmse_hi90=float(np.percentile(bs, 95)))
            rows.append(row_)
    print(lab, flush=True)
pd.DataFrame(rows).to_csv(OUT / "ladder.csv", index=False)
