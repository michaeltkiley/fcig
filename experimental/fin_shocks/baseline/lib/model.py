"""The window-identified mixed-frequency VAR of Note B.

Daily block (estimated from DAILY_START = January 1996, the same start as the shocks and the monthly equations; averages use earlier days): HAR regressions in levels of the 2-year yield form (`pol`) and, when included, the market index (`idx`), on 1/5/22/66-day averages
and the monthly macro variables (this month and last: macro first within the month). Monthly block: for each macro variable (unemployment gap, core PCE
inflation, optionally the excess bond premium) an OLS equation on its own lags and lagged monthly averages of the daily financial variables, 3/6/12 lags.
Response to a policy surprise: the 30-minute window impact (2-year +1 pp; index = its window move; macro zero) applied on the event day, simulated forward
through the daily block and the monthly equations, averaged over six event-position bins. Price level = cumulated inflation / 12. Uncertainty: 500 draws that
resample announcements and monthly residuals and re-estimate the daily block on moving blocks of 66 days; the same announcement draws for every case.
Rate forms: nom | real | rstar (Laubach-Williams) | kiley (Kiley's r*). FCI: 0 | nom | real | rstar | kiley (Note A's index, same step).
Trend: none | spline (natural cubic spline, knots at the sample ends and at NBER peaks inside the sample; monthly equations only).
Start before 1990: months without daily data use the monthly series (2-year yield: FRED DGS2 monthly mean, before 1976-06 Gurkaynak-Sack-Wright SVENY02 shifted by
the mean DGS2 - SVENY02 gap of 1976-06 to 1989-12; expected inflation: Cleveland Fed from 1982, Livingston before; the index and r* from Note A).
2020: 'in' = all data; 'out' = March-December 2020 dropped from the monthly and daily equations (2020 values still enter as lags)."""
import zlib
import numpy as np, pandas as pd
from .paths import DATA, OUT
from .daily import (CALW, POL, MON, HAR, DAILY, W, lev, d10, interp_monthly, fred_daily, event_index, window_impact, window_impact_components, positions)
from . import noteA
from . import daily as _daily

H = 36                       # response horizon (months)
DAILY_START = "1996-01-01"    # first day of the daily-block estimation sample (lagged averages may use earlier days)
LAGS = (3, 6, 12)
HORIZ = (12, 24, 36)

