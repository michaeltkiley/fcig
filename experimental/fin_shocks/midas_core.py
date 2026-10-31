"""Core cases of the window-identified MIDAS-VAR (FS-A16). All with the NS surprise, 1994+, BASE ordering (macro first within the month), MODEL,
3/6/12 monthly lags, 200 draws. Monthly block: [u gap, core PCE inflation] (+ IP = 100 log INDPRO as robustness). Daily block: the 2-year yield in one
of three forms, with or without the market index (FCI) in the matching form:
   Steps identical to the parallel note (fci_note, section 3; FS-A18): nominal -> real -> r*.
   nom   : 2-year nominal (DGS2);                                         FCI = the note's nominal market index (indexes_nominal.csv)
   real  : 2-year minus matched-horizon (2-year) expected inflation;     FCI = the note's real market index (indexes_real.csv)
   rstar : 2-year minus 2-year expected inflation minus LW r*;           FCI = the note's r*-gap market index (indexes_rstar.csv, baseline)
   (expected inflation: Cleveland Fed EXPINF2YR, monthly; r*: one-sided Laubach-Williams, as in the note)
Daily FCI = the daily nominal index (note weights on daily 10-year, CAPE, dollar) plus a smooth offset (interpolated between mid-months) so its
monthly average equals the monthly index in the stated form; daily rate adjustments are interpolated the same way. The window impact is the
30-minute change (2-year scaled to +1 pp; index window change), unaffected by the slow offsets; macro zero in the window.
Without the FCI the daily block is the rate alone and the window impact is the 2-year move alone.
Output: midas_core.log, midas_core{,_irf}.csv"""
import os, sys, time, numpy as np, pandas as pd
from mf_common import *
from mf_common import M as MM0, D0
from route_a_pos import positions
from midas_var import POL, MON, CALW, HAR, H, interp_monthly
import midas_bs as MB
rng = np.random.default_rng(31)

_d0 = D0.load()
_e2 = fred("EXPINF2YR"); _e2 = pd.Series(_e2.values, index=_e2.index.to_period("M"))
RATE = {"nom": POL["y2"], "real": POL["y2"] - interp_monthly(_e2), "rstar": POL["y2"] - interp_monthly(_e2 + _d0["rstar LW"]),
        "kiley": POL["y2"] - interp_monthly(_e2 + _d0["rstar Kiley"]),                     # robustness (FS-A19): Kiley's r*
        "ma8": POL["y2"] - POL["y2"].rolling(8 * 261, min_periods=8 * 250).mean()}           # robustness (FS-A20): 2-year minus its trailing 8-year moving average
_nomd = DAILY["idx"].reindex(CALW).ffill(limit=3)
def _daily_fci(target):
    off = (target - _nomd.groupby(_nomd.index.to_period("M")).mean()).dropna()
    return _nomd + interp_monthly(off)
FCI = {"nom": _daily_fci(MM0.market_nominal), "real": _daily_fci(MM0.market_real), "rstar": _daily_fci(MM0.market_rstar),
       "kiley": _daily_fci(D0.read("indexes_rstar_kiley.csv").market)}                 # the FCI note's r* (Kiley) check index
TREND = False   # robustness (FS-A19): quadratic time trend (t, t^2; t in decades from 2010) in every monthly equation
MAC = MB.MAC

def daily_frame(form, fci):
    """form = rate form; fci = 0 (no FCI), 1 (FCI in the same form as the rate) or the name of an FCI form."""
    ff = form if fci == 1 else fci
    return pd.DataFrame({"pol": RATE[form], **({"idx": FCI[ff]} if fci else {})})

def har_block(form, fci, mvars):
    D = daily_frame(form, fci).loc["1990-01-02":].dropna(); mo = D.index.to_period("M"); MMv = MAC[mvars]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
    return np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]

def macro_data(form, fci, mvars, L):
    FB = daily_frame(form, fci).set_index(MON).groupby(level=0).mean(); MMv = MAC[mvars]; X, Y = [], []
    for p in MMv.index:
        if p < pd.Period("1994-02", "M") or p > pd.Period("2026-09", "M") or (p.year == 2020 and p.month >= 3): continue
        try:
            xm = np.concatenate([MMv.loc[p - l].values for l in range(1, L + 1)]); xf = np.concatenate([FB.loc[p - l].values for l in range(1, L + 1)])
        except KeyError: continue
        tt = (p.year + (p.month - 1) / 12 - 2010) / 10
        x = np.r_[1.0, xm, xf] if not TREND else np.r_[1.0, xm, xf, tt, tt * tt]; y = MMv.loc[p].values
        if np.isnan(x).any() or np.isnan(y).any(): continue
        X.append(x); Y.append(y)
    return np.array(X), np.array(Y)

