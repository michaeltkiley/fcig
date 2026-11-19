"""How much do policy shocks explain? Historical and variance decompositions (Section 3.5; FS-A76, D6-D9; ported from explore_decomp/B5_route2_baseline.py, lib_r2.py, 01_run.py).

Route 1 (measured surprises): the window surprises of the 252 announcements (1996-2026) propagated through Note B's model. Identified with no further assumption.
Route 2 (policy-direction shocks):
  daily (April 1990 on): Note B's daily block (2-year yield, FCI and funds rate, real; baseline_real; estimated without March-December 2020) gives daily innovations eps_d; the shock of day d is the
     GLS projection on the window direction b = (1, b_F, b_ff):  s_d = b' Omega^-1 eps_d / b' Omega^-1 b, Omega the innovation covariance over 1990-2026 excluding March-December 2020.
     On announcement days s_d correlates with the measured surprise; on other days it is the movement of the yield and FCI in the window proportion.
  monthly (1974 to April 1990, before the daily data): a monthly VAR in monthly averages from 1973 (u gap, core inflation, 2-year yield [, FCI]; 12 lags; March-December 2020 dropped),
     shock e_t = b' S^-1 u_t / b' S^-1 b with b = (0, 0, window column) (lib/monthly.window_column), scaled to the daily shocks' monthly standard deviation over May 1990-2026 (2020 excluded).
Propagation: Note B's model (real, 12 lags, 2020 dropped) from 1996 and from 1973, day-of-month specific responses (120 months). Two treatments of March-December 2020: "infer"
(main: the estimated coefficients are applied to the 2020 data and those shocks decomposed like any other) and "absorb" (robustness: the month dummies absorb them; shocks set to zero).
Variance share at h: variance over the period of the contribution of the shocks of the last h months, divided by the data's h-month forecast-error variance (the monthly VAR above,
innovation covariance of the period); March-December 2020 excluded from the shares in both treatments. Bands: 5th-95th percentiles over the 500 block-bootstrap draws of Note B's responses
(output/draws of step 3; same specification).
Diagnostics (appendix): Route 2 from monthly VAR innovations alone (does the monthly VAR recover the window surprise? R-squared of the surprise on the month's innovations, correlation,
lead test) and a Monte Carlo with Note B's model as the true process (lib/simulate.py) in which the policy shock is the window surprise by construction.
Caveats (stated in the paper): within a day the shock is assumed recoverable from the yield and FCI innovations; the daily block is estimated from 1996 and applied from 1990; in the 1973
model the shock size and daily dynamics are those of 1996 on."""
import numpy as np, pandas as pd
from . import model as M, monthly as MO, daily as DD
from .daily import event_index, positions, HAR, CALW
from .paths import OUT

END = pd.Period(MO.END, "M")
MONTHS = pd.period_range("1974-01", END, freq="M"); NM = len(MONTHS); MI = {p: i for i, p in enumerate(MONTHS)}
COVID = (MONTHS >= pd.Period("2020-03", "M")) & (MONTHS <= pd.Period("2020-12", "M"))
ERAS = {"1974-1989": ("1974-01", "1989-12"), "1990-2026": ("1990-05", "2026-09"), "1996-2026": ("1996-01", "2026-09")}
SOURCES = ("spliced", "daily_all", "daily_other", "daily_ann", "measured")
HS = (12, 24, 36)
NAMES = ["u", "pi", "pol", "idx", "ff"]      # baseline_real: the funds rate last (names are taken from the data columns)
_idx0 = event_index(); _ev = DD.EV.iloc[_idx0]; _mon = _ev.Date.dt.to_period("M")
EVD = pd.DatetimeIndex(DD.EV.d.values[_idx0]); NS = pd.Series(DD.EV.ns.values[_idx0], index=EVD)
Z_FIRST, Z_LAST = _mon.min(), _mon.max(); ZFULL = _ev.ns.groupby(_mon).sum().reindex(pd.period_range(Z_FIRST, END, freq="M")).fillna(0.0)
def in_covid_day(d): return (d >= pd.Timestamp("2020-03-01")) & (d <= pd.Timestamp("2020-12-31"))

