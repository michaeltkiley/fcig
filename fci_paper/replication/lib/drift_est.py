"""Helpers for step 16 (weights drift): the weight estimate inside one window of announcements, exactly as 02_weights.py, plus the scale of the raw policy-news factor."""
import numpy as np
from lib import indexes as I

MIN_N = 80                      # first expanding-window estimate shown: the 80th announcement (about 2006)


def est(df):
    """GLS weights and responses on the policy-news factor computed inside the window; returns (weights, responses, scale of raw factor, sd of the factor)."""
    f = I.ns_factor(df)
    w, psi, se = I.gls_weights(df[["UST10Y", "SP500", "DXY"]].values, f)
    X = df[["MP1", "MP2", "ED2", "ED3", "ED4"]].values
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    raw = U[:, 0] * S[0]
    if raw @ df.ED4.values < 0:
        raw = -raw
    load = (raw @ df.UST2Y.values) / (raw @ raw)      # pp of the 2-year yield per unit of the raw factor
    return w, psi, load, f.std()
