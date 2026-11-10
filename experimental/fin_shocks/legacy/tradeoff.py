"""Implied policy trade-off (Phillips multiplier) and the financial paths of the shock (FS-A40).
Re-runs the baseline cases of midas_core.py (quadratic trend, NS surprise, u gap and core PCE inflation, 200 draws, same bootstrap as the
baseline: announcements resampled, monthly residuals resampled, daily block held fixed) and keeps every draw, so that ratios get proper sets.

Phillips multiplier (Barnichon-Mesters 2021): kappa_H = P_H / U_H, with P_H the core PCE price level at month H (percent) and
U_H = sum_{h=1..H} u_h / 12 the cumulative unemployment-gap response (percentage-point years). The sacrifice ratio is -1/kappa_H.
Confidence set (Anderson-Rubin style, because U_H can be near zero): {kappa : the 90% bootstrap interval of P_H - kappa U_H contains 0},
on a grid; sets that reach the grid edge are reported as unbounded. Financial paths: monthly averages of the daily 2-year yield and FCI.

Usage (sample settings via the same environment variables as midas_core.py, e.g. SAMPLE=end2019, MSTART=1973-01):
   python3 tradeoff.py [draws] [cases]      cases like nom-1,rstar-1 (default: all six steps)    --force to rerun
Output: tradeoff{suffix}.csv (multipliers), tradeoff{suffix}_fin.csv (financial paths); logs in runs_tradeoff/"""
import os, sys, time, numpy as np, pandas as pd
import midas_core as mc
from midas_core import *  # noqa: F401,F403 (event_index, slopes, positions, H)

GRID = np.round(np.arange(-6.0, 3.0001, 0.01), 2)
HS = (12, 24, 36)      # responses run to H = 36 months

def ar_set(Pd, Ud):
    """Pd, Ud: draws of P_H and U_H. Returns (lo, hi, bounded, connected)."""
    ok = np.array([np.percentile(Pd - k * Ud, 5) <= 0 <= np.percentile(Pd - k * Ud, 95) for k in GRID])
    if not ok.any(): return np.nan, np.nan, True, True
    i = np.where(ok)[0]
    return GRID[i[0]], GRID[i[-1]], not (ok[0] or ok[-1]), bool(np.all(np.diff(i) == 1))