# ---------------------------------------------------------------- monthly VAR (monthly averages)
def monthly_var(step, fci, start="1973-01", L=12, t2020="out", wc_t2020="out", H=60):
    """Monthly VAR on monthly averages; rows from the first month with L lags (or start). Coefficients estimated without March-December 2020 when t2020 = "out" (innovations U are
    computed for every row, 2020 included). b = (0, 0, window column); e = recovered shock (zero in the dropped months). wc_t2020: 2020 treatment of the daily block behind the window column."""
    D = MO.data(step, fci); K = D.shape[1]
    X, Y, per = MO.design(D, L, str(max(D.index[L], pd.Period(start, "M"))), MO.END)
    keep = np.ones(len(per), bool) if t2020 == "in" else ~per.isin(MO.C2020)
    C = np.linalg.lstsq(X[keep], Y[keep], rcond=None)[0]; U = Y - X @ C; S = U[keep].T @ U[keep] / (keep.sum() - X.shape[1])
    T = MO.ma(C, K, L, max(H, len(per)))
    b = np.r_[0.0, 0.0, MO.window_column(step, fci, wc_t2020)][:K]
    Si = np.linalg.inv(S); w = Si @ b; d = float(b @ w); e = U @ w / d; e[~keep] = 0.0
    return dict(step=step, fci=fci, start=start, L=L, t2020=t2020, D=D, X=X, Y=Y, per=per, keep=keep, C=C, U=U, S=S, T=T, b=b, e=e, s2=1.0 / d, K=K, names=list(D.columns))

def all_shocks(T, U, keep):
    """Stochastic part of y_t: sum_j Theta_j u_{t-j} (2020 innovations zeroed where keep is False)."""
    Uk = U.copy(); Uk[~keep] = 0.0; n, K = U.shape; out = np.zeros((n, K))
    for i in range(K):
        for m in range(K): out[:, i] += np.convolve(Uk[:, m], T[:, i, m])[:n]
    return out

def fevd(T, S, r, s2, H=(1, 3, 6, 12, 24, 36, 60)):
    num = np.cumsum(r ** 2, axis=0) * s2; den = np.cumsum(np.einsum("hij,jk,hik->hi", T, S, T), axis=0)
    return {h: num[h - 1] / den[h - 1] for h in H}

def lead_lag_test(U, per, keep, k=6, lags=False):
    """Surprise z_t on u_t and u_{t+1..t+k} (leads) or u_{t-1..t-k} (lags), instrument months; HC1 Wald test that the extra coefficients are zero.
    Returns (R-squared with u_t only, R-squared with the extra terms, p-value, restrictions)."""
    from scipy import stats
    pos = {p: i for i, p in enumerate(per)}; rows, z = [], []
    for p in ZFULL.index:
        sh = [p + (j if not lags else -j) for j in range(1, k + 1)]
        if p not in pos or not all(q in pos for q in sh) or not keep[pos[p]] or not all(keep[pos[q]] for q in sh): continue
        rows.append(np.concatenate([U[pos[p]]] + [U[pos[q]] for q in sh])); z.append(ZFULL[p])
    Xr = np.column_stack([np.ones(len(rows)), np.array(rows)]); z = np.array(z); K = U.shape[1]
    def ols(X):
        xx = np.linalg.pinv(X.T @ X); bb = xx @ X.T @ z; return bb, z - X @ bb, xx
    _, r0, _ = ols(Xr[:, :1 + K]); bb, r, xx = ols(Xr); n, m = Xr.shape; V = xx @ (Xr.T * r ** 2) @ Xr @ xx * n / (n - m)
    R = np.arange(1 + K, m); W = bb[R] @ np.linalg.pinv(V[np.ix_(R, R)]) @ bb[R]; tss = ((z - z.mean()) ** 2).sum()
    return 1 - (r0 ** 2).sum() / tss, 1 - (r ** 2).sum() / tss, float(1 - stats.chi2.cdf(W, len(R))), len(R)

