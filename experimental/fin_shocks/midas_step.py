"""Restricted (step-weight) MIDAS-VAR. Same daily financial block and window identification as midas_var.py; the macro equations use
EQUAL weights within each month (monthly averages of the daily financial variables) and a free coefficient for each monthly lag:
   m_t = c + sum_{l=1}^{L} A_l m_{t-l} + sum_{l=L0}^{L} G_l fbar_{t-l} + e_t,   fbar_s = average over the weekdays of month s of [policy, index].
Each macro equation is a row of an L-lag monthly VAR, estimated by OLS (no weight parameters). Choices (user, 31 Oct): L = 6 and 12;
BASE L0 = 1 (lagged averages only: macro does not respond in the event month); ROBUSTNESS L0 = 0 (current-month average added: macro may respond
within the event month to the post-announcement days, but still not in the window). Months 2020-03..12 dropped.
IRF: window impact vector b on the event day (macro zero, no credit spread); daily HAR block carries the financial variables forward (MODEL) or the
direct event-day path through the end of month t+1 (PATH); month-t macro computed once month t's days are known. Event day from the empirical position bins.
Uncertainty: B draws over events and a residual bootstrap of the macro equations. Output: midas_step.log, midas_step.csv"""
import sys, time, numpy as np, pandas as pd
from mf_common import *
from route_a_pos import positions
from midas_var import IDX, POL, MON, har_block, HAR, SPECS, H
rng = np.random.default_rng(12)

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

def simulate(Bd, C, L, L0, b_day, k0, n0, path=None, months=H + 1, nother=21):
    """C: (1 + 2L + 2(L-L0+1)) x 2 coefficient matrix of the two macro equations."""
    lens = [n0] + [nother] * (months - 1); start = np.concatenate([[0], np.cumsum(lens)]); off = 70
    f = np.zeros((start[-1] + off, 2)); macro = np.zeros((months, 2)); fb = np.zeros((months, 2))
    He = (n0 - 1 - k0) + nother
    A = C[1:1 + 2 * L].T.reshape(2, L, 2); G = C[1 + 2 * L:].T.reshape(2, L - L0 + 1, 2)
    for t in range(months):
        for tau in range(start[t], start[t + 1]):
            if tau < k0: continue
            if tau == k0: f[off + tau] = b_day; continue
            if path is not None and tau - k0 <= min(He, HZ): f[off + tau] = path[tau - k0]; continue
            x = np.concatenate([[0.0]] + [f[off + tau - h:off + tau].mean(axis=0) for h in HAR] + [macro[t - 1] if t >= 1 else np.zeros(2)])
            f[off + tau] = x @ Bd
        fb[t] = f[off + start[t]:off + start[t + 1]].mean(axis=0)
        for i in range(2):
            m = sum(A[i, l - 1] @ macro[t - l] for l in range(1, L + 1) if t - l >= 0)
            m += sum(G[i, l - L0] @ fb[t - l] for l in range(L0, L + 1) if t - l >= 0)
            macro[t, i] = m
    return macro

def irf(Bd, C, L, L0, P, fin_d, idx, pos, sk, use_path):
    wr = win_response(sk, idx); b_day = np.array([wr[v] for v in fin_d])
    path = np.column_stack([np.concatenate([[b_day[j]], P[v][1:HZ + 1]]) for j, v in enumerate(fin_d)]) if use_path else None
    return sum(w * simulate(Bd, C, L, L0, b_day, k0, n0, path) for k0, n0, w in pos)

if __name__ == "__main__":
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    rows = []; t0 = time.time()
    print("Restricted (step-weight) MIDAS-VAR: unemployment-gap response (pp) per +1 pp event-day rise in the scaling variable (2-year for NS/NS-GB, funds rate for MP1); median [90% interval] over", B, "draws")
    print("MODEL = daily block dynamics after the event day; PATH = direct event-day path through the end of month t+1, then the model. BASE = lagged monthly averages; +CUR = current-month average added (robustness)\n")
    for lab, pol, fm in SPECS:
        Bd = har_block(pol); fin_d = [pol, "idx"]
        for L in (6, 12):
            for L0, tag in ((1, "BASE"), (0, "+CUR")):
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
                        rows.append(dict(spec=lab, lags=L, timing=tag, shock=sk, variant=var, **{f"u{h}": base[h, 0] for h in (6, 12, 24, 36)},
                                         lo12=lo[12], hi12=hi[12], lo24=lo[24], hi24=hi[24], lo36=lo[36], hi36=hi[36], pi12=base[12, 1], pilo12=plo[12], pihi12=phi[12], P12=float(np.mean(dr[:, 12, 0] > 0))))
                        print(f"   {sk:6s} {var:5s}: u6 {base[6, 0]:+.2f}  u12 {base[12, 0]:+.2f} [{lo[12]:+.2f},{hi[12]:+.2f}]  u24 {base[24, 0]:+.2f} [{lo[24]:+.2f},{hi[24]:+.2f}]  u36 {base[36, 0]:+.2f} [{lo[36]:+.2f},{hi[36]:+.2f}]  P(u12>0) {np.mean(dr[:, 12, 0] > 0):.2f}"
                              f"  | core PCE 12m {base[12, 1]:+.2f} [{plo[12]:+.2f},{phi[12]:+.2f}]  ({time.time() - t0:.0f}s)", flush=True)
                print()
    pd.DataFrame(rows).to_csv("midas_step.csv", index=False, float_format="%.4f")
