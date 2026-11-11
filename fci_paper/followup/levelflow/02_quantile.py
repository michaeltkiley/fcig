"""(b) Growth-at-risk style quantile regressions (tau = 0.1, 0.5, 0.9) of 12-month payroll growth (monthly) and 4-quarter GDP growth (quarterly) on own lags plus
level, flow, both. In-sample: coefficients on standardised level/flow in the joint spec, with 90% intervals from a moving-block bootstrap of (y,X) rows
(block 24 months / 8 quarters, 200 draws, fixed seed). Out of sample: recursive from 1995, pinball (quantile) loss ratio to own-lags benchmark and a paired
Diebold-Mariano t (HAC 12 / 4).
PRIMARY pre-specified family: payroll growth, tau=0.1, OOS pinball, 14 series x 3 specs = 42 tests; Holm and Benjamini-Hochberg across that family reported.
Everything else (tau 0.5/0.9, GDP, in-sample bootstrap) is secondary; total counted statistics are listed in RESULT.md."""
import numpy as np, pandas as pd, statsmodels.api as sm, warnings, sys
from statsmodels.regression.quantile_regression import QuantReg
from multiprocessing import Pool
from common import *
warnings.filterwarnings("ignore")
TAUS = (0.1, 0.5, 0.9); B = 200

def qfit(y, X, tau):
    return QuantReg(y, X).fit(q=tau, max_iter=2000).params

def pin(e, tau): return np.where(e >= 0, tau * e, (tau - 1) * e)

def bootstrap(D, cols, tau, blk, rng):
    n = len(D); yv = D.y.values; Xv = np.c_[np.ones(n), D[cols].values]; k = int(np.ceil(n / blk)); out = []
    for _ in range(B):
        st = rng.integers(0, n - blk + 1, k); ix = np.concatenate([np.arange(s, s + blk) for s in st])[:n]
        try: out.append(qfit(yv[ix], Xv[ix], tau))
        except Exception: pass
    return np.array(out)

def job(args):
    lab, freq = args
    x = load_indexes()[lab]
    own = ["g12", "g3"] if freq == "M" else ["g4"]
    D = monthly_design(x, "pay") if freq == "M" else quarterly_design(x)
    h = H if freq == "M" else 4; blk = 24 if freq == "M" else 8; first = FIRST_OOS if freq == "M" else "1995Q1"
    rng = np.random.default_rng(20261111)
    rows = []
    specs = {"own": [], "lvl": ["lvl"], "flw": ["flw"], "both": ["lvl", "flw"]}
    origins = [t for t in D.index if t >= pd.Period(first, freq=D.index.freqstr)]
    for tau in TAUS:
        # in-sample
        c = own + ["lvl", "flw"]; X = np.c_[np.ones(len(D)), D[c].values]; p = qfit(D.y.values, X, tau)
        bs = bootstrap(D, c, tau, blk, rng)
        row = {"series": lab, "freq": freq, "tau": tau, "n": len(D), "first": str(D.index[0]), "last": str(D.index[-1])}
        for nm in ("lvl", "flw"):
            j = 1 + c.index(nm); row[f"b_{nm}"] = p[j]; row[f"lo_{nm}"] = np.percentile(bs[:, j], 5); row[f"hi_{nm}"] = np.percentile(bs[:, j], 95)
        # OOS
        loss = {k: [] for k in specs}
        for t in origins:
            tr = D.loc[:t - h]
            if len(tr) < (100 if freq == "M" else 40): continue
            for k, cols in specs.items():
                cc = own + cols
                b = qfit(tr.y.values, np.c_[np.ones(len(tr)), tr[cc].values], tau)
                loss[k].append(float(pin(np.array(D.loc[t, "y"] - b @ np.r_[1, D.loc[t, cc].values.astype(float)]), tau)))
        loss = {k: np.array(v) for k, v in loss.items()}
        row["n_oos"] = len(loss["own"])
        for k in ("lvl", "flw", "both"):
            d = loss[k] - loss["own"]
            r = sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": 12 if freq == "M" else 4})
            row[f"qs_{k}"] = loss[k].mean() / loss["own"].mean(); row[f"dm_{k}"] = r.tvalues[0]; row[f"p_{k}"] = r.pvalues[0]
        rows.append(row)
    print(lab, freq, flush=True)
    return rows

if __name__ == "__main__":
    jobs = [(lab, f) for f in ("M", "Q") for lab in load_indexes()]
    with Pool(4) as P: res = P.map(job, jobs)
    pd.DataFrame([r for rr in res for r in rr]).to_csv(OUT / "quantile_results.csv", index=False)
