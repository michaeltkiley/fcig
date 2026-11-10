"""Monte Carlo: how noisy is a monthly proxy VAR if the estimated model is the true process?

Data-generating process = the estimated r*-gap mixed-frequency model with the FCI (lib/model.py), the paper's baseline, with the data's calendar (weekdays 1996-01 to 2026-09, 369 months)
and the actual announcement days:  daily block f_d = B'x_d + eps_d (HAR regressors, macro first within the month) with a policy surprise s_j added on announcement days, f_d += b s_j,
b = (1, b_F) the window impact; monthly macro m_t = c + sum A_l m_{t-l} + sum G_l fbar_{t-l} + e_t, fbar the monthly average of the daily block. Policy therefore reaches unemployment
and inflation only through the 2-year yield and the FCI. Innovations are bootstrapped independently: daily eps_d from the model's daily residuals (non-announcement days; announcement days
purged of b s_j), monthly e_t jointly from its residuals; s_j drawn with replacement from the observed Nakamura-Steinsson surprises. Pre-sample lags are the actual 1995 data.
On each simulated sample the proxy VAR of lib/monthly.py (12 lags, instrument = surprises summed over the month, instrument months as in the data) is estimated with and without the FCI,
and the monthly window-impact estimator too. True responses: the model's own, per +1 pp in the window, and in the proxy VAR's unit (+1 pp on the monthly-average 2-year yield) as the ratio of the
window response to its contemporaneous monthly-average response [inference: ratio of averages]."""
import numpy as np, pandas as pd, zlib
from . import model as M
from . import monthly as MO
from .daily import CALW, MON, HAR, EV, event_index

L = 12
TARGETS = [("u", 12), ("u", 24), ("P", 12), ("P", 24), ("P", 36)]

class DGP:
    def __init__(self, start="1996-01"):
        form, fci = "rstar", "rstar"; self.mv = ["u", "pi"]
        D = M.daily_frame(form, fci).loc["1990-01-02":].dropna(); mo = D.index.to_period("M"); MMv = M.MAC[self.mv]
        X = np.column_stack([np.ones(len(D))] + [D.rolling(h).mean().shift(1).values for h in HAR] + [MMv.reindex(mo - 1).values, MMv.reindex(mo).values]); Y = D.values
        ok = ~np.isnan(X).any(axis=1) & ~np.isnan(Y).any(axis=1)
        self.Bd = np.linalg.lstsq(X[ok], Y[ok], rcond=None)[0]; self.rd = Y[ok] - X[ok] @ self.Bd; self.rd_dates = D.index[ok]
        Xm, Ym = M.macro_data(form, fci, self.mv, L, start, None, "in", "none"); self.C = np.linalg.lstsq(Xm, Ym, rcond=None)[0]; self.rm = Ym - Xm @ self.C
        self.idx0 = event_index(); self.s_obs = EV.ns.values[self.idx0]; self.b = M.impact(fci, self.idx0)
        self.ev_pos = CALW.get_indexer(pd.DatetimeIndex(EV.d.values[self.idx0])); assert (self.ev_pos >= 0).all()
        isev = np.isin(self.rd_dates, pd.DatetimeIndex(EV.d.values[self.idx0])); self.pool_non = self.rd[~isev]
        sj = pd.Series(self.s_obs, index=pd.DatetimeIndex(EV.d.values[self.idx0])); s_on = sj.reindex(self.rd_dates[isev]).values
        self.pool_ev = self.rd[isev] - np.outer(s_on, self.b); self.nd = self.rd.shape[1]          # event-day residuals purged of the policy impact
        est = next(M.estimate(form, fci, "u,pi", start, None, "in", "none", 5, (L,)))             # the model's own responses (point estimates)
        self.s0, self.f0 = est["s0"], est["f0"]; self.mon_avg = self.f0[0, 0]
        self.truth = {(v, h): self.s0[h, 0 if v == "u" else 1] / self.mon_avg for v, h in TARGETS}; self.truth_window = {(v, h): self.s0[h, 0 if v == "u" else 1] for v, h in TARGETS}
        self.truth_fci = self.f0[0, 1] / self.f0[0, 0]
        T0 = int(np.argmax(CALW >= pd.Timestamp("1996-01-01"))); T1 = int(np.max(np.where(CALW <= pd.Timestamp("2026-09-30"))[0])); self.T0, self.T1 = T0, T1
        self.months = pd.period_range("1996-01", "2026-09", freq="M"); mday = MON[T0:T1 + 1]
        self.bounds = [(int(np.argmax(mday == m)) + T0, int(np.max(np.where(mday == m)[0])) + T0) for m in self.months]
        self.F0 = M.daily_frame(form, fci).ffill().iloc[T0 - 70:T0].values; assert not np.isnan(self.F0).any()
        pre = pd.period_range("1995-01", "1995-12", freq="M"); self.m0 = M.MAC[self.mv].loc[pre].values; self.fb0 = M.fin_monthly(form, fci).loc[pre].values

    def simulate(self, S, rng):
        """S simulated samples: monthly macro (S, 12+M, 2) and financial averages (S, 12+M, 2) with the 12 pre-sample months first, and the monthly instrument (S, M)."""
        nd, K, nm = self.nd, 2, len(self.months); T = self.T1 + 1 - (self.T0 - 70)
        F = np.zeros((S, T, nd)); F[:, :70] = self.F0; cs = np.zeros((S, T + 1, nd)); cs[:, 1:71] = np.cumsum(F[:, :70], axis=1)
        m = np.zeros((S, 12 + nm, K)); m[:, :12] = self.m0; fb = np.zeros((S, 12 + nm, nd)); fb[:, :12] = self.fb0
        s_draw = rng.choice(self.s_obs, size=(S, len(self.s_obs)), replace=True); ev_day = {int(p) - (self.T0 - 70): j for j, p in enumerate(self.ev_pos)}
        z = np.zeros((S, nm)); starts = [b[0] for b in self.bounds]
        for j, p in enumerate(self.ev_pos): z[:, int(np.searchsorted(starts, p, side="right") - 1)] += s_draw[:, j]
        for t in range(nm):
            lags_m = np.concatenate([m[:, 12 + t - l] for l in range(1, L + 1)], axis=1); lags_f = np.concatenate([fb[:, 12 + t - l] for l in range(1, L + 1)], axis=1)
            x = np.concatenate([np.ones((S, 1)), lags_m, lags_f], axis=1); m[:, 12 + t] = x @ self.C + self.rm[rng.integers(0, len(self.rm), S)]       # macro first
            lo, hi = self.bounds[t]
            for tau in range(lo, hi + 1):
                k = tau - (self.T0 - 70)
                xd = np.concatenate([np.ones((S, 1))] + [(cs[:, k] - cs[:, k - h]) / h for h in HAR] + [m[:, 12 + t - 1], m[:, 12 + t]], axis=1)
                if k in ev_day: eps = self.pool_ev[rng.integers(0, len(self.pool_ev), S)] + s_draw[:, ev_day[k]][:, None] * self.b[None, :]
                else: eps = self.pool_non[rng.integers(0, len(self.pool_non), S)]
                F[:, k] = xd @ self.Bd + eps; cs[:, k + 1] = cs[:, k] + F[:, k]
            fb[:, 12 + t] = F[:, lo - (self.T0 - 70):hi - (self.T0 - 70) + 1].mean(axis=1)
        return m, fb, z

