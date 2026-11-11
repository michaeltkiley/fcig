"""Shared design: outcomes, predictors, fits. Reads ../../replication/{data,results} and ../data. Writes only here (out/)."""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
REP = HERE.parent.parent / "replication"
sys.path.insert(0, str(REP))
from lib import data as D  # package loader (unemployment gap)
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
RES, FD = REP / "results", HERE.parent / "data"
STEPS = ("nominal", "real", "rstar")
HORIZONS = (6, 12, 24)
FIRST_OOS, LAST_END = "1995-01", "2026-10"
SUBS = {"1995-2007": ("1995-01", "2007-12"), "2008-16": ("2008-01", "2016-12"), "2017-19": ("2017-01", "2019-12"), "2021-26": ("2021-01", "2026-12")}
START = "1976-03"
FAMILIES = {  # name -> (file kind, column)
    "Market level": ("idx", "market"), "Market forward impetus": ("flow", "forward_impetus"), "GS level": ("idx", "gs"),
    "FRB/US level": ("idx", "frbus"), "FRB/US growth impetus": ("idx", "frbus_gi_hp"), "FCI-G 1yr": ("idx", "fcig_1yr"), "FCI-G 3yr": ("idx", "fcig_3yr")}
REFS = {"NFCI": "nfci", "ANFCI": "anfci"}  # no step: identical at every step

def covid(p): return p.year == 2020 or (p.year == 2021 and p.month <= 3)

def read(f): 
    d = pd.read_csv(f, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d

def predictors():
    X = {}
    for s in STEPS:
        I = read(RES / f"indexes_{s}.csv"); F = read(RES / f"flow_{s}_p12.csv")
        for nm, (k, c) in FAMILIES.items(): X[(nm, s)] = (I if k == "idx" else F)[c]
    I = read(RES / "indexes_rstar.csv")
    for nm, c in REFS.items(): X[(nm, "ref")] = I[c]
    return X

def fred(name):
    d = pd.read_csv(FD / f"{name}.csv"); s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    return s

def monthly(name):
    s = fred(name); s.index = s.index.to_period("M"); return s

def outcome(name, h):
    """Returns DataFrame indexed by origin month with y (outcome), c (own-lag control), ok (not touching Covid window), and step (months between origins)."""
    u = D.load().u_gap
    mi = pd.period_range("1972-01", LAST_END, freq="M")
    if name == "ugap":
        J = pd.DataFrame({"y": u.shift(-h), "c": u}).reindex(mi)
        ok = [not (covid(t + h) or covid(t)) for t in J.index]  # package rule
        step = 1
    elif name in ("payroll", "corepce"):
        s = np.log(monthly("PAYEMS" if name == "payroll" else "PCEPILFE")) * 100
        s = s.reindex(mi)
        J = pd.DataFrame({"y": s.shift(-h) - s, "c": s - s.shift(12)}).reindex(mi)
        ok = [not any(covid(t + k) for k in range(-12, h + 1)) for t in J.index]; step = 1
    elif name == "gdp":
        g = fred("GDPC1"); q = g.index.to_period("Q"); lg = pd.Series(np.log(g.values) * 100, index=q.asfreq("M", "e"))  # quarter-end month
        qi = lg.index; nq = h // 3
        J = pd.DataFrame({"y": lg.shift(-nq) - lg, "c": lg - lg.shift(4)}).reindex(mi)
        ok = [not any(covid(t + k) for k in range(-12, h + 1)) for t in J.index]; step = 3
        J.loc[[t for t in J.index if t.month % 3 != 0]] = np.nan
    elif name == "recession":
        r = monthly("USREC").reindex(mi)
        fut = pd.concat([r.shift(-k) for k in range(1, 13)], axis=1)
        y = fut.max(axis=1).where(fut.notna().all(axis=1))
        J = pd.DataFrame({"y": y, "c": r}).reindex(mi)
        ok = [not any(covid(t + k) for k in range(0, 13)) for t in J.index]; step = 1
    J["ok"] = ok; J.attrs["step"] = step
    return J

def sample(name, h, xs):
    """Common sample over the predictors xs (list of Series): rows with all non-missing, ok, from START."""
    J = outcome(name, h)
    for i, x in enumerate(xs): J[f"x{i}"] = x.reindex(J.index)
    J = J[J.ok].loc[START:]
    return J.drop(columns="ok").dropna(), J.attrs["step"] if hasattr(J, "attrs") else 1

def logit_fit(X, y, ridge=1e-6, it=50):
    b = np.zeros(X.shape[1]); R = np.eye(X.shape[1]) * ridge; R[0, 0] = 0
    for _ in range(it):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30))); W = p * (1 - p) + 1e-9
        g = X.T @ (y - p) - R @ b; H = (X * W[:, None]).T @ X + R
        d = np.linalg.solve(H, g); b = b + d
        if np.abs(d).max() < 1e-8: break
    return b

def loglik(X, y, b):
    z = np.clip(X @ b, -30, 30); return float((y * z - np.log1p(np.exp(z))).sum())

def prob(X, b): return 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
