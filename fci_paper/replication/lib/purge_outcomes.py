"""Step 14 helpers: outcomes (unemployment gap, payroll, GDP, core PCE, recession within 12 months), predictors by step, logit."""
import numpy as np, pandas as pd
from . import data as D
from .purge_util import covid, fred, monthly, read_res

STEPS = ("nominal", "real", "rstar")
HORIZONS = (6, 12, 24)
FIRST_OOS, LAST_END, START = "1995-01", "2026-10", "1976-03"
SUBS = {"1995-2007": ("1995-01", "2007-12"), "2008-16": ("2008-01", "2016-12"), "2017-19": ("2017-01", "2019-12"), "2021-26": ("2021-01", "2026-12")}
FAMILIES = {"Market level": ("idx", "market"), "Market forward impetus": ("flow", "forward_impetus"), "GS level": ("idx", "gs"),
            "FRB/US level": ("idx", "frbus"), "FRB/US growth impetus": ("idx", "frbus_gi_hp"), "FCI-G 1yr": ("idx", "fcig_1yr"), "FCI-G 3yr": ("idx", "fcig_3yr")}
REFS = {"NFCI": "nfci", "ANFCI": "anfci"}


def predictors():
    X = {}
    for s in STEPS:
        I = read_res(f"indexes_{s}.csv"); F = read_res(f"flow_{s}_p12.csv")
        for nm, (k, c) in FAMILIES.items():
            X[(nm, s)] = (I if k == "idx" else F)[c]
    I = read_res("indexes_rstar.csv")
    for nm, c in REFS.items():
        X[(nm, "ref")] = I[c]
    return X


def outcome(name, h, u):
    """DataFrame indexed by origin month: y (outcome), c (own-lag control), ok (window clear of the Covid months)."""
    mi = pd.period_range("1972-01", LAST_END, freq="M")
    if name == "ugap":
        J = pd.DataFrame({"y": u.shift(-h), "c": u}).reindex(mi)
        ok = [not (covid(t + h) or covid(t)) for t in J.index]
    elif name in ("payroll", "corepce"):
        s = (np.log(monthly("PAYEMS" if name == "payroll" else "PCEPILFE")) * 100).reindex(mi)
        J = pd.DataFrame({"y": s.shift(-h) - s, "c": s - s.shift(12)}).reindex(mi)
        ok = [not any(covid(t + k) for k in range(-12, h + 1)) for t in J.index]
    elif name == "gdp":
        g = fred("GDPC1"); q = g.index.to_period("Q"); lg = pd.Series(np.log(g.values) * 100, index=q.asfreq("M", "e"))
        J = pd.DataFrame({"y": lg.shift(-(h // 3)) - lg, "c": lg - lg.shift(4)}).reindex(mi)
        ok = [not any(covid(t + k) for k in range(-12, h + 1)) for t in J.index]
        J.loc[[t for t in J.index if t.month % 3 != 0]] = np.nan
    elif name == "recession":
        r = monthly("USREC").reindex(mi)
        fut = pd.concat([r.shift(-k) for k in range(1, 13)], axis=1)
        J = pd.DataFrame({"y": fut.max(axis=1).where(fut.notna().all(axis=1)), "c": r}).reindex(mi)
        ok = [not any(covid(t + k) for k in range(0, 13)) for t in J.index]
    J["ok"] = ok
    return J


def sample(name, h, xs, u):
    """Common sample over the predictors xs: rows with everything non-missing, clear of Covid, from START."""
    J = outcome(name, h, u)
    for i, x in enumerate(xs):
        J[f"x{i}"] = x.reindex(J.index)
    return J[J.ok].loc[START:].drop(columns="ok").dropna()


def logit_fit(X, y, ridge=1e-6, it=50):
    b = np.zeros(X.shape[1]); R = np.eye(X.shape[1]) * ridge; R[0, 0] = 0
    for _ in range(it):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30))); W = p * (1 - p) + 1e-9
        g = X.T @ (y - p) - R @ b; H = (X * W[:, None]).T @ X + R
        d = np.linalg.solve(H, g); b = b + d
        if np.abs(d).max() < 1e-8:
            break
    return b


def loglik(X, y, b):
    z = np.clip(X @ b, -30, 30); return float((y * z - np.log1p(np.exp(z))).sum())


def prob(X, b):
    return 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
