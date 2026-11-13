"""Daily data, the weekday calendar, and the policy announcements (events) with their 30-minute windows.
Calendar CALW: weekdays from 1972, on which the daily financial block is defined; daily series are forward-filled up to 3 days."""
import numpy as np, pandas as pd
from .paths import DATA, OUT
from . import noteA

WINDOW_DAYS = 63                                    # an event needs this many trading days after it (the longest daily path in the original design)
HAR = (1, 5, 22, 66)                                # averaging windows (days) of the daily HAR block
CALW = pd.bdate_range("1972-01-03", "2026-10-30")

def fred_daily(name):
    d = pd.read_csv(DATA / f"{name}.csv")
    return pd.Series(d.iloc[:, 1].values.astype(float), index=pd.to_datetime(d.iloc[:, 0])).dropna()

def interp_monthly(s):
    """Monthly (PeriodIndex) series -> smooth daily series on CALW by linear interpolation between mid-month dates."""
    s = s.dropna(); mid = pd.to_datetime([p.to_timestamp() + pd.Timedelta(days=14) for p in s.index])
    return pd.Series(np.interp(CALW.asi8, mid.asi8, s.values, left=np.nan, right=s.values[-1]), index=CALW)

W = pd.read_csv(OUT / "market_weights.csv", index_col=0).weight
d2, d10 = fred_daily("DGS2"), fred_daily("DGS10")
CAL = d2.index                                      # trading-day calendar (days with a 2-year yield)
lev = pd.read_csv(DATA / "gs_daily_levels.csv", parse_dates=["date"]).set_index("date")         # daily CAPE and dollar levels (see data/SOURCES.md)
DAILY = pd.DataFrame({"y2": d2, "y10": d10}, index=CAL)
DAILY["idx"] = (W["y10"] * d10 + W["equities"] * 100 * np.log(lev.x_cape) + W["dollar"] * 100 * np.log(lev.x_usd)).reindex(CAL)
W_JK = pd.read_csv(OUT / "market_weights_jk.csv", index_col=0).weight              # weights estimated on the Jarocinski-Karadi subset (robustness)
DAILY["idx_jk"] = (W_JK["y10"] * d10 + W_JK["equities"] * 100 * np.log(lev.x_cape) + W_JK["dollar"] * 100 * np.log(lev.x_usd)).reindex(CAL)
DAILY = DAILY.ffill(limit=3)                        # DAILY.idx = the nominal market index at daily frequency (idx_jk: with the Jarocinski-Karadi-subset weights)
_baa = fred_daily("DBAA")
BAA = (_baa - d10).reindex(CAL).ffill(limit=3)     # daily Moody's Baa yield less the 10-year Treasury yield, pp (robustness: credit)

POL = d2.reindex(CALW).ffill(limit=3)               # daily 2-year yield on the weekday calendar
MON = CALW.to_period("M")

# ---------------------------------------------------------------- events
EV = noteA.events(); EV["d"] = EV.Date.dt.normalize()
POS = {d: i for i, d in enumerate(CAL)}
MONTH = pd.Series(CAL.to_period("M"), index=CAL); NB = MONTH.groupby(MONTH).transform("size")
EV["p"] = EV.d.map(POS)
EV["n"] = [NB.iloc[int(p)] if pd.notna(p) else np.nan for p in EV.p]                                                      # trading days in the event month
EV["k"] = [int((MONTH.iloc[:int(p) + 1] == MONTH.iloc[int(p)]).sum()) - 1 if pd.notna(p) else np.nan for p in EV.p]      # position of the event day in its month
EV["idx_win"] = W["y10"] * EV.UST10Y + W["equities"] * EV.SP500 + W["dollar"] * EV.DXY                                    # index change in the window
EV["idx_win_jk"] = W_JK["y10"] * EV.UST10Y + W_JK["equities"] * EV.SP500 + W_JK["dollar"] * EV.DXY                       # the same with the Jarocinski-Karadi-subset weights
GOOD = (EV.p.notna() & (EV.p >= 1) & (EV.p + WINDOW_DAYS < len(CAL)) & (EV.d >= "1996-01-01")).values

