"""Helpers for steps 08 (stance) and 12 (checks on 1996+): outcomes, funds-rate gaps, regression designs, recursive forecasts, tests.
No FOMC-window surprises are used here; indexes are read from results/ (made by step 03), the weights from results/weights_variants.csv.

Conventions (from followup2/stance and followup3/core_1996): outcomes at h = 12 months; origins whose window t-12..t+12 touches 2020-01..2021-03 are dropped (and, in row c,
2008-01..2015-12); regressors other than own lags are standardised on the estimation sample; HAC (Newey-West) standard errors; recursive (expanding) out-of-sample forecasts
whose training sample ends h months before the origin; positive Diebold-Mariano / Clark-West t = larger model better."""
import numpy as np, pandas as pd, statsmodels.api as sm
from .config import DATA, RES

H = 12
STEPS = ["nominal", "real", "rstar"]
SERIES = [("market", "Market"), ("gs", "GS"), ("frbus", "FRB/US")]
LAST_ORIGIN = "2025-09"


def pcols(path):
    d = pd.read_csv(path, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def fred(name):
    d = pd.read_csv(DATA / f"{name}.csv")
    s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    s.index = s.index.to_period("M"); return s


M = pcols(RES / "data_monthly.csv")
REC = fred("USREC")
_IDX = {}


def index(step, key, w2019=False):
    """Index level series for a step ('nominal', 'real', 'rstar', 'rstar_kiley'); w2019: market index with weights estimated on announcements through 2019."""
    if w2019 and key == "market": return w2019_market()[step]
    if step not in _IDX: _IDX[step] = pcols(RES / f"indexes_{step}.csv")
    return _IDX[step][key]


_W2019 = {}


def w2019_market():
    if not _W2019:
        from . import data, cases, indexes as I
        V = pd.read_csv(RES / "weights_variants.csv").set_index("variant")
        w = V.loc["to_2019", ["w_ten", "w_eq", "w_usd"]].values.astype(float)
        D = data.load()
        for case, rs in (("nominal", None), ("real", None), ("rstar", "rstar LW")):
            X = cases.inputs(D, "rstar" if rs else case, rstar=rs or "rstar LW")
            _W2019[case] = I.market(X, w)[0].loc["1973-01":"2026-09"]
    return _W2019


def ffg(step, rstar="rstar LW"):
    """Funds-rate gap: nominal FEDFUNDS; real less 1-year expected inflation; r*: less r* as well (same series as the indexes)."""
    return {"nominal": M.ffr, "real": M.ffr - M.einf_1y, "rstar": M.ffr - M.einf_1y - M[rstar]}[step]


def outcomes():
    u = M.u_gap; pay = np.log(fred("PAYEMS")) * 100; px = np.log(fred("PCEPILFE")) * 100
    y = pd.DataFrame({"du": u.shift(-H) - u, "pay": pay.shift(-H) - pay, "pi": px.shift(-H) - px})
    ctl = {"du": pd.DataFrame({"u": u, "du12": u - u.shift(12)}),
           "pay": pd.DataFrame({"g12": pay - pay.shift(12), "g3": 4 * (pay - pay.shift(3))}),
           "pi": pd.DataFrame({"p12": px - px.shift(12), "p3": 4 * (px - px.shift(3))})}
    return y, ctl


Y, CTL = outcomes()


def own(yn): return list(CTL[yn].columns)


def covid(p): return p.year == 2020 or (p.year == 2021 and p.month <= 3)
def _in(p, a, b): return pd.Period(a, "M") <= p <= pd.Period(b, "M")


def keep(idx, excl=()):
    def bad(p): return covid(p) or any(_in(p, a, b) for a, b in excl)
    return np.array([not any(bad(t + k) for k in range(-12, 13)) for t in idx])


def design(yn, f, x, form, start="1976-03", excl=()):
    """origins x [y, own lags, ff, idx] (or lvl, flw for form 'lf'); non-own regressors standardised. Forms: level, flow (12-month changes of both),
    mixed (funds-rate gap level, index 12-month change), lf (index level and 12-month change, no funds-rate gap)."""
    cols = {"y": Y[yn]}
    for c in CTL[yn]: cols[c] = CTL[yn][c]
    if form == "lf":
        cols["lvl"] = x; cols["flw"] = x.diff(12)
    else:
        cols["ff"] = f.diff(12) if form == "flow" else f
        cols["idx"] = x.diff(12) if form in ("flow", "mixed") else x
    D = pd.DataFrame(cols).loc[start:"2026-09"]
    D = D[keep(D.index, excl)].dropna()
    for c in D.columns:
        if c not in ["y"] + own(yn): D[c] = (D[c] - D[c].mean()) / D[c].std()
    return D


def hac_ols(D, cols, lags=18):
    return sm.OLS(D.y, sm.add_constant(D[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": lags})


def mean_t(d, lags=12):
    return float(sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lags}).tvalues[0])


def oos(D, sets, first_oos="1995-01", nmin=100, last=None):
    """Recursive forecasts for each model in sets {name: columns}; DataFrame indexed by origin with the actual y and each forecast.
    Origins before first_oos (if given) or after last (if given) are skipped; an origin needs at least nmin training months (training ends h months before the origin)."""
    rows = {}
    for t in D.index:
        if first_oos and t < pd.Period(first_oos, "M"): continue
        if last and t > pd.Period(last, "M"): continue
        tr = D.loc[:t - H]
        if len(tr) < nmin: continue
        r = {"y": D.loc[t, "y"]}
        for k, c in sets.items():
            b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[c].values], tr.y.values, rcond=None)[0]
            r[k] = float(b @ np.r_[1, D.loc[t, c].values.astype(float)])
        rows[t] = r
    return pd.DataFrame(rows).T