def diagnostics(c):
    """Monthly invertibility diagnostic for one monthly VAR (appendix): does the shock recovered from the month's innovations line up with the measured surprise?"""
    per, e, keep = c["per"], c["e"], c["keep"]; ok = (per >= Z_FIRST) & keep; z = ZFULL.reindex(per[ok]).fillna(0.0).values
    post = (per >= pd.Period("1996-01", "M")) & keep; Sp = np.cov(c["U"][post].T); s2_post = 1.0 / float(c["b"] @ np.linalg.inv(Sp) @ c["b"])
    s2_z = float((ZFULL.reindex(per[post]).fillna(0.0) ** 2).mean()); r2_0, r2_lead, p_lead, _ = lead_lag_test(c["U"], per, keep, 6)
    return dict(step=c["step"], fci=c["fci"], start=c["start"], L=c["L"], t2020=c["t2020"], first=str(per[0]), n=int(keep.sum()), F=MO.first_stage(c["U"][ok & (per <= Z_LAST)][:, 2], ZFULL.reindex(per[ok & (per <= Z_LAST)]).values)[1],
                r2_z_u=r2_0, r2_z_u_leads=r2_lead, p_leads=p_lead, p_lags=lead_lag_test(c["U"], per, keep, 6, lags=True)[2], corr_e_z=float(np.corrcoef(e[ok], z)[0, 1]),
                sd_e_post_inv=float(np.sqrt(s2_post)), sd_z=float(np.sqrt(s2_z)), var_ratio=float(s2_post / s2_z))

# ---------------------------------------------------------------- daily shocks and Note B's responses
def daily_shocks(form, fci, mode="infer"):
    """Daily policy-direction shocks from April 1990 (see the module notes); mode "absorb" sets March-December 2020 to zero."""
    Xn, Yn = M.har_rows(form, fci, ["u", "pi"], None, "out"); Bd = M.har_fit(Xn, Yn, fci)
    D = M.daily_frame(form, fci).loc["1990-01-02":].dropna(); mo = D.index.to_period("M"); MMv = M.MAC[["u", "pi"]]
    X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1) & (D.index <= "2026-09-30"); X, Y, dates = X[ok], Y[ok], D.index[ok]
    E = Y - X @ Bd; cv = in_covid_day(dates); b = M.impact(fci, _idx0)
    if E.shape[1] == 1: s = E[:, 0].copy()
    else: Om = np.cov(E[~cv].T); w = np.linalg.solve(Om, b); s = E @ w / float(b @ w)
    if mode == "absorb": s[cv] = 0.0
    cal = pd.Series(np.arange(len(CALW)), index=CALW); mon = CALW.to_period("M")
    return pd.DataFrame(dict(date=dates, t=[MI.get(p, -1) for p in dates.to_period("M")], s=s, ann=dates.isin(EVD).astype(int), ns=NS.reindex(dates).fillna(0.0).values,
                             k=cal.groupby(mon).cumcount().reindex(dates).values, n=cal.groupby(mon).transform("size").reindex(dates).values))

class NoteB:
    """Note B's point model (real with the funds rate, 2020 dropped) with responses for a shock on day k of an n-day month: (u, price level, yield, FCI) by month, h = 0..H."""
    def __init__(self, form, fci, start, L=12, H=120):
        Xd, Yd = M.har_rows(form, fci, ["u", "pi"], None, "out"); self.Bd = M.har_fit(Xd, Yd, fci); self.nd = Yd.shape[1]
        X, Y = M.macro_data(form, fci, ["u", "pi"], L, start, None, "out", "none"); self.C = np.linalg.lstsq(X, Y, rcond=None)[0]
        self.L, self.H, self.b = L, H, M.impact(fci, _idx0); self.cache = {}; self.pos0 = positions(_idx0)
    def resp(self, k, n):
        if (k, n) not in self.cache:
            m, fb, _ = M.simulate(self.Bd, self.C, 2, self.nd, self.L, self.b, int(k), int(n), months=self.H + 1); self.cache[(k, n)] = np.column_stack([m, fb])
        return self.cache[(k, n)]
    def resp_avg(self): return sum(w * self.resp(k0, n0) for k0, n0, w in self.pos0)

def conv(x, r): return np.column_stack([np.convolve(x, r[:, v])[:NM] for v in range(r.shape[1])])
def trunc(r, h): r = r.copy(); r[h:] = 0.0; return r

def contributions(nb, daily, pre, h=None):
    """Contributions (months x variables) of each shock source; h truncates the responses to the shocks of the last h months."""
    d = daily[daily.t >= 0]; out = {}
    for name, sel, col in (("daily_all", np.ones(len(d), bool), "s"), ("daily_other", d.ann.values == 0, "s"), ("daily_ann", d.ann.values == 1, "s"), ("measured", d.ann.values == 1, "ns")):
        g = d[sel].groupby(["k", "n", "t"])[col].sum(); tot = np.zeros((NM, 2 + nb.nd))
        for (k, n), gg in g.groupby(level=[0, 1]):
            x = np.zeros(NM); x[gg.index.get_level_values(2).values] = gg.values; r = nb.resp(k, n); tot += conv(x, r if h is None else trunc(r, h))
        out[name] = tot
    ra = nb.resp_avg(); out["monthly_pre1990"] = conv(pre, ra if h is None else trunc(ra, h)); out["spliced"] = out["monthly_pre1990"] + out["daily_all"]
    return out

