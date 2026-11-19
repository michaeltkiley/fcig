"""Note B's announcement sample, policy-news factor and market-index weights (FS_QA FS-A75, 16 Nov 2026).

Same method as Note A (fci_note; code vendored in lib/noteA.py): the Nakamura-Steinsson policy-news factor is the first principal component of the
announcement-window changes in MP1, MP2, ED2, ED3, ED4 (USMPD monetary-event windows), and the weights are the one-factor GLS weights of the 10-year yield,
S&P 500 and dollar window changes on that factor. Note B differs from Note A in two respects, so that every window regression in the note uses
one sample and one specification:
  1. Sample: the announcements used everywhere in Note B (factor, weights, window responses, daily model): from January 1996, on a trading day with
     a previous trading day and WINDOW_DAYS trading days of daily data after it (252 announcements, 31 Jan 1996 to 29 Jul 2026, with daily data to
     30 Oct 2026; Note A also uses 16 Sep 2026).
  2. Intercept: the factor is scaled so that the OLS slope, with an intercept, of the 2-year window change on the factor is 1 (Note A: through the
     origin). The weight regressions have an intercept (as in Note A). Hence, on this sample, a unit of the factor raises the 2-year yield 1 pp and the
     market index 1 unit: both are in 2-year-yield units."""
import numpy as np, pandas as pd
from .paths import DATA
from . import noteA

WINDOW_DAYS = 63                                    # an event needs this many trading days after it (the longest daily path of the model)
_d2 = pd.read_csv(DATA / "DGS2.csv")
CAL = pd.Series(_d2.iloc[:, 1].values.astype(float), index=pd.to_datetime(_d2.iloc[:, 0])).dropna().index      # trading-day calendar (days with a 2-year yield)

def slope(y, x):
    """OLS slope of y on x with an intercept."""
    x = np.asarray(x, float) - np.mean(x); return float(np.sum((np.asarray(y, float) - np.mean(y)) * x) / np.sum(x * x))

def ns_factor(ev):
    """First principal component of MP1, MP2, ED2, ED3, ED4 (as in Note A), signed to raise ED4, scaled so that its slope (with an intercept) on the
    2-year window change is 1."""
    U, S, _ = np.linalg.svd(ev[["MP1", "MP2", "ED2", "ED3", "ED4"]].values, full_matrices=False)
    f = U[:, 0] * S[0]
    if f @ ev.ED4.values < 0: f = -f
    return f * slope(ev.UST2Y.values, f)

def events():
    """Note A's USMPD monetary events restricted to Note B's sample, with Note B's factor in column `ns`."""
    ev = noteA.events().drop(columns="ns"); d = ev.Date.dt.normalize(); pos = {x: i for i, x in enumerate(CAL)}; p = d.map(pos)
    ok = (p.notna() & (p >= 1) & (p + WINDOW_DAYS < len(CAL)) & (d >= "1996-01-01")).values
    ev = ev[ok].reset_index(drop=True); ev["ns"] = ns_factor(ev)
    return ev

def weights(ev, rows=None):
    """One-factor GLS weights (noteA.gls_weights, intercept in each regression) on the events `rows` (default: all of `ev`), with the factor of `ev`."""
    rows = np.ones(len(ev), bool) if rows is None else np.asarray(rows)
    return noteA.gls_weights(ev.loc[rows, ["UST10Y", "SP500", "DXY"]].values, ev.ns.values[rows])
