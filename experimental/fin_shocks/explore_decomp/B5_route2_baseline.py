"""Part B5: Route 2 with the proposed baselines (D-A21, D-A22): Note B's model, r*-gap, 12 lags, March-December 2020 dropped, propagation with the model from 1973 and from 1996;
r*-gap with the FCI (main) and the 2-year yield alone (comparison).
Shocks: (i) daily from April 1990: Note B's daily block estimated without March-December 2020; s_d = b'Omega^-1 eps_d / b'Omega^-1 b (Omega over 1990-2026 excluding those months).
Two treatments of March-December 2020 (D-A23): "infer" (main): the estimated coefficients are applied to the 2020 data and the 2020 shocks are recovered and decomposed like any
other; "absorb" (robustness): the month dummies absorb March-December 2020, so the recovered shocks of those days are zero and those months are left out of the variance shares; (ii) monthly 1974-April 1990: monthly VAR in monthly averages from 1973 (12 lags, window column,
2020 months dummied), scaled to the daily shocks' monthly standard deviation over May 1990-2026 (2020 months excluded) as in D-A13; (iii) measured window surprises.
Responses: exact day-of-month responses from Note B's model (point estimates, 120 months); bands from 500 block-bootstrap draws of Note B's responses (same specification;
month-aggregated shocks, 36-month responses). Variance share at h: variance over the period (March-December 2020 excluded in the absorb case only) of the contribution of the shocks of the last h months,
divided by the data's h-month forecast-error variance (monthly VAR in monthly averages from 1973, 12 lags, 2020 months dummied, innovation covariance of the period).
   python3 B5_route2_baseline.py [--draws 500]  -> results_route2_base/"""
import argparse, os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, pandas as pd
import lib_r2 as R
from lib import daily as DD
from lib.daily import event_index, positions, HAR, CALW

M = R.M
OUT = R.Path(__file__).resolve().parent / "results_route2_base"; OUT.mkdir(exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument("--draws", type=int, default=500); a = ap.parse_args()
idx0 = event_index(); POS0 = positions(idx0); EVD = pd.DatetimeIndex(DD.EV.d.values[idx0]); NS = pd.Series(DD.EV.ns.values[idx0], index=EVD)
MONTHS = pd.period_range("1974-01", R.END, freq="M"); NM = len(MONTHS); MI = {p: i for i, p in enumerate(MONTHS)}
COVID = (MONTHS >= pd.Period("2020-03", "M")) & (MONTHS <= pd.Period("2020-12", "M"))
ERAS = {"1974-1989": ("1974-01", "1989-12"), "1990-2026": ("1990-05", "2026-09"), "1996-2026": ("1996-01", "2026-09")}
in_covid_day = lambda d: (d >= pd.Timestamp("2020-03-01")) & (d <= pd.Timestamp("2020-12-31"))

def daily_shocks(form, fci, mode="infer"):
    Xn, Yn = M.har_rows(form, fci, ["u", "pi"], None, "out"); Bd = M.har_fit(Xn, Yn, fci)
    D = M.daily_frame(form, fci).loc["1990-01-02":].dropna(); mo = D.index.to_period("M"); MMv = M.MAC[["u", "pi"]]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1) & (D.index <= "2026-09-30"); X, Y, dates = X[ok], Y[ok], D.index[ok]
    E = Y - X @ Bd; cv = in_covid_day(dates); b = M.impact(fci, idx0)
    if E.shape[1] == 1: s = E[:, 0].copy()
    else: Om = np.cov(E[~cv].T); w = np.linalg.solve(Om, b); s = E @ w / float(b @ w)
    if mode == "absorb": s[cv] = 0.0                                         # robustness: the dummies absorb March-December 2020
    cal = pd.Series(np.arange(len(CALW)), index=CALW); mon = CALW.to_period("M")
    return pd.DataFrame(dict(date=dates, t=[MI.get(p, -1) for p in dates.to_period("M")], s=s, ann=dates.isin(EVD).astype(int), ns=NS.reindex(dates).fillna(0.0).values,
                             k=cal.groupby(mon).cumcount().reindex(dates).values, n=cal.groupby(mon).transform("size").reindex(dates).values))