def monthly_avg_resp(s, f):
    """(u, price level) and monthly-average financial responses -> (u, monthly inflation at an annual rate, yield, FCI)."""
    return np.column_stack([s[:, 0], 12 * np.diff(np.r_[0.0, s[:, 1]]), f])

def _draws(form, fci, start, B):
    """Bootstrap draws of Note B's responses (12 lags): step 3's saved draws when present, else re-estimated (same seeds, so identical)."""
    import importlib; CS = importlib.import_module("cases")
    c = dict(form=form, fci=fci, macro="u,pi", start=start, end=None, t2020="out", trend="none"); f = OUT / "draws" / f"{CS.case_id(c)}_L12.npz"
    if f.exists():
        z = np.load(f); return z["sd"], z["fd"], z["s0"], z["f0"]
    est = next(M.estimate(form, fci, "u,pi", start, None, "out", "none", B, (12,))); return est["sd"], est["fd"], est["s0"], est["f0"]

# ---------------------------------------------------------------- the decomposition
def run(fci, starts=("1973-01", "1996-01"), modes=("infer", "absorb"), B=500, wc_t2020="out", bands=True, save_hd=None, scale_pre=True):
    """Route 1 and Route 2 for the real model (baseline_real: 2-year yield and funds rate) without (fci = 0) or with the FCI ("real"). Returns shares, bands, overlap rows and the historical decompositions.
    scale_pre = False: the pre-1990 monthly shocks enter unscaled (robustness, D9)."""
    form = "real"
    c = monthly_var(form, fci, "1973-01", 12, "out", wc_t2020); names = c["names"]; em = pd.Series(c["e"], index=c["per"]).reindex(MONTHS).fillna(0.0)
    Uall = c["Y"] - c["X"] @ c["C"]
    DS = {mode: daily_shocks(form, fci, mode) for mode in ("infer", "absorb")}
    dmA = {mode: DS[mode][DS[mode].t >= 0].groupby("t").s.sum().reindex(range(NM)).fillna(0.0).values for mode in DS}
    ovm = (MONTHS >= pd.Period("1990-05", "M")) & ~COVID; sc = dmA["infer"][ovm].std() / em.values[ovm].std()
    overlap = dict(fci=fci, corr=np.corrcoef(dmA["infer"][ovm], em.values[ovm])[0, 1], sd_daily=dmA["infer"][ovm].std(), sd_monthly=em.values[ovm].std(), scale=sc)
    pre = np.where(MONTHS < pd.Period("1990-05", "M"), em.values, 0.0) * (sc if scale_pre else 1.0)
    S_ = {}
    for era, (lo, hi) in ERAS.items():
        m = (c["per"] >= pd.Period(lo, "M")) & (c["per"] <= pd.Period(hi, "M")) & c["keep"]; S_[era] = np.cov(Uall[m].T)
    fev = lambda h, era: np.einsum("hij,jk,hik->i", c["T"][:h], S_[era], c["T"][:h])
    rows, brows, hds = [], [], {}
    for start in starts:
        nb = NoteB(form, fci, start)
        if bands: sd, fd, s0_, f0_ = _draws(form, fci, start, B); rd = [monthly_avg_resp(sd[b], fd[b]) for b in range(len(sd))]; r0_ = monthly_avg_resp(s0_, f0_)
        for mode in modes:
            daily = DS[mode]; tag = f"{form}_{fci}_model{start[:4]}_{mode}"; Cfull = contributions(nb, daily, pre)
            keep = c["keep"] if mode == "absorb" else np.ones(len(c["per"]), bool)
            sto = pd.DataFrame(all_shocks(c["T"], Uall, keep), index=c["per"]).reindex(MONTHS)
            hds[tag] = pd.concat([pd.DataFrame(dict(month=MONTHS.astype(str), var=n, all_shocks_var=sto[i].values, **{k: v[:, i] for k, v in Cfull.items()})) for i, n in enumerate(names)])
            for h in HS:
                W = contributions(nb, daily, pre, h)
                for era, (lo, hi) in ERAS.items():
                    mm = (MONTHS >= pd.Period(lo, "M")) & (MONTHS <= pd.Period(hi, "M")) & ~COVID; F = fev(h, era)
                    for src in SOURCES:
                        if era == "1974-1989" and src != "spliced": continue
                        rows.append(dict(mode=mode, fci=fci, model=start[:4], h=h, era=era, source=src, **{n: W[src][mm, i].var() / F[i] for i, n in enumerate(names)}))
            if not bands: continue
            d = daily[daily.t >= 0]; dm = dmA[mode]
            series = {"spliced": pre + dm, "daily_all": dm, "daily_other": d[d.ann == 0].groupby("t").s.sum().reindex(range(NM)).fillna(0.0).values,
                      "measured": d[d.ann == 1].groupby("t").ns.sum().reindex(range(NM)).fillna(0.0).values}
            if save_hd is not None: np.savez_compressed(save_hd / f"bands_hd_{tag}.npz", hd=np.array([conv(series["spliced"], r) for r in rd], dtype=np.float32), months=MONTHS.astype(str).values)
            for h in HS:
                for era, (lo, hi) in ERAS.items():
                    mm = (MONTHS >= pd.Period(lo, "M")) & (MONTHS <= pd.Period(hi, "M")) & ~COVID; F = fev(h, era)
                    for src, x in series.items():
                        if era == "1974-1989" and src != "spliced": continue
                        dr = np.array([conv(x, trunc(r, h))[mm].var(axis=0) / F for r in rd]); d0 = conv(x, trunc(r0_, h))[mm].var(axis=0) / F      # FS-A108: bias-corrected bands around the point share
                        Q = M.IV.quantiles(dr, d0, (5, 95))
                        for i, n in enumerate(names): brows.append(dict(mode=mode, fci=fci, model=start[:4], h=h, era=era, source=src, var=n, p5=Q[0][i], p95=Q[1][i]))
    return dict(shares=rows, bands=brows, overlap=overlap, hd=hds, daily=DS)

