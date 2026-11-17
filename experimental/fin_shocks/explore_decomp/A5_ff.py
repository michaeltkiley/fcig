"""Part A5: Note B's model with the federal funds rate added as a third financial variable (D-A16). Point estimates only (user: no bootstrap).
The shock is unchanged: the Nakamura-Steinsson policy news, per +1 pp on the 2-year yield in the window. The funds rate enters the daily block (its own HAR equation and the
regressors of all daily equations, next to the 2-year yield and the FCI) and the monthly equations (lagged monthly averages), and moves with the yield and the FCI on the
announcement day by its response to the NS surprise: main = window move of current-month fed funds futures (USMPD MP1; slope on NS / slope of the 2-year yield = 0.72);
check = change in the effective funds rate (DFF) from the day before to the day after the announcement (0.89).
Version: the funds rate in the same version as the 2-year yield (nominal; real and r*-gap subtract the same expected inflation and r* as the 2-year yield), so the funds
rate - 2-year spread is the same in every version. Daily DFF on weekdays (holidays filled as the other daily series); months without a daily adjusted value (before 1982 for
the real and r*-gap versions) use the monthly mean of DFF less the monthly adjustment of the 2-year yield.
Note B's code is not changed: model functions are wrapped in this process only.
   python3 A5_ff.py  -> results_ff/point_responses.csv"""
import numpy as np, pandas as pd
import lib_r2 as R
from lib import daily as DD

M = R.M
OUT = R.Path(__file__).resolve().parent / "results_ff"; OUT.mkdir(exist_ok=True)
idx0 = DD.event_index(); EVs = DD.EV.iloc[idx0]
_x = EVs.ns.values - EVs.ns.values.mean(); _sl = lambda y: float(np.sum((y - y.mean()) * _x) / np.sum(_x * _x))
B_MP1 = _sl(EVs.MP1.values) / _sl(EVs.UST2Y.values)
_dff_c = DD.fred_daily("DFF"); _cal = _dff_c.reindex(pd.date_range("1954-07-01", "2026-10-31")).ffill()
_chg = np.array([_cal.get(t + pd.Timedelta(days=1), np.nan) - _cal.get(t - pd.Timedelta(days=1), np.nan) for t in pd.DatetimeIndex(EVs.d)])
B_DFF = _sl(_chg) / _sl(EVs.UST2Y.values)
DFFW = _dff_c.reindex(DD.CALW).ffill(limit=3)                     # weekdays
DFFM = _dff_c.groupby(_dff_c.index.to_period("M")).mean()

_orig_df, _orig_fm, _orig_imp, _orig_irfb = M.daily_frame, M.fin_monthly, M.impact, M.irf_b
STATE = dict(on=False, b_ff=B_MP1)

def daily_frame(form, fci):
    D = _orig_df(form, fci)
    if not STATE["on"]: return D
    D = D.copy(); D["ff"] = DFFW - (M.POL - M.RATE[form])                 # same adjustment as the 2-year yield
    return D

def fin_monthly(form, fci):
    FB = _orig_fm(form, fci)
    if not STATE["on"]: return FB
    FB = FB.copy(); ext = DFFM - (M.Y2M - M.RATEM[form])
    if "ff" not in FB: FB["ff"] = np.nan
    FB["ff"] = FB["ff"].combine_first(ext.reindex(FB.index))
    return FB

def impact(fci, idx):
    b = _orig_imp(fci, idx)
    return np.r_[b, STATE["b_ff"]] if STATE["on"] else b

def irf_b(Bd, C, K, nd, L, b, pos):                                     # path B (ordinary FCI movement): the funds rate starts at zero
    return _orig_irfb(Bd, C, K, nd, L, np.r_[b, np.zeros(nd - len(b))], pos)

M.daily_frame, M.fin_monthly, M.impact, M.irf_b = daily_frame, fin_monthly, impact, irf_b

def point(form, fci, start, L, ff, b_ff=B_MP1):
    STATE.update(on=ff, b_ff=b_ff)
    e = next(M.estimate(form, fci, "u,pi", start, None, "in", "none", 1, (L,)))
    s, f = e["s0"], e["f0"]; names = ["pol", "idx"] if fci else ["pol"]
    if ff: names = names + ["ff"]
    out = {f"u{h}": s[h, 0] for h in (6, 12, 24, 36)} | {f"P{h}": s[h, 1] for h in (6, 12, 24, 36)}
    out |= {f"{n}{h}": f[h, j] for j, n in enumerate(names) for h in (0, 1, 6, 12, 24)}
    return out, s, f, names

if __name__ == "__main__":
    print(f"funds-rate impact per +1 pp on the 2-year yield: MP1 window {B_MP1:.3f}; DFF day before to day after {B_DFF:.3f}")
    rows, paths = [], []
    for start in ("1996-01", "1973-01"):
        for form in ("nom", "real", "rstar"):
            for fci in (0, form):
                for L in (12, 6, 3):
                    for ff, bff, tag in ((False, None, "no funds rate"), (True, B_MP1, "funds rate, impact MP1"), (True, B_DFF, "funds rate, impact DFF")):
                        if L != 12 and tag.endswith("DFF"): continue
                        o, s, f, names = point(form, fci, start, L, ff, bff or B_MP1)
                        rows.append(dict(start=start, form=form, fci=fci, lags=L, model=tag, **o))
                        if L == 12:
                            for h in range(s.shape[0]):
                                paths.append(dict(start=start, form=form, fci=fci, model=tag, h=h, u=s[h, 0], P=s[h, 1], **{n: f[h, j] for j, n in enumerate(names)}))
                print(start, form, fci, flush=True)
    pd.DataFrame(rows).to_csv(OUT / "point_responses.csv", index=False, float_format="%.4f"); pd.DataFrame(paths).to_csv(OUT / "point_paths.csv", index=False, float_format="%.4f")