class NoteB:
    def __init__(self, form, fci, start, L=12, H=120):
        Xd, Yd = M.har_rows(form, fci, ["u", "pi"], None, "out"); self.Bd = M.har_fit(Xd, Yd, fci); self.nd = Yd.shape[1]
        X, Y = M.macro_data(form, fci, ["u", "pi"], L, start, None, "out", "none"); self.C = np.linalg.lstsq(X, Y, rcond=None)[0]; self.L, self.H, self.b = L, H, M.impact(fci, idx0); self.cache = {}
    def resp(self, k, n):
        if (k, n) not in self.cache:
            m, fb, fe, _ = M.simulate(self.Bd, self.C, 2, self.nd, self.L, self.b, int(k), int(n), months=self.H + 1); self.cache[(k, n)] = np.column_stack([m, fb])
        return self.cache[(k, n)]
    def resp_avg(self): return sum(w * self.resp(k0, n0) for k0, n0, w in POS0)

def conv(x, r): return np.column_stack([np.convolve(x, r[:, v])[:NM] for v in range(r.shape[1])])
def trunc(r, h): r = r.copy(); r[h:] = 0.0; return r

def contributions(nb, daily, em_scaled, h=None):
    d = daily[daily.t >= 0]; out = {}
    for name, sel, col in (("daily_all", np.ones(len(d), bool), "s"), ("daily_other", d.ann.values == 0, "s"), ("daily_ann", d.ann.values == 1, "s"), ("measured", d.ann.values == 1, "ns")):
        g = d[sel].groupby(["k", "n", "t"])[col].sum(); tot = np.zeros((NM, 2 + nb.nd))
        for (k, n), gg in g.groupby(level=[0, 1]):
            x = np.zeros(NM); x[gg.index.get_level_values(2).values] = gg.values; r = nb.resp(k, n); tot += conv(x, r if h is None else trunc(r, h))
        out[name] = tot
    ra = nb.resp_avg(); out["monthly_pre1990"] = conv(em_scaled, ra if h is None else trunc(ra, h)); out["spliced"] = out["monthly_pre1990"] + out["daily_all"]
    return out

def monthly_avg_resp(s, f):
    pi = 12 * np.diff(np.r_[0.0, s[:, 1]]); return np.column_stack([s[:, 0], pi, f])