# ---------------------------------------------------------------- monthly data
def _read_monthly(name):
    d = pd.read_csv(OUT / name, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d
D0, M0 = _read_monthly("data_monthly.csv"), _read_monthly("macro_monthly.csv")
MAC = pd.DataFrame({"u": M0.u_gap, "pi": M0.pi_core, "ebp": M0.ebp})
IDXM = {"nom": _read_monthly("indexes_nominal.csv").market, "real": _read_monthly("indexes_real.csv").market,
        "rstar": _read_monthly("indexes_rstar.csv").market, "kiley": _read_monthly("indexes_rstar_kiley.csv").market}

# ---------------------------------------------------------------- daily rate forms and daily FCIs
_e2 = fred_daily("EXPINF2YR"); _e2 = pd.Series(_e2.values, index=_e2.index.to_period("M"))     # Cleveland Fed 2-year expected inflation
RATE = {"nom": POL, "real": POL - interp_monthly(_e2),
        "rstar": POL - interp_monthly(_e2 + D0["rstar LW"]), "kiley": POL - interp_monthly(_e2 + D0["rstar Kiley"])}
_nomd = DAILY["idx"].reindex(CALW).ffill(limit=3)
def _daily_fci(target):
    """Daily nominal index plus a smooth offset (interpolated between mid-months) so that its monthly average equals the monthly index in the stated step."""
    off = (target - _nomd.groupby(_nomd.index.to_period("M")).mean()).dropna()
    return _nomd + interp_monthly(off)
FCI = {k: _daily_fci(v) for k, v in IDXM.items()}

# The three weighted components of the index (weight x demeaned input), monthly and daily, in each step (used only when the FCI is replaced by its components).
CMPKEYS = ["y10", "equities", "dollar"]; CMPNAMES = ["y10", "eq", "usd"]
# The three weighted components replace the FCI ("cmp"); the daily block is then restricted (see har_block) to keep the number of parameters reasonable.
CMPGROUPS = {"cmp": [["y10"], ["equities"], ["dollar"]]}
_short = {"y10": "y10", "equities": "eq", "dollar": "usd"}
def cmp_cols(fci, frame): return {"+".join(_short[k] for k in g): frame[g].sum(axis=1) for g in CMPGROUPS[fci]}
_cases = {"nom": ("nominal", "rstar LW"), "real": ("real", "rstar LW"), "rstar": ("rstar", "rstar LW"), "kiley": ("rstar", "rstar Kiley")}
_wv = pd.Series(W, index=CMPKEYS)
CMPM = {}; CMPD = {}
_P = pd.DataFrame({"y10": d10.reindex(DAILY.index), "equities": 100 * np.log(lev.x_cape).reindex(DAILY.index), "dollar": 100 * np.log(lev.x_usd).reindex(DAILY.index)}) * _wv
_P = _P.where(_P.notna().all(axis=1)).ffill(limit=3).reindex(CALW).ffill(limit=3)          # the same availability and filling as the daily index (DAILY.idx), so the components add up to it
for _f, (_c, _r) in _cases.items():
    _X = noteA.index_inputs(D0, _c, _r)[CMPKEYS]; CMPM[_f] = (_X - _X.loc[noteA.START:noteA.END].mean()) * _wv
    _cols = {}
    for _k in CMPKEYS:
        _d = _P[_k]; _off = (CMPM[_f][_k] - _d.groupby(_d.index.to_period("M")).mean()).dropna(); _cols[_k] = _d + interp_monthly(_off)
    CMPD[_f] = pd.DataFrame(_cols)

# ---------------------------------------------------------------- monthly extension before the daily data
_gsw = pd.read_csv(DATA / "gsw_sveny02.csv", parse_dates=["Date"]).set_index("Date").SVENY02
_gswm = _gsw.groupby(_gsw.index.to_period("M")).mean()
_dgs = fred_daily("DGS2"); _dgsm = _dgs.groupby(_dgs.index.to_period("M")).mean()
Y2M = _dgsm.combine_first(_gswm + (_dgsm - _gswm).loc["1976-06":"1989-12"].mean())
_e2m = _e2.combine_first(D0["einf_1y"])
RATEM = {"nom": Y2M, "real": Y2M - _e2m, "rstar": Y2M - _e2m - D0["rstar LW"], "kiley": Y2M - _e2m - D0["rstar Kiley"]}

def daily_frame(form, fci):
    """fci: 0 (none), a step name (Note A's index in that step) or "cmp" (the index replaced by its three weighted components in the same step as the rate)."""
    if fci in CMPGROUPS: return pd.DataFrame({"pol": RATE[form], **cmp_cols(fci, CMPD[form])})
    return pd.DataFrame({"pol": RATE[form], **({"idx": FCI[fci]} if fci else {})})

def fin_monthly(form, fci):
    """Monthly averages of the daily block; months without daily data filled from the monthly series."""
    FB = daily_frame(form, fci).set_index(MON).groupby(level=0).mean()
    ext = pd.DataFrame({"pol": RATEM[form], **(cmp_cols(fci, CMPM[form]) if fci in CMPGROUPS else {"idx": IDXM[fci]} if fci else {})})
    FB = FB.combine_first(ext)
    return FB[FB.index >= pd.Period("1973-01", "M")]

def fin_eom(form, fci):
    """End-of-month values of the daily block (the last weekday of each month, forward-filled): the 2-year yield and, when included, the FCI. Used by the monthly VAR
    benchmarks, whose unit is then +1 pp on the end-of-month yield (0.95-0.99 of the announcement-window move in this model)."""
    return daily_frame(form, fci).ffill().set_index(MON).groupby(level=0).last()

def impact(fci, idx):
    if fci in CMPGROUPS:
        w = window_impact_components(idx)[1:]; pos = {k: i for i, k in enumerate(CMPKEYS)}
        return np.r_[1.0, [sum(w[pos[k]] for k in g) for g in CMPGROUPS[fci]]]
    wi = window_impact(idx)
    return wi if fci else wi[:1]

# ---------------------------------------------------------------- estimation
NBER_PEAKS = ["1969-12", "1973-11", "1980-01", "1981-07", "1990-07", "2001-03", "2007-12", "2020-02"]
def last_month(end): return pd.Period(f"{end}-12" if end else "2026-09", "M")
def _dec(p): return (p.year + (p.month - 1) / 12 - 2010) / 10

def trend_cols(periods, start, end):
    """Natural cubic spline basis in time (without the constant): t plus K-2 nonlinear terms; knots = sample ends and the NBER peaks inside."""
    t = np.array([_dec(p) for p in periods]); a, b = pd.Period(start, "M"), last_month(end)
    kn = [_dec(a)] + [_dec(pd.Period(k, "M")) for k in NBER_PEAKS if a < pd.Period(k, "M") < b] + [_dec(b)]
    K = len(kn); d = lambda k: (np.maximum(t - kn[k], 0) ** 3 - np.maximum(t - kn[-1], 0) ** 3) / (kn[-1] - kn[k])
    return np.c_[t, *[d(k) - d(K - 2) for k in range(K - 2)]]

def har_rows(form, fci, mvars, end, t2020):
    """Regressors and outcomes (rows of the daily block's estimation sample): constant, the 1/5/22/66-day averages of the daily variables, the monthly macro variables (this month and last)."""
    D = daily_frame(form, fci).loc["1990-01-02":(f"{end}-12-31" if end else None)].dropna(); mo = D.index.to_period("M"); MMv = MAC[mvars]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1) & (D.index >= DAILY_START)
    if t2020 == "out": ok &= ~((D.index >= "2020-03-01") & (D.index <= "2020-12-31"))
    return X[ok], Y[ok]

