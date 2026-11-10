"""Monte Carlo: how would a monthly proxy VAR behave if the estimated model were the true process?

Data-generating process = the estimated mixed-frequency model of the baseline (lib/model.py), same calendar (weekdays 1996-01 to 2026-09, 369 months) and the actual announcement
days:  daily financial block f_d = B'x_d + eps_d (HAR regressors, macro first within the month) with a policy surprise s_j added on announcement days, f_d += b s_j,
b = (1, b_F) the window impact; monthly macro m_t = c + sum A_l m_{t-l} + sum G_l fbar_{t-l} + e_t, with fbar the monthly average of the daily block, so that policy reaches
unemployment and inflation only through the 2-year yield and the FCI. Innovations are bootstrapped: daily eps_d from the model's daily residuals (non-announcement days; announcement
days purged of b s_j), monthly e_t jointly from its residuals; s_j drawn with replacement from the observed Nakamura-Steinsson surprises. Pre-sample lags are the actual 1995 data.
On each simulated sample the proxy VAR of lib/monthly.py (12 lags, instrument = surprises summed over the month, instrument months as in the data) is estimated with and without
the FCI, and the window-impact monthly estimator too. The true process is always the r*-gap model with the FCI. The nominal and real versions are what a researcher who measures the 2-year yield and the FCI in nominal or real form
observes: the simulated r*-gap series plus the actual monthly gap between the nominal (real) and the r*-gap series (expected inflation and r*, and the corresponding terms of the index),
which do not depend on the policy shock. Compared with the data and with the true response, per +1 pp on the monthly-average 2-year yield
(true response = model response per +1 pp window / its contemporaneous monthly-average 2-year response [inference: ratio of averages])."""
import numpy as np, pandas as pd, zlib
from lib import model as M            # needs experimental/fin_shocks/baseline on PYTHONPATH
from lib import monthly as MO
from lib.daily import CALW, MON, HAR, EV, event_index

L = 12
TARGETS = [("u", 12), ("u", 24), ("P", 12), ("P", 24), ("P", 36)]