# ---------------------------------------------------------------- alternative surprises (robustness): the model reads the surprise from EV.ns
EV["ns_orig"] = EV.ns.copy()
_bs = pd.read_csv(DATA / "bauer_swanson_mps.csv", parse_dates=["Date"]).groupby("Date").MPS_ORTH.sum()
SURPRISES = {"ns": EV.ns_orig, "bs": pd.Series(EV.d.map(_bs).values, index=EV.index),            # Bauer-Swanson (2023) orthogonalized surprise (FOMC announcements 1988-2019; later events dropped)
             "jk": EV.ns_orig.where(np.sign(EV.UST2Y) * np.sign(EV.SP500) < 0)}                    # Jarocinski-Karadi (2020) sign restriction: keep NS when the 2-year and the S&P 500 move in opposite directions
CURRENT = ["ns"]
def use_surprise(name):
    """Switch the surprise used everywhere (events used, window impact, bootstrap positions)."""
    EV["ns"] = SURPRISES[name].values; CURRENT[0] = name

def event_index():
    """Announcements used: inside the daily calendar with a full window, from January 1996 (the first announcement with all window variables), with a policy-news value (252)."""
    return np.where(GOOD & ~EV.ns.isna().values)[0]

def window_impact(idx, col="idx_win"):
    """Window response per unit shock: OLS slope on the shock of the 30-minute change in the 2-year yield (scaling variable) and in the market index.
    Returns [2-year, index] scaled so that the 2-year moves +1 pp; the index entry is the index's window move per +1 pp on the 2-year."""
    s = EV.ns.values[idx]; ok = ~np.isnan(s); idx = idx[ok]; x = s[ok] - s[ok].mean()
    slope = lambda col: float(np.sum((EV[col].values[idx] - EV[col].values[idx].mean()) * x) / np.sum(x * x))
    return np.array([1.0, slope(col) / slope("UST2Y")])

def baa_impact(idx):
    """Announcement-day response of the Baa-10-year spread per +1 pp on the 2-year yield in the window: OLS slope on the surprise of the one-day change in the spread
    (close before to close of the announcement day; the spread has no intraday series) over the window slope of the 2-year yield."""
    s = EV.ns.values[idx]; ok = ~np.isnan(s); idx = idx[ok]; x = s[ok] - s[ok].mean()
    b = BAA.values; pp = EV.p.values[idx].astype(int); y = b[pp] - b[pp - 1]; g = ~np.isnan(y)
    num = float(np.sum((y[g] - y[g].mean()) * x[g]) / np.sum(x[g] ** 2))
    y2 = EV.UST2Y.values[idx]; return num / float(np.sum((y2 - y2.mean()) * x) / np.sum(x * x))

def window_impact_components(idx):
    """Window response of the three weighted components of the market index (10-year yield, equity valuation, dollar), per +1 pp on the 2-year yield:
    [1, w_y10 * slope(10-year), w_equities * slope(S&P 500), w_dollar * slope(DXY)] / slope(2-year); the last three sum to the index entry of window_impact."""
    s = EV.ns.values[idx]; ok = ~np.isnan(s); idx = idx[ok]; x = s[ok] - s[ok].mean()
    slope = lambda col: float(np.sum((EV[col].values[idx] - EV[col].values[idx].mean()) * x) / np.sum(x * x))
    return np.array([1.0, W["y10"] * slope("UST10Y") / slope("UST2Y"), W["equities"] * slope("SP500") / slope("UST2Y"), W["dollar"] * slope("DXY") / slope("UST2Y")])

def positions(idx):
    """Event-position bins within the month (days 0-3, 4-7, ..., 20-23): (mean position, mean trading days in the month, share of events)."""
    k = np.array([int(EV.k[i]) for i in idx]); n = np.array([int(EV.n[i]) for i in idx])
    out = []
    for lo, hi in [(0, 3), (4, 7), (8, 11), (12, 15), (16, 19), (20, 23)]:
        m = (k >= lo) & (k <= hi)
        if m.sum(): out.append((int(round(k[m].mean())), int(round(n[m].mean())), m.mean()))
    return out
