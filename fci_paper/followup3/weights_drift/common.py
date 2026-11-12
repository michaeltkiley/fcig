"""Weights drift (Note A; no FOMC-window identification beyond the already-built announcement data used by replication/02_weights.py).
PRE-SPECIFIED DESIGN (before any estimate was looked at):
 weights  : lib.indexes gls_weights on the NS factor, factor re-computed (SVD + 2y scaling) inside each window, exactly as replication/02_weights.py
 paths    : expanding window, first estimate at the 80th announcement (check: 100th), re-estimated at every announcement; 20-year rolling window of announcements, first window ending 2016-01
 bands    : announcement-resampling bootstrap, 500 draws (seed config.SEED), at a coarse grid (year ends 2006..2025 plus the last date), for each window type
 verdict  : (i) point path inside the baseline full-sample 90% bootstrap band (weights_boot.csv 5-95) at every date after 2010, per weight;
            (ii) expanding-window flows correlate > 0.9 with baseline flows; (iii) bands at the grid date vs baseline band (width ratio)
 index    : pseudo-real-time market index in nominal, real, r* steps: month-t weight = latest expanding estimate with announcements through month t (first estimate before that);
            X demeaned over 1973-2026 as in the baseline (not real time); flows: forward impetus with baseline Phi and with Phi re-estimated by the p=12 VAR on the pseudo-RT index, and 12-month change
 unit     : scale of the raw NS factor (loading of the 2y yield on the first PC) and the per-unit-of-2y responses over the same windows
 tests    : none formal; descriptive. 
"""
import sys, numpy as np, pandas as pd
from pathlib import Path
HERE = Path(__file__).resolve().parent
REP = HERE.parent.parent / "replication"
sys.path.insert(0, str(REP))
from lib import indexes as I, data, cases, var
from lib.config import RES, SEED
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
RAW = I.events_raw()
MIN_N = 80
def est(df):
    f = I.ns_factor(df)
    w, psi, se = I.gls_weights(df[["UST10Y", "SP500", "DXY"]].values, f)
    X = df[["MP1", "MP2", "ED2", "ED3", "ED4"]].values
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    raw = U[:, 0] * S[0]
    if raw @ df.ED4.values < 0: raw = -raw
    load = (raw @ df.UST2Y.values) / (raw @ raw)      # pp of 2y per unit of raw factor: the scale
    return w, psi, load, f.std()
