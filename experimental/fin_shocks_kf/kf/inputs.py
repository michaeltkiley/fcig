"""Inputs of the Kalman-filter version of Note B, built from data/ (new code; nothing imported from ../fin_shocks/).

Definitions follow Note B (../fin_shocks/baseline/lib/{daily,model}.py, read 13 Nov 2026):
- Weekday calendar CALW 1972-01-03 .. 2026-10-30; daily series forward-filled up to 3 days.
- Daily 2-year yield (FRED DGS2); daily nominal market index = w_y10 * DGS10 + w_eq * 100 ln CAPE + w_usd * 100 ln dollar (gs_daily_levels), on DGS2's trading days.
- Rate forms: nom = 2-year; real = less 2-year expected inflation (Cleveland, monthly, interpolated between mid-months); rstar = also less Laubach-Williams r*.
- Daily FCI in a step = daily nominal index + a smooth offset (interpolated between mid-months) so that its monthly average equals Note A's monthly index in that step.
- Monthly macro: unemployment gap (UNRATE less CBO NROU placed mid-quarter and interpolated; October 2025 interpolated), core PCE inflation (1200 x log difference of the monthly mean of PCEPILFE).
- Announcements: USMPD monetary events, unscheduled no-move events and March-April 2020 dropped; Nakamura-Steinsson policy news = first principal component of MP1, MP2, ED2-ED4 scaled to move the 2-year 1 pp.
Frozen inputs (data/frozen/, KF-A1): Note A's monthly indexes, the market weights, the monthly r* (LW) column of data_monthly.csv."""
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, FROZEN, OUT, RES = ROOT / "data", ROOT / "data" / "frozen", ROOT / "output", ROOT / "results"
CALW = pd.bdate_range("1972-01-03", "2026-10-30")
MONTHS = pd.period_range("1973-01", "2026-09", freq="M")
FILL = 3


def series_csv(name):
    d = pd.read_csv(DATA / f"{name}.csv")
    return pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()


def monthly_mean(s):
    return s.groupby(s.index.to_period("M")).mean()


def to_daily(m):
    """Monthly series (PeriodIndex) -> weekday series: linear between the 15th of each month; NaN before the first, last value held after the last."""
    m = m.dropna()
    x = pd.DatetimeIndex([p.to_timestamp() + pd.Timedelta(days=14) for p in m.index]).as_unit("ns").asi8
    return pd.Series(np.interp(CALW.as_unit("ns").asi8, x, m.values, left=np.nan, right=m.values[-1]), index=CALW)


def frozen_monthly(name, col):
    d = pd.read_csv(FROZEN / name, index_col=0)
    return pd.Series(d[col].values, index=pd.PeriodIndex(d.index, freq="M"))


# ---------------------------------------------------------------- monthly macro
def macro():
    u = monthly_mean(series_csv("UNRATE"))
    n = pd.read_csv(DATA / "NROU.csv")
    q = pd.Series(n.iloc[:, 1].values.astype(float), index=pd.PeriodIndex(pd.to_datetime(n.iloc[:, 0]), freq="Q"))
    nm = pd.Series(q.values, index=[p.asfreq("M", "s") + 1 for p in q.index])                      # middle month of the quarter
    nm = nm.reindex(pd.period_range(nm.index[0], "2026-09", freq="M")).interpolate(limit_area="inside").ffill()
    gap = (u - nm.reindex(u.index))
    gap = gap.reindex(pd.period_range(gap.index[0], "2026-09", freq="M")).interpolate(limit_area="inside")   # Oct 2025: no release
    pce = monthly_mean(series_csv("PCEPILFE"))
    pi = 1200 * np.log(pce).diff()
    return pd.DataFrame({"u": gap, "pi": pi}).reindex(MONTHS)


