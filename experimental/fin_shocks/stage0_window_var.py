"""Stage 0 (go / no-go) for the window-identified mixed-frequency VAR idea. NOT the state-space model: a monthly VAR in the spirit of Faust-Swanson-Wright (2004) whose IMPACT VECTOR comes from the event windows.
Idea. IRF_h = Theta_h b (Theta_h = reduced-form MA matrices of the VAR; b = impact vector). b is taken from the announcement windows, not from monthly residual regressions:
  * the shock is a window surprise (three versions: NS policy-news factor; MP1, the current-meeting surprise; NS purged of Greenbook forecasts, as in Miranda-Agrippino and Ricco), rescaled to a +1 pp rise in the 2-year yield on the event day;
  * the responses of the financial variables are estimated at DAILY frequency by local projections on that surprise (close before the event to the close k trading days after; k = 0..63);
  * a monthly-average exposure converts those daily paths into the impact on the monthly average of the event month (a shock on day d of a month with n trading days moves the average by (1/n) sum_{i>=d} r(i-d));
  * macro variables (unemployment gap, core PCE) get zero impact (they do not respond inside the window), the weakest version of the timing restriction;
  * the VAR then propagates b: Theta_h comes from a monthly VAR (12 lags, 2020 dummied) over a long sample (from 1973, or 1976-06 when the 2-year yield is used) or the USMPD-matched sample (1994-).
Systems: financial block = policy variable (2-year, or funds rate for the 1973 sample) + market index (r*-gap, daily changes built from the 10-year, CAPE and dollar with the note's weights); with and without the Baa-10y credit spread.
Uncertainty: 100 draws resampling events (for b) and residual-bootstrapping the VAR (for Theta). Response unit: unemployment gap in pp per +1 pp 2-year yield on the event day (also per +25 bp).
PRE-REGISTERED PASS CRITERIA (written before running): GO to the state-space build if, for the NS and NS-GB shocks, in at least one VAR sample with the credit spread included, (i) the median unemployment response is positive at 12 and 24 months and its 90% interval is not entirely below zero,
and (ii) the VAR-implied path of the 2-year and the index at months 1-2 is within the 90% interval of the directly estimated daily path (common-dynamics diagnostic). NO-GO if the interval lies entirely below zero in all cases, or the intervals are so wide that sign is not informative.
Revision (same day): (a) MP1 is scaled on the funds rate (+1 pp funds-rate move on the event day) and run only in the funds-rate specification, because its 2-year first stage is weak (F = 5);
(b) every cell is run with two timing assumptions for the event-month impact: EVENT = exposure-weighted (shock on its actual day) and START = the shock hits on the first day of the month (full-month average of the next 21 days), which brackets the temporal-aggregation effect that a monthly VAR cannot represent;
(c) the common-dynamics diagnostic now has bootstrap intervals for both the VAR-implied and the directly estimated (daily local projection) paths in months 1 and 2.
Output: stage0_window_var.log, stage0_window_var.csv"""
import sys, calendar, numpy as np, pandas as pd, warnings
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
sys.path.insert(0, "../mp_var_fci")
import mpcommon as C
from mpcommon import *
warnings.filterwarnings("ignore")
rng = np.random.default_rng(31)
HZ, B = 63, 80

# ---------------------------------------------------------------- daily data
d2, d10, dff, dbaa = fred("DGS2").dropna(), fred("DGS10").dropna(), fred("DFF").dropna(), fred("DBAA").dropna()
cal = d2.index
gsd = pd.read_csv(HERE.parents[1] / "fcig_gs_daily.csv", parse_dates=["date"]).set_index("date")
W = pd.read_csv(HERE.parents[1] / "fci_note/replication/output/market_weights.csv", index_col=0).weight
DAILY = pd.DataFrame({"y2": d2, "ff": dff, "y10": d10, "baa10": dbaa - d10}, index=cal)
DAILY["idx"] = (W["y10"] * d10 + W["equities"] * 100 * np.log(gsd.x_cape) + W["dollar"] * 100 * np.log(gsd.x_usd)).reindex(cal)
DAILY["eq"] = (100 * np.log(gsd.x_cape)).reindex(cal); DAILY["usd"] = (100 * np.log(gsd.x_usd)).reindex(cal)
DAILY = DAILY.ffill(limit=3)