def har_fit(X, Y, fci):
    """OLS of each daily variable on the regressors. With the FCI replaced by its components (fci in CMPGROUPS) each component's equation keeps only its own averages and those of the 2-year yield
    (plus the macro variables), and the 2-year yield's equation its own averages: 9 coefficients for the yield and 13 for each component (48 in all with three components, against 84 unrestricted)."""
    nd = Y.shape[1]
    if fci not in CMPGROUPS: return np.linalg.lstsq(X, Y, rcond=None)[0]
    Bd = np.zeros((X.shape[1], nd)); macro_cols = list(range(1 + len(HAR) * nd, X.shape[1]))
    for j in range(nd):
        vars_ = sorted({0, j}); cols = [0] + [1 + a * nd + v for a in range(len(HAR)) for v in vars_] + macro_cols
        Bd[cols, j] = np.linalg.lstsq(X[:, cols], Y[:, j], rcond=None)[0]
    return Bd

def har_block(form, fci, mvars, end, t2020):
    """Daily block coefficients (estimated from DAILY_START; see har_fit)."""
    X, Y = har_rows(form, fci, mvars, end, t2020); return har_fit(X, Y, fci)

def macro_data(form, fci, mvars, L, start, end, t2020, trend):
    FB = fin_monthly(form, fci); MMv = MAC[mvars]; X, Y, P = [], [], []
    for p in MMv.index:
        if p < pd.Period(start, "M") or p > last_month(end) or (t2020 == "out" and p.year == 2020 and p.month >= 3): continue
        try:
            xm = np.concatenate([MMv.loc[p - l].values for l in range(1, L + 1)]); xf = np.concatenate([FB.loc[p - l].values for l in range(1, L + 1)])
        except KeyError: continue
        x = np.r_[1.0, xm, xf]; y = MMv.loc[p].values
        if np.isnan(x).any() or np.isnan(y).any(): continue
        X.append(x); Y.append(y); P.append(p)
    X = np.array(X)
    if trend == "spline": X = np.c_[X, trend_cols(P, start, end)]
    return X, np.array(Y)

def simulate(Bd, C, K, nd, L, b_day, k0, n0, months=H + 1, nother=21):
    """Macro first in each month (from lags), then the days of the month (event day = b_day). Returns monthly macro, monthly-average financial paths and end-of-month financial values."""
    lens = [n0] + [nother] * (months - 1); start = np.concatenate([[0], np.cumsum(lens)]); off = 70
    f = np.zeros((start[-1] + off, nd)); macro = np.zeros((months, K)); fb = np.zeros((months, nd)); fe = np.zeros((months, nd))
    A = C[1:1 + K * L].T.reshape(K, L, K); G = C[1 + K * L:1 + K * L + nd * L].T.reshape(K, L, nd)
    for t in range(months):
        macro[t] = sum(A[:, l - 1] @ macro[t - l] for l in range(1, L + 1) if t - l >= 0) + sum(G[:, l - 1] @ fb[t - l] for l in range(1, L + 1) if t - l >= 0) if t else 0.0
        for tau in range(start[t], start[t + 1]):
            if tau < k0: continue
            if tau == k0: f[off + tau] = b_day; continue
            x = np.concatenate([[0.0]] + [f[off + tau - h:off + tau].mean(axis=0) for h in HAR] + [macro[t - 1] if t >= 1 else np.zeros(K), macro[t]])
            f[off + tau] = x @ Bd
        fb[t] = f[off + start[t]:off + start[t + 1]].mean(axis=0); fe[t] = f[off + start[t + 1] - 1]
    return macro, fb, fe