if __name__ == "__main__":
    rows, ov, bands = [], [], []
    for fci in ("rstar", 0):
        names = ["u", "pi", "pol", "idx"][:2 + (2 if fci else 1)]
        c = R.run("rstar", fci, "avg", "1973-01", 12, "WE", "dummy"); em = pd.Series(c["e"], index=c["per"]).reindex(MONTHS).fillna(0.0)
        Uall = c["Y"] - c["X"] @ c["C"]                                             # innovations with the estimated coefficients, 2020 included
        DS = {mode: daily_shocks("rstar", fci, mode) for mode in ("infer", "absorb")}
        for mode, daily in DS.items(): daily.to_csv(OUT / f"daily_shocks_rstar_{fci}_{mode}.csv", index=False, float_format="%.6f")
        dmA = {mode: DS[mode][DS[mode].t >= 0].groupby("t").s.sum().reindex(range(NM)).fillna(0.0).values for mode in DS}
        ovm = (MONTHS >= pd.Period("1990-05", "M")) & ~COVID; sc = dmA["infer"][ovm].std() / em.values[ovm].std()
        ov.append(dict(fci=fci, corr=np.corrcoef(dmA["infer"][ovm], em.values[ovm])[0, 1], sd_daily=dmA["infer"][ovm].std(), sd_monthly=em.values[ovm].std(), scale=sc))
        pre = np.where(MONTHS < pd.Period("1990-05", "M"), em.values, 0.0) * sc
        def fev_fn(mode):
            S_ = {}
            for era, (lo, hi) in ERAS.items():
                m = (c["per"] >= pd.Period(lo, "M")) & (c["per"] <= pd.Period(hi, "M")) & (c["keep"] if mode == "absorb" else True); S_[era] = np.cov(Uall[m].T)
            return lambda h, era: np.einsum("hij,jk,hik->i", c["T"][:h], S_[era], c["T"][:h])
        for start in ("1973-01", "1996-01"):
            nb = NoteB("rstar", fci, start)
            est = next(M.estimate("rstar", fci, "u,pi", start, None, "out", "none", a.draws, (12,)))
            rd = [monthly_avg_resp(est["sd"][b], est["fd"][b]) for b in range(len(est["sd"]))]
            for mode, daily in DS.items():
                tag = f"rstar_{fci}_model{start[:4]}_{mode}"; fev = fev_fn(mode); excl = COVID if mode == "absorb" else np.zeros(NM, bool)
                Cfull = contributions(nb, daily, pre)
                keep = c["keep"] if mode == "absorb" else np.ones(len(c["per"]), bool)
                sto = pd.DataFrame(R.all_shocks(c["T"], Uall, keep), index=c["per"]).reindex(MONTHS)
                pd.concat([pd.DataFrame(dict(month=MONTHS.astype(str), var=n, all_shocks_var=sto[i].values, **{k: v[:, i] for k, v in Cfull.items()})) for i, n in enumerate(names)]).to_csv(
                    OUT / f"hd_{tag}.csv", index=False, float_format="%.5f")
                for h in (12, 24, 36):
                    W = contributions(nb, daily, pre, h)
                    for era, (lo, hi) in ERAS.items():
                        mm = (MONTHS >= pd.Period(lo, "M")) & (MONTHS <= pd.Period(hi, "M")) & ~excl; F = fev(h, era)
                        for src in ("spliced", "daily_all", "daily_other", "daily_ann", "measured"):
                            if era == "1974-1989" and src != "spliced": continue
                            rows.append(dict(mode=mode, fci=fci, model=start[:4], h=h, era=era, source=src, **{n: W[src][mm, i].var() / F[i] for i, n in enumerate(names)}))
                d = daily[daily.t >= 0]; dm = dmA[mode]
                series = {"spliced": pre + dm, "daily_all": dm, "daily_other": d[d.ann == 0].groupby("t").s.sum().reindex(range(NM)).fillna(0.0).values,
                          "measured": d[d.ann == 1].groupby("t").ns.sum().reindex(range(NM)).fillna(0.0).values}
                np.savez_compressed(OUT / f"bands_hd_{tag}.npz", hd=np.array([conv(series["spliced"], r) for r in rd], dtype=np.float32), months=MONTHS.astype(str).values)
                for h in (12, 24, 36):
                    for era, (lo, hi) in ERAS.items():
                        mm = (MONTHS >= pd.Period(lo, "M")) & (MONTHS <= pd.Period(hi, "M")) & ~excl; F = fev(h, era)
                        for src, x in series.items():
                            if era == "1974-1989" and src != "spliced": continue
                            dr = np.array([conv(x, trunc(r, h))[mm].var(axis=0) / F for r in rd])
                            for i, n in enumerate(names): bands.append(dict(mode=mode, fci=fci, model=start[:4], h=h, era=era, source=src, var=n, p5=np.percentile(dr[:, i], 5), p95=np.percentile(dr[:, i], 95)))
                print(fci, start, mode, flush=True)
    pd.DataFrame(rows).to_csv(OUT / "shares.csv", index=False, float_format="%.5f"); pd.DataFrame(ov).to_csv(OUT / "overlap.csv", index=False, float_format="%.4f")
    pd.DataFrame(bands).to_csv(OUT / "bands_shares.csv", index=False, float_format="%.5f"); print(pd.DataFrame(ov).round(3).to_string())
