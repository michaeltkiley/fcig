"""Real case with an unobserved random-walk r* filtered inside the VAR: Note B's real case with the FCI, 12 lags, from 1996 and from 1973 (2 cases; author, 18 Nov 2026).
Monthly VAR in gaps (monthly averages, as Note B's monthly series): g_t = (u_t, pi_t, x_t - r_t, F_t - c r_t) = c0 + sum_{l=1..12} A_l g_{t-l} + e_t,  e_t ~ N(0, S);  r_t = r_{t-1} + eta_t, eta_t ~ N(0, q).
x = real 2-year, F = real market index; c = w_y10 + |w_eq| x 100 / mean(E/P) = 1.53 (the FCI's loading on r* in Note A's r*-gap formula). State alpha_t = (r_t, ..., r_{t-12});
observation Y_t - c0 - sum A_l Y_{t-l} = Z alpha_t + e_t, Z = [d, -A_1 d, ..., -A_12 d], d = (0, 0, 1, c). Exact EM (Kalman filter and smoother; M-step = OLS on the smoothed moments; q updated) = MLE.
March-December 2020: no observation (as the model drops them). The r* level is not identified (absorbed by c0); its prior is centred at LW at the start.
IRFs (point estimates, per +1 pp on the 2-year in the window): (A) this VAR with Note B's window impact; (B) Note B's mixed-frequency model with the one-sided filtered r*_t|t in place of LW.
Comparison: the same VAR with LW r* (A) and Note B's stored r*-gap and real results (B). Writes rw_real.md, rw_real_rstar.csv."""
import os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
HERE = Path(__file__).resolve().parent; BASE = HERE.parent / "baseline"; sys.path.insert(0, str(BASE)); os.chdir(BASE)
import numpy as np, pandas as pd
from lib import model as M, monthly as MV, noteA
from lib.daily import interp_monthly, POL
D0 = M.D0; L = 12; END = pd.Period("2026-09", "M"); C2020 = pd.period_range("2020-03", "2020-12", freq="M"); HS = (6, 12, 18, 24, 36)
w = pd.read_csv(M.OUT / "market_weights.csv", index_col=0).weight
CF = float(w["y10"] + (-w["equities"]) * 100 / (100 / D0.cape).loc[noteA.START:noteA.END].mean())
MAXIT = int(os.environ.get("MAXIT", "3000"))

