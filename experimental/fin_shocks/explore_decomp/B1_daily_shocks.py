"""Part B1: policy shocks recovered from Note B's DAILY innovations, 1990-2026 (Route 2 at daily frequency; D-A11).
Note B's daily block (HAR regressions of the 2-year yield and the FCI, estimated on Note B's sample from 1996) gives daily innovations eps_d = (eps_i, eps_F)'. With the window
impact b = (1, b_F) as the policy column and Omega = Var(eps_d), the policy shock of day d under invertibility within the day is
    s_d = b' Omega^-1 eps_d / (b' Omega^-1 b)       (units: +1 pp on the 2-year yield in the window),
on every weekday from 1990 (announcement days and all other days). Without the FCI the daily block has the yield only and s_d = eps_i.
Also: the measured window surprise on announcement days, the day's position in its month (k = 0, 1, ...) and the month's number of weekdays.
   python3 B1_daily_shocks.py  -> results_route2/daily_shocks_<step>_<fci>.csv, results_route2/daily_summary.csv"""
import numpy as np, pandas as pd
import lib_r2 as R
from lib import daily as DD
from lib.daily import EV, event_index, HAR, MON, CALW

M = R.M
OUT = R.Path(__file__).resolve().parent / "results_route2"; OUT.mkdir(exist_ok=True)
idx0 = event_index(); EVD = pd.DatetimeIndex(EV.d.values[idx0]); NS = pd.Series(EV.ns.values[idx0], index=EVD)

def daily_rows(form, fci):
    """As model.har_rows, from the first day with all regressors (1990), not only from DAILY_START."""
    D = M.daily_frame(form, fci).loc["1990-01-02":].dropna(); mo = D.index.to_period("M"); MMv = M.MAC[["u", "pi"]]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1) & (D.index <= "2026-09-30")
    return X[ok], Y[ok], D.index[ok]

def run(form, fci, est_start="1996"):
    Xn, Yn = M.har_rows(form, fci, ["u", "pi"], None, "in")                 # Note B's estimation sample (from 1996)
    Bd = M.har_fit(Xn, Yn, fci) if est_start == "1996" else None
    X, Y, dates = daily_rows(form, fci)
    if Bd is None: Bd = M.har_fit(X, Y, fci)                                 # check: daily block re-estimated on 1990-2026
    E = Y - X @ Bd; isev = dates.isin(EVD)
    b = M.impact(fci, idx0)
    if E.shape[1] == 1: s = E[:, 0]; Om = np.var(E[:, 0], ddof=1) * np.ones((1, 1))
    else:
        Om = np.cov(E.T); w = np.linalg.solve(Om, b); s = E @ w / float(b @ w)
    # position in the month (weekday calendar, as Note B's positions): k = index of the day among the month's weekdays, n = weekdays in the month
    cal = pd.Series(np.arange(len(CALW)), index=CALW); mon = CALW.to_period("M")
    k_all = cal.groupby(mon).cumcount(); n_all = cal.groupby(mon).transform("size")
    k = k_all.reindex(dates).values; n = n_all.reindex(dates).values
    df = pd.DataFrame(dict(date=dates, month=dates.to_period("M").astype(str), eps_pol=E[:, 0], eps_fci=(E[:, 1] if E.shape[1] > 1 else np.nan), s=s,
                           ann=isev.astype(int), ns=NS.reindex(dates).fillna(0.0).values, k=k, n=n))
    info = dict(form=form, fci=fci, est=est_start, b_F=(b[1] if len(b) > 1 else np.nan), sd_eps_pol=E[:, 0].std(), sd_eps_fci=(E[:, 1].std() if E.shape[1] > 1 else np.nan),
                corr_eps=(np.corrcoef(E.T)[0, 1] if E.shape[1] > 1 else np.nan), ordinary_loading=(np.cov(E[~isev].T)[0, 1] / E[~isev, 0].var(ddof=1) if E.shape[1] > 1 else np.nan),
                sd_s_all=s.std(), sd_s_ann=s[isev].std(), sd_s_other=s[~isev].std(), sd_ns=NS.std(), corr_s_ns_ann=np.corrcoef(s[isev], NS.reindex(dates[isev]).values)[0, 1],
                slope_s_on_ns_ann=np.polyfit(NS.reindex(dates[isev]).values, s[isev], 1)[0], n_days=len(s), n_ann=int(isev.sum()), first=str(dates[0].date()))
    return df, info

if __name__ == "__main__":
    infos = []
    for form in ("nom", "real", "rstar"):
        for fci in (0, form):
            for est in ("1996", "1990"):
                df, info = run(form, fci, est); infos.append(info)
                if est == "1996": df.to_csv(OUT / f"daily_shocks_{form}_{fci}.csv", index=False, float_format="%.6f")
    S = pd.DataFrame(infos); S.to_csv(OUT / "daily_summary.csv", index=False, float_format="%.4f"); print(S.round(3).to_string())
