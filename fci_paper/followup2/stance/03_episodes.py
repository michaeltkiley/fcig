"""Episodes (descriptive): index (relative to r*) minus funds-rate gap, 2004-06 'conundrum' (2004-06..2006-06) and 2022-24 (2022-03..2024-12), with intervals over
the 500 bootstrap draws of the market weights (results/weights_boot.csv) and r* by Laubach-Williams versus Kiley. Both series are demeaned over 1973-2026, so the
difference is the deviation of the index from its usual relation to the gap on average (index in 2-year-yield units, gap in funds-rate points; the units are not
reconciled, so a standardised version divides each by its full-sample standard deviation). Also: bootstrap of the in-sample test (index given FFG, r* step, Market) over the draws."""
import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "replication"))
from common import *
from lib import data, cases, indexes as I
D0 = data.load(); W = pd.read_csv(REP / "results" / "weights_boot.csv")[["w_ten", "w_eq", "w_usd"]].values
w0 = pd.read_csv(REP / "results" / "market_weights.csv", index_col=0).weight.values
EP = {"conundrum 2004-06..2006-06": ("2004-06", "2006-06"), "tightening 2022-03..2024-12": ("2022-03", "2024-12"), "2022-03..2023-12": ("2022-03", "2023-12")}
rows = []; pct = lambda a, q: float(np.percentile(a, q))
for rs, lab in (("rstar LW", "LW"), ("rstar Kiley", "Kiley")):
    X = cases.demean(cases.inputs(D0, "rstar", rstar=rs)[I.MARKET_VARS]).loc["1973-01":"2026-09"]
    f = ffg("rstar", rs).loc["1973-01":"2026-09"]; f = f - f.mean(); sf = f.std()
    base = X @ w0; draws = X.values @ W.T                       # months x 500
    for en, (a, b) in EP.items():
        sl = (X.index >= pd.Period(a, "M")) & (X.index <= pd.Period(b, "M"))
        fm = float(f[sl].mean()); im = draws[sl].mean(0)
        sx = draws.std(0)
        r = dict(rstar=lab, episode=en, ffg=fm, index_point=float(base[sl].mean()), index_lo=pct(im, 5), index_hi=pct(im, 95),
                 diff_point=float(base[sl].mean() - fm), diff_lo=pct(im - fm, 5), diff_hi=pct(im - fm, 95),
                 zdiff_point=float(base[sl].mean() / base.std() - fm / sf), zdiff_lo=pct(im / sx - fm / sf, 5), zdiff_hi=pct(im / sx - fm / sf, 95),
                 share_draws_diff_neg=float(((im - fm) < 0).mean()), n_months=int(sl.sum()))
        for k in ("gs", "frbus"):
            s = cases.demean(cases.inputs(D0, "rstar", rstar=rs)[["policy"]])  # placeholder to keep imports used
        rows.append(r)
    for k in ("gs", "frbus"):
        if lab == "LW":
            ix = index("rstar", k).loc["1973-01":"2026-09"]
        else:
            ix = index("rstar_kiley", k).loc["1973-01":"2026-09"]
        for en, (a, b) in EP.items():
            sl = (ix.index >= pd.Period(a, "M")) & (ix.index <= pd.Period(b, "M"))
            rows.append(dict(rstar=lab, episode=en, comparison=k, ffg=float(f[sl].mean()), index_point=float(ix[sl].mean()), diff_point=float(ix[sl].mean() - f[sl].mean()), n_months=int(sl.sum())))
E=pd.DataFrame(rows); E.to_csv(OUT / "episodes.csv", index=False); print(E.round(2).to_string())
# monthly series for the figure/inspection: market index (point, 5-95 over draws) minus FFG, LW
X = cases.demean(cases.inputs(D0, "rstar")[I.MARKET_VARS]).loc["1990-01":"2026-09"]; f = ffg("rstar").loc["1973-01":"2026-09"]; f = (f - f.mean()).loc["1990-01":]
dr = X.values @ W.T
pd.DataFrame({"market": X @ w0, "ffg": f, "diff": X @ w0 - f, "diff_lo": np.percentile(dr - f.values[:, None], 5, axis=1), "diff_hi": np.percentile(dr - f.values[:, None], 95, axis=1)}).to_csv(OUT / "diff_series.csv")
# bootstrap of the in-sample incremental test over weight draws (Market, r*, full sample)
Xf = cases.demean(cases.inputs(D0, "rstar")[I.MARKET_VARS]); f = ffg("rstar"); res = []
for b in W:
    x = (Xf @ b).loc["1973-01":"2026-09"]
    for yn in OUTCOMES:
        for form in FORMS:
            S = design(yn, f, x, form); ow = own(yn)
            r1 = hac_ols(S, ow + ["ff"], 18); r3 = hac_ols(S, ow + ["ff", "idx"], 18)
            res.append(dict(outcome=yn, form=form, t_idx_both=r3.tvalues["idx"], gain=r3.rsquared_adj - r1.rsquared_adj))
R = pd.DataFrame(res).groupby(["outcome", "form"]).agg(t_med=("t_idx_both", "median"), t_lo=("t_idx_both", lambda a: np.percentile(a, 5)), t_hi=("t_idx_both", lambda a: np.percentile(a, 95)),
                                                    gain_med=("gain", "median"), gain_lo=("gain", lambda a: np.percentile(a, 5)), gain_hi=("gain", lambda a: np.percentile(a, 95)))
R.to_csv(OUT / "boot_insample.csv"); print(R.round(3))
