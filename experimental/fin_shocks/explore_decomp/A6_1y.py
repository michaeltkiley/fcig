"""Part A6: Note B's model with the 1-year Treasury yield in place of the 2-year yield everywhere (D-A17). Point estimates only.
The policy variable in the daily block and in the monthly equations is the 1-year yield (FRED DGS1, daily from 1962; monthly means before 1990 come from the same daily series),
in the same three versions: nominal; real = less Cleveland Fed 1-year expected inflation (FRED EXPINF1YR from 1982; Livingston-based 1-year expectation before, as Note A's
einf_1y); r*-gap = less also Laubach-Williams r*. The shock is the NS surprise. Unit: a surprise that raises the 1-year yield 1 pp in the window. USMPD has no 1-year window
change, so the 1-year window move is the 2-year window move times the ratio of the 1-year to the 2-year announcement-day (close-to-close) responses to the NS surprise (0.78);
the FCI's window move per +1 pp on the 1-year is then b_F / 0.78. The FCI itself is unchanged (still in 2-year-yield units; rescaling it would not change the macro responses).
Note B's code is not changed: model objects are replaced in this process only.
   python3 A6_1y.py  -> results_1y/point_responses.csv, point_paths.csv"""
import numpy as np, pandas as pd
import lib_r2 as R
from lib import daily as DD

M = R.M
OUT = R.Path(__file__).resolve().parent / "results_1y"; OUT.mkdir(exist_ok=True)
d1 = pd.read_csv(R.BASE.parents[1] / "mp_var_fci" / "data" / "DGS1.csv"); d1 = pd.Series(pd.to_numeric(d1.DGS1, errors="coerce").values, index=pd.to_datetime(d1.observation_date)).dropna()
idx0 = DD.event_index(); EVs = DD.EV.iloc[idx0]; _x = EVs.ns.values - EVs.ns.values.mean(); _sl = lambda y: float(np.sum((y - y.mean()) * _x) / np.sum(_x * _x))
def _day_change(x):
    out = []
    for t in pd.DatetimeIndex(EVs.d):
        a, b = x[:t], x[:t - pd.Timedelta(days=1)]; out.append(a.iloc[-1] - b.iloc[-1] if a.index[-1] == t else np.nan)
    return np.array(out)
RATIO = _sl(_day_change(d1)) / _sl(_day_change(DD.d2))            # 1-year / 2-year announcement-day response to the NS surprise

# 1-year versions, daily and monthly, built as model.RATE / model.RATEM are for the 2-year
_e1 = DD.fred_daily("EXPINF1YR"); _e1 = pd.Series(_e1.values, index=_e1.index.to_period("M"))
POL1 = d1.reindex(DD.CALW).ffill(limit=3)
RATE1 = {"nom": POL1, "real": POL1 - DD.interp_monthly(_e1), "rstar": POL1 - DD.interp_monthly(_e1 + M.D0["rstar LW"]), "kiley": POL1 - DD.interp_monthly(_e1 + M.D0["rstar Kiley"])}
Y1M = d1.groupby(d1.index.to_period("M")).mean(); _e1m = _e1.combine_first(M.D0["einf_1y"])
RATEM1 = {"nom": Y1M, "real": Y1M - _e1m, "rstar": Y1M - _e1m - M.D0["rstar LW"], "kiley": Y1M - _e1m - M.D0["rstar Kiley"]}
RATE2, RATEM2, _imp2 = dict(M.RATE), dict(M.RATEM), M.impact

def use(one_year):
    M.RATE.clear(); M.RATE.update(RATE1 if one_year else RATE2); M.RATEM.clear(); M.RATEM.update(RATEM1 if one_year else RATEM2)
    M.impact = (lambda fci, idx: (lambda b: np.r_[1.0, b[1:] / RATIO])(_imp2(fci, idx))) if one_year else _imp2

def point(form, fci, start, L, one_year):
    use(one_year); e = next(M.estimate(form, fci, "u,pi", start, None, "in", "none", 1, (L,))); use(False)
    return e["s0"], e["f0"]

if __name__ == "__main__":
    print(f"1-year / 2-year announcement-day response ratio: {RATIO:.3f}")
    rows, paths = [], []
    for start in ("1996-01", "1973-01"):
        for form in ("nom", "real", "rstar"):
            for fci in (0, form):
                for L in (12, 6, 3):
                    for one_year, tag in ((False, "2-year"), (True, "1-year")):
                        s, f = point(form, fci, start, L, one_year)
                        rows.append(dict(start=start, form=form, fci=fci, lags=L, rate=tag, **{f"u{h}": s[h, 0] for h in (6, 12, 24, 36)}, **{f"P{h}": s[h, 1] for h in (6, 12, 24, 36)},
                                         **{f"pol{h}": f[h, 0] for h in (0, 1, 6, 12, 24)}, **({f"idx{h}": f[h, 1] for h in (0, 1, 6, 12, 24)} if f.shape[1] > 1 else {})))
                        if L == 12:
                            for h in range(s.shape[0]): paths.append(dict(start=start, form=form, fci=fci, rate=tag, h=h, u=s[h, 0], P=s[h, 1], pol=f[h, 0], idx=(f[h, 1] if f.shape[1] > 1 else np.nan)))
                print(start, form, fci, flush=True)
    pd.DataFrame(rows).to_csv(OUT / "point_responses.csv", index=False, float_format="%.4f"); pd.DataFrame(paths).to_csv(OUT / "point_paths.csv", index=False, float_format="%.4f")