class DGP:
    def __init__(self, form, fci, start="1996-01"):
        self.form, self.fci, self.mv = form, fci, ["u", "pi"]
        # daily block (as lib.model.har_block) with residuals
        D = M.daily_frame(form, fci).loc["1990-01-02":].dropna(); mo = D.index.to_period("M"); MMv = M.MAC[self.mv]
        X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
        ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
        self.Bd = np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]; self.rd = Y[ok] - X[ok] @ self.Bd; self.rd_dates = D.index[ok]
        # monthly equations
        Xm, Ym = M.macro_data(form, fci, self.mv, L, start, None, "in", "none"); self.C = np.linalg.lstsq(Xm, Ym, rcond=None)[0]; self.rm = Ym - Xm @ self.C
        # announcements: 252 used; surprises, window impact
        self.idx0 = event_index(); self.s_obs = EV.ns.values[self.idx0]; self.b = M.impact(fci, self.idx0)
        self.ev_pos = CALW.get_indexer(pd.DatetimeIndex(EV.d.values[self.idx0])); assert (self.ev_pos >= 0).all()
        isev = np.isin(self.rd_dates, pd.DatetimeIndex(EV.d.values[self.idx0]))
        self.pool_non = self.rd[~isev]
        sj = pd.Series(self.s_obs, index=pd.DatetimeIndex(EV.d.values[self.idx0])); s_on = sj.reindex(self.rd_dates[isev]).values
        self.pool_ev = self.rd[isev] - np.outer(s_on, self.b)                 # event-day residuals purged of the policy impact
        self.rd_pur = self.rd.copy(); self.rd_pur[isev] = self.pool_ev        # the whole daily residual series with announcement days purged (used by the block bootstrap)
        self.nd = self.rd.shape[1]
        # truth: model response (window units) and contemporaneous monthly-average response
        est = next(M.estimate(form, fci, "u,pi", start, None, "in", "none", 5, (L,)))
        self.s0, self.f0 = est["s0"], est["f0"]
        self.mon_avg = self.f0[0, 0]
        self.truth = {(v, h): self.s0[h, 0 if v == "u" else 1] / self.mon_avg for v, h in TARGETS}
        self.truth_window = {(v, h): self.s0[h, 0 if v == "u" else 1] for v, h in TARGETS}
        self.truth_fci = (self.f0[0, 1] / self.f0[0, 0]) if fci else np.nan
        # calendar
        T0 = int(np.argmax(CALW >= pd.Timestamp("1996-01-01"))); T1 = int(np.max(np.where(CALW <= pd.Timestamp("2026-09-30"))[0])); self.T0, self.T1 = T0, T1
        self.months = pd.period_range("1996-01", "2026-09", freq="M"); mday = MON[T0:T1 + 1]
        self.bounds = [(int(np.argmax(mday == m)) + T0, int(np.max(np.where(mday == m)[0])) + T0) for m in self.months]
        # pre-sample actual data
        self.F0 = M.daily_frame(form, fci).ffill().iloc[T0 - 70:T0].values; assert not np.isnan(self.F0).any()
        pre = pd.period_range("1995-01", "1995-12", freq="M")
        self.m0 = M.MAC[self.mv].loc[pre].values; self.fb0 = M.fin_monthly(form, fci).loc[pre].values
        allm = pd.period_range("1995-01", "2026-09", freq="M"); base = M.fin_monthly("rstar", "rstar").loc[allm]
        T = self.T1 + 1 - (self.T0 - 70); sl = slice(self.T0 - 70, self.T1 + 1)
        self.off_daily = {"rstar": np.zeros((T, 2)), **{f: np.column_stack([(M.RATE[f] - M.RATE["rstar"]).ffill().values[sl], (M.FCI[f] - M.FCI["rstar"]).ffill().values[sl]]) for f in ("nom", "real")}}
        self.offset = {"rstar": np.zeros((len(allm), 2)), "nom": (M.fin_monthly("nom", "nom").loc[allm] - base).values, "real": (M.fin_monthly("real", "real").loc[allm] - base).values}

    def simulate(self, S, rng, block=None):
        """S simulated samples: monthly macro (S, M, 2), monthly financial averages (S, M, nd), the monthly instrument (S, M) and the daily series (S, T, nd).
        block=None: innovations drawn independently; block=(bm, bd): monthly residuals in blocks of bm months and daily residuals in blocks of bd days (keeps serial dependence and volatility clustering)."""
        nd, K, nm = self.nd, 2, len(self.months); T = self.T1 + 1 - (self.T0 - 70)
        F = np.zeros((S, T, nd)); F[:, :70] = self.F0; cs = np.zeros((S, T + 1, nd)); cs[:, 1:71] = np.cumsum(F[:, :70], axis=1)
        m = np.zeros((S, 12 + nm, K)); m[:, :12] = self.m0; fb = np.zeros((S, 12 + nm, nd)); fb[:, :12] = self.fb0
        s_draw = rng.choice(self.s_obs, size=(S, len(self.s_obs)), replace=True); ev_day = {int(p) - (self.T0 - 70): j for j, p in enumerate(self.ev_pos)}
        z = np.zeros((S, nm)); mon_of = {int(p): int(np.searchsorted([b[0] for b in self.bounds], p, side="right") - 1) for p in self.ev_pos}
        for j, p in enumerate(self.ev_pos): z[:, mon_of[int(p)]] += s_draw[:, j]
        Tsim = self.T1 + 1 - self.T0
        if block:
            bm, bd = block; ib = lambda n, b, nn: (rng.integers(0, n - b + 1, (S, int(np.ceil(nn / b))))[:, :, None] + np.arange(b)).reshape(S, -1)[:, :nn]
            e_all = self.rm[ib(len(self.rm), bm, nm)]; eps_all = self.rd_pur[ib(len(self.rd_pur), bd, Tsim)]
        for t in range(nm):
            # monthly macro first
            lags_m = np.concatenate([m[:, 12 + t - l] for l in range(1, L + 1)], axis=1); lags_f = np.concatenate([fb[:, 12 + t - l] for l in range(1, L + 1)], axis=1)
            x = np.concatenate([np.ones((S, 1)), lags_m, lags_f], axis=1); m[:, 12 + t] = x @ self.C + (e_all[:, t] if block else self.rm[rng.integers(0, len(self.rm), S)])
            lo, hi = self.bounds[t]
            for tau in range(lo, hi + 1):
                k = tau - (self.T0 - 70)
                means = [(cs[:, k] - cs[:, k - h]) / h for h in HAR]
                xd = np.concatenate([np.ones((S, 1))] + means + [m[:, 12 + t - 1], m[:, 12 + t]], axis=1)
                if block:
                    eps = eps_all[:, k - 70] + ((s_draw[:, ev_day[k]][:, None] * self.b[None, :]) if k in ev_day else 0.0)
                elif k in ev_day:
                    j = ev_day[k]; eps = self.pool_ev[rng.integers(0, len(self.pool_ev), S)] + s_draw[:, j][:, None] * self.b[None, :]
                else: eps = self.pool_non[rng.integers(0, len(self.pool_non), S)]
                F[:, k] = xd @ self.Bd + eps; cs[:, k + 1] = cs[:, k] + F[:, k]
            fb[:, 12 + t] = F[:, lo - (self.T0 - 70):hi - (self.T0 - 70) + 1].mean(axis=1)
        return m, fb, z, F