# ---------------------------------------------------------------- events and shock variants
ev = events().reset_index(drop=True)
ev["d"] = ev.Date.dt.normalize()
GBD = HERE.parents[0] / "mp_var_fci/data/greenbook"
def load_gb(name):
    out = {}
    for f in (f"{name}_1967_1984.xlsx", f"{name}_1985_Last.xlsx"):
        dd = pd.read_excel(GBD / f); q = dd["Date"].astype(float)
        idx = pd.PeriodIndex([f"{int(x)}Q{int(round((x - int(x)) * 10))}" for x in q], freq="Q")
        for c in dd.columns:
            if c != "Date": out[pd.Timestamp(c.split("_")[1])] = pd.Series(dd[c].values, index=idx)
    return out
GB = {k: load_gb(k) for k in ("gRGDP", "gPGDP", "UNEMP")}; gbd = sorted(GB["gRGDP"])
def gbrow(date):
    prev = [x for x in gbd if x <= date]
    if len(prev) < 2 or (date - prev[-1]).days > 35: return None
    v, v0 = prev[-1], prev[-2]; q = pd.Period(v, "Q"); r = {}
    for var in ("gRGDP", "gPGDP"):
        for j in range(-1, 4): r[f"{var}_L{j}"] = GB[var][v].get(q + j, np.nan)
        for j in range(-1, 3): r[f"{var}_R{j}"] = GB[var][v].get(q + j, np.nan) - GB[var][v0].get(q + j, np.nan)
    r["UNEMP_L0"] = GB["UNEMP"][v].get(q, np.nan); return r
R = pd.DataFrame([gbrow(x) or {} for x in ev.Date]); okgb = R.notna().all(axis=1).values & (ev.Date <= "2020-12-31").values
ns_gb = pd.Series(np.nan, index=ev.index); ns_gb[okgb] = sm.OLS(ev.ns[okgb].values, sm.add_constant(R[okgb].values)).fit().resid
SHOCKS = {"NS": ev.ns, "MP1": ev.MP1, "NS-GB": ns_gb}

# ---------------------------------------------------------------- daily response paths (local projections) and monthly-average exposure
VARS = ["y2", "ff", "y10", "baa10", "idx", "eq", "usd"]
pos = {d: i for i, d in enumerate(cal)}
ev["p"] = ev.d.map(pos)
good = ev.p.notna() & (ev.p >= 1) & (ev.p + HZ < len(cal)) & (ev.d >= "1994-02-01")
Dl = {v: np.full((len(ev), HZ + 1), np.nan) for v in VARS}
for i in np.where(good)[0]:
    p = int(ev.p[i]); base = DAILY.iloc[p - 1]
    for v in VARS: Dl[v][i] = DAILY[v].iloc[p:p + HZ + 1].values - base[v]
# trading-day position of each event within its month and month length
month = pd.Series(cal.to_period("M"), index=cal); nb = month.groupby(month).transform("size")
ev["n"] = [nb.iloc[int(p)] if pd.notna(p) else np.nan for p in ev.p]
ev["k"] = [int((month.iloc[:int(p) + 1] == month.iloc[int(p)]).sum()) - 1 if pd.notna(p) else np.nan for p in ev.p]

def slopes(idx, s, scale="y2"):
    """beta_v(h) of daily change on the shock (OLS with constant), for events idx; scaled so the 2-year at h=0 is +1."""
    x = s.values[idx]; ok = ~np.isnan(x); idx = idx[ok]; x = x[ok] - x[ok].mean(); out = {}
    for v in VARS:
        Y = Dl[v][idx]; out[v] = np.array([np.nansum((Y[:, h] - np.nanmean(Y[:, h])) * x) / np.sum(x * x) for h in range(HZ + 1)])
    sc = out[scale][0]
    return {v: out[v] / sc for v in VARS}, sc, idx

def exposure(paths, idx, vars_, mode="event"):
    """Mean over events of the monthly-average response in the event month: (1/n) sum_{i = k}^{n-1} r(i - k)."""
    res = {}
    for v in vars_:
        A = np.cumsum(paths[v]); vals = []
        for i in idx:
            n, k = int(ev.n[i]), int(ev.k[i]); vals.append(A[n - 1 - k] / n if mode == "event" else A[20] / 21)
        res[v] = float(np.mean(vals))
    return res

