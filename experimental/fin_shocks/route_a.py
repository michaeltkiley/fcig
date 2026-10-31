"""Route A: block-recursive daily-to-monthly model with the impact vector from the windows (FS-A5; macro entries zero in the window and, by construction, in the event month).
DAILY financial block f = [policy (2-year, or funds rate), market index, credit spread]: a heterogeneous-autoregression (HAR) VAR in levels, estimated by OLS on daily data (1990-01-02 to 2026-10):
   f_tau = c + sum_{h in {1,5,22,66} days} B_h * avg_h(f)_{tau-1} + G * m_{t-1} + e_tau        (m_{t-1} = previous month's unemployment gap and core PCE: macro feeds finance with a lag)
MONTHLY macro block: the unemployment-gap and core-PCE equations of the 12-lag monthly VAR (stage-0 VAR; lagged macro and lagged monthly-average financial variables, no contemporaneous financial regressor).
Shock: +1 pp rise in the scaling variable on the event day; the event-day deviation of the financial block equals the window local-projection response at h = 0; macro unchanged in the event month. After the event the daily block runs on its own dynamics
(this is where the within-month timing is handled exactly), monthly averages of the simulated daily deviations feed the macro equations, and the macro deviations feed back into the daily block with a one-month lag.
The event day is drawn from the empirical distribution of event positions (six bins of the day of the month). Variant HYBRID: the first 63 trading days of the financial path are forced to the directly estimated window local-projection path, then the daily dynamics take over.
Uncertainty: 80 draws over events (shock response, positions) and VAR residuals (macro equations); the daily block coefficients are held fixed (9,000 observations).
Output: route_a.log, route_a.csv"""
import numpy as np, pandas as pd
import mf_common as F
from mf_common import *
rng = np.random.default_rng(5); B, H, LAGS = 80, 36, 12
HAR = (1, 5, 22, 66)

def daily_block(fin, start="1990-01-02"):
    D = DAILY[fin].loc[start:].dropna().copy(); mo = D.index.to_period("M")
    prev = (mo - 1); mac = pd.DataFrame({"u": M.u_gap, "p": M.pi_core}).reindex(prev).values
    cols = []
    for h in HAR:
        a = D.rolling(h).mean().shift(1)
        cols.append(a.values)
    X = np.column_stack([np.ones(len(D))] + cols + [mac]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
    Bd = np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]                  # (1 + 4k + 2) x k
    res = Y[ok] - X[ok] @ Bd
    return Bd, res

def macro_rows(r0, nf):
    """Coefficients of the u and pi equations: A[l] (2x2) on lagged macro, C[l] (2 x nf) on lagged monthly-average financial variables."""
    co = r0.coefs                                                        # (L, k, k): eq i, var j at lag l+1
    return co[:, :2, :2], co[:, :2, 2:2 + nf]

def simulate(Bd, A, C, b_day, k0, n0, months=H + 1, fixed_path=None, nother=21):
    nf = Bd.shape[1]; nd = n0 + nother * (months - 1); off = max(HAR)
    f = np.zeros((nd + off, nf)); macro = np.zeros((months, 2)); fbar = np.zeros((months, nf))
    month_of = np.concatenate([np.zeros(n0, int)] + [np.full(nother, t, int) for t in range(1, months)])
    start = np.concatenate([[0], np.cumsum([n0] + [nother] * (months - 1))])
    for tau in range(nd):
        t = month_of[tau]
        if tau == start[t] and t >= 1:                                   # new month: macro deviation from lagged information
            m = np.zeros(2)
            for l in range(1, LAGS + 1):
                if t - l >= 0: m += A[l - 1] @ macro[t - l] + C[l - 1] @ fbar[t - l]
            macro[t] = m
        if tau < k0: continue
        if tau == k0: f[off + tau] = b_day; continue
        if fixed_path is not None and tau - k0 <= HZ: f[off + tau] = fixed_path[tau - k0]; continue
        x = np.concatenate([[0.0]] + [f[off + tau - h:off + tau].mean(axis=0) for h in HAR] + [macro[t - 1] if t >= 1 else np.zeros(2)])
        f[off + tau] = x @ Bd
        if tau == start[t] + nother - 1 or tau == nd - 1 or (t == 0 and tau == n0 - 1):
            pass
        # monthly average bookkeeping happens below
        fb_end = start[t + 1] if t + 1 < len(start) else nd
    for t in range(months):
        s, e = start[t], (start[t + 1] if t + 1 < len(start) else nd)
        fbar[t] = f[off + s:off + e].mean(axis=0)
    # recompute macro with complete fbar (loop above used fbar of earlier months only, which were still zero): iterate to a fixed point
    return f[off:], macro, fbar