def irf(Bd, C, K, nd, L, idx, pos, fci):
    wr = win_response("NS", idx); b = np.array([wr["y2"]] + ([wr["idx"]] if fci else []))
    out = [(w, MB.simulate(Bd, C, K, nd, L, b, k0, n0)[0]) for k0, n0, w in pos]
    return sum(w * m for w, m in out)

if __name__ == "__main__":
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    SEL = sys.argv[2].split(",") if len(sys.argv) > 2 else None        # e.g. "nom-0,nom-1" (rate form - fci: 0, 1 = same form, or an FCI form name)
    TREND = len(sys.argv) > 3 and sys.argv[3] == "trend"
    MAC_SETS = {"u,pi": ["u", "pi"], "u,pi,ip": ["u", "pi", "ip"]}
    if os.environ.get("MACRO_ONLY"): MAC_SETS = {k: v for k, v in MAC_SETS.items() if k == os.environ["MACRO_ONLY"]}
    rows, irfrows = [], []; t0 = time.time()
    print("Core cases, NS surprise, 1994+, MODEL; per +1 pp window move in the 2-year; u gap pp, core PCE price level %, IP %; point [90%],", B, "draws\n")
    idx0 = event_index("NS"); _, _, idx0 = slopes(idx0, "NS"); pos0 = positions(idx0)
    bidx = [rng.choice(idx0, size=len(idx0), replace=True) for _ in range(B)]; bpos = [positions(ib) for ib in bidx]
    for mlab, mvars in MAC_SETS.items():
        combos = [s_.split("-") for s_ in SEL] if SEL else [(f, c) for f in ("nom", "real", "rstar") for c in ("0", "1")]
        for form, fci in combos:
                fci = int(fci) if fci in ("0", "1") else fci
                K, nd = len(mvars), 1 + (fci != 0); Bd = har_block(form, fci, mvars)
                for L in (3, 6, 12):
                    X, Y = macro_data(form, fci, mvars, L); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
                    def tr(m):
                        z = m.copy(); z[:, 1] = np.cumsum(z[:, 1]) / 12; return z
                    s0 = tr(irf(Bd, C0, K, nd, L, idx0, pos0, fci))
                    sd = np.array([tr(irf(Bd, np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0], K, nd, L, ib, pb, fci)) for ib, pb in zip(bidx, bpos)])
                    lo, hi = np.percentile(sd, [5, 95], axis=0); lo68, hi68 = np.percentile(sd, [16, 84], axis=0)
                    names = ["u", "P"] + (["ip"] if "ip" in mvars else [])
                    case = f"[{mlab}] rate {form}, {'FCI ' + (form if fci == 1 else fci) if fci else 'no FCI'}{', trend' if TREND else ''}, {L} lags"
                    print(f"{case:40s}: " + "  ".join(f"{n} " + " ".join(f"{h}:{s0[h, j]:+.2f}[{lo[h, j]:+.2f},{hi[h, j]:+.2f}]" for h in (12, 24, 36)) for j, n in enumerate(names)) + f"  ({time.time() - t0:.0f}s)", flush=True)
                    for j, n in enumerate(names):
                        rows.append(dict(macro=mlab, rate=form, fci=fci, trend=int(TREND), lags=L, var=n, **{f"r{h}": s0[h, j] for h in (6, 12, 24, 36)}, **{f"lo{h}": lo[h, j] for h in (12, 24, 36)}, **{f"hi{h}": hi[h, j] for h in (12, 24, 36)},
                                         **{f"lo68_{h}": lo68[h, j] for h in (12, 24, 36)}, **{f"hi68_{h}": hi68[h, j] for h in (12, 24, 36)}))
                        irfrows.append(pd.DataFrame(dict(macro=mlab, rate=form, fci=fci, trend=int(TREND), lags=L, var=n, h=np.arange(H + 1), r=s0[:, j], lo=lo[:, j], hi=hi[:, j], lo68=lo68[:, j], hi68=hi68[:, j])))
    suf = ("" if not SEL else "_" + "_".join(SEL)) + ("_trend" if TREND else "")
    pd.DataFrame(rows).to_csv(f"midas_core{suf}.csv", index=False, float_format="%.4f")
    pd.concat(irfrows).to_csv(f"midas_core{suf}_irf.csv", index=False, float_format="%.4f")
