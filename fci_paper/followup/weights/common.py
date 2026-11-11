"""Shared code: data, weight sets on the three market variables, outcomes, and recursive forecasts.
Reads ../../replication/{data,results} and ../data. Writes nothing outside this folder (bytecode off)."""
import sys, warnings
sys.dont_write_bytecode = True
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy.optimize import nnls
warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
REP = HERE.parents[1] / "replication"
sys.path.insert(0, str(REP))
from lib import cases as C                      # noqa: E402  (builds the inputs at each step)

RES_IN = REP / "results"; EXT = HERE.parent / "data"; OUT = HERE / "results"; OUT.mkdir(exist_ok=True)
VARS = ["y10", "equities", "dollar"]
ORIENT = np.array([1.0, -1.0, 1.0])             # sign so that a rise is a tightening (pre-specified, = sign of the market weights)
HORIZONS = (6, 12, 24)
FIRST, SAMPLE0 = "1995-01", "1976-03"           # first forecast origin; first training row (as lib/lp.py)
NBOOT, BLOCK, SEED = 500, 24, 20261112
# outcome: sign of the expected effect of tightening on the outcome (used only to sign-constrain the activity-fitted weights)
OUTCOMES = {"ugap": +1, "payroll": -1, "gdp": -1, "corepce": -1, "recession": +1}


def per(i): return pd.PeriodIndex(pd.to_datetime(i), freq="M")


