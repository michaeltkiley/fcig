"""Step 15 helpers: weight sets on the three market variables, outcomes, recursive out-of-sample forecasts, Diebold-Mariano and Clark-West."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy.optimize import nnls
from . import cases as C
from .purge_util import fred, read_res

VARS = ["y10", "equities", "dollar"]
ORIENT = np.array([1.0, -1.0, 1.0])             # sign so that a rise is a tightening (= sign of the market weights)
HORIZONS = (6, 12, 24)
FIRST, SAMPLE0 = "1995-01", "1976-03"
BLOCK = 24
OUTCOMES = {"ugap": +1, "payroll": -1, "gdp": -1, "corepce": -1, "recession": +1}   # sign of the expected effect of tightening (constrains the activity-fitted weights)


def covid(p, lo="2020-01", hi="2021-03"):
    return (p >= pd.Period(lo, "M")) & (p <= pd.Period(hi, "M"))


def monthly_log(name, quarterly=False):
    s = fred(name)
    if quarterly:                                # quarter value in the middle month, log-linear interpolation inside, no extrapolation
        s.index = pd.PeriodIndex([p.asfreq("M", "s") + 1 for p in s.index.to_period("Q")], freq="M")
        return np.log(s).reindex(pd.period_range(s.index[0], s.index[-1], freq="M")).interpolate()
    s.index = s.index.to_period("M"); return np.log(s)


def outcomes(D, h):
    """For each outcome: y(t+h), own-lag control at t (None for recession), and a mask of usable origins t."""
    idx = pd.period_range("1958-01", "2026-12", freq="M"); out = {}
    ug = D.u_gap.reindex(idx)
    out["ugap"] = (ug.shift(-h), ug, ~(covid(idx) | covid(idx + h)))
    wide = ~(covid(idx, "2020-01", "2022-03") | covid(idx + h, "2020-01", "2022-03"))
    for nm, lg in (("payroll", monthly_log("PAYEMS")), ("gdp", monthly_log("GDPC1", True)), ("corepce", monthly_log("PCEPILFE"))):
        g = (100 * (lg - lg.shift(12))).reindex(idx); out[nm] = (g.shift(-h), g, wide)
    rec = fred("USREC"); rec.index = rec.index.to_period("M"); rec = rec.reindex(idx)
    fwd = pd.concat([rec.shift(-k) for k in range(1, h + 1)], axis=1)
    out["recession"] = (fwd.max(axis=1).where(fwd.notna().all(axis=1)), None, (rec == 0) & ~covid(idx, "2020-01", "2021-03"))
    return out


def three_vars(D, case):
    return C.demean(C.inputs(D, case)[VARS])


def fixed_sets(D, case, mkt_w, fr_w):
    """Fixed-weight indexes on the three variables, plus full indexes as given."""
    Z = three_vars(D, case); I = read_res(f"indexes_{case}.csv")
    return {"MKT": Z @ mkt_w, "FRBUS3": Z @ fr_w, "GS": I.gs, "FRBUS_full": I.frbus, "NFCI": I.nfci, "ANFCI": I.anfci}, I, Z


def to_form(x, form):
    return x if form == "level" else x - x.shift(12)


def recursive_forecasts(J, y, own, valid, fixed, Zo, h, origins, sign):
    """Expanding-window forecasts of y(t+h) at each origin: baseline (constant + own lag), each fixed index added, and three re-estimated sets
    (PC1 first principal component, EQ equal-weight standardised, ACT sign-constrained least-squares weights)."""
    Zv = Zo.reindex(J).values; names = list(fixed); F = {k: fixed[k].reindex(J).values for k in names}
    ov = own.reindex(J).values if own is not None else None
    yv = y.reindex(J).values
    ok = pd.Series(np.asarray(valid), index=pd.period_range("1958-01", "2026-12", freq="M")).reindex(J).values & ~np.isnan(yv) & (~np.isnan(ov) if ov is not None else True)
    for k in names:
        ok = ok & ~np.isnan(F[k])
    ok = ok & ~np.isnan(Zv).any(axis=1)
    res = {k: [] for k in ["base"] + names + ["PC1", "EQ", "ACT"]}; act = []; tl = []
    pos0 = {p: i for i, p in enumerate(J)}
    for t in origins:
        i = pos0[t]
        if not ok[i]:
            continue
        tr = np.where(ok[: i - h + 1])[0]
        if len(tr) < 120:
            continue

        def design(extra):
            cols = [np.ones(len(tr))] + ([ov[tr]] if ov is not None else []) + ([e[tr] for e in extra] if extra else [])
            row = [1.0] + ([ov[i]] if ov is not None else []) + ([e[i] for e in extra] if extra else [])
            return np.column_stack(cols), np.array(row)

        def fc(extra):
            A, r = design(extra); b = np.linalg.lstsq(A, yv[tr], rcond=None)[0]; return r @ b
        res["base"].append(fc(None))
        for k in names:
            res[k].append(fc([F[k]]))
        Zh = Zv[: i + 1]; fin = ~np.isnan(Zh).any(axis=1); mu = Zh[fin].mean(0); sd = Zh[fin].std(0, ddof=1); Zs = (Zv - mu) / sd
        R = np.corrcoef(Zs[: i + 1][fin].T); ev, V = np.linalg.eigh(R); v = V[:, -1]; v = v if v.sum() > 0 else -v
        res["PC1"].append(fc([Zs @ v])); res["EQ"].append(fc([Zs.mean(axis=1)]))
        A, r = design(None); P = A @ np.linalg.pinv(A)
        w, _ = nnls(Zs[tr] - P @ Zs[tr], sign * (yv[tr] - P @ yv[tr]))
        b0 = np.linalg.lstsq(A, yv[tr] - sign * (Zs[tr] @ w), rcond=None)[0]
        res["ACT"].append(r @ b0 + sign * (Zs[i] @ w))
        act.append(yv[i]); tl.append(t)
    out = {k: np.array(v) for k, v in res.items()}; out["actual"] = np.array(act); out["t"] = tl
    return out


def haclag(h):
    return max(h, 12)


def dm(d, lag):
    return float(sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lag}).tvalues[0])


def cw(e0, e1, f0, f1, lag):
    """Clark-West adjusted loss differential, baseline (0) against the larger model (1); positive t favours the model."""
    return dm(e0 ** 2 - (e1 ** 2 - (f0 - f1) ** 2), lag)


def nnls_shares(Zs, y, own, sign):
    A = np.column_stack([np.ones(len(y))] + ([own] if own is not None else [])); P = A @ np.linalg.pinv(A)
    w, _ = nnls(Zs - P @ Zs, sign * (y - P @ y)); s = w.sum()
    return (w / s if s > 0 else np.full(3, np.nan)), w
