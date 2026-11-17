"""Part B2: Route 2 historical and variance decompositions through Note B's own model (D-A11 to D-A14).
Shocks (all in units of +1 pp on the 2-year yield in the window):
  daily_all    s_d from Note B's daily innovations (B1), every weekday 1990-2026
  daily_ann    the same, announcement days only;  daily_other: all other days
  measured     the measured window surprises (Route 1), 1996-2026
  monthly      e_t recovered from the monthly VAR in monthly averages (window column, 12 lags, from 1973; lib_r2), used for 1974-1989 (spliced with daily_all from April 1990)
Responses: Note B's model with the monthly equations from 1973 (R1a; daily block from 1996), 12 lags, point estimates. A daily shock enters on its own day of the month
(responses simulated for each position k and month length n, 120 months); a monthly shock enters with the response averaged over announcement positions (as the window column).
Historical decomposition H_t = sum of responses to all shocks dated up to t. Variance share at h: Var_t[contribution of the shocks of the last h months] / forecast-error variance
of the data at h (monthly VAR in monthly averages from 1973, 12 lags, innovation covariance of the same period).
   python3 B2_route2.py [--start 1973-01]  -> results_route2/hd_<step>_<fci>.csv, results_route2/shares.csv, results_route2/overlap.csv"""
import argparse
import numpy as np, pandas as pd
import lib_r2 as R
from lib.daily import event_index, positions

M = R.M
OUT = R.Path(__file__).resolve().parent / "results_route2"
ap = argparse.ArgumentParser(); ap.add_argument("--start", default="1973-01"); ap.add_argument("--hmax", type=int, default=120); a = ap.parse_args()
idx0 = event_index(); POS0 = positions(idx0)
MONTHS = pd.period_range("1974-01", R.END, freq="M"); NM = len(MONTHS); MI = {p: i for i, p in enumerate(MONTHS)}
ERAS = {"1974-1989": ("1974-01", "1989-12"), "1990-2026": ("1990-05", "2026-09"), "1996-2026": ("1996-01", "2026-09")}

class NoteB:
    """Note B's model (point estimates) for one case; responses to a window shock at day k of a month of n weekdays."""
    def __init__(self, form, fci, start, L=12, H=a.hmax):
        mv = ["u", "pi"]; Xd, Yd = M.har_rows(form, fci, mv, None, "in"); self.Bd = M.har_fit(Xd, Yd, fci); self.nd = Yd.shape[1]
        X, Y = M.macro_data(form, fci, mv, L, start, None, "in", "none"); self.C = np.linalg.lstsq(X, Y, rcond=None)[0]
        self.L, self.H, self.b = L, H, M.impact(fci, idx0); self.cache = {}
    def resp(self, k, n):
        if (k, n) not in self.cache:
            m, fb, fe, _ = M.simulate(self.Bd, self.C, 2, self.nd, self.L, self.b, int(k), int(n), months=self.H + 1)
            self.cache[(k, n)] = np.column_stack([m, fb])                       # u, pi (monthly, annual rate), yield [, FCI] (monthly averages)
        return self.cache[(k, n)]
    def resp_avg(self): return sum(w * self.resp(k0, n0) for k0, n0, w in POS0)

def conv(series, r):
    """series (NM,) monthly shock sums, r (H+1, V) responses -> (NM, V) contributions."""
    return np.column_stack([np.convolve(series, r[:, v])[:NM] for v in range(r.shape[1])])

SCALE = {}                                                                          # (step, fci) -> sd ratio used to put the pre-1990 monthly shocks on the daily scale

def contributions(nb, daily, monthly_e, scale=1.0):
    """Historical contributions (NM, V) of each source, at exact positions for daily shocks."""
    out = {}
    d = daily[daily.month.map(lambda m: pd.Period(m, "M") in MI)].copy(); d["t"] = d.month.map(lambda m: MI[pd.Period(m, "M")])
    for name, sel in (("daily_all", d.index == d.index), ("daily_ann", d.ann.values == 1), ("daily_other", d.ann.values == 0)):
        g = d[sel].groupby(["k", "n", "t"]).s.sum(); tot = None
        for (k, n), gg in g.groupby(level=[0, 1]):
            ser = np.zeros(NM); ser[gg.index.get_level_values(2).values] = gg.values; c = conv(ser, nb.resp(k, n)); tot = c if tot is None else tot + c
        out[name] = tot
    g = d[d.ann == 1].groupby(["k", "n", "t"]).ns.sum(); tot = None                 # measured surprises at their own positions
    for (k, n), gg in g.groupby(level=[0, 1]):
        ser = np.zeros(NM); ser[gg.index.get_level_values(2).values] = gg.values; c = conv(ser, nb.resp(k, n)); tot = c if tot is None else tot + c
    out["measured"] = tot
    em = monthly_e.reindex(MONTHS).fillna(0.0).values; ra = nb.resp_avg()
    pre = np.where(MONTHS < pd.Period("1990-05", "M"), em, 0.0)                    # first full month of daily shocks: May 1990 (daily innovations start mid-April)
    out["monthly_pre1990"] = conv(pre, ra); out["monthly_all"] = conv(em, ra)
    out["spliced_raw"] = out["monthly_pre1990"] + out["daily_all"]
    out["spliced"] = scale * out["monthly_pre1990"] + out["daily_all"]          # main (D-A13): pre-1990 monthly shocks rescaled to the daily shocks' monthly sd over 1990-2026
    return out

