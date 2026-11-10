"""Estimation engine for the baseline and robustness tables of Note B (trimmed from ../midas_core.py; same numbers for the same case).

One case = (rate form, FCI, monthly macro set, first month, last year, treatment of 2020). Everything else is fixed:
  NS surprise (252 announcements, window-identified), macro first within the month, no deterministic trend, 3/6/12 monthly lags,
  u gap and core PCE inflation (+ monthly EBP in the EBP case), responses per +1 pp 2-year yield, price LEVEL (cumulated inflation).
Rate forms: nom | real | rstar (Laubach-Williams) | kiley (Kiley r*) | ma8 (2-year minus its trailing 8-year average).
FCI: 0 (none) | nom | real | rstar (Note A's market index in that form) | baa (r*-gap FCI plus the daily Baa-10y spread).
Start before 1990: monthly series fill the months before the daily data (splices flagged in ../FS_QA.md FS-A29).
2020: 'in' = all data; 'out' = monthly rows and daily HAR rows for March-December 2020 dropped (2020 values still enter as lags).
The low-level data modules (mf_common, midas_var, midas_bs, route_a_pos, fci) are still imported from the parent folder."""
import os, sys, zlib
HERE = os.path.dirname(os.path.abspath(__file__)); PARENT = os.path.dirname(HERE)
sys.path.insert(0, PARENT); os.chdir(PARENT)      # the helper modules use paths relative to fin_shocks/
import numpy as np, pandas as pd
from mf_common import *
from mf_common import M as MM0, D0
from route_a_pos import positions
from midas_var import POL, MON, CALW, HAR, H, interp_monthly
import midas_bs as MB

LAGS = (3, 6, 12)
HORIZ = (12, 24, 36)
_d0 = D0.load()
_e2 = fred("EXPINF2YR"); _e2 = pd.Series(_e2.values, index=_e2.index.to_period("M"))

# ---- daily rate forms and daily FCIs -------------------------------------------------------------------------------------------------------
RATE = {"nom": POL["y2"], "real": POL["y2"] - interp_monthly(_e2), "rstar": POL["y2"] - interp_monthly(_e2 + _d0["rstar LW"]),
        "kiley": POL["y2"] - interp_monthly(_e2 + _d0["rstar Kiley"]),
        "ma8": POL["y2"] - POL["y2"].rolling(8 * 261, min_periods=8 * 250).mean()}
_nomd = DAILY["idx"].reindex(CALW).ffill(limit=3)
def _daily_fci(target):
    off = (target - _nomd.groupby(_nomd.index.to_period("M")).mean()).dropna()
    return _nomd + interp_monthly(off)
FCI = {"nom": _daily_fci(MM0.market_nominal), "real": _daily_fci(MM0.market_real), "rstar": _daily_fci(MM0.market_rstar)}
BAA = DAILY["baa10"].reindex(CALW).ffill(limit=3)
MAC = MB.MAC
MAC["ebp"] = MM0.ebp                                   # monthly excess bond premium (source file undocumented: see PROJECT_MEMORY)

# ---- monthly extension before the daily data (start before 1990) ---------------------------------------------------------------------------
_gsw = pd.read_csv(os.path.join(PARENT, "data", "gsw_sveny02.csv"), parse_dates=["Date"]).set_index("Date").SVENY02
_gswm = _gsw.groupby(_gsw.index.to_period("M")).mean()
_dgs = fred("DGS2").dropna(); _dgsm = _dgs.groupby(_dgs.index.to_period("M")).mean()
Y2M = _dgsm.combine_first(_gswm + (_dgsm - _gswm).loc["1976-06":"1989-12"].mean())
_e2m = _e2.combine_first(_d0["einf_1y"])
RATEM = {"nom": Y2M, "real": Y2M - _e2m, "rstar": Y2M - _e2m - _d0["rstar LW"], "kiley": Y2M - _e2m - _d0["rstar Kiley"],
         "ma8": Y2M - Y2M.rolling(96, min_periods=96).mean()}
FCIM = {"nom": MM0.market_nominal, "real": MM0.market_real, "rstar": MM0.market_rstar}

def daily_frame(form, fci):
    if fci == "baa": return pd.DataFrame({"pol": RATE[form], "idx": FCI["rstar"], "baa": BAA})
    return pd.DataFrame({"pol": RATE[form], **({"idx": FCI[fci]} if fci else {})})

def fin_monthly(form, fci):
    """Monthly averages of the daily block; months without daily data (or without the 8-year average) filled from the monthly series."""
    FB = daily_frame(form, fci).set_index(MON).groupby(level=0).mean()
    if fci != "baa":
        ext = pd.DataFrame({"pol": RATEM[form], **({"idx": FCIM[fci]} if fci else {})})
        FB = FB.combine_first(ext)
    return FB[FB.index >= pd.Period("1973-01", "M")]

