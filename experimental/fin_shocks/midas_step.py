"""Restricted (step-weight) MIDAS-VAR. Same daily financial block and window identification as midas_var.py; the macro equations use
EQUAL weights within each month (monthly averages of the daily financial variables) and a free coefficient for each monthly lag:
   m_t = c + sum_{l=1}^{L} A_l m_{t-l} + sum_{l=L0}^{L} G_l fbar_{t-l} + e_t,   fbar_s = average over the weekdays of month s of [policy, index].
Each macro equation is a row of an L-lag monthly VAR, estimated by OLS (no weight parameters). Choices (user, 31 Oct): L = 6 and 12;
BASE L0 = 1 (lagged averages only: macro does not respond in the event month); ROBUSTNESS L0 = 0 (current-month average added: macro may respond
within the event month to the post-announcement days, but still not in the window). Months 2020-03..12 dropped.
Within-month ordering (user, 1 Nov): BASE = macro first: the daily block includes this month's and last month's (u, pi), so markets respond to macro
conditions within the month (in the event month macro has not moved, so nothing macro enters the window or the event day); +CUR = financial first:
the daily block has last month's (u, pi) only (both orderings in the same month would not be identified by timing).
IRF: window impact vector b on the event day (macro zero, no credit spread); daily HAR block carries the financial variables forward (MODEL) or the
direct event-day path through the end of month t+1 (PATH); month-t macro computed once month t's days are known. Event day from the empirical position bins.
Uncertainty: B draws over events and a residual bootstrap of the macro equations. Output: midas_step.log, midas_step.csv"""
import sys, time, numpy as np, pandas as pd
from mf_common import *
from route_a_pos import positions
from midas_var import IDX, POL, MON, HAR, SPECS, H
rng = np.random.default_rng(12)

def har_block(pol, cur):
    """Daily HAR block for [policy, index], OLS 1990-. Macro regressors: last month's (u, pi) and, if cur, also this month's (u, pi):
    macro ordered first within the month (BASE); without cur, macro affects financial variables only with a one-month lag (+CUR ordering)."""
    D = pd.DataFrame({"pol": POL[pol], "idx": IDX}).loc["1990-01-02":].dropna(); mo = D.index.to_period("M")
    MM = pd.DataFrame({"u": M.u_gap, "p": M.pi_core})
    mac = [MM.reindex(mo - 1).values] + ([MM.reindex(mo).values] if cur else [])
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + mac); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
    return np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]

def fbar_monthly(pol):
    D = pd.DataFrame({"pol": POL[pol].values, "idx": IDX.values}, index=MON)
    return D.groupby(level=0).mean()

def macro_data(pol, first, L, L0):
    FB = fbar_monthly(pol); MM = M[["u_gap", "pi_core"]]
    rows, X, Y = [], [], []
    for p in MM.index:
        if p < pd.Period(first, "M") or p > pd.Period("2026-09", "M") or (p.year == 2020 and p.month >= 3): continue
        try:
            xm = np.concatenate([MM.loc[p - l].values for l in range(1, L + 1)]); xf = np.concatenate([FB.loc[p - l].values for l in range(L0, L + 1)])
        except KeyError: continue
        x = np.r_[1.0, xm, xf]; y = MM.loc[p].values
        if np.isnan(x).any() or np.isnan(y).any(): continue
        rows.append(p); X.append(x); Y.append(y)
    return rows, np.array(X), np.array(Y)

def macro_step(macro, fb, A, G, L, L0, t):
    for i in range(2):
        m = sum(A[i, l - 1] @ macro[t - l] for l in range(1, L + 1) if t - l >= 0)
        macro[t, i] = m + sum(G[i, l - L0] @ fb[t - l] for l in range(L0, L + 1) if t - l >= 0)

def simulate(Bd, C, L, L0, b_day, k0, n0, path=None, months=H + 1, nother=21):
    """C: (1 + 2L + 2(L-L0+1)) x 2 coefficient matrix of the two macro equations. Bd has 2 macro rows (lagged month) or 4 (lagged and current month).
    With current-month macro in Bd (requires L0 = 1), month-t macro is set first (from lags), then the days of month t; otherwise the days first, then macro."""
    cur = Bd.shape[0] > 1 + 2 * len(HAR) + 2
    lens = [n0] + [nother] * (months - 1); start = np.concatenate([[0], np.cumsum(lens)]); off = 70
    f = np.zeros((start[-1] + off, 2)); macro = np.zeros((months, 2)); fb = np.zeros((months, 2))
    He = (n0 - 1 - k0) + nother
    A = C[1:1 + 2 * L].T.reshape(2, L, 2); G = C[1 + 2 * L:].T.reshape(2, L - L0 + 1, 2)
    for t in range(months):
        if cur: macro_step(macro, fb, A, G, L, L0, t)
        for tau in range(start[t], start[t + 1]):
            if tau < k0: continue
            if tau == k0: f[off + tau] = b_day; continue
            if path is not None and tau - k0 <= min(He, HZ): f[off + tau] = path[tau - k0]; continue
            x = np.concatenate([[0.0]] + [f[off + tau - h:off + tau].mean(axis=0) for h in HAR] + [macro[t - 1] if t >= 1 else np.zeros(2)] + ([macro[t]] if cur else []))
            f[off + tau] = x @ Bd
        fb[t] = f[off + start[t]:off + start[t + 1]].mean(axis=0)
        if not cur: macro_step(macro, fb, A, G, L, L0, t)
    return macro

