"""Restricted MIDAS-VAR with Bauer-Swanson-style monthly variables (FS-A11). Same design as midas_step.py (BASE ordering: macro first within the
month; macro equations on lagged MONTHLY averages of the daily financial variables, a free coefficient per monthly lag; window impact vector with
macro entries zero; MODEL = daily block after the event day, PATH = direct event-day path through the end of month t+1), generalised to K monthly
variables and extra daily variables. Cases (1994+, 2-year, NS base / NS-GB robustness, 3/6/12 lags):
   BS1 : monthly [u gap, core PCE inflation, IP]                               (IP = 100 log INDPRO, level)
   BS2 : monthly [u gap, core PCE inflation, IP, commodity prices]             (100 log IMF all-commodity index PALLFNFINDEXM, 1992-; Bauer-Swanson use
                                                                                the CRB index, which is not on FRED)
   BS3 : monthly [u gap, core PCE inflation, IP]; daily [2-year, index, oil]   (100 log WTI spot DCOILWTICO; no free daily broad commodity index was
                                                                                reachable: S&P GSCI on stooq refused, S&P site 403). Oil has no 30-minute
                                                                                window series: its event-day impact is the one-day change on the event
                                                                                day regressed on the shock, divided by the window slope of the 2-year
                                                                                (so per +1 pp window 2-year). MODEL only (no oil path estimated).
Units: u gap pp; core PCE price level % (inflation cumulated /12); IP %; commodity / oil % (monthly average). Output: midas_bs.log, midas_bs{,_irf}.csv"""
import sys, time, numpy as np, pandas as pd
from mf_common import *
from mf_common import M as MM0
from route_a_pos import positions
from midas_var import IDX, POL, MON, CALW, HAR, H
rng = np.random.default_rng(21)

def monthly(n):
    s = fred(n); return pd.Series(s.values, index=s.index.to_period("M"))
MAC = pd.DataFrame({"u": MM0.u_gap, "pi": MM0.pi_core})
MAC["ip"] = (100 * np.log(monthly("INDPRO"))).reindex(MAC.index)
MAC["com"] = (100 * np.log(monthly("PALLFNFINDEXM"))).reindex(MAC.index)
_oil = fred("DCOILWTICO"); _oil = _oil.where(_oil > 0)
OIL = (100 * np.log(_oil)).reindex(CALW).ffill(limit=5)
OIL_CAL = (100 * np.log(_oil)).reindex(CAL).ffill(limit=5)
CASES = {"BS1": (["u", "pi", "ip"], []), "BS2": (["u", "pi", "ip", "com"], []), "BS3": (["u", "pi", "ip"], ["oil"])}
FIRST = "1994-02"

def daily_frame(extra):
    D = pd.DataFrame({"pol": POL["y2"], "idx": IDX})
    if "oil" in extra: D["oil"] = OIL
    return D

def har_block(extra, mvars):
    """Daily HAR for [2-year, index (, oil)], OLS 1990-; macro regressors: this month's and last month's values of the monthly variables (macro first)."""
    D = daily_frame(extra).loc["1990-01-02":].dropna(); mo = D.index.to_period("M"); MMv = MAC[mvars]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
    return np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]

def macro_data(extra, mvars, L):
    FB = daily_frame(extra).set_index(MON).groupby(level=0).mean(); MMv = MAC[mvars]
    X, Y = [], []
    for p in MMv.index:
        if p < pd.Period(FIRST, "M") or p > pd.Period("2026-09", "M") or (p.year == 2020 and p.month >= 3): continue
        try:
            xm = np.concatenate([MMv.loc[p - l].values for l in range(1, L + 1)]); xf = np.concatenate([FB.loc[p - l].values for l in range(1, L + 1)])
        except KeyError: continue
        x = np.r_[1.0, xm, xf]; y = MMv.loc[p].values
        if np.isnan(x).any() or np.isnan(y).any(): continue
        X.append(x); Y.append(y)
    return np.array(X), np.array(Y)

def simulate(Bd, C, K, nd, L, b_day, k0, n0, path=None, months=H + 1, nother=21):
    """Macro first in each month (from lags), then the days of the month (event day = b_day; PATH for the first nd_path daily variables)."""
    lens = [n0] + [nother] * (months - 1); start = np.concatenate([[0], np.cumsum(lens)]); off = 70
    f = np.zeros((start[-1] + off, nd)); macro = np.zeros((months, K)); fb = np.zeros((months, nd)); He = (n0 - 1 - k0) + nother
    A = C[1:1 + K * L].T.reshape(K, L, K); G = C[1 + K * L:].T.reshape(K, L, nd)
    for t in range(months):
        macro[t] = sum(A[:, l - 1] @ macro[t - l] for l in range(1, L + 1) if t - l >= 0) + sum(G[:, l - 1] @ fb[t - l] for l in range(1, L + 1) if t - l >= 0) if t else 0.0
        for tau in range(start[t], start[t + 1]):
            if tau < k0: continue
            if tau == k0: f[off + tau] = b_day; continue
            if path is not None and tau - k0 <= min(He, HZ): f[off + tau] = path[tau - k0]; continue
            x = np.concatenate([[0.0]] + [f[off + tau - h:off + tau].mean(axis=0) for h in HAR] + [macro[t - 1] if t >= 1 else np.zeros(K), macro[t]])
            f[off + tau] = x @ Bd
        fb[t] = f[off + start[t]:off + start[t + 1]].mean(axis=0)
    return macro, fb

