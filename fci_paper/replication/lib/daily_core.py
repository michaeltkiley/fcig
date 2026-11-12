"""Helpers for step 20 (announcement against non-announcement movements at the same horizon, daily data). No network, no files written."""
import numpy as np, pandas as pd
from .config import DATA
from . import indexes as I


def load_daily(start="1996-01-01", end="2026-09-30"):
    """Daily levels on dates where all three series exist: y10 (pp), equities (100 ln CAPE), dollar (100 ln nominal broad dollar; DTWEXB changes before 2006, DTWEXBGS from 2006).
    Returns DataFrame indexed by date with columns y10, equities, dollar."""
    rd = lambda f, c: pd.read_csv(DATA / "daily" / f, na_values=".", index_col=0, parse_dates=True)[c].dropna()
    y = rd("DGS10.csv", "DGS10"); new = rd("DTWEXBGS.csv", "DTWEXBGS"); old = rd("DTWEXB.csv", "DTWEXB")
    cape = pd.read_csv(DATA / "gs_daily.csv", parse_dates=["date"]).set_index("date").cape.dropna()
    d100 = lambda s: 100 * np.log(s).diff()
    usd_ch = pd.concat([d100(old).loc[:"2005-12-31"], d100(new).loc["2006-01-01":]]).dropna()
    # first change of the new series (2006-01-03 against 2006-01-02) uses the new series itself
    usd = usd_ch.cumsum()
    df = pd.concat([y.rename("y10"), (100 * np.log(cape)).rename("equities"), usd.rename("dollar")], axis=1, join="inner").dropna()
    return df.loc[start:end]


def day_flags(dates):
    """ann: scheduled-meeting dates kept by lib.indexes.events_raw. excl: March-April 2020 and the dates of USMPD events dropped by events_raw (unscheduled no-move)."""
    raw = pd.read_csv(DATA / "usmpd_monetary_events.csv", parse_dates=["Date"])
    ev = I.events_raw()
    ann = pd.DatetimeIndex(ev.Date)
    dropped = pd.DatetimeIndex(raw.Date[~raw.Date.isin(ann)])
    a = dates.isin(ann); ex = dates.isin(dropped) | ((dates >= "2020-03-01") & (dates <= "2020-04-30"))
    return np.asarray(a & ~ex), np.asarray(ex & ~a)


def stats(D, m):
    """Mean |D|, mean |m|, ratio of means, sd ratio, and shares of windows with |D| above fractions of |m|."""
    a, am = np.abs(D), np.abs(m)
    return {"mean_abs_D": a.mean(), "mean_abs_market": am.mean(), "ratio": a.mean() / am.mean(), "sd_ratio": D.std() / m.std(),
            "share_gt_quarter": (a > 0.25 * am).mean(), "share_gt_half": (a > 0.5 * am).mean(), "share_gt_one": (a > am).mean()}


def mbb(T, L, rng):
    L = max(1, min(L, T)); nb = int(np.ceil(T / L)); st = rng.integers(0, T - L + 1, nb)
    return (st[:, None] + np.arange(L)).ravel()[:T]


def ci(a, lo=5, hi=95):
    a = np.asarray(a, float)
    return float(np.nanpercentile(a, lo)), float(np.nanpercentile(a, hi))