def irf(Bd, C, K, nd, L, idx, pos, fci):
    """Event-position-weighted monthly macro, monthly-average and end-of-month financial responses to a unit shock, h = 0..H."""
    b = impact(fci, idx); out = [(w, simulate(Bd, C, K, nd, L, b, k0, n0)) for k0, n0, w in pos]
    return sum(w * m[0] for w, m in out), sum(w * m[1] for w, m in out), sum(w * m[2] for w, m in out)

_EV = {}
def events(B):
    """Announcements used and the bootstrap resamples of announcements: fixed seed, identical for every case (paired draws)."""
    key = (B, _daily.CURRENT[0])
    if key not in _EV:
        idx0 = event_index(); r = np.random.default_rng(31); bidx = [r.choice(idx0, size=len(idx0), replace=True) for _ in range(B)]
        _EV[key] = (idx0, positions(idx0), bidx, [positions(ib) for ib in bidx])
    return _EV[key]

def to_level(m):
    """Cumulate the inflation response (column 1) to the price-level response, percent."""
    z = m.copy(); z[:, 1] = np.cumsum(z[:, 1]) / 12; return z

def block_rows(n, rng, length=66):
    """Row indices of a moving-block resample of n daily rows (blocks of `length` days, the longest HAR window)."""
    nb = -(-n // length); st = rng.integers(0, n - length + 1, nb); return np.concatenate([np.arange(a, a + length) for a in st])[:n]

def estimate(form, fci, macro="u,pi", start="1996-01", end=None, t2020="in", trend="none", B=200, lags=LAGS):
    """Point responses and B draws for each lag length. Each draw resamples the announcements (new window impact and event positions), resamples the monthly residuals and re-estimates the monthly
    block, and re-estimates the daily block on a moving-block resample of its rows (66-day blocks). Yields dicts: lags, nobs, names, s0 (H+1, K), sd (B, H+1, K), f0 (H+1, nd), fd (B, H+1, nd)."""
    mvars = macro.split(","); K = len(mvars); nd = daily_frame(form, fci).shape[1]
    idx0, pos0, bidx, bpos = events(B); Xd, Yd = har_rows(form, fci, mvars, end, t2020); Bd0 = har_fit(Xd, Yd, fci)
    for L in lags:
        X, Y = macro_data(form, fci, mvars, L, start, end, t2020, trend); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
        tag = f"{form}|{fci}|{macro}|{start}|{end}|{t2020}|{L}" + ("" if trend == "none" else "|" + trend)
        rng = np.random.default_rng(zlib.crc32(tag.encode())); rng_d = np.random.default_rng(zlib.crc32(("block|" + tag).encode()))
        m0, f0, e0 = irf(Bd0, C0, K, nd, L, idx0, pos0, fci)
        draws = []
        for ib, pb in zip(bidx, bpos):
            r = block_rows(len(Xd), rng_d); Bd = har_fit(Xd[r], Yd[r], fci)
            draws.append(irf(Bd, np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0], K, nd, L, ib, pb, fci))
        yield dict(lags=L, nobs=len(Y), names=["P" if v == "pi" else v for v in mvars], s0=to_level(m0), sd=np.array([to_level(d[0]) for d in draws]),
                   f0=f0, fd=np.array([d[1] for d in draws]), e0=e0)

# ---------------------------------------------------------------- summaries
def pct(a, q): return np.percentile(a, q, axis=0)

def summary_rows(spec, est):
    """One row per variable: point responses and 90% / 68% bootstrap intervals at 12, 24, 36 months."""
    rows = []
    for j, n in enumerate(est["names"]):
        s0, sd = est["s0"][:, j], est["sd"][:, :, j]
        rows.append(dict(**spec, lags=est["lags"], var=n, nobs=est["nobs"], draws=len(sd), **{f"r{h}": s0[h] for h in HORIZ},
                         **{f"lo{h}": pct(sd, 5)[h] for h in HORIZ}, **{f"hi{h}": pct(sd, 95)[h] for h in HORIZ},
                         **{f"lo68_{h}": pct(sd, 16)[h] for h in HORIZ}, **{f"hi68_{h}": pct(sd, 84)[h] for h in HORIZ}))
    return rows