def oil_impact(sk, idx):
    """Event-day one-day change in 100 log WTI on the shock, per +1 pp window move in the 2-year."""
    s = SHOCKS[sk].values[idx]; ok = ~np.isnan(s); idx = idx[ok]; x = s[ok] - s[ok].mean()
    p = EV.p.values[idx].astype(int); y = OIL_CAL.values[p] - OIL_CAL.values[p - 1]; g = ~np.isnan(y)
    num = np.sum((y[g] - y[g].mean()) * x[g]) / np.sum(x[g] ** 2)
    y2 = EV.UST2Y.values[idx]; g2 = ~np.isnan(y2)
    return num / (np.sum((y2[g2] - y2[g2].mean()) * x[g2]) / np.sum(x[g2] ** 2))

def irf(Bd, C, K, nd, L, P, idx, pos, sk, extra, use_path):
    wr = win_response(sk, idx); b = [wr["y2"], wr["idx"]] + ([oil_impact(sk, idx)] if "oil" in extra else []); b = np.array(b)
    path = np.column_stack([np.concatenate([[b[j]], P[v][1:HZ + 1]]) for j, v in enumerate(["y2", "idx"])]) if use_path else None
    out = [simulate(Bd, C, K, nd, L, b, k0, n0, path) for k0, n0, w in pos]; ws = [w for _, _, w in pos]
    return sum(w * m for w, (m, _) in zip(ws, out)), sum(w * fbv for w, (_, fbv) in zip(ws, out))

if __name__ == "__main__":
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    ONLY = sys.argv[2].split(",") if len(sys.argv) > 2 else list(CASES)
    LAGS = tuple(int(x) for x in sys.argv[3].split(",")) if len(sys.argv) > 3 else (3, 6, 12)
    rows, irfrows = [], []; t0 = time.time()
    print("Restricted MIDAS-VAR with Bauer-Swanson-style monthly variables, 1994+, 2-year; responses per +1 pp window move in the 2-year; median-path point estimate [90% interval],", B, "draws")
    print("u: pp; P: core PCE price level %; ip: industrial production %; com: IMF commodity price index % (monthly); oil: WTI % (monthly average of daily)\n")
    for case in ONLY:
        mvars, extra = CASES[case]; K, nd = len(mvars), 2 + len(extra)
        Bd = har_block(extra, mvars)
        for L in LAGS:
            X, Y = macro_data(extra, mvars, L); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
            print(f"=== {case} {mvars}{' + daily ' + str(extra) if extra else ''}, {L} lags: {len(Y)} months, {X.shape[1]} regressors per equation", flush=True)
            for sk in ("NS", "NS-GB"):
                idx0 = event_index(sk); P0, _, idx0 = slopes(idx0, sk); pos0 = positions(idx0)
                draws = []
                for _ in range(B):
                    ib = rng.choice(idx0, size=len(idx0), replace=True); Pb, _, ib = slopes(ib, sk); posb = positions(ib)
                    draws.append((np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0], Pb, ib, posb))
                for var, up in (("MODEL", False), ("PATH", True)):
                    if up and extra: continue
                    m0, f0 = irf(Bd, C0, K, nd, L, P0, idx0, pos0, sk, extra, up)
                    dr = [irf(Bd, Cb, K, nd, L, Pb, ib, posb, sk, extra, up) for Cb, Pb, ib, posb in draws]
                    allv = mvars + extra
                    def series(m, fbv):          # (months, K + extra): price level for pi; extra daily variables as monthly averages
                        z = m.copy(); j = mvars.index("pi"); z[:, j] = np.cumsum(z[:, j]) / 12
                        return np.column_stack([z] + ([fbv[:, 2:]] if extra else []))
                    s0 = series(m0, f0); sd = np.array([series(m, fbv) for m, fbv in dr]); lo, hi = np.percentile(sd, [5, 95], axis=0)
                    names = ["P" if v == "pi" else v for v in allv]
                    line = "  ".join(f"{n} " + " ".join(f"{h}:{s0[h, j]:+.2f}[{lo[h, j]:+.2f},{hi[h, j]:+.2f}]" for h in (10, 24, 36)) for j, n in enumerate(names))
                    print(f"   {sk:6s} {var:5s}: {line}  ({time.time() - t0:.0f}s)", flush=True)
                    for j, n in enumerate(names):
                        rows.append(dict(case=case, lags=L, shock=sk, variant=var, var=n, **{f"r{h}": s0[h, j] for h in (6, 10, 12, 24, 36)},
                                         **{f"lo{h}": lo[h, j] for h in (10, 12, 24, 36)}, **{f"hi{h}": hi[h, j] for h in (10, 12, 24, 36)}))
                        irfrows.append(pd.DataFrame(dict(case=case, lags=L, shock=sk, variant=var, var=n, h=np.arange(H + 1), r=s0[:, j], lo=lo[:, j], hi=hi[:, j])))
            print()
    suf = "" if len(ONLY) == len(CASES) else "_" + "-".join(ONLY)
    pd.DataFrame(rows).to_csv(f"midas_bs{suf}.csv", index=False, float_format="%.4f")
    pd.concat(irfrows).to_csv(f"midas_bs{suf}_irf.csv", index=False, float_format="%.4f")