def full_irf(Bd, A, C, b_day, k0, n0, fixed_path=None, months=H + 1, nother=21):
    """Iterate daily and monthly blocks month by month so that macro uses completed monthly averages."""
    nf = Bd.shape[1]; off = max(HAR); nd = n0 + nother * (months - 1)
    f = np.zeros((nd + off, nf)); macro = np.zeros((months, 2)); fbar = np.zeros((months, nf))
    lens = [n0] + [nother] * (months - 1); start = np.concatenate([[0], np.cumsum(lens)])
    for t in range(months):
        if t >= 1:
            m = np.zeros(2)
            for l in range(1, LAGS + 1):
                if t - l >= 0: m += A[l - 1] @ macro[t - l] + C[l - 1] @ fbar[t - l]
            macro[t] = m
        for tau in range(start[t], start[t + 1]):
            if tau < k0: continue
            if tau == k0: f[off + tau] = b_day; continue
            if fixed_path is not None and tau - k0 <= HZ: f[off + tau] = fixed_path[tau - k0]; continue
            x = np.concatenate([[0.0]] + [f[off + tau - h:off + tau].mean(axis=0) for h in HAR] + [macro[t - 1] if t >= 1 else np.zeros(2)])
            f[off + tau] = x @ Bd
        fbar[t] = f[off + start[t]:off + start[t + 1]].mean(axis=0)
    return macro, fbar, f[off:]

def positions(idx):
    k = np.array([int(EV.k[i]) for i in idx]); n = np.array([int(EV.n[i]) for i in idx])
    bins = [(0, 3), (4, 7), (8, 11), (12, 15), (16, 19), (20, 23)]; out = []
    for lo, hi in bins:
        m = (k >= lo) & (k <= hi)
        if m.sum(): out.append((int(round(k[m].mean())), int(round(n[m].mean())), m.mean()))
    return out

def irf_u(Bd, A, C, P, fin_d, idx, pos, hybrid=False, sk="NS"):
    wr = win_response(sk, idx)                                          # impact vector from the 30-minute windows (credit spread: close-to-close, flagged)
    b_day = np.array([wr[v] if v in wr else P[v][0] for v in fin_d])
    fixed = np.column_stack([np.concatenate([[b_day[j]], P[v][1:HZ + 1]]) for j, v in enumerate(fin_d)]) if hybrid else None
    tot = np.zeros((H + 1, 2)); fb = np.zeros((H + 1, len(fin_d)))
    for k0, n0, w in pos:
        macro, fbar, _ = full_irf(Bd, A, C, b_day, k0, n0, fixed)
        tot += w * macro; fb += w * fbar
    return tot, fb