def path_rows(spec, est):
    """Response paths h = 0..H: macro variables (and the price level) and the monthly-average 2-year yield and FCI, with 90% and 68% bands."""
    out = []
    eom = pd.DataFrame(dict(**spec, lags=est["lags"], kind="fin_eom", var="pol", h=np.arange(H + 1), r=est["e0"][:, 0], lo=np.nan, hi=np.nan, lo68=np.nan, hi68=np.nan))   # 2-year yield at the end of the month (point estimate)
    for kind, names, s0, sd in (("macro", est["names"], est["s0"], est["sd"]), ("fin", (["pol", "idx"] if est["f0"].shape[1] <= 2 else ["pol"] + [f"c{i}" for i in range(1, est["f0"].shape[1])])[:est["f0"].shape[1]], est["f0"], est["fd"])):
        for j, n in enumerate(names):
            out.append(pd.DataFrame(dict(**spec, lags=est["lags"], kind=kind, var=n, h=np.arange(H + 1), r=s0[:, j], lo=pct(sd[:, :, j], 5), hi=pct(sd[:, :, j], 95),
                                         lo68=pct(sd[:, :, j], 16), hi68=pct(sd[:, :, j], 84))))
    return pd.concat(out + [eom])

# ---------------------------------------------------------------- implied trade-off (Phillips multiplier, Barnichon-Mesters 2021)
KAPPA = np.sort(np.concatenate([-np.logspace(-3, 4, 3000), [0.0], np.logspace(-3, 4, 3000)]))     # -1e4 .. 1e4, dense near zero

def ar_set(Pd, Ud):
    """Confidence set for kappa = P_H / U_H (Anderson-Rubin style): {kappa : the 90% bootstrap interval of P_H - kappa U_H contains 0}, computed on a wide
    log-spaced grid (|kappa| up to 1e4) with each boundary refined by bisection, so a finite boundary is never cut off by the grid. A side is reported as
    infinite only if the set still contains +-1e4; for large |kappa| the condition reduces to the 90% interval of U_H containing zero, so that is a statistical
    result (the data cannot rule out arbitrarily steep trade-offs), not a grid limit. Returns (lo, hi, connected); lo = -inf / hi = +inf when unbounded."""
    inside = lambda k: np.percentile(Pd - k * Ud, 5) <= 0 <= np.percentile(Pd - k * Ud, 95)
    Z = Pd[:, None] - KAPPA[None, :] * Ud[:, None]; ok = (np.percentile(Z, 5, axis=0) <= 0) & (np.percentile(Z, 95, axis=0) >= 0)
    if not ok.any(): return np.nan, np.nan, True
    i = np.where(ok)[0]
    def edge(a, b):                                   # a outside, b inside the set: bisect to the boundary
        for _ in range(40):
            mid = (a + b) / 2
            if inside(mid): b = mid
            else: a = mid
        return b
    lo = -np.inf if ok[0] else edge(KAPPA[i[0] - 1], KAPPA[i[0]])
    hi = np.inf if ok[-1] else edge(KAPPA[i[-1] + 1], KAPPA[i[-1]])
    return lo, hi, bool(np.all(np.diff(i) == 1))

def cum_u(s):
    """Cumulative unemployment-gap response, percentage-point years: index h holds sum_{1..h} u_h / 12 (axis -2 is time)."""
    return np.cumsum(s, axis=-2) / 12

def multiplier_rows(spec, est):
    """kappa_H = P_H / U_H at H = 12, 24, 36 with the confidence set; P is the price level (%), U the cumulative unemployment gap (pp-years)."""
    s0, sd = est["s0"], est["sd"]; U0 = np.cumsum(s0[:, 0]) / 12; Ud = np.cumsum(sd[:, :, 0], axis=1) / 12; rows = []
    for h in HORIZ:
        lo, hi, con = ar_set(sd[:, h, 1], Ud[:, h])
        rows.append(dict(**spec, lags=est["lags"], H=h, P=s0[h, 1], U=U0[h], U_lo=np.percentile(Ud[:, h], 5), U_hi=np.percentile(Ud[:, h], 95),
                         kappa=s0[h, 1] / U0[h], k_lo=lo, k_hi=hi, connected=con))
    return rows