# ---------------------------------------------------------------- announcements
def announcements():
    d = pd.read_csv(DATA / "usmpd_monetary_events.csv", parse_dates=["Date"])
    d = d[~((d.Unscheduled == 1) & (d.MP1 == 0))]
    d = d[~((d.Date >= "2020-03-01") & (d.Date <= "2020-04-30"))]
    d = d.dropna(subset=["MP1", "MP2", "ED2", "ED3", "ED4", "UST2Y", "UST10Y", "SP500", "DXY"]).reset_index(drop=True)
    U, S, _ = np.linalg.svd(d[["MP1", "MP2", "ED2", "ED3", "ED4"]].values, full_matrices=False)
    f = U[:, 0] * S[0]
    f = -f if f @ d.ED4.values < 0 else f
    d["ns"] = f * (f @ d.UST2Y.values) / (f @ f)
    return d


# ---------------------------------------------------------------- daily data
class Inputs:
    def __init__(self):
        self.w = pd.read_csv(FROZEN / "market_weights.csv", index_col=0).weight
        d2, d10 = series_csv("DGS2"), series_csv("DGS10")
        lev = pd.read_csv(DATA / "gs_daily_levels.csv", parse_dates=["date"]).set_index("date")
        self.trading = d2.index                                                                   # trading days (days with a 2-year yield)
        w = self.w
        nom_idx = (w["y10"] * d10 + w["equities"] * 100 * np.log(lev.x_cape) + w["dollar"] * 100 * np.log(lev.x_usd)).reindex(self.trading).ffill(limit=FILL)
        y2 = d2.reindex(CALW).ffill(limit=FILL)
        e2 = monthly_mean(series_csv("EXPINF2YR"))
        rs = frozen_monthly("data_monthly.csv", "rstar LW")
        self.rate = {"nom": y2, "real": y2 - to_daily(e2), "rstar": y2 - to_daily(e2 + rs)}
        nd = nom_idx.reindex(CALW).ffill(limit=FILL)
        self.fci = {}
        for k, f in (("nom", "indexes_nominal.csv"), ("real", "indexes_real.csv"), ("rstar", "indexes_rstar.csv")):
            off = (frozen_monthly(f, "market") - monthly_mean(nd)).dropna()
            self.fci[k] = nd + to_daily(off)
        self.mac = macro()
        ev = announcements(); ev["day"] = ev.Date.dt.normalize()
        pos = pd.Series(np.arange(len(self.trading)), index=self.trading)
        mon = pd.Series(self.trading.to_period("M"), index=self.trading)
        ev["p"] = ev.day.map(pos)
        first = mon.groupby(mon).transform(lambda s: s.index.min())
        size = mon.groupby(mon).transform("size")
        ev["k"] = [pos[d] - pos[first[d]] if d in pos.index else np.nan for d in ev.day]           # position of the announcement in its month (trading days)
        ev["n"] = [size[d] if d in pos.index else np.nan for d in ev.day]                          # trading days in its month
        ev["idx_win"] = w["y10"] * ev.UST10Y + w["equities"] * ev.SP500 + w["dollar"] * ev.DXY
        ok = ev.p.notna() & (ev.p >= 1) & (ev.p + 63 < len(self.trading)) & (ev.day >= "1996-01-01") & ev.ns.notna()
        self.ev = ev
        self.used = np.where(ok.values)[0]                                                         # 252 announcements

    def daily(self, form, fci):
        return pd.DataFrame({"pol": self.rate[form], **({"idx": self.fci[fci]} if fci else {})})


def window_impact(ev, idx):
    """[1, b_F]: the FCI's window move per +1 pp on the 2-year (OLS slopes on policy news, idx_win over UST2Y)."""
    x = ev.ns.values[idx]; x = x - x.mean()
    sl = lambda c: float(((ev[c].values[idx] - ev[c].values[idx].mean()) * x).sum() / (x @ x))
    return np.array([1.0, sl("idx_win") / sl("UST2Y")])


BINS = [(0, 3), (4, 7), (8, 11), (12, 15), (16, 19), (20, 23)]


def position_bins(ev, idx):
    """(mean position in the month, mean trading days in the month, share) for the six position bins of Note B."""
    k = ev.k.values[idx].astype(int); n = ev.n.values[idx].astype(int); out = []
    for lo, hi in BINS:
        m = (k >= lo) & (k <= hi)
        if m.any(): out.append((int(round(k[m].mean())), int(round(n[m].mean())), m.mean()))
    return out
