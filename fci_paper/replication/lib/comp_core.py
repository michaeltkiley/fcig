"""Step 19 helpers: matched normalized FRB/US-minus-market difference D, designs, HAC fits, block bootstrap, recursive forecasts. Reads RES and DATA only."""
import numpy as np, pandas as pd, statsmodels.api as sm
from scipy import stats
from . import data, cases
from .config import RES, SEED
from .stance_core import M, Y, CTL, own, keep, mean_t, oos, n_recessions, H, LAST_ORIGIN, ffg, index

VARS = ["y10", "equities", "dollar"]
SAMPLES = {"main": dict(start="1976-03", excl=[], first_oos="1995-01", nmin=100),
           "1996+": dict(start="1996-01", excl=[], first_oos=None, nmin=96),
           "ex2008-15": dict(start="1976-03", excl=[("2008-01", "2015-12")], first_oos="1995-01", nmin=100)}
BLOCK = 24          # months (8 quarters for GDP)


def weights():
    mw = pd.read_csv(RES / "market_weights.csv", index_col=0).reindex(VARS)
    fw = pd.read_csv(RES / "frbus_weights.csv", index_col=0).reindex(VARS)
    wM, psi, b = mw.weight.values, mw.response.values, fw.frbus_weight.values
    bpsi = float(b @ psi)
    return dict(wM=wM, psi=psi, b=b, bpsi=bpsi, wB=b / bpsi)


def changes():
    """12-month changes of the three market variables at the r* step (r* equity transformation), and the market index change, D, FRB/US-weight change dB."""
    X = cases.inputs(data.load(), "rstar")[VARS]
    X12 = X.diff(12).loc["1973-01":"2026-09"]
    W = weights()
    dM = X12 @ W["wM"]; dB = X12 @ W["wB"]; D = dB - dM
    # check against the package's market index (step 03)
    chk = float((dM - index("rstar", "market").diff(12)).abs().max())
    return X, X12, dM, D, dB, chk, W


def frame(yn, regs, ffc, start, excl):
    """Origins x [y, own lags, regressors]; one common sample for every specification (rows complete in all regressors); raw (unstandardised) regressors."""
    cols = {"y": Y[yn]}
    for c in CTL[yn]: cols[c] = CTL[yn][c]
    for k, v in regs.items(): cols[k] = v
    cols["ff"] = ffc
    Dd = pd.DataFrame(cols).loc[start:"2026-09"]
    return Dd[keep(Dd.index, excl)].dropna()


def gdp_frame(regs, ffc, start, excl):
    """Quarterly alignment: origin = last month of a quarter; y = 100 ln(GDP(q+4)/GDP(q)); own lags: 4-quarter and (annualised) 1-quarter past growth."""
    from .config import DATA
    d = pd.read_csv(DATA / "GDPC1.csv")
    g = pd.Series(d.GDPC1.values, index=pd.PeriodIndex(pd.to_datetime(d.observation_date), freq="Q"))
    lg = 100 * np.log(g)
    y = lg.shift(-4) - lg; g4 = lg - lg.shift(4); g1 = 4 * (lg - lg.shift(1))
    ix = pd.PeriodIndex([q.asfreq("M", "e") for q in g.index], freq="M")
    cols = {"y": pd.Series(y.values, ix), "g4": pd.Series(g4.values, ix), "g1": pd.Series(g1.values, ix)}
    for k, v in regs.items(): cols[k] = v.reindex(ix)
    cols["ff"] = ffc.reindex(ix)
    Dd = pd.DataFrame(cols).loc[start:"2026-09"]
    return Dd[keep(Dd.index, excl)].dropna()


def hac(D, cols, lags):
    return sm.OLS(D.y, sm.add_constant(D[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": lags})


def block_idx(n, reps, tag, block=BLOCK):
    """Moving-block resampling of rows (whole rows jointly), deterministic: seed (SEED, 19, tag)."""
    rng = np.random.default_rng([SEED, 19, tag]); nb = int(np.ceil(n / block)); out = np.empty((reps, n), dtype=int)
    for b in range(reps):
        s = rng.integers(0, n - block + 1, nb)
        out[b] = (s[:, None] + np.arange(block)).ravel()[:n]
    return out


def boot_coefs(D, cols, idx):
    X = np.c_[np.ones(len(D)), D[cols].values]; y = D.y.values; out = np.empty((len(idx), len(cols) + 1))
    for b, ix in enumerate(idx):
        out[b] = np.linalg.lstsq(X[ix], y[ix], rcond=None)[0]
    return out


def pct(a, q): return float(np.percentile(a, q))


def prop_test(theta, V, w, boot=None):
    """H0: theta proportional to w (2 restrictions). HAC Wald p (chi2(2)) and bootstrap p (Mahalanobis distance of R theta under the bootstrap covariance)."""
    R = np.array([[w[1], -w[0], 0.0], [w[2], 0.0, -w[0]]])
    r = R @ theta; Wd = float(r @ np.linalg.solve(R @ V @ R.T, r)); p_hac = float(1 - stats.chi2.cdf(Wd, 2))
    p_b = np.nan
    if boot is not None:
        rb = boot @ R.T; Vb = np.cov(rb.T); cen = rb - rb.mean(0)
        wd0 = float(r @ np.linalg.solve(Vb, r)); wdb = np.einsum("ij,jk,ik->i", cen, np.linalg.inv(Vb), cen)
        p_b = float((wdb >= wd0).mean())
    return Wd, p_hac, p_b


def cw_stats(F, small, large, lags):
    e0, e1 = F.y - F[small], F.y - F[large]
    d = e0 ** 2 - e1 ** 2; cw = d + (F[small] - F[large]) ** 2
    t = mean_t(cw.values, lags)
    return dict(rmse_ratio=float(np.sqrt((e1 ** 2).mean() / (e0 ** 2).mean())), cw_t=t, cw_p=float(1 - stats.norm.cdf(t)), dm_t=mean_t(d.values, lags))