def n_recessions(origins):
    """NBER recession episodes with a month in the outcome window (t, t+12] of some out-of-sample origin."""
    rm = REC[REC == 1].index; hit = set()
    for t in origins:
        for k in range(1, 13):
            if (t + k) in rm: hit.add(t + k)
    n = 0; prev = None
    for p in sorted(hit):
        if prev is None or (p - prev).n > 1: n += 1
        prev = p
    return n


def holm(p):
    """Holm step-down adjusted p-values for a Series."""
    o = p.sort_values().index; m = len(p); out = pd.Series(np.nan, index=p.index); run = 0.0
    for i, ix in enumerate(o):
        run = max(run, min(1.0, (m - i) * p[ix])); out[ix] = run
    return out


# ---------------------------------------------------------------------------------------------------------------- step 12
ROWS = {  # origins start, exclusion windows, first OOS date (None: first origin with nmin training months), min training months, VAR start, VAR dummy ranges, VAR lags
    "a": dict(start="1976-03", excl=[], first_oos="1995-01", nmin=100, var_start="1973-01", var_dum=[], lags=[12]),
    "b": dict(start="1996-01", excl=[], first_oos=None, nmin=96, var_start="1996-01", var_dum=[], lags=[12, 4]),
    "c": dict(start="1976-03", excl=[("2008-01", "2015-12")], first_oos="1995-01", nmin=100, var_start="1973-01", var_dum=[("2008-01", "2015-12")], lags=[12]),
    "d": dict(start="1976-03", excl=[], first_oos="1995-01", nmin=100, var_start="1973-01", var_dum=[], lags=[12], w2019=True),
    "e": dict(start="1974-01", excl=[], first_oos=None, nmin=100, var_start="1973-01", var_dum=[], lags=[12]),
}
ROW_LABEL = {"a": "main (VAR 1973+; regressions 1976+)", "b": "fixed 1996+", "c": "excluding 2008-15", "d": "weights through 2019", "e": "origins from 1974-01"}


def row_design(yn, step, key, form, row):
    R = ROWS[row]
    return design(yn, ffg(step), index(step, key, R.get("w2019", False)), form, R["start"], R["excl"])


def var_frame(u, m, start, dum_ranges):
    D = pd.DataFrame({"u": u, "M": m}).loc[start:"2026-09"].dropna()
    dums = {f"d2020_{k:02d}": (D.index == pd.Period(f"2020-{k:02d}", "M")).astype(float) for k in range(1, 13)}
    for a, b in dum_ranges:
        for p in pd.period_range(a, b, freq="M"): dums[f"d{p}"] = (D.index == p).astype(float)
    dum = pd.DataFrame(dums, index=D.index); dum = dum.loc[:, dum.any()]
    D.index = D.index.to_timestamp(); dum.index = D.index
    return D, dum


def var_job(a):
    """One VAR: Phi(12) with 90% block-bootstrap interval, Granger p. a = (label, step, key, lags, var_start, var_end, dum_ranges, w2019, reps). Module-level so that Pool can pickle it."""
    from statsmodels.tsa.api import VAR
    from . import var
    lab, step, key, p, start, end, dums, w19, reps = a
    m = index(step, key, w19)
    D, dum = var_frame(M.u_gap, m.loc[:end], start, dums)
    r = VAR(D, exog=dum if dum.shape[1] else None).fit(p)
    Phi, _ = var.response(r)
    gc = r.test_causality("u", ["M"], kind="f")
    ph, _ = var.bootstrap(D, dum, p, 36, reps)
    lo, hi = var.bands(ph, 0.90)
    return dict(spec=lab, step=step, series=key, lags=p, n=len(D), start=str(D.index[0].to_period("M")), end=str(D.index[-1].to_period("M")), phi6=Phi[6], phi12=Phi[12], lo90=lo[12], hi90=hi[12],
                phi24=Phi[24], lo90_24=lo[24], hi90_24=hi[24], granger_F=gc.test_statistic, granger_p=gc.pvalue, boot_share_pos=float((ph[:, 12] > 0).mean()))