# ---------------------------------------------------------------- monthly VAR
Dm = D0_load = None
from fci import data as D0
Dr = D0.load()
M["baa10"] = (Dr.baa - Dr.y10).reindex(M.index)
def fit_var(cols, vstart, vend="2026-09", p=12):
    X = M.loc[vstart:vend, cols].dropna(); idx = X.index
    ms = [m for m in pd.period_range("2020-01", "2020-12", freq="M") if m in idx]
    dum = pd.DataFrame({f"d{m}": (idx == m).astype(float) for m in ms}, index=idx) if ms else None
    X = X.copy(); X.index = X.index.to_timestamp()
    if dum is not None: dum.index = X.index
    return VAR(X, exog=dum).fit(p), X, dum
def boot_var(r, X, dum, p=12):
    Y = X.values; k = Y.shape[1]; c, A, e = r.params.values, r.coefs, r.resid.values; nd = 0 if dum is None else dum.shape[1]
    Yb = Y.copy(); dr = e[rng.integers(0, len(e), size=len(Y) - p)]
    for t in range(p, len(Y)):
        Yb[t] = c[0] + ((dum.values[t] @ c[1:1 + nd]) if nd else 0) + sum(A[l] @ Yb[t - 1 - l] for l in range(p)) + dr[t - p]
    return VAR(pd.DataFrame(Yb, index=X.index, columns=X.columns), exog=dum).fit(p)