if __name__ == "__main__":
    force = "--force" in sys.argv; argv = [a for a in sys.argv if a != "--force"]
    B = int(argv[1]) if len(argv) > 1 else 200
    SEL = argv[2].split(",") if len(argv) > 2 else [f"{f}-{c}" for f in ("nom", "real", "rstar") for c in ("0", "1")]
    suf = "_" + "_".join(SEL) + (f"_{mc.SAMPLE}" if mc.SAMPLE else "") + (f"_m{mc.MSTART.replace('-', '')}" if mc.MSTART else "")
    out = f"tradeoff{suf}.csv"
    if os.path.exists(out) and not force: print(f"{out} exists; skip (use --force)"); sys.exit(0)
    mc.TREND = True; mvars = ["u", "pi"]; K = 2; rng = mc.rng; t0 = time.time()
    idx0 = event_index(mc.SHOCK); _, _, idx0 = slopes(idx0, mc.SHOCK); pos0 = positions(idx0)
    bidx = [rng.choice(idx0, size=len(idx0), replace=True) for _ in range(B)]; bpos = [positions(ib) for ib in bidx]   # shared across cases: paired draws
    rows, frows, keep = [], [], {}
    def tr(m):
        z = m.copy(); z[:, 1] = np.cumsum(z[:, 1]) / 12; return z
    for c in SEL:
        form, fci = c.split("-"); fci = int(fci); nd = daily_frame(form, fci).shape[1]; Bd = mc.har_block(form, fci, mvars)
        for L in mc.LAGS:
            X, Y = mc.macro_data(form, fci, mvars, L); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
            draws = [np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0] for _ in range(B)]
            s0 = tr(mc.irf(Bd, C0, K, nd, L, idx0, pos0, fci)); sd = np.array([tr(mc.irf(Bd, Cb, K, nd, L, ib, pb, fci)) for Cb, ib, pb in zip(draws, bidx, bpos)])
            f0 = mc.irf(Bd, C0, K, nd, L, idx0, pos0, fci, fin=True); fd = np.array([mc.irf(Bd, Cb, K, nd, L, ib, pb, fci, fin=True) for Cb, ib, pb in zip(draws, bidx, bpos)])
            U0 = np.cumsum(s0[:, 0]) / 12; Ud = np.cumsum(sd[:, :, 0], axis=1) / 12      # index h holds sum_{1..h} (h=0 is zero)
            keep[(c, L)] = (s0[:, 1], U0, sd[:, :, 1], Ud)
            for Hh in HS:
                lo, hi, bnd, con = ar_set(sd[:, Hh, 1], Ud[:, Hh])
                rows.append(dict(case=c, rate=form, fci=fci, lags=L, H=Hh, P=s0[Hh, 1], U=U0[Hh], kappa=s0[Hh, 1] / U0[Hh], k_lo=lo, k_hi=hi, bounded=bnd, connected=con,
                                 P_lo=np.percentile(sd[:, Hh, 1], 5), P_hi=np.percentile(sd[:, Hh, 1], 95), U_lo=np.percentile(Ud[:, Hh], 5), U_hi=np.percentile(Ud[:, Hh], 95)))
            for j, nm in enumerate(daily_frame(form, fci).columns):
                frows.append(pd.DataFrame(dict(case=c, lags=L, var=nm, h=np.arange(H + 1), r=f0[:, j], lo=np.percentile(fd[:, :, j], 5, axis=0), hi=np.percentile(fd[:, :, j], 95, axis=0))))
            r36 = [r for r in rows if r["case"] == c and r["lags"] == L and r["H"] == 36][0]
            print(f"{c:8s} L{L:2d}: kappa36 {r36['kappa']:+.2f} set [{r36['k_lo']:+.2f},{r36['k_hi']:+.2f}]{'' if r36['bounded'] else ' unbounded'}  "
                  f"2y h0/12/24 {f0[0,0]:+.2f}/{f0[12,0]:+.2f}/{f0[24,0]:+.2f}" + (f"  FCI {f0[0,1]:+.2f}/{f0[12,1]:+.2f}/{f0[24,1]:+.2f}" if fci else "") + f"  ({time.time()-t0:.0f}s)", flush=True)
    # paired difference in the multiplier, r*-gap with FCI minus nominal with FCI: percentile interval of draw-by-draw differences (same
    # announcement draws), using draws in which both cumulative unemployment responses exceed 0.05 pp-years; column "share" = share of draws used
    for L in mc.LAGS:
        if ("rstar-1", L) in keep and ("nom-1", L) in keep:
            for Hh in HS:
                a, b = keep[("rstar-1", L)], keep[("nom-1", L)]; ok = (a[3][:, Hh] > 0.05) & (b[3][:, Hh] > 0.05)
                dk = a[2][ok, Hh] / a[3][ok, Hh] - b[2][ok, Hh] / b[3][ok, Hh]
                rows.append(dict(case="diff rstar-1 minus nom-1", rate="", fci=-1, lags=L, H=Hh, kappa=a[0][Hh] / a[1][Hh] - b[0][Hh] / b[1][Hh],
                                 k_lo=np.percentile(dk, 5), k_hi=np.percentile(dk, 95), bounded=True, connected=True, share=float(ok.mean())))
    pd.DataFrame(rows).to_csv(out, index=False, float_format="%.4f")
    pd.concat(frows).to_csv(out.replace(".csv", "_fin.csv"), index=False, float_format="%.4f")
    print("wrote", out)