class RW:
    def __init__(self, start):
        D = M.MAC[["u", "pi"]].join(M.fin_monthly("real", "real"), how="inner").dropna(); D = D[D.index <= END]; self.K = K = D.shape[1]; self.d = d = np.r_[0, 0, 1, CF]
        P0 = max(pd.Period(start, "M"), D.index[0] + L); self.per = pd.period_range(P0, END, freq="M"); self.T = T = len(self.per)
        self.Y = D.reindex(pd.period_range(P0 - L, END, freq="M")).values; assert not np.isnan(self.Y).any()
        self.obs = ~self.per.isin(C2020); self.m0 = float(D0["rstar LW"].loc[P0 - 1]); n = L + 1
        self.Tm = np.zeros((n, n)); self.Tm[0, 0] = 1; self.Tm[1:, :-1] = np.eye(L)
        self.Xd = np.column_stack([np.ones(T)] + [self.Y[L - l:L - l + T] for l in range(1, L + 1)])        # data part of the regressors [1, Y_{t-1}, ..., Y_{t-12}]
        self.Yd = self.Y[L:]
        self.Bx = np.zeros((1 + K * L, n)); [self.Bx.__setitem__((slice(1 + K * (l - 1), 1 + K * l), l), -d) for l in range(1, L + 1)]   # loading of the regressors on alpha_t
        self.By = np.zeros((K, n)); self.By[:, 0] = -d
    def kalman(self, C, S, q):
        K, n, d, T = self.K, L + 1, self.d, self.T; A = [C[1 + K * (l - 1):1 + K * l].T for l in range(1, L + 1)]
        Z = np.column_stack([d] + [-A[l - 1] @ d for l in range(1, L + 1)]); W = self.Yd - self.Xd @ C            # w_t = Y_t - c0 - sum A_l Y_{t-l}
        a = np.full(n, self.m0); P = 4.0 * np.ones((n, n)) + q * np.minimum.outer(np.arange(n), np.arange(n)); Tm = self.Tm; ll = 0.0
        ap = np.zeros((T, n)); Pp = np.zeros((T, n, n)); af = np.zeros((T, n)); Pf = np.zeros((T, n, n))
        for i in range(T):
            a = Tm @ a; P = Tm @ P @ Tm.T; P[0, 0] += q; ap[i] = a; Pp[i] = P
            if self.obs[i]:
                v = W[i] - Z @ a; ZP = Z @ P; F = ZP @ Z.T + S; Fi = np.linalg.inv(F); Kg = ZP.T @ Fi
                a = a + Kg @ v; P = P - Kg @ ZP; P = (P + P.T) / 2; ll += -0.5 * (K * np.log(2 * np.pi) + np.linalg.slogdet(F)[1] + v @ Fi @ v)
            af[i] = a; Pf[i] = P
        as_ = af.copy(); Ps = Pf.copy(); Pl = np.zeros((T, n, n))
        for i in range(T - 2, -1, -1):
            J = Pf[i] @ Tm.T @ np.linalg.pinv(Pp[i + 1]); as_[i] = af[i] + J @ (as_[i + 1] - ap[i + 1]); Ps[i] = Pf[i] + J @ (Ps[i + 1] - Pp[i + 1]) @ J.T
        return af, ll, as_, Ps
    def mstep(self, as_, Ps):
        o = self.obs; X = self.Xd[o] + as_[o] @ self.Bx.T; Y = self.Yd[o] + as_[o] @ self.By.T; Pt = Ps[o].sum(axis=0)
        xx = X.T @ X + self.Bx @ Pt @ self.Bx.T; xy = X.T @ Y + self.Bx @ Pt @ self.By.T; yy = Y.T @ Y + self.By @ Pt @ self.By.T
        C = np.linalg.solve(xx, xy); S = (yy - xy.T @ C) / o.sum()
        q = float(np.mean((as_[:, 0] - as_[:, 1]) ** 2 + Ps[:, 0, 0] + Ps[:, 1, 1] - 2 * Ps[:, 0, 1]))
        return C, S, q
    def ols(self, r):
        rr = r.reindex(pd.period_range(self.per[0] - L, END, freq="M")).ffill().bfill().values; G = self.Y - np.outer(rr, self.d)
        X = np.column_stack([np.ones(self.T)] + [G[L - l:L - l + self.T] for l in range(1, L + 1)])[self.obs]; Yg = G[L:][self.obs]
        C = np.linalg.lstsq(X, Yg, rcond=None)[0]; return C, np.cov((Yg - X @ C).T)
    def fit(self, tag):
        C, S = self.ols(D0["rstar LW"]); q = float(D0["rstar LW"].diff().var()); old = -np.inf; t0 = time.time(); hist = []
        for it in range(MAXIT):
            af, ll, as_, Ps = self.kalman(C, S, q); C, S, q = self.mstep(as_, Ps); hist.append((it, ll, np.sqrt(q)))
            if it % 250 == 0: print(f"{tag}: it {it} ll {ll:.3f} sd_eta {np.sqrt(q):.4f} {time.time() - t0:.0f}s", flush=True)
            if it > 50 and ll - old < 1e-6: break
            old = ll
        af, ll, as_, Ps = self.kalman(C, S, q); self.C, self.S, self.q, self.ll, self.it = C, S, q, ll, it; self.hist = hist
        self.rf = pd.Series(af[:, 0], index=self.per); self.rs = pd.Series(as_[:, 0], index=self.per); return self
    def irf(self, C, win):
        T = MV.ma(C, self.K, L); b = np.r_[0, 0, win]; return {(v, h): float(MV.row_of(T, v, h) @ b) for v in ("u", "P") for h in HS}

def run(start):
    m = RW(start).fit(start[:4]); return start, m.rf, m.rs, m.C, m.q, m.ll, m.it, m.hist

