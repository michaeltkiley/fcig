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
# Market-based r* (FS-A22): the 9-10 year nominal forward rate (Gurkaynak-Sack-Wright, Fed yield-curve data, SVEN1F09), which replaces both the
# expected-inflation and r* adjustments. Rate: 2-year minus the forward (daily). FCI: the FCI note's construction with the forward: 10-year minus
# the forward; equities as the nominal earnings yield (E/P plus 10-year expected inflation) minus the forward, i.e. E/P - (forward - e10), converted
# at the sample-average E/P as in the note; real dollar; same weights.
from fci import cases as _cases, indexes as _ix
_g = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "gsw_sven1f09.csv"), parse_dates=["Date"]).set_index("Date").SVEN1F09
FWD_D = _g.reindex(CALW).ffill(limit=5); FWD_M = _g.groupby(_g.index.to_period("M")).mean()
def _fwd_index():
    X = _cases.inputs(_d0, "nominal"); f = FWD_M.reindex(X.index)
    X["y10"] = _d0.y10 - f
    ep = 100 / _d0.cape; r = f - _d0.einf_10y
    X["equities"] = -(100 / ep.loc[_cases.START:_cases.END].mean()) * (ep - r)
    w = pd.read_csv(D0.OUT / "market_weights.csv", index_col=0).weight.values
    return _ix.market(X, w)[0]
MKT_FWD = _fwd_index()
RATE["fwd"] = POL["y2"] - FWD_D
FCI["fwd"] = _daily_fci(MKT_FWD)
SAMPLE = os.environ.get("SAMPLE", "")   # FS-A22: "" (baseline), "drop2021" (also drop 2021 months, whose lags include 2020), "end2019";
                                        # FS-A26: "endYYYY" (end the sample in December YYYY, daily block too), "dropYYYY" (drop that year's months)
END_Y = int(SAMPLE[3:]) if SAMPLE.startswith("end") else None
DROP_Y = int(SAMPLE[4:]) if SAMPLE.startswith("drop") else None
BOOT_REC = os.environ.get("BOOT_REC", "") == "1"      # FS-A26: recursive-design wild (Rademacher) bootstrap of the monthly block
LAGS = tuple(int(x) for x in os.environ.get("LAGS", "3,6,12").split(","))
TREND = False   # robustness (FS-A19): quadratic time trend (t, t^2; t in decades from 2010) in every monthly equation
MAC = MB.MAC

def daily_frame(form, fci):
    """form = rate form; fci = 0 (no FCI), 1 (FCI in the same form as the rate) or the name of an FCI form."""
    ff = form if fci == 1 else fci
    return pd.DataFrame({"pol": RATE[form], **({"idx": FCI[ff]} if fci else {})})

SHOCK = os.environ.get("SHOCK", "NS")          # FS-A25: alternative shocks "BS-ORTH", "NS-JK"
BOOT_DAILY = os.environ.get("BOOT_DAILY", "") == "1"   # FS-A25: re-estimate the daily block in each draw (moving-block bootstrap of daily rows, 66-day blocks)
_HAR_DATA = {}

def har_block(form, fci, mvars):
    D = daily_frame(form, fci).loc["1990-01-02":(f"{END_Y}-12-31" if END_Y else None)].dropna(); mo = D.index.to_period("M"); MMv = MAC[mvars]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
    _HAR_DATA[(form, fci, tuple(mvars))] = (X[ok], Y[ok])
    return np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]

def har_boot(form, fci, mvars, blk=66):
    """Daily block re-estimated on a moving-block resample of its (regressor, outcome) rows."""
    X, Y = _HAR_DATA[(form, fci, tuple(mvars))]; n = len(Y); starts = rng.integers(0, n - blk, int(np.ceil(n / blk)))
    ii = np.concatenate([np.arange(s0, s0 + blk) for s0 in starts])[:n]
    return np.linalg.lstsq(X[ii], Y[ii], rcond=None)[0]

def macro_data(form, fci, mvars, L):
    ROWS.clear()
    FB = daily_frame(form, fci).set_index(MON).groupby(level=0).mean(); MMv = MAC[mvars]; X, Y = [], []
    for p in MMv.index:
        if p < pd.Period("1994-02", "M") or p > pd.Period(f"{END_Y}-12" if END_Y else "2026-09", "M") or (p.year == 2020 and p.month >= 3): continue
        if DROP_Y and p.year == DROP_Y: continue
        try:
            xm = np.concatenate([MMv.loc[p - l].values for l in range(1, L + 1)]); xf = np.concatenate([FB.loc[p - l].values for l in range(1, L + 1)])
        except KeyError: continue
        tt = (p.year + (p.month - 1) / 12 - 2010) / 10
        x = np.r_[1.0, xm, xf] if not TREND else np.r_[1.0, xm, xf, tt, tt * tt]; y = MMv.loc[p].values
        if np.isnan(x).any() or np.isnan(y).any(): continue
        X.append(x); Y.append(y); ROWS.append(p)
    return np.array(X), np.array(Y)

ROWS = []

_REC_CACHE = {}