def irf(Bd, C, L, L0, P, fin_d, idx, pos, sk, use_path):
    wr = win_response(sk, idx); b_day = np.array([wr[v] for v in fin_d])
    path = np.column_stack([np.concatenate([[b_day[j]], P[v][1:HZ + 1]]) for j, v in enumerate(fin_d)]) if use_path else None
    return sum(w * simulate(Bd, C, L, L0, b_day, k0, n0, path) for k0, n0, w in pos)

if __name__ == "__main__":
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    ONLY = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "ALL" else None   # "BASE" or "+CUR" to run one ordering; output then goes to midas_step_<ordering>.csv
    SPEC = sys.argv[3] if len(sys.argv) > 3 else None          # substring of the spec label, e.g. "1994" (output midas_step_<ordering>_<SPEC>_L<lags>.csv)
    LAGS = tuple(int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 else (6, 12)
    rows, irfrows = [], []; t0 = time.time()
    print("Restricted (step-weight) MIDAS-VAR: unemployment-gap response (pp) per +1 pp event-day rise in the scaling variable (2-year for NS/NS-GB, funds rate for MP1); median [90% interval] over", B, "draws")
    print("MODEL = daily block dynamics after the event day; PATH = direct event-day path through the end of month t+1, then the model. BASE = lagged monthly averages; +CUR = current-month average added (robustness)\n")
    for lab, pol, fm in SPECS:
        if SPEC and SPEC not in lab: continue
        fin_d = [pol, "idx"]
        for L in LAGS:
            for L0, tag in ((1, "BASE"), (0, "+CUR")):
                if ONLY and tag != ONLY: continue
                Bd = har_block(pol, cur=(L0 == 1))
                mon, X, Y = macro_data(pol, fm, L, L0); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
                print(f"=== {lab}, {L} lags, {tag}: {mon[0]}..{mon[-1]} ({len(mon)} months); R2 u {1 - res[:, 0].var() / Y[:, 0].var():.4f}, pi {1 - res[:, 1].var() / Y[:, 1].var():.3f}", flush=True)
                for sk in ("NS", "NS-GB") + (("MP1",) if pol == "ff" else ()):
                    idx0 = event_index(sk); P0, _, idx0 = slopes(idx0, sk); pos0 = positions(idx0)
                    draws = []
                    for _ in range(B):
                        ib = rng.choice(idx0, size=len(idx0), replace=True); Pb, _, ib = slopes(ib, sk); posb = positions(ib)
                        Cb = np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0]
                        draws.append((Cb, Pb, ib, posb))
                    for var, up in (("MODEL", False), ("PATH", True)):
                        base = irf(Bd, C0, L, L0, P0, fin_d, idx0, pos0, sk, up)
                        dr = np.array([irf(Bd, Cb, L, L0, Pb, fin_d, ib, posb, sk, up) for Cb, Pb, ib, posb in draws])
                        lo, hi = np.percentile(dr[:, :, 0], [5, 95], axis=0); plo, phi = np.percentile(dr[:, :, 1], [5, 95], axis=0)
                        lev = np.cumsum(base[:, 1]) / 12; dlev = np.cumsum(dr[:, :, 1], axis=1) / 12      # core PCE price level (%): pi is an annualized monthly rate
                        llo, lhi = np.percentile(dlev, [5, 95], axis=0)
                        irfrows.append(pd.DataFrame(dict(spec=lab, lags=L, timing=tag, shock=sk, variant=var, h=np.arange(H + 1), u=base[:, 0], u_lo=lo, u_hi=hi,
                                                         pi=base[:, 1], plev=lev, plev_lo=llo, plev_hi=lhi)))
                        rows.append(dict(spec=lab, lags=L, timing=tag, shock=sk, variant=var, **{f"u{h}": base[h, 0] for h in (6, 12, 24, 36)},
                                         lo12=lo[12], hi12=hi[12], lo24=lo[24], hi24=hi[24], lo36=lo[36], hi36=hi[36], pi12=base[12, 1], pilo12=plo[12], pihi12=phi[12],
                                         plev12=lev[12], plev24=lev[24], plev36=lev[36], plevlo24=llo[24], plevhi24=lhi[24], P12=float(np.mean(dr[:, 12, 0] > 0))))
                        print(f"   {sk:6s} {var:5s}: u6 {base[6, 0]:+.2f}  u12 {base[12, 0]:+.2f} [{lo[12]:+.2f},{hi[12]:+.2f}]  u24 {base[24, 0]:+.2f} [{lo[24]:+.2f},{hi[24]:+.2f}]  u36 {base[36, 0]:+.2f} [{lo[36]:+.2f},{hi[36]:+.2f}]  P(u12>0) {np.mean(dr[:, 12, 0] > 0):.2f}"
                              f"  | core PCE 12m {base[12, 1]:+.2f} [{plo[12]:+.2f},{phi[12]:+.2f}]  price level 24m {lev[24]:+.2f} [{llo[24]:+.2f},{lhi[24]:+.2f}]  ({time.time() - t0:.0f}s)", flush=True)
                print()
    suf = ("_" + ONLY.strip("+") if ONLY else "") + (f"_{SPEC}_L{'-'.join(map(str, LAGS))}" if SPEC else "")
    pd.DataFrame(rows).to_csv(f"midas_step{suf}.csv", index=False, float_format="%.4f")
    pd.concat(irfrows).to_csv(f"midas_step{suf}_irf.csv", index=False, float_format="%.4f")