SPECS = [("long 1976- (2-year), BASELINE no credit", ["u_gap", "pi_core", "gs2", "market_rstar"], ["y2", "idx"], "1976-06"),
         ("short 1994- (2-year), BASELINE no credit", ["u_gap", "pi_core", "gs2", "market_rstar"], ["y2", "idx"], "1994-01"),
         ("long 1973- (funds rate), BASELINE no credit", ["u_gap", "pi_core", "ffr", "market_rstar"], ["ff", "idx"], "1973-01"),
         ("long 1976- (2-year) + Baa [contaminated]", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10"], ["y2", "idx", "baa10"], "1976-06"),
         ("short 1994- (2-year) + Baa [contaminated]", ["u_gap", "pi_core", "gs2", "market_rstar", "baa10"], ["y2", "idx", "baa10"], "1994-01")]
rows = []
print("Route A: unemployment-gap response (pp) per +1 pp rise in the scaling variable on the event day; median [90% interval]; daily block HAR, macro equations from the monthly VAR\n")
for sk in ("NS", "NS-GB", "MP1"):
    idx0 = event_index(sk); P0, _, idx0 = slopes(idx0, sk); pos0 = positions(idx0)
    print(f"=== shock {sk}: {len(idx0)} events; event-position bins (day, month length, weight): " + ", ".join(f"({k},{n},{w:.2f})" for k, n, w in pos0))
    for lab, cols, fin_d, vs in SPECS:
        if sk == "MP1" and fin_d[0] != "ff": continue
        Bd, res = daily_block(fin_d)
        r0, X, dum = fit_var(cols, vs); A0, C0 = macro_rows(r0, len(fin_d))
        # stability of the daily block: response of a unit shock to the first variable dies out?
        tot, fb = irf_u(Bd, A0, C0, P0, fin_d, idx0, pos0, sk=sk)
        tot_h, fb_h = irf_u(Bd, A0, C0, P0, fin_d, idx0, pos0, hybrid=True, sk=sk)
        dr, drh = [], []
        for _ in range(B):
            ib = rng.choice(idx0, size=len(idx0), replace=True); Pb, _, ib = slopes(ib, sk); posb = positions(ib)
            rb = boot_var(r0, X, dum, rng); Ab, Cb = macro_rows(rb, len(fin_d))
            dr.append(irf_u(Bd, Ab, Cb, Pb, fin_d, ib, posb, sk=sk)[0][:, 0]); drh.append(irf_u(Bd, Ab, Cb, Pb, fin_d, ib, posb, hybrid=True, sk=sk)[0][:, 0])
        dr, drh = np.array(dr), np.array(drh); lo, hi = np.percentile(dr, [5, 95], axis=0); loh, hih = np.percentile(drh, [5, 95], axis=0)
        rows.append(dict(shock=sk, spec=lab, variant="daily", u12=tot[12, 0], lo12=lo[12], hi12=hi[12], u24=tot[24, 0], lo24=lo[24], hi24=hi[24], u36=tot[36, 0], pi12=tot[12, 1]))
        rows.append(dict(shock=sk, spec=lab, variant="hybrid", u12=tot_h[12, 0], lo12=loh[12], hi12=hih[12], u24=tot_h[24, 0], lo24=loh[24], hi24=hih[24], u36=tot_h[36, 0], pi12=tot_h[12, 1]))
        print(f"   {lab:30s} DAILY : u12 {tot[12, 0]:+.3f} [{lo[12]:+.3f},{hi[12]:+.3f}]  u24 {tot[24, 0]:+.3f} [{lo[24]:+.3f},{hi[24]:+.3f}]  u36 {tot[36, 0]:+.3f}  | core PCE 12m {tot[12, 1]:+.2f}  | financial monthly avg months 0,1,2: policy {fb[0, 0]:+.2f},{fb[1, 0]:+.2f},{fb[2, 0]:+.2f}  index {fb[0, 1]:+.2f},{fb[1, 1]:+.2f},{fb[2, 1]:+.2f}")
        print(f"   {'':30s} HYBRID: u12 {tot_h[12, 0]:+.3f} [{loh[12]:+.3f},{hih[12]:+.3f}]  u24 {tot_h[24, 0]:+.3f} [{loh[24]:+.3f},{hih[24]:+.3f}]  u36 {tot_h[36, 0]:+.3f}", flush=True)
    print()
pd.DataFrame(rows).to_csv("route_a.csv", index=False, float_format="%.4f")