def impact(fci, idx):
    wr = win_response("NS", idx)
    if fci == "baa":
        s_ = SHOCKS["NS"].values[idx]; ok = ~np.isnan(s_); ii = idx[ok]; x = s_[ok] - s_[ok].mean()
        pp = EV.p.values[ii].astype(int); y = DAILY["baa10"].values[pp] - DAILY["baa10"].values[pp - 1]; g = ~np.isnan(y)
        num = np.sum((y[g] - y[g].mean()) * x[g]) / np.sum(x[g] ** 2)
        y2 = EV.UST2Y.values[ii]; g2 = ~np.isnan(y2)
        return np.array([wr["y2"], wr["idx"], num / (np.sum((y2[g2] - y2[g2].mean()) * x[g2]) / np.sum(x[g2] ** 2))])
    return np.array([wr["y2"]] + ([wr["idx"]] if fci else []))

# ---- estimation ------------------------------------------------------------------------------------------------------------------------------
def last_month(end): return pd.Period(f"{end}-12" if end else "2026-09", "M")

def har_block(form, fci, mvars, end, t2020):
    D = daily_frame(form, fci).loc["1990-01-02":(f"{end}-12-31" if end else None)].dropna(); mo = D.index.to_period("M"); MMv = MAC[mvars]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
    if t2020 == "out": ok &= ~((D.index >= "2020-03-01") & (D.index <= "2020-12-31"))
    return np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]

def macro_data(form, fci, mvars, L, start, end, t2020):
    FB = fin_monthly(form, fci); MMv = MAC[mvars]; X, Y = [], []
    for p in MMv.index:
        if p < pd.Period(start, "M") or p > last_month(end) or (t2020 == "out" and p.year == 2020 and p.month >= 3): continue
        try:
            xm = np.concatenate([MMv.loc[p - l].values for l in range(1, L + 1)]); xf = np.concatenate([FB.loc[p - l].values for l in range(1, L + 1)])
        except KeyError: continue
        x = np.r_[1.0, xm, xf]; y = MMv.loc[p].values
        if np.isnan(x).any() or np.isnan(y).any(): continue
        X.append(x); Y.append(y)
    return np.array(X), np.array(Y)

def irf(Bd, C, K, nd, L, idx, pos, fci):
    b = impact(fci, idx)
    return sum(w * MB.simulate(Bd, C, K, nd, L, b, k0, n0)[0] for k0, n0, w in pos)

_EV = None
def events(B):
    """Announcement indices and the (fixed) bootstrap resamples of announcements: identical for every case."""
    global _EV
    if _EV is None or _EV[0] != B:
        idx0 = event_index("NS"); _, _, idx0 = slopes(idx0, "NS"); r = np.random.default_rng(31)
        bidx = [r.choice(idx0, size=len(idx0), replace=True) for _ in range(B)]
        _EV = (B, idx0, positions(idx0), bidx, [positions(ib) for ib in bidx])
    return _EV[1:]

def run_case(form, fci, macro="u,pi", start="1994-02", end=None, t2020="in", B=200):
    """Rows (one per lag length and variable) of point responses and 90%/68% bootstrap intervals at 12, 24, 36 months."""
    mvars = macro.split(","); K = len(mvars); nd = daily_frame(form, fci).shape[1]
    idx0, pos0, bidx, bpos = events(B); Bd = har_block(form, fci, mvars, end, t2020); rows = []
    def tr(m): z = m.copy(); z[:, 1] = np.cumsum(z[:, 1]) / 12; return z          # inflation -> price level (% )
    for L in LAGS:
        X, Y = macro_data(form, fci, mvars, L, start, end, t2020); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
        rng = np.random.default_rng(zlib.crc32(f"{form}|{fci}|{macro}|{start}|{end}|{t2020}|{L}".encode()))
        s0 = tr(irf(Bd, C0, K, nd, L, idx0, pos0, fci))
        sd = np.array([tr(irf(Bd, np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0], K, nd, L, ib, pb, fci)) for ib, pb in zip(bidx, bpos)])
        lo, hi = np.percentile(sd, [5, 95], axis=0); lo68, hi68 = np.percentile(sd, [16, 84], axis=0)
        for j, n in enumerate(["P" if v == "pi" else v for v in mvars]):
            rows.append(dict(form=form, fci=fci, macro=macro, start=start, end=end or "", t2020=t2020, lags=L, var=n, nobs=len(Y), draws=B,
                             **{f"r{h}": s0[h, j] for h in HORIZ}, **{f"lo{h}": lo[h, j] for h in HORIZ}, **{f"hi{h}": hi[h, j] for h in HORIZ},
                             **{f"lo68_{h}": lo68[h, j] for h in HORIZ}, **{f"hi68_{h}": hi68[h, j] for h in HORIZ}))
    return rows
