"""Shared pieces for the window-identified mixed-frequency work (stage-0 follow-ups, route A, route B, Monte Carlo).
Daily data and calendar; events and the three shock versions (NS, MP1, NS purged of Greenbook forecasts); window local projections (daily paths of the financial variables per unit shock);
monthly-average exposure; monthly VAR helpers. Units: unemployment gap in pp; financial variables in pp (yields, spreads) or the market-index units; shock normalised to +1 pp in the scaling variable on the event day."""
import sys, numpy as np, pandas as pd, warnings
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
sys.path.insert(0, "../mp_var_fci")
import mpcommon as C
from mpcommon import M, HERE, fred, events
from fci import data as D0
warnings.filterwarnings("ignore")
HZ = 63
VARS = ["y2", "ff", "y10", "baa10", "idx", "eq", "usd"]

# ---------------------------------------------------------------- daily data
def daily():
    d2, d10, dff, dbaa = fred("DGS2").dropna(), fred("DGS10").dropna(), fred("DFF").dropna(), fred("DBAA").dropna()
    cal = d2.index
    gsd = pd.read_csv(HERE.parents[1] / "fcig_gs_daily.csv", parse_dates=["date"]).set_index("date")
    W = pd.read_csv(HERE.parents[1] / "fci_note/replication/output/market_weights.csv", index_col=0).weight
    D = pd.DataFrame({"y2": d2, "ff": dff, "y10": d10, "baa10": dbaa - d10}, index=cal)
    D["idx"] = (W["y10"] * d10 + W["equities"] * 100 * np.log(gsd.x_cape) + W["dollar"] * 100 * np.log(gsd.x_usd)).reindex(cal)
    D["eq"] = (100 * np.log(gsd.x_cape)).reindex(cal); D["usd"] = (100 * np.log(gsd.x_usd)).reindex(cal)
    return D.ffill(limit=3), cal
DAILY, CAL = daily()
POS = {d: i for i, d in enumerate(CAL)}
MONTH = pd.Series(CAL.to_period("M"), index=CAL); NB = MONTH.groupby(MONTH).transform("size")

# ---------------------------------------------------------------- events and shocks
EV = events().reset_index(drop=True); EV["d"] = EV.Date.dt.normalize()
EV["p"] = EV.d.map(POS)
EV["n"] = [NB.iloc[int(p)] if pd.notna(p) else np.nan for p in EV.p]
EV["k"] = [int((MONTH.iloc[:int(p) + 1] == MONTH.iloc[int(p)]).sum()) - 1 if pd.notna(p) else np.nan for p in EV.p]
GOOD = (EV.p.notna() & (EV.p >= 1) & (EV.p + HZ < len(CAL)) & (EV.d >= "1994-02-01")).values

def _load_gb(name):
    out = {}
    for f in (f"{name}_1967_1984.xlsx", f"{name}_1985_Last.xlsx"):
        dd = pd.read_excel(HERE.parents[0] / "mp_var_fci/data/greenbook" / f); q = dd["Date"].astype(float)
        idx = pd.PeriodIndex([f"{int(x)}Q{int(round((x - int(x)) * 10))}" for x in q], freq="Q")
        for c in dd.columns:
            if c != "Date": out[pd.Timestamp(c.split("_")[1])] = pd.Series(dd[c].values, index=idx)
    return out
_GB = {k: _load_gb(k) for k in ("gRGDP", "gPGDP", "UNEMP")}; _gbd = sorted(_GB["gRGDP"])
def _gbrow(date):
    prev = [x for x in _gbd if x <= date]
    if len(prev) < 2 or (date - prev[-1]).days > 35: return None
    v, v0 = prev[-1], prev[-2]; q = pd.Period(v, "Q"); r = {}
    for var in ("gRGDP", "gPGDP"):
        for j in range(-1, 4): r[f"{var}_L{j}"] = _GB[var][v].get(q + j, np.nan)
        for j in range(-1, 3): r[f"{var}_R{j}"] = _GB[var][v].get(q + j, np.nan) - _GB[var][v0].get(q + j, np.nan)
    r["UNEMP_L0"] = _GB["UNEMP"][v].get(q, np.nan); return r
_R = pd.DataFrame([_gbrow(x) or {} for x in EV.Date]); _ok = _R.notna().all(axis=1).values & (EV.Date <= "2020-12-31").values
NS_GB = pd.Series(np.nan, index=EV.index); NS_GB[_ok] = sm.OLS(EV.ns[_ok].values, sm.add_constant(_R[_ok].values)).fit().resid
# Alternative shocks (FS-A25): Bauer-Swanson (2023) orthogonalized surprise (MPS_ORTH, FOMC announcements 1988-2019, from their posted data,
# data/bauer_swanson_mps.csv), matched to our events by date; Jarocinski-Karadi (2020) "poor man's" sign restriction applied to NS: the event
# counts as a monetary policy shock only when the 2-year and the S&P 500 move in opposite directions in the window (other events dropped).
_bs = pd.read_csv(HERE.parents[0] / "fin_shocks/data/bauer_swanson_mps.csv", parse_dates=["Date"]).groupby("Date").MPS_ORTH.sum()
BS_ORTH = pd.Series(EV.d.map(_bs).values, index=EV.index)
NS_JK = EV.ns.where(np.sign(EV.UST2Y) * np.sign(EV.SP500) < 0)
SHOCKS = {"NS": EV.ns, "MP1": EV.MP1, "NS-GB": NS_GB, "BS-ORTH": BS_ORTH, "NS-JK": NS_JK}
SCALE = {"NS": "y2", "MP1": "ff", "NS-GB": "y2", "BS-ORTH": "y2", "NS-JK": "y2"}