def sim_invertibility(S=200, seed=b"r2sim"):
    """Monte Carlo (appendix): Note B's real model with the FCI as the true process (lib/simulate.py: 2020 dropped, monthly averages); on each sample the monthly VAR route is applied
    as to the data (12 lags; window column; shock from u_t). In the simulation the policy shock is the window surprise by construction."""
    import zlib
    from . import simulate as SIM
    dg = SIM.DGP(); rng = np.random.default_rng(zlib.crc32(seed)); m, fb, z = dg.simulate(S, rng); b = np.r_[0, 0, dg.win]; rows = []
    for s in range(S):
        Z = np.concatenate([m[s], fb[s]], axis=1); nm = Z.shape[0] - 12; L = 12
        X = np.column_stack([np.ones(nm)] + [Z[12 - l:12 - l + nm] for l in range(1, L + 1)]); Y = Z[12:]
        C = np.linalg.lstsq(X, Y, rcond=None)[0]; U = Y - X @ C; Sg = U.T @ U / (nm - X.shape[1]); T = MO.ma(C, Z.shape[1], L, 60)
        w = np.linalg.solve(Sg, b); d = float(b @ w); e = U @ w / d; zz = z[s]
        Zx = np.column_stack([np.ones(nm), U]); res = zz - Zx @ np.linalg.lstsq(Zx, zz, rcond=None)[0]; r2 = 1 - res @ res / ((zz - zz.mean()) @ (zz - zz.mean()))
        r = T @ b; up = fevd(T, Sg, r, 1 / d, (24,))[24]; lo = fevd(T, Sg, r, float((zz ** 2).mean()), (24,))[24]
        rows.append(dict(sim=s, r2_z_u=r2, corr_e_z=np.corrcoef(e, zz)[0, 1], sd_e=np.sqrt(1 / d), sd_z=np.sqrt((zz ** 2).mean()), var_ratio=(1 / d) / (zz ** 2).mean(),
                         fevd_u24_upper=up[0], fevd_u24_lower=lo[0], fevd_pi24_upper=up[1], fevd_pi24_lower=lo[1]))
    return pd.DataFrame(rows)