def load_monthly():
    d = pd.read_csv(RES_IN / "data_monthly.csv", index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def ext(name):
    d = pd.read_csv(EXT / f"{name}.csv"); s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    return s


def monthly_log(name, quarterly=False):
    s = ext(name)
    if quarterly:                                # quarter value placed in the middle month, log-linear interpolation inside, no extrapolation
        s.index = pd.PeriodIndex([p.asfreq("M", "s") + 1 for p in s.index.to_period("Q")], freq="M")
        full = pd.period_range(s.index[0], s.index[-1], freq="M")
        return np.log(s).reindex(full).interpolate()
    s.index = s.index.to_period("M"); return np.log(s)


def read_idx(case):
    d = pd.read_csv(RES_IN / f"indexes_{case}.csv", index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def covid(p, lo="2020-01", hi="2021-03"): return (p >= pd.Period(lo, "M")) & (p <= pd.Period(hi, "M"))


def outcomes(D, h):
    """For each outcome: y(t+h), own-lag control at t (None for recession), and a mask of usable origins t. All on a monthly PeriodIndex."""
    idx = pd.period_range("1958-01", "2026-12", freq="M"); out = {}
    ug = D.u_gap.reindex(idx)
    m = ~(covid(idx) | covid(idx + h)); out["ugap"] = (ug.shift(-h), ug, m)
    wide = ~(covid(idx, "2020-01", "2022-03") | covid(idx + h, "2020-01", "2022-03"))
    for nm, lg in (("payroll", monthly_log("PAYEMS")), ("gdp", monthly_log("GDPC1", True)), ("corepce", monthly_log("PCEPILFE"))):
        g = (100 * (lg - lg.shift(12))).reindex(idx); out[nm] = (g.shift(-h), g, wide)
    rec = ext("USREC"); rec.index = rec.index.to_period("M"); rec = rec.reindex(idx)
    fwd = pd.concat([rec.shift(-k) for k in range(1, h + 1)], axis=1)
    y = fwd.max(axis=1).where(fwd.notna().all(axis=1))
    out["recession"] = (y, None, (rec == 0) & ~covid(idx, "2020-01", "2021-03"))
    return out


def three_vars(D, case):
    X = C.inputs(D, case); Z = C.demean(X[VARS]); return Z


def fixed_sets(D, case, mkt_w, fr_w):
    """Fixed-weight indexes on the three variables (level form), plus the full indexes as given."""
    Z = three_vars(D, case); I = read_idx(case); S = {}
    S["MKT"] = Z @ mkt_w; S["FRBUS3"] = Z @ fr_w
    S["GS"] = I.gs; S["FRBUS_full"] = I.frbus; S["NFCI"] = I.nfci; S["ANFCI"] = I.anfci
    return S, I, Z


def to_form(x, form): return x if form == "level" else x - x.shift(12)


def recursive_forecasts(J, y, own, valid, fixed, Zo, h, origins, sign, with_dyn=True):
    """J: PeriodIndex of rows (array positions). y, own (or None), valid (bool) at origin t. fixed: dict name -> series (already in the form).
    Zo: oriented three-variable frame in the form (rows over the full sample). Returns dict name -> array of forecasts, plus actuals; baseline included."""
    n = len(J); Zv = Zo.reindex(J).values; names = list(fixed); F = {k: fixed[k].reindex(J).values for k in names}
    ov = own.reindex(J).values if own is not None else None
    yv = y.reindex(J).values
    ok = pd.Series(np.asarray(valid), index=pd.period_range('1958-01', '2026-12', freq='M')).reindex(J).values & ~np.isnan(yv) & (~np.isnan(ov) if ov is not None else True)
    for k in names: ok = ok & ~np.isnan(F[k])
    ok = ok & ~np.isnan(Zv).any(axis=1)
    res = {k: [] for k in ["base"] + names + (["PC1", "EQ", "ACT"] if with_dyn else [])}; act = []; tl = []; wts = []
    pos0 = {p: i for i, p in enumerate(J)}
    for t in origins:
        i = pos0[t]
        if not ok[i]: continue
        tr = np.where(ok[: i - h + 1])[0]
        if len(tr) < 120: continue
        def design(extra):
            cols = [np.ones(len(tr))] + ([ov[tr]] if ov is not None else []) + ([e[tr] for e in extra] if extra else [])
            row = [1.0] + ([ov[i]] if ov is not None else []) + ([e[i] for e in extra] if extra else [])
            return np.column_stack(cols), np.array(row)
        def fc(extra):
            A, r = design(extra); b = np.linalg.lstsq(A, yv[tr], rcond=None)[0]; return r @ b
        res["base"].append(fc(None))
        for k in names: res[k].append(fc([F[k]]))
        if with_dyn:
            Zh = Zv[: i + 1]; fin = ~np.isnan(Zh).any(axis=1); mu = Zh[fin].mean(0); sd = Zh[fin].std(0, ddof=1); Zs = (Zv - mu) / sd
            R = np.corrcoef(Zs[: i + 1][fin].T); ev, V = np.linalg.eigh(R); v = V[:, -1]; v = v if v.sum() > 0 else -v
            res["PC1"].append(fc([Zs @ v])); res["EQ"].append(fc([Zs.mean(axis=1)]))
            # activity-fitted: sign-constrained least squares on the oriented standardized variables, own lag and constant partialled out
            A, r = design(None); P = A @ np.linalg.pinv(A)
            yy = sign * (yv[tr] - P @ yv[tr]); XX = Zs[tr] - P @ Zs[tr]
            w, _ = nnls(XX, yy)
            b0 = np.linalg.lstsq(A, yv[tr] - sign * (Zs[tr] @ w), rcond=None)[0]
            res["ACT"].append(r @ b0 + sign * (Zs[i] @ w))
            wts.append((str(t), *w))
        act.append(yv[i]); tl.append(t)
    out = {k: np.array(v) for k, v in res.items()}; out["actual"] = np.array(act); out["t"] = tl; out["wts"] = wts
    return out


HACLAG = lambda h: max(h, 12)


def dm(d, lag):
    """t-statistic of the mean of d (HAC, Bartlett)."""
    r = sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": lag}); return float(r.tvalues[0])


def cw(e0, e1, f0, f1, lag):
    """Clark-West adjusted loss differential, baseline (0) against the larger model (1); one-sided test, positive t favours the model."""
    d = e0 ** 2 - (e1 ** 2 - (f0 - f1) ** 2); return dm(d, lag)