# ---------------------------------------------------------------- window local projections
DL = {v: np.full((len(EV), HZ + 1), np.nan) for v in VARS}
for _i in np.where(GOOD)[0]:
    _p = int(EV.p[_i]); _base = DAILY.iloc[_p - 1]
    for _v in VARS: DL[_v][_i] = DAILY[_v].iloc[_p:_p + HZ + 1].values - _base[_v]

def event_index(shock):
    return np.where(GOOD & ~SHOCKS[shock].isna().values)[0]

def slopes(idx, shock, scale=None, vars_=VARS):
    """Daily paths r_v(h) per unit shock (OLS slope with constant) for the events idx; scaled so the scaling variable moves +1 at h = 0. Returns paths, the unscaled slope, and the retained events."""
    scale = scale or SCALE[shock]; s = SHOCKS[shock].values[idx]; ok = ~np.isnan(s); idx = idx[ok]; x = s[ok] - s[ok].mean(); out = {}
    for v in vars_:
        Y = DL[v][idx]; out[v] = np.array([np.nansum((Y[:, h] - np.nanmean(Y[:, h])) * x) / np.sum(x * x) for h in range(HZ + 1)])
    sc = out[scale][0]
    return {v: out[v] / sc for v in vars_}, sc, idx

def first_stage_F(idx, shock, scale=None):
    scale = scale or SCALE[shock]; s = SHOCKS[shock].values[idx]
    return sm.OLS(DL[scale][idx, 0], sm.add_constant(s)).fit(cov_type="HC1").tvalues[1] ** 2

def exposure(paths, idx, vars_, mode="event"):
    """Mean over events of the event-month average response: EVENT = (1/n) sum_{i>=k} r(i-k) with the event's own day k; START = shock on the first day of the month (average of r(0..20))."""
    res = {}
    for v in vars_:
        A = np.cumsum(paths[v]); res[v] = float(np.mean([A[int(EV.n[i]) - 1 - int(EV.k[i])] / EV.n[i] if mode == "event" else A[20] / 21 for i in idx]))
    return res

# ---------------------------------------------------------------- monthly VAR helpers
M["baa10"] = (D0.load().baa - D0.load().y10).reindex(M.index)
_eb = pd.read_csv(HERE / "data/ebp.csv"); _eb.index = pd.PeriodIndex(pd.to_datetime(_eb.date), freq="M"); M["ebp"] = _eb.ebp.reindex(M.index)
_nf = pd.read_csv(HERE.parents[1] / "fci_note/replication/data/NFCI.csv"); _nf = pd.Series(_nf.iloc[:, 1].values, index=pd.to_datetime(_nf.iloc[:, 0])); M["nfci"] = _nf.groupby(_nf.index.to_period("M")).mean().reindex(M.index)
DV = {"gs2": "y2", "ffr": "ff", "market_rstar": "idx", "baa10": "baa10"}

def fit_var(cols, vstart, vend="2026-09", p=12):
    X = M.loc[vstart:vend, cols].dropna(); idx = X.index
    ms = [m for m in pd.period_range("2020-01", "2020-12", freq="M") if m in idx]
    dum = pd.DataFrame({f"d{m}": (idx == m).astype(float) for m in ms}, index=idx) if ms else None
    X = X.copy(); X.index = X.index.to_timestamp()
    if dum is not None: dum.index = X.index
    return VAR(X, exog=dum).fit(p), X, dum

def boot_var(r, X, dum, rng, p=12):
    Y = X.values; c, A, e = r.params.values, r.coefs, r.resid.values; nd = 0 if dum is None else dum.shape[1]
    Yb = Y.copy(); dr = e[rng.integers(0, len(e), size=len(Y) - p)]
    for t in range(p, len(Y)):
        Yb[t] = c[0] + ((dum.values[t] @ c[1:1 + nd]) if nd else 0) + sum(A[l] @ Yb[t - 1 - l] for l in range(p)) + dr[t - p]
    return VAR(pd.DataFrame(Yb, index=X.index, columns=X.columns), exog=dum).fit(p)

def bvec(cols, ex, macro_zero=True):
    b = np.zeros(len(cols))
    for j, c in enumerate(cols):
        if c in DV: b[j] = ex[DV[c]]
    return b


# ---------------------------------------------------------------- 30-minute window responses (USMPD intraday changes: UST2Y, UST10Y, SP500, DXY)
_W = pd.read_csv(HERE.parents[1] / "fci_note/replication/output/market_weights.csv", index_col=0).weight
EV["idx_win"] = _W["y10"] * EV.UST10Y + _W["equities"] * EV.SP500 + _W["dollar"] * EV.DXY      # index change in the window (equity term: S&P 500 change in %, CAPE log points with E10 fixed)

def win_response(shock, idx):
    """Response of the variables observed INSIDE the 30-minute windows to a unit shock: OLS slope on the shock, scaled so the scaling variable moves +1.
    y2, y10 (pp), eq, usd (%), idx (index units). The funds rate has no window series; its window response is the futures-based surprise MP1 (slope of MP1 on the shock). The credit spread has NO intraday series (not returned)."""
    s = SHOCKS[shock].values[idx]; ok = ~np.isnan(s); idx = idx[ok]; x = s[ok] - s[ok].mean(); out = {}
    for nm, col in (("y2", "UST2Y"), ("y10", "UST10Y"), ("eq", "SP500"), ("usd", "DXY"), ("idx", "idx_win"), ("ff", "MP1")):
        y = EV[col].values[idx]; out[nm] = float(np.sum((y - y.mean()) * x) / np.sum(x * x))
    sc = out["ff"] if shock == "MP1" else out["y2"]
    return {k: v / sc for k, v in out.items()}