def proxy_stats(Z, z, ok, K):
    """Proxy VAR (12 lags, no trend) on Z = (12 pre-sample rows + sample, K variables [u, pi, i, (FCI)]): first stage, impact vector, point estimates and exact AR sets."""
    nm = Z.shape[0] - 12; X = np.column_stack([np.ones(nm)] + [Z[12 - l:12 - l + nm] for l in range(1, L + 1)]); Y = Z[12:]
    C = np.linalg.lstsq(X, Y, rcond=None)[0]; res = Y - X @ C; T = MO.ma(C, K, L)
    zz = z[ok]; r = res[ok]; g = np.array([MO.first_stage(r[:, j], zz)[0] for j in range(K)]); F = MO.first_stage(r[:, 2], zz)[1]; S = g / g[2]
    out = dict(F=F, impact_fci=(S[3] if K == 4 else np.nan))
    for v, h in TARGETS:
        c = MO.row_of(T, v, h); lo, hi, unb = MO.ar_set(r @ c, r[:, 2], zz)
        out.update({f"{v}{h}": float(c @ S), f"{v}{h}_lo": lo, f"{v}{h}_hi": hi, f"{v}{h}_unb": int(unb)})
    return out, T

def run(S=1000):
    """Simulate S samples and estimate on each: proxy VAR with and without the FCI, and the monthly window-impact estimator (with the FCI)."""
    dg = DGP(); rng = np.random.default_rng(zlib.crc32(b"sim|rstar|rstar")); m, fb, z = dg.simulate(S, rng)
    ev = EV.iloc[dg.idx0]; mon = ev.Date.dt.to_period("M"); ok = np.asarray((dg.months >= mon.min()) & (dg.months <= mon.max())); phi = MO.share(dg.idx0); rows = []
    for s in range(S):
        r4, T4 = proxy_stats(np.concatenate([m[s], fb[s]], axis=1), z[s], ok, 4); r3, _ = proxy_stats(np.concatenate([m[s], fb[s][:, :1]], axis=1), z[s], ok, 3)
        row = {f"fci_{k}": v for k, v in r4.items()}; row.update({f"nofci_{k}": v for k, v in r3.items()})
        row.update({f"we_{v}{h}": float(MO.row_of(T4, v, h) @ (phi * np.r_[0, 0, dg.b])) for v, h in TARGETS}); row["sim"] = s; rows.append(row)
    return dg, pd.DataFrame(rows)
