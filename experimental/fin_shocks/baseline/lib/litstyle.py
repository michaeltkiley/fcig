"""Literature-style monthly estimators, run on the same data and units as the main model so that results are comparable (08_literature_style.py).
Variables (end-of-month, unemployment gap, core PCE inflation, policy variable i_t in percentage points); 12 lags, constant, no trend; unit of every response: +1 pp on i.
 CHOL  Recursive (Cholesky) VAR, order (u, inflation, i): the policy variable responds within the month to unemployment and inflation, which do not respond to it within the month
       (Christiano, Eichenbaum and Evans 1999 style). Impact vector (0, 0, 1) (or (0, 0, 0, 1) with the commodity-price control). Inference: 5-95% of 200 residual-bootstrap draws.
       Check with a commodity price index (log PPI all commodities, monthly average, in the first block): the standard remedy for the price puzzle (Sims 1992; Ramey 2016, section 3.5).
 P1    The monthly proxy VAR of lib/monthly.py, all horizons."""
import zlib
import numpy as np, pandas as pd
from .daily import EV, event_index, fred_daily, CALW
from . import monthly as MO
from .model import MAC, fin_eom
from .paths import DATA

L = 12; H = 36; CRIT = MO.CRIT

def policy(kind):
    """Monthly end-of-month policy variable: '2y' = nominal 2-year Treasury yield (the main model's), 'ffr' = effective federal funds rate."""
    if kind == "2y": return fin_eom("nom", False)["pol"].dropna()
    d = fred_daily("DFF").reindex(CALW).ffill(); d.index = d.index.to_period("M"); return d.groupby(level=0).last()

def commodity():
    d = pd.read_csv(DATA / "PPIACO.csv"); return pd.Series(100 * np.log(d.iloc[:, 1].values.astype(float)), index=pd.PeriodIndex(pd.to_datetime(d.iloc[:, 0]), freq="M"), name="com")

def frame(kind, start, end, com=False):
    D = MAC[["u", "pi"]]
    if com: D = D.join(commodity(), how="inner")
    D = D.join(policy(kind).rename("i"), how="inner").dropna()
    return D[(D.index >= pd.Period(start, "M") - L) & (D.index <= pd.Period(end, "M"))]    # L months before the start supply the first lags, as in lib/monthly.py

def paths_chol(D, start, B=200, seed="x"):
    X, Y, per = MO.design(D, L, start, str(D.index.max())); K = D.shape[1]
    C = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C; res = Y - fit; s = np.zeros(K); s[-1] = 1.0
    def resp(Cm): T = MO.ma(Cm, K, L, H); return {v: np.array([MO.row_of(T, v, h) @ s for h in range(H + 1)]) for v in ("u", "P")}
    pt = resp(C); rng = np.random.default_rng(zlib.crc32(seed.encode())); dr = {v: [] for v in pt}
    for _ in range(B):
        Cb = np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0]; r = resp(Cb)
        for v in pt: dr[v].append(r[v])
    return {v: (pt[v], np.percentile(dr[v], 5, axis=0), np.percentile(dr[v], 95, axis=0)) for v in pt}, len(Y)

def paths_p1(start="1996-01"):
    """Monthly proxy VAR (P1) of lib/monthly.py for the nominal two-year yield without FCI, all horizons."""
    idx0 = event_index(); ev = EV.iloc[idx0]; mon = ev.Date.dt.to_period("M"); z_all = ev.ns.groupby(mon).sum(); first, last = mon.min(), mon.max()
    D = MAC[["u", "pi"]].join(fin_eom("nom", False), how="inner").dropna(); K = 3
    X, Y, per = MO.design(D, L, start); C = np.linalg.lstsq(X, Y, rcond=None)[0]; res = Y - X @ C; T = MO.ma(C, K, L, H)
    ok = (per >= first) & (per <= last); z = z_all.reindex(per[ok]).fillna(0.0).values; r = res[ok]
    g = np.array([MO.first_stage(r[:, j], z)[0] for j in range(K)]); F = MO.first_stage(r[:, 2], z)[1]; S = g / g[2]; out = {}
    for v in ("u", "P"):
        pts, los, his = [], [], []
        for h in range(H + 1):
            c = MO.row_of(T, v, h); lo, hi, unb = MO.ar_set(r @ c, r[:, 2], z); pts.append(float(c @ S)); los.append(lo); his.append(hi)
        out[v] = (np.array(pts), np.array(los), np.array(his))
    return out, F, len(Y)