SPECS = [("long 1973- (funds rate)", ["u_gap", "pi_core", "ffr", "market_rstar"], "ff", "ffr", "1973-01"),
         ("long 1976-06- (2-year)", ["u_gap", "pi_core", "gs2", "market_rstar"], "y2", "gs2", "1976-06"),
         ("short 1994- (2-year)", ["u_gap", "pi_core", "gs2", "market_rstar"], "y2", "gs2", "1994-01"),
         ("long 1976-06- (2-year) + Baa", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10"], "y2", "gs2", "1976-06"),
         ("short 1994- (2-year) + Baa", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10"], "y2", "gs2", "1994-01")]
DV = {"gs2": "y2", "ffr": "ff", "market_rstar": "idx", "baa10": "baa10"}
SPECS = [("long 1973- (funds rate)", ["u_gap", "pi_core", "ffr", "market_rstar"], "ff", "ffr", "1973-01"),
         ("long 1976-06- (2-year) + Baa", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10"], "y2", "gs2", "1976-06"),
         ("short 1994- (2-year)", ["u_gap", "pi_core", "gs2", "market_rstar"], "y2", "gs2", "1994-01"),
         ("short 1994- (2-year) + Baa", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10"], "y2", "gs2", "1994-01")]
H = 36; rows = []
def bvec(cols, ex):
    b = np.zeros(len(cols))
    for j, c in enumerate(cols):
        if c in DV: b[j] = ex[DV[c]]
    return b
def pct(x, q=(5, 95)): return np.percentile(x, q, axis=0)
print("Stage 0: window-identified impact vector in a monthly VAR (macro impact set to zero). Unemployment-gap response (pp) per +1 pp event-day move in the scaling variable; median [90% interval]. EVENT = exposure-weighted timing; START = shock on the first day of the month.\n")
for sk, s in SHOCKS.items():
    scale = "ff" if sk == "MP1" else "y2"; unit = "funds rate" if sk == "MP1" else "2-year yield"
    idx0 = np.where(good.values & ~s.isna().values)[0]
    P0, sc0, idx0 = slopes(idx0, s, scale)
    t = sm.OLS(Dl[scale][idx0, 0], sm.add_constant(s.values[idx0])).fit(cov_type="HC1")
    print(f"=== shock {sk} (unit: +1 pp {unit} on the event day): {len(idx0)} events; first stage on the event-day {unit} move F = {t.tvalues[1] ** 2:.0f}")
    print("   daily responses (h = 0 / 5 / 21 trading days): " + "; ".join(f"{v} {P0[v][0]:+.2f}/{P0[v][5]:+.2f}/{P0[v][21]:+.2f}" for v in ("y2", "ff", "y10", "idx", "eq", "usd", "baa10")))
    for lab, cols, dpol, mpol, vstart in SPECS:
        if sk == "MP1" and dpol != "ff": continue
        dvars = [DV[c] for c in cols if c in DV]
        r0, X, dum = fit_var(cols, vstart); pol = cols.index(mpol); ii = cols.index("market_rstar")
        bE, bS = bvec(cols, exposure(P0, idx0, dvars, "event")), bvec(cols, exposure(P0, idx0, dvars, "start"))
        Th0 = r0.ma_rep(H); iE, iS = np.einsum("hij,j->hi", Th0, bE), np.einsum("hij,j->hi", Th0, bS)
        dE, dS, vp, vi, dp, di = [], [], [], [], [], []
        for _ in range(B):
            ib = rng.choice(idx0, size=len(idx0), replace=True); Pb, _, ib = slopes(ib, s, scale)
            rb = boot_var(r0, X, dum); Th = rb.ma_rep(H)
            eE, eS = bvec(cols, exposure(Pb, ib, dvars, "event")), bvec(cols, exposure(Pb, ib, dvars, "start"))
            dE.append(np.einsum("hij,j->hi", Th, eE)[:, 0]); dS.append(np.einsum("hij,j->hi", Th, eS)[:, 0])
            vp.append(np.einsum("hij,j->hi", Th, eE)[1:3, pol]); vi.append(np.einsum("hij,j->hi", Th, eE)[1:3, ii])
            m1p, m2p, m1i, m2i = [], [], [], []
            for i in ib:
                n, k = int(ev.n[i]), int(ev.k[i]); a = n - k
                Ap, Ai = np.cumsum(Pb[dpol]), np.cumsum(Pb["idx"])
                if a + 41 <= HZ:
                    m1p.append((Ap[a + 20] - Ap[a - 1]) / 21); m2p.append((Ap[a + 41] - Ap[a + 20]) / 21); m1i.append((Ai[a + 20] - Ai[a - 1]) / 21); m2i.append((Ai[a + 41] - Ai[a + 20]) / 21)
            dp.append([np.mean(m1p), np.mean(m2p)]); di.append([np.mean(m1i), np.mean(m2i)])
        dE, dS = np.array(dE), np.array(dS); lE, hE = pct(dE); lS, hS = pct(dS)
        vp, vi, dp, di = map(np.array, (vp, vi, dp, di)); pv, pvh, pd_, pdh = pct(vp), None, pct(dp), None
        for mode, i0, lo, hi in (("EVENT", iE, lE, hE), ("START", iS, lS, hS)):
            rows.append(dict(shock=sk, spec=lab, timing=mode, u12=i0[12, 0], lo12=lo[12], hi12=hi[12], u24=i0[24, 0], lo24=lo[24], hi24=hi[24], u36=i0[36, 0]))
        print(f"   {lab:30s} b(monthly avg) EVENT: policy {bE[pol]:+.2f}, index {bE[ii]:+.2f}; START: policy {bS[pol]:+.2f}, index {bS[ii]:+.2f}")
        print(f"      EVENT: u12 {iE[12, 0]:+.3f} [{lE[12]:+.3f},{hE[12]:+.3f}]  u24 {iE[24, 0]:+.3f} [{lE[24]:+.3f},{hE[24]:+.3f}]  u36 {iE[36, 0]:+.3f}  | per 25bp {0.25 * iE[12, 0]:+.3f}, {0.25 * iE[24, 0]:+.3f}")
        print(f"      START: u12 {iS[12, 0]:+.3f} [{lS[12]:+.3f},{hS[12]:+.3f}]  u24 {iS[24, 0]:+.3f} [{lS[24]:+.3f},{hS[24]:+.3f}]  u36 {iS[36, 0]:+.3f}")
        print(f"      diagnostic (policy variable, months 1 and 2): VAR-implied {np.median(vp, 0)[0]:+.2f} [{pv[0][0]:+.2f},{pv[1][0]:+.2f}], {np.median(vp, 0)[1]:+.2f} [{pv[0][1]:+.2f},{pv[1][1]:+.2f}]  vs direct daily LP {np.median(dp, 0)[0]:+.2f} [{pd_[0][0]:+.2f},{pd_[1][0]:+.2f}], {np.median(dp, 0)[1]:+.2f} [{pd_[0][1]:+.2f},{pd_[1][1]:+.2f}]")
        vi_l, vi_h = pct(vi); di_l, di_h = pct(di)
        print(f"      diagnostic (index): VAR-implied {np.median(vi, 0)[0]:+.2f} [{vi_l[0]:+.2f},{vi_h[0]:+.2f}], {np.median(vi, 0)[1]:+.2f} [{vi_l[1]:+.2f},{vi_h[1]:+.2f}]  vs direct {np.median(di, 0)[0]:+.2f} [{di_l[0]:+.2f},{di_h[0]:+.2f}], {np.median(di, 0)[1]:+.2f} [{di_l[1]:+.2f},{di_h[1]:+.2f}]", flush=True)
    print()
pd.DataFrame(rows).to_csv("stage0_window_var.csv", index=False, float_format="%.4f")
