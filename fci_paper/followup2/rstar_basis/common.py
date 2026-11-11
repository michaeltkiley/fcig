"""Shared design for rstar_basis. Reads ../../replication/{data,results}; writes only to ./out.

PRE-SPECIFIED DESIGN (fixed before any estimate was looked at)
 series   : market, GS, FRB/US at the nominal, real and r*-gap (LW) steps = 9 series (indexes_<step>.csv); Kiley-r* market index for part B
 projection (A1): u(t+12)-u(t) on const, u(t), u(t)-u(t-12), and x(t) (level) or x(t)-x(t-12) (flow); x scaled by its full-sample sd;
            origins t from 1976-03 to 2025-09; any t whose window t-12..t+12 touches 2020-01..2021-03 is dropped (package rule); HAC(18)
 subperiods (origin dates): P1 1976-03..1989-12, P2 1990-01..2007-12, P3 2009-01..2019-12 (2008 and 2020-21 excluded), P4 2022-04..2025-09 (descriptive only)
 rolling  : 20-year windows (240 origin months), step 12 months (rows after the Covid drop; windows containing the gap are shorter in rows, not in calendar time)
 stability: (i) Wald equality of the index slope across P1-P3 (HAC 18), (ii) Wald equality of all coefficients across P1-P3 (Chow-type), (iii) sup-F for a
            single break in the index slope (15% trimming, breaks every 3 months) with p-values from a moving-block (24 months) residual bootstrap
            under stability, 499 draws, fixed regressors; dispersion = sd of the P1-P3 slopes (per full-sample sd of x), with block-bootstrap CI (within-period blocks)
 VAR (A2) : package VAR (u first, 12 lags, 1973 start) by subperiod 1973-89, 1990-2007, 2009-19; Phi(12) with 12-month block bootstrap (300 draws); P4 infeasible (68 months)
 B        : see 02_unit_restriction.py;  C: see 03_neutrality.py
"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
REP = HERE.parent.parent / "replication"
sys.path.insert(0, str(REP))
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
RES = REP / "results"
H = 12
START, LAST = "1976-03", "2025-09"
SUBS = {"P1_1976-89": ("1976-03", "1989-12"), "P2_1990-2007": ("1990-01", "2007-12"), "P3_2009-19": ("2009-01", "2019-12"), "P4_2022-25": ("2022-04", "2025-09")}
MAIN = ["P1_1976-89", "P2_1990-2007", "P3_2009-19"]
STEPS = ("nominal", "real", "rstar")
FAM = {"Market": "market", "GS": "gs", "FRBUS": "frbus"}

def covid(p): return p.year == 2020 or (p.year == 2021 and p.month <= 3)

def read(f):
    d = pd.read_csv(f, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d

DM = read(RES / "data_monthly.csv")
U = DM.u_gap

def index(step, col):
    return read(RES / f"indexes_{step}.csv")[col]

def all_series():
    out = {}
    for fam, col in FAM.items():
        for s in STEPS: out[(fam, s)] = index(s, col)
    return out

def keep(idx):
    return np.array([not any(covid(t + k) for k in range(-12, 13)) for t in idx])

def design(x, kind):
    """DataFrame: y, u, du12, x (kind 'level' or 'flow', unscaled) for origins START..LAST, Covid rule applied."""
    D = pd.DataFrame({"y": U.shift(-H) - U, "u": U, "du12": U - U.shift(12),
                      "x": x if kind == "level" else x - x.shift(12)}).loc[START:LAST]
    return D[keep(D.index)].dropna()

def ols(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ b; return b, e

def hac(X, e, L):
    """Newey-West (Bartlett) covariance of OLS coefficients."""
    n = len(e); XtXi = np.linalg.inv(X.T @ X); S = (X * e[:, None]).T @ (X * e[:, None])
    for l in range(1, L + 1):
        G = (X[l:] * e[l:, None]).T @ (X[:-l] * e[:-l, None]); S += (1 - l / (L + 1)) * (G + G.T)
    return XtXi @ S @ XtXi

def wald(b, V, R, r=None):
    from scipy import stats
    R = np.atleast_2d(R); r = np.zeros(R.shape[0]) if r is None else np.atleast_1d(r)
    d = R @ b - r; W = float(d @ np.linalg.solve(R @ V @ R.T, d)); return W, float(1 - stats.chi2.cdf(W, R.shape[0]))

def blocks(n, block, rng):
    nb = -(-n // block); return np.concatenate([np.arange(s, s + block) for s in rng.integers(0, n - block + 1, nb)])[:n] % n