def window_contrib(nb, daily, monthly_e, h, scale=1.0):
    """Contributions of the shocks dated in the last h months only (t-h+1..t): sum over j<h of r(j) x shocks(t-j); all sources."""
    return contributions(_Trunc(nb, h), daily, monthly_e, scale)

class _Trunc:
    def __init__(self, nb, h): self.nb, self.h = nb, h
    def resp(self, k, n): r = self.nb.resp(k, n).copy(); r[self.h:] = 0.0; return r
    def resp_avg(self): r = self.nb.resp_avg().copy(); r[self.h:] = 0.0; return r

def data_fev(step, fci, h, era):
    """Forecast-error variance at h of the data: monthly VAR in monthly averages from 1973 (12 lags), innovation covariance over the era."""
    c = R.run(step, fci, "avg", "1973-01", 12, "WE", "in"); lo, hi = map(lambda x: pd.Period(x, "M"), ERAS[era]); m = (c["per"] >= lo) & (c["per"] <= hi)
    S = np.cov(c["U"][m].T); T = c["T"][:h]
    return np.einsum("hij,jk,hik->i", T, S, T), c

if __name__ == "__main__":
    rows, ov = [], []
    for step in ("rstar", "nom", "real"):
        for fci in (step, 0):
            daily = pd.read_csv(OUT / f"daily_shocks_{step}_{fci}.csv"); c12 = R.run(step, fci, "avg", "1973-01", 12, "WE", "in")
            em = pd.Series(c12["e"], index=c12["per"])
            # overlap: monthly VAR shock vs monthly sum of daily shocks (1990-05 to 2026-09)
            dm = daily.groupby("month").s.sum(); dm.index = pd.PeriodIndex(dm.index, freq="M"); o = pd.concat([em.rename("e"), dm.rename("d")], axis=1).loc["1990-05":"2026-09"].dropna()
            dn = dm.shift(-1).rename("dnext"); o = o.join(dn, how="left").dropna()
            fit = np.linalg.lstsq(np.column_stack([np.ones(len(o)), o.d, o.dnext]), o.e, rcond=None)
            r2 = 1 - ((o.e - np.column_stack([np.ones(len(o)), o.d, o.dnext]) @ fit[0]) ** 2).sum() / ((o.e - o.e.mean()) ** 2).sum()
            ov.append(dict(step=step, fci=fci, corr_same_month=np.corrcoef(o.e, o.d)[0, 1], r2_same_and_next=r2, sd_monthly_var_shock=o.e.std(), sd_daily_sum=o.d.std(),
                           sd_monthly_var_shock_pre1990=em.loc[:"1989-12"].std(), scale=o.d.std() / o.e.std(), proj_slope=np.polyfit(o.e, o.d, 1)[0]))
            scale = o.d.std() / o.e.std()
            nb = NoteB(step, fci, a.start); V = 2 + nb.nd; names = ["u", "pi", "pol", "idx"][:V]
            C = contributions(nb, daily, em, scale)
            # historical decomposition file (with the data's all-shocks component from the monthly VAR, for reference)
            sto = R.all_shocks(c12["T"], c12["U"], c12["keep"]); sto = pd.DataFrame(sto, index=c12["per"]).reindex(MONTHS)
            frames = []
            for v, nm in enumerate(names):
                frames.append(pd.DataFrame(dict(month=MONTHS.astype(str), var=nm, all_shocks_var=sto[v].values, **{k: C[k][:, v] for k in C})))
            pd.concat(frames).to_csv(OUT / f"hd_{step}_{fci}.csv", index=False, float_format="%.5f")
            for h in (1, 12, 24, 36):
                for era in ERAS:
                    fev, _ = data_fev(step, fci, h, era); lo, hi = map(lambda x: pd.Period(x, "M"), ERAS[era]); m = (MONTHS >= lo) & (MONTHS <= hi)
                    W = window_contrib(nb, daily, em, h, scale)
                    for src in ("spliced", "spliced_raw", "daily_all", "daily_other", "daily_ann", "measured", "monthly_all"):
                        if era == "1974-1989" and src not in ("spliced", "spliced_raw", "monthly_all"): continue
                        x = W[src][m]
                        rows.append(dict(step=step, fci=fci, h=h, era=era, source=src, **{n: x[:, i].var() / fev[i] for i, n in enumerate(names)}))
            print(step, fci, flush=True)
    pd.DataFrame(rows).to_csv(OUT / "shares.csv", index=False, float_format="%.5f"); pd.DataFrame(ov).to_csv(OUT / "overlap.csv", index=False, float_format="%.4f")
    print(pd.DataFrame(ov).round(3).to_string())
