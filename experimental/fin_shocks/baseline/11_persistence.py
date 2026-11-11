"""Step 11. Financial persistence beyond the announcement window: direct event-based responses of the 2-year yield and the FCI (r*-gap forms) at 5, 22 and 66 trading days and their average over the first 22 trading days,
compared with the model's daily paths on the same clock.   python3 11_persistence.py      Output: results/persistence.csv

Clock. Day 0 is the announcement day; day h is h trading days later (the model uses weekdays; holidays make 66 weekdays about 63-65 trading days). The model sets the level on day 0 equal to the window impact
(unit: +1 pp on the 2-year yield in the window) and propagates it with the daily block. The event-based change at day h is therefore built the same way: the 30-minute window move (the policy-news window,
which contains the announcement) plus the close-to-close change from the announcement day's close to the close on day h:  D_h = window move + (level_h - level_0).  Endpoint = D_h (levels on day h);
average = mean of D_0..D_21 (22 trading days, announcement day included). The alternative builds D_h from the close before the announcement (level_h - level_{-1}); the difference between the two, the part of the
announcement day's close-to-close move that the window does not contain, is reported as the window-to-close gap.
Estimate. D_h is regressed on the policy-news surprise over the usable announcements (those with 66 trading days after them); the response per +1 pp in the window is the slope divided by the window slope of the
2-year yield on the same announcements. Controls (second variant): the sum of the surprises of the announcements that follow within h trading days. Inference: 2,000 draws of moving blocks of 12 calendar months
(the announcements of the months drawn, as in the bootstrap of the model), with the normalization re-estimated in each draw; 90% percentile intervals.
Model: r*-gap yield plus FCI, 12 lags, daily paths of the point estimate and of the 500 bootstrap draws (output/draws/..npz, fday)."""
import numpy as np, pandas as pd
from lib import model as M, daily as D
from lib.paths import RESULTS, OUT
import cases as CS

EV = D.EV; CAL = D.CAL; ie = D.event_index(); p = EV.p.values[ie].astype(int); s = EV.ns.values[ie]
usable = p + 66 < len(CAL); ie, p, s = ie[usable], p[usable], s[usable]; n = len(p)
yc = M.RATE["rstar"].reindex(CAL).ffill().values; fc = M.FCI["rstar"].reindex(CAL).ffill().values
wy = EV.UST2Y.values[ie]; wf = EV.idx_win.values[ie]; mon = pd.PeriodIndex(EV.d.iloc[ie].dt.to_period("M"))
print(f"{n} announcements with 66 trading days after them ({len(D.event_index())} in the model)")
H = (5, 22, 66)

def D_h(level, w, h, pre=False):
    return (level[p + h] - level[p - 1]) if pre else w + (level[p + h] - level[p])
def avg22(level, w, pre=False):
    return np.mean([D_h(level, w, h, pre) for h in range(22)], axis=0)
series = {"y": (yc, wy), "f": (fc, wf)}
ENDP = {"y": {}, "f": {}}
meas = {}; later = {h: np.array([s[(p > p[i]) & (p <= p[i] + h)].sum() for i in range(n)]) for h in H + (21,)}
for k, (lev, w) in series.items():
    for pre in (False, True):
        for h in H: meas[(k, f"h{h}", pre)] = D_h(lev, w, h, pre)
        meas[(k, "avg22", pre)] = avg22(lev, w, pre)
gap = {k: (series[k][0][p] - series[k][0][p - 1]) - series[k][1] for k in series}
def slope(y, x, ctrl=None):
    X = np.c_[np.ones(len(x)), x - x.mean()] if ctrl is None else np.c_[np.ones(len(x)), x - x.mean(), ctrl]
    return np.linalg.lstsq(X, y, rcond=None)[0][1]
def resp(rows, key, ctrl_h=None):
    """Response per +1 pp in the window yield on the announcements `rows` (index array)."""
    k, m, pre = key; y = meas[key][rows]; c = None if ctrl_h is None else later[ctrl_h][rows]
    return slope(y, s[rows], c) / slope(wy[rows], s[rows])
CTRL = {"h5": 5, "h22": 22, "h66": 66, "avg22": 21}
cal = pd.period_range("1996-01", "2026-09", freq="M"); rowsby = {m: np.where(mon == m)[0] for m in cal}
rng = np.random.default_rng(2026); B = 2000; bd = []
for b in range(B):
    mo = []
    while len(mo) < len(cal): mo += list(cal[M.block_rows(len(cal), rng, M.BLOCK_M)])
    bd.append(np.concatenate([rowsby[m] for m in mo[:len(cal)]]))
allr = np.arange(n); out = []
z = np.load(OUT / "draws" / "rstar_rstar_upi_1996-01_all_in_L12.npz"); fday0, fdayd = z["fday0"], z["fdayd"]
def model_stat(path, m):
    return path[22] if m == "h22" else path[5] if m == "h5" else path[66] if m == "h66" else path[:22].mean()
for k in ("y", "f"):
    j = 0 if k == "y" else 1
    for m in ("h5", "h22", "h66", "avg22"):
        mp = model_stat(fday0[:, j], m); md = np.array([model_stat(d[:, j], m) for d in fdayd])
        for pre in (False, True):
            for ctrl in (False, True):
                if pre and ctrl: continue
                key = (k, m, pre); ch = CTRL[m] if ctrl else None
                est = resp(allr, key, ch); dr = np.array([resp(r, key, ch) for r in bd])
                out.append(dict(series=k, measure=m, base="pre-event close" if pre else "window plus later closes", controls=ctrl, est=est, lo=np.percentile(dr, 5), hi=np.percentile(dr, 95), lo68=np.percentile(dr, 16), hi68=np.percentile(dr, 84),
                                model=mp, model_lo=np.percentile(md, 5), model_hi=np.percentile(md, 95), n=n))
# the window-to-close gap, per +1 pp in the window
for k in ("y", "f"):
    est = slope(gap[k], s) / slope(wy, s); dr = np.array([slope(gap[k][r], s[r]) / slope(wy[r], s[r]) for r in bd])
    out.append(dict(series=k, measure="gap", base="close minus window", controls=False, est=est, lo=np.percentile(dr, 5), hi=np.percentile(dr, 95), lo68=np.percentile(dr, 16), hi68=np.percentile(dr, 84), n=n))
R = pd.DataFrame(out); R.to_csv(RESULTS / "persistence.csv", index=False, float_format="%.4f"); print(R.round(3).to_string())