def rec_boot_data(form, fci, mvars, L, C, res):
    """Recursive-design wild bootstrap: regenerate the monthly variables month by month from the estimated equations with Rademacher-signed
    residuals, using simulated lags where available (data before the sample and in excluded months), the data's financial averages and trend;
    then rebuild the regressors. Returns (Xb, Yb). Array version."""
    key = (form, fci, tuple(mvars), L, len(ROWS))
    if key not in _REC_CACHE:
        FB = daily_frame(form, fci).set_index(MON).groupby(level=0).mean(); MMv = MAC[mvars]
        idx = MMv.index; FBa = FB.reindex(idx).values; pos = np.array([idx.get_loc(p) for p in ROWS])
        tt = np.array([(p.year + (p.month - 1) / 12 - 2010) / 10 for p in ROWS])
        _REC_CACHE[key] = (MMv.values.copy(), FBa, pos, tt)
    MM0, FBa, pos, tt = _REC_CACHE[key]; MMb = MM0.copy(); eta = rng.choice([-1.0, 1.0], size=len(res))
    lagi = np.arange(1, L + 1)
    def xrow(k):
        q = pos[k]; xm = MMb[q - lagi].ravel(); xf = FBa[q - lagi].ravel()
        return np.r_[1.0, xm, xf] if not TREND else np.r_[1.0, xm, xf, tt[k], tt[k] ** 2]
    for k in range(len(pos)):
        MMb[pos[k]] = xrow(k) @ C + eta[k] * res[k]
    Xb = np.array([xrow(k) for k in range(len(pos))]); Yb = MMb[pos]
    return Xb, Yb

def irf(Bd, C, K, nd, L, idx, pos, fci):
    wr = win_response(SHOCK, idx); b = np.array([wr["y2"]] + ([wr["idx"]] if fci else []))
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
    idx0 = event_index(SHOCK); _, _, idx0 = slopes(idx0, SHOCK); pos0 = positions(idx0)
    print(f"shock {SHOCK}: {len(idx0)} events{'; daily block re-estimated in each draw' if BOOT_DAILY else ''}", flush=True)
    bidx = [rng.choice(idx0, size=len(idx0), replace=True) for _ in range(B)]; bpos = [positions(ib) for ib in bidx]
    for mlab, mvars in MAC_SETS.items():
        combos = [s_.split("-") for s_ in SEL] if SEL else [(f, c) for f in ("nom", "real", "rstar") for c in ("0", "1")]
        for form, fci in combos:
                fci = int(fci) if fci in ("0", "1") else fci
                K, nd = len(mvars), 1 + (fci != 0); Bd = har_block(form, fci, mvars)
                for L in LAGS:
                    X, Y = macro_data(form, fci, mvars, L); C0 = np.linalg.lstsq(X, Y, rcond=None)[0]; fit = X @ C0; res = Y - fit
                    def tr(m):
                        z = m.copy(); z[:, 1] = np.cumsum(z[:, 1]) / 12; return z
                    s0 = tr(irf(Bd, C0, K, nd, L, idx0, pos0, fci))
                    def cdraw():
                        if BOOT_REC:
                            Xb, Yb = rec_boot_data(form, fci, mvars, L, C0, res); return np.linalg.lstsq(Xb, Yb, rcond=None)[0]
                        return np.linalg.lstsq(X, fit + res[rng.integers(0, len(res), len(res))], rcond=None)[0]
                    sd = np.array([tr(irf(har_boot(form, fci, mvars) if BOOT_DAILY else Bd, cdraw(), K, nd, L, ib, pb, fci)) for ib, pb in zip(bidx, bpos)])
                    lo, hi = np.percentile(sd, [5, 95], axis=0); lo68, hi68 = np.percentile(sd, [16, 84], axis=0)
                    names = ["u", "P"] + (["ip"] if "ip" in mvars else [])
                    case = f"[{mlab}] rate {form}, {'FCI ' + (form if fci == 1 else fci) if fci else 'no FCI'}{', trend' if TREND else ''}, {L} lags"
                    print(f"{case:40s}: " + "  ".join(f"{n} " + " ".join(f"{h}:{s0[h, j]:+.2f}[{lo[h, j]:+.2f},{hi[h, j]:+.2f}]" for h in (12, 24, 36)) for j, n in enumerate(names)) + f"  ({time.time() - t0:.0f}s)", flush=True)
                    for j, n in enumerate(names):
                        rows.append(dict(macro=mlab, rate=form, fci=fci, trend=int(TREND), shock=SHOCK, bootd=int(BOOT_DAILY) + 2 * int(BOOT_REC), draws=B, lags=L, var=n, **{f"r{h}": s0[h, j] for h in (6, 12, 24, 36)}, **{f"lo{h}": lo[h, j] for h in (12, 24, 36)}, **{f"hi{h}": hi[h, j] for h in (12, 24, 36)},
                                         **{f"lo68_{h}": lo68[h, j] for h in (12, 24, 36)}, **{f"hi68_{h}": hi68[h, j] for h in (12, 24, 36)}))
                        irfrows.append(pd.DataFrame(dict(macro=mlab, rate=form, fci=fci, trend=int(TREND), shock=SHOCK, bootd=int(BOOT_DAILY) + 2 * int(BOOT_REC), draws=B, lags=L, var=n, h=np.arange(H + 1), r=s0[:, j], lo=lo[:, j], hi=hi[:, j], lo68=lo68[:, j], hi68=hi68[:, j])))
    suf = ("" if not SEL else "_" + "_".join(SEL)) + ("_trend" if TREND else "") + ("_" + SAMPLE if SAMPLE else "") + ("_" + os.environ["MACRO_ONLY"].replace(",", "") if os.environ.get("MACRO_ONLY") else "") + ("" if SHOCK == "NS" else "_" + SHOCK) + ("_bootd" if BOOT_DAILY else "") + ("_bootrec" if BOOT_REC else "") + ("_L" + "-".join(map(str, LAGS)) if LAGS != (3, 6, 12) else "")
    pd.DataFrame(rows).to_csv(f"midas_core{suf}.csv", index=False, float_format="%.4f")
    pd.concat(irfrows).to_csv(f"midas_core{suf}_irf.csv", index=False, float_format="%.4f")
