"""Core cases of the window-identified MIDAS-VAR (FS-A16). All with the NS surprise, 1994+, BASE ordering (macro first within the month), MODEL,
3/6/12 monthly lags, 200 draws. Monthly block: [u gap, core PCE inflation] (+ IP = 100 log INDPRO as robustness). Daily block: the 2-year yield in one
of three forms, with or without the market index (FCI) in the matching form:
   nom : 2-year nominal (DGS2);                        FCI = nominal market index (note's nominal case)
   rs  : 2-year minus r* (Laubach-Williams);           FCI = nominal index + (r* index - real index)  [the note's r* adjustment applied to the nominal index;
                                                              no 'nominal minus r*' case exists in the note]
   rr  : 2-year minus 1-year expected inflation and r*; FCI = r*-gap market index (the note's baseline)
Daily FCI = the daily nominal index (note weights on daily 10-year, CAPE, dollar) plus a smooth offset (interpolated between mid-months) so its
monthly average equals the monthly index in the stated form; daily rate adjustments are interpolated the same way. The window impact is the
30-minute change (2-year scaled to +1 pp; index window change), unaffected by the slow offsets; macro zero in the window.
Without the FCI the daily block is the rate alone and the window impact is the 2-year move alone.
Output: midas_core.log, midas_core{,_irf}.csv"""
import sys, time, numpy as np, pandas as pd
from mf_common import *
from mf_common import M as MM0, D0
from route_a_pos import positions
from midas_var import POL, MON, CALW, HAR, H, interp_monthly
import midas_bs as MB
rng = np.random.default_rng(31)

_d0 = D0.load()
RATE = {"nom": POL["y2"], "rs": POL["y2"] - interp_monthly(_d0["rstar LW"]), "rr": POL["y2"] - interp_monthly(_d0.einf_1y + _d0["rstar LW"])}
_nomd = DAILY["idx"].reindex(CALW).ffill(limit=3)
def _daily_fci(target):
    off = (target - _nomd.groupby(_nomd.index.to_period("M")).mean()).dropna()
    return _nomd + interp_monthly(off)
FCI = {"nom": _daily_fci(MM0.market_nominal), "rs": _daily_fci(MM0.market_nominal + MM0.market_rstar - MM0.market_real), "rr": _daily_fci(MM0.market_rstar)}
MAC = MB.MAC

def daily_frame(form, fci):
    return pd.DataFrame({"pol": RATE[form], **({"idx": FCI[form]} if fci else {})})

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
        x = np.r_[1.0, xm, xf]; y = MMv.loc[p].values
        if np.isnan(x).any() or np.isnan(y).any(): continue
        X.append(x); Y.append(y)
    return np.array(X), np.array(Y)

def irf(Bd, C, K, nd, L, idx, pos, fci):
    wr = win_response("NS", idx); b = np.array([wr["y2"]] + ([wr["idx"]] if fci else []))
    out = [(w, MB.simulate(Bd, C, K, nd, L, b, k0, n0)[0]) for k0, n0, w in pos]
    return sum(w * m for w, m in out)

if __name__ == "__main__":
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    SEL = sys.argv[2].split(",") if len(sys.argv) > 2 else None        # e.g. "nom-0,nom-1" (form-fci)
    MAC_SETS = {"u,pi": ["u", "pi"], "u,pi,ip": ["u", "pi", "ip"]}
    rows, irfrows = [], []; t0 = time.time()
    print("Core cases, NS surprise, 1994+, MODEL; per +1 pp window move in the 2-year; u gap pp, core PCE price level %, IP %; point [90%],", B, "draws\n")
    idx0 = event_index("NS"); _, _, idx0 = slopes(idx0, "NS"); pos0 = positions(idx0)
    bidx = [rng.choice(idx0, size=len(idx0), replace=True) for _ in range(B)]; bpos = [positions(ib) for ib in bidx]
    for mlab, mvars in MAC_SETS.items():
        for form in ("nom", "rs", "rr"):
            for fci in (0, 1):
                if SEL and f"{form}-{fci}" not in SEL: continue
                K, nd = len(mvars), 1 + fci; Bd = har_block(form, fci, mvars)
                for L in (3, 6, 12):
                    X, Y = macro_data(form, fci, mvars, L); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
                    def tr(m):
                        z = m.copy(); z[:, 1] = np.cumsum(z[:, 1]) / 12; return z
                    s0 = tr(irf(Bd, C0, K, nd, L, idx0, pos0, fci))
                    sd = np.array([tr(irf(Bd, np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0], K, nd, L, ib, pb, fci)) for ib, pb in zip(bidx, bpos)])
                    lo, hi = np.percentile(sd, [5, 95], axis=0)
                    names = ["u", "P"] + (["ip"] if "ip" in mvars else [])
                    case = f"[{mlab}] rate {form}, {'with' if fci else 'no'} FCI, {L} lags"
                    print(f"{case:40s}: " + "  ".join(f"{n} " + " ".join(f"{h}:{s0[h, j]:+.2f}[{lo[h, j]:+.2f},{hi[h, j]:+.2f}]" for h in (12, 24, 36)) for j, n in enumerate(names)) + f"  ({time.time() - t0:.0f}s)", flush=True)
                    for j, n in enumerate(names):
                        rows.append(dict(macro=mlab, rate=form, fci=fci, lags=L, var=n, **{f"r{h}": s0[h, j] for h in (6, 12, 24, 36)}, **{f"lo{h}": lo[h, j] for h in (12, 24, 36)}, **{f"hi{h}": hi[h, j] for h in (12, 24, 36)}))
                        irfrows.append(pd.DataFrame(dict(macro=mlab, rate=form, fci=fci, lags=L, var=n, h=np.arange(H + 1), r=s0[:, j], lo=lo[:, j], hi=hi[:, j])))
    suf = "" if not SEL else "_" + "_".join(SEL)
    pd.DataFrame(rows).to_csv(f"midas_core{suf}.csv", index=False, float_format="%.4f")
    pd.concat(irfrows).to_csv(f"midas_core{suf}_irf.csv", index=False, float_format="%.4f")