def proxy_stats(Z, z, ok, K, per_ok_first=None):
    """Proxy VAR (12 lags, no trend) on Z = (pre-sample 12 rows + sample, K variables [u, pi, i, (FCI)]): first stage, impact vector, point estimates and exact AR sets."""
    nm = Z.shape[0] - 12; X = np.column_stack([np.ones(nm)] + [Z[12 - l:12 - l + nm] for l in range(1, L + 1)]); Y = Z[12:]
    C = np.linalg.lstsq(X, Y, rcond=None)[0]; res = Y - X @ C; T = MO.ma(C, K, L)
    zz = z[ok]; r = res[ok]; g = np.array([MO.first_stage(r[:, j], zz)[0] for j in range(K)]); F = MO.first_stage(r[:, 2], zz)[1]; S = g / g[2]
    out = dict(F=F, impact_u=S[0], impact_pi=S[1], impact_fci=(S[3] if K == 4 else np.nan))
    for v, h in TARGETS:
        c = MO.row_of(T, v, h); lo, hi, unb = MO.ar_set(r @ c, r[:, 2], zz)
        out.update({f"{v}{h}": float(c @ S), f"{v}{h}_lo": lo, f"{v}{h}_hi": hi, f"{v}{h}_unb": int(unb)})
    return out, T

def window_stats(T, b, phi, K):
    s = phi * np.r_[0, 0, b]; return {f"we_{v}{h}": float(MO.row_of(T, v, h) @ s) for v, h in TARGETS}

# ---------------------------------------------------------------- the paper's estimator on the simulated samples
_G = {}
DTARGETS = [("u", 12), ("u", 24), ("P", 12), ("P", 24)]