if __name__ == "__main__":
    t0 = time.time(); print(f"c = {CF:.3f}", flush=True)
    from multiprocessing import Pool
    with Pool(2) as pool: res = pool.map(run, ["1996-01", "1973-01"])
    WIN = MV.window_column("rstar", "rstar", "out")                         # month-average response of the yield gap and FCI gap to +1 pp in the window (r* does not move in the window)
    rows, md_l = [], []; out = {}
    for start, rf, rs, C, q, ll, it, hist in res:
        m = RW(start); lab = start[:4]; out[f"{lab} filtered"] = rf; out[f"{lab} smoothed"] = rs
        Cl, _ = m.ols(D0["rstar LW"]); Cc, _ = m.ols(D0["rstar LW"] * 0)
        for rl, Cx in (("RW r* (filtered in the VAR)", C), ("LW r*, same VAR", Cl), ("constant r* (real case), same VAR", Cc)):
            for (v, h), x in m.irf(Cx, WIN).items(): rows.append(dict(start=lab, method="A monthly VAR", rstar=rl, var=v, h=h, r=x))
        # B: Note B's model with r*_t|t (before the sample start: the first filtered value)
        r = rf.reindex(D0.index).bfill().ffill(); key = "rwreal"
        M.IDXM[key] = M.IDXM["real"] - CF * r.reindex(M.IDXM["real"].index); M.FCI[key] = M._daily_fci(M.IDXM[key])
        M.RATE[key] = POL - interp_monthly(M._e2 + r); M.RATE2[key] = M.RATE[key]; M.RATEM[key] = M.Y2M - M._e2m - r; M.RATEM2[key] = M.RATEM[key]
        est = next(M.estimate(key, key, "u,pi", start, None, "out", "none", 2, lags=(12,)))
        for j, n in enumerate(est["names"]):
            for h in HS: rows.append(dict(start=lab, method="B Note B model", rstar="RW r* (filtered in the VAR)", var=n, h=h, r=float(est["s0"][h, j])))
        for f, rl in (("rstar", "LW r* (package baseline)"), ("real", "real case (package baseline)")):
            p = pd.read_csv(BASE / "results" / f"{f}_{f}_upi_{start}_all_out_paths.csv"); p = p[(p.lags == 12) & (p.kind == "macro")]
            for _, x in p[p.h.isin(HS)].iterrows(): rows.append(dict(start=lab, method="B Note B model", rstar=rl, var=x["var"], h=int(x.h), r=x.r))
        lw = D0["rstar LW"].reindex(rf.index)
        md_l.append(f"| {lab} | {rf.index[0]} | {np.sqrt(q):.4f} | {ll:.1f} | {it} | {rf.diff().std():.3f} | {lw.diff().std():.3f} | {rf.corr(lw):.2f} | {(rf - rf.mean()).sub(lw - lw.mean()).pow(2).mean() ** 0.5:.2f} | {rf.loc['2008':'2015'].mean() - rf.mean():+.2f} / {lw.loc['2008':'2015'].mean() - lw.mean():+.2f} |")
    R = pd.DataFrame(rows); R.to_csv(HERE / "rw_real_irf.csv", index=False, float_format="%.4f"); pd.DataFrame(out).to_csv(HERE / "rw_real_rstar.csv", float_format="%.4f")
    md = ["# Real case with a random-walk r* filtered inside the VAR (with the FCI, 12 lags, point estimates)", "", f"c (FCI loading on r*) = {CF:.3f}. Window impact on the month's averages (yield gap, FCI gap): {np.round(WIN, 3).tolist()}.", "",
          "## Estimated r*", "", "| start | first month | sd_eta (MLE, per month) | log-likelihood | EM iterations | sd of monthly change, r*_t|t | same, LW | corr with LW | RMSE vs LW (demeaned) | 2008-15 minus sample mean: RW / LW |",
          "|---|---|---|---|---|---|---|---|---|---|"] + md_l
    for meth in ("A monthly VAR", "B Note B model"):
        md += ["", f"## IRFs, {meth}", "", "| start | r* | " + " | ".join(f"u {h}m" for h in HS) + " | " + " | ".join(f"P {h}m" for h in HS) + " |", "|---|---|" + "---|" * 10]
        for (s, rl), g in R[R.method == meth].groupby(["start", "rstar"], sort=False):
            q = g.set_index(["var", "h"]).r; md.append(f"| {s} | {rl} | " + " | ".join(f"{q[('u', h)]:+.2f}" for h in HS) + " | " + " | ".join(f"{q[('P', h)]:+.2f}" for h in HS) + " |")
    (HERE / "rw_real.md").write_text("\n".join(md)); print("\n".join(md)); print(f"total {time.time() - t0:.0f}s")