def model_stats(dg, F, m, form, use_fci):
    """Estimate the mixed-frequency model (daily HAR block and monthly equations, 12 lags) on one simulated sample with the variables in the given form, with or without the FCI,
    and return its impulse responses (window units) at 12 and 24 months. F: daily r*-gap-form series incl. the 70 pre-sample days; m: monthly macro incl. 12 pre-sample months."""
    nd = 2 if use_fci else 1; K = 2; nm = len(dg.months); Fo = (F + dg.off_daily[form])[:, :nd]; T = Fo.shape[0]
    mo = np.concatenate([np.zeros(70, int) - 1, np.concatenate([[t] * (hi - lo + 1) for t, (lo, hi) in enumerate(dg.bounds)])])        # month index of each day (-1 = pre-sample)
    cs = np.vstack([np.zeros((1, nd)), np.cumsum(Fo, axis=0)]); kk = np.arange(70, T); mi = mo[kk]
    Xd = np.column_stack([np.ones(len(kk))] + [(cs[kk] - cs[kk - h]) / h for h in HAR] + [m[12 + mi - 1], m[12 + mi]]); Bd = np.linalg.lstsq(Xd, Fo[kk], rcond=None)[0]
    fbm = np.array([Fo[lo - (dg.T0 - 70):hi - (dg.T0 - 70) + 1].mean(axis=0) for lo, hi in dg.bounds]); fb = np.vstack([dg.fb0[:, :nd] + dg.offset[form][:12, :nd], fbm])
    Xm = np.array([np.r_[1.0, np.concatenate([m[12 + t - l] for l in range(1, L + 1)]), np.concatenate([fb[12 + t - l] for l in range(1, L + 1)])] for t in range(nm)])
    C = np.linalg.lstsq(Xm, m[12:], rcond=None)[0]
    idx0, pos0 = dg.idx0, M.events(1)[1]; mac, _ = M.irf(Bd, C, K, nd, L, idx0, pos0, "x" if use_fci else 0); lev = M.to_level(mac)
    return {f"{v}{h}": float(lev[h, 0 if v == "u" else 1]) for v, h in DTARGETS}

def _one(s):
    dg, F, m, fb, z, ok, phi = (_G[k] for k in ("dg", "F", "m", "fb", "z", "ok", "phi")); mrows, drows = [], []
    for form in ("rstar", "nom", "real"):
        f = fb[s] + dg.offset[form]; Z4 = np.concatenate([m[s], f], axis=1); Z3 = np.concatenate([m[s], f[:, :1]], axis=1)
        r4, T4 = proxy_stats(Z4, z[s], ok, 4); r3, _ = proxy_stats(Z3, z[s], ok, 3)
        row = {f"fci_{k}": v for k, v in r4.items()}; row.update({f"nofci_{k}": v for k, v in r3.items()}); row.update({f"fci_{k}": v for k, v in window_stats(T4, dg.b, phi, 4).items()})
        mrows.append(dict(sim=s, form=form, **row))
        for use_fci in (0, 1): drows.append(dict(sim=s, form=form, fci=use_fci, **model_stats(dg, F[s], m[s], form, use_fci)))
    return mrows, drows

def run_sims(S=500, block=None, jobs=4):
    """Simulate S samples from the r*-gap model (innovations iid or in blocks) and analyse each with (i) the monthly proxy VAR and window-impact estimator and (ii) the full daily-block
    model, with the 2-year yield and FCI in r*-gap, nominal and real form. Returns the DGP, a DataFrame of monthly estimators and a DataFrame of daily-block estimates."""
    dg = DGP("rstar", "rstar"); rng = np.random.default_rng(zlib.crc32(b"sim|rstar|rstar" + (b"" if not block else f"|block{block}".encode())))
    m, fb, z, F = dg.simulate(S, rng, block); ev = EV.iloc[dg.idx0]; mon = ev.Date.dt.to_period("M"); ok = np.asarray((dg.months >= mon.min()) & (dg.months <= mon.max()))
    _G.update(dg=dg, F=F, m=m, fb=fb, z=z, ok=ok, phi=MO.share(dg.idx0)); mr, dr = [], []
    if jobs > 1:
        from multiprocessing import Pool
        with Pool(jobs) as p:
            for a, b in p.imap_unordered(_one, range(S), chunksize=5): mr += a; dr += b
    else:
        for s_ in range(S): a, b = _one(s_); mr += a; dr += b
    return dg, pd.DataFrame(mr).sort_values(["form", "sim"]).reset_index(drop=True), pd.DataFrame(dr).sort_values(["form", "fci", "sim"]).reset_index(drop=True)
