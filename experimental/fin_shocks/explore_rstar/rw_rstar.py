"""Real case with an unobserved random-walk r* filtered inside the VAR (author, 18 Nov 2026).
Model (monthly; u = unemployment gap, pi = core PCE inflation, x = real 2-year, F = real market index, monthly averages as in Note B; without the FCI, F is left out):
    g_t = (u_t, pi_t, x_t - r_t, F_t - c r_t) = c0 + sum_{l=1..L} A_l g_{t-l} + e_t,   e_t ~ N(0, S)
    r_t = r_{t-1} + eta_t,   eta_t ~ N(0, q)
c = the FCI's loading on r* in Note A's r*-gap formula: w_y10 + |w_eq| x 100 / mean(E/P) = 1.53 (10-year term and the earnings-yield term). r is the only unobserved state, so the state is
alpha_t = (r_t, ..., r_{t-L}) (13 elements with L = 12) and the observation equation is  Y_t - c0 - sum A_l Y_{t-l} = Z alpha_t + e_t,  Z = [d, -A_1 d, ..., -A_L d],  d = (0, 0, 1, c).
Estimation: exact EM (Kalman filter + RTS smoother; M-step = OLS of the VAR on smoothed first and second moments of the state, which contains every lag needed; q from E[(r_t - r_{t-1})^2]),
either with q estimated (MLE) or fixed on a grid (profile likelihood). March-December 2020: no observation (prediction step only), as the model drops them; the r* level is not identified
(absorbed by c0) and is pinned by the prior at LW's value at the start. 12 lags; samples from 1996 and 1973 as Note B's baselines.
IRFs (point estimates): (A) the monthly gap VAR with Note B's window impact (0, 0, e_x, e_F) = response of the month's average yield and FCI to +1 pp in the window (lib/monthly.window_column);
(B) Note B's mixed-frequency model with the one-sided filtered r* (r_{t|t}) in place of LW in the 2-year (x - r) and the FCI (F_real - c r).
Writes rw_rstar.md, rw_rstar_irf.csv, rw_rstar_paths.csv, fig_rw_rstar.png."""
import sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.argv = [sys.argv[0], "--draws", "2"]
exec(open(HERE / "run_rstar_alt.py").read().split("if __name__")[0])
from lib import monthly as MV
w = pd.read_csv(M.OUT / "market_weights.csv", index_col=0).weight
CFCI = float(w["y10"] + (-w["equities"]) * 100 / (100 / D0.cape).loc[noteA.START:noteA.END].mean())
L = 12; END = pd.Period("2026-09", "M"); C2020 = pd.period_range("2020-03", "2020-12", freq="M")

def data(fci):
    F = M.fin_monthly("real", "real" if fci else 0); D = M.MAC[["u", "pi"]].join(F, how="inner").dropna(); return D[D.index <= END]

class RW:
    def __init__(self, fci, start):
        self.D = data(fci); self.K = self.D.shape[1]; self.d = np.r_[0, 0, 1, CFCI][:self.K]
        start = str(max(pd.Period(start, "M"), self.D.index[0] + L))       # as the package: the financial block starts in 1973-01, so 12 lags start the 1973 sample in 1974-01
        self.per = pd.period_range(start, END, freq="M"); P0 = pd.Period(start, "M")
        self.Y = self.D.reindex(pd.period_range(P0 - L, END, freq="M")).values          # rows: start-L .. END
        assert not np.isnan(self.Y).any(), "missing data"
        self.obs = ~self.per.isin(C2020); self.T = len(self.per); self.m0 = float(D0["rstar LW"].loc[P0 - 1])
        n = L + 1; self.Tm = np.zeros((n, n)); self.Tm[0, 0] = 1; self.Tm[1:, :-1] = np.eye(L)
        # a_t (data part of [g_t; 1; g_{t-1}..g_{t-L}]) and B (its loading on alpha_t) for the M-step
        K = self.K; self.A_ = np.zeros((self.T, K + 1 + K * L)); self.B = np.zeros((K + 1 + K * L, n))
        for i in range(self.T):
            t = i + L; self.A_[i, :K] = self.Y[t]; self.A_[i, K] = 1
            for l in range(1, L + 1): self.A_[i, K + 1 + K * (l - 1):K + 1 + K * l] = self.Y[t - l]
        self.B[:K, 0] = -self.d
        for l in range(1, L + 1): self.B[K + 1 + K * (l - 1):K + 1 + K * l, l] = -self.d
    def kalman(self, C, S, q, smooth=True):
        K, n, d = self.K, L + 1, self.d; c0 = C[0]; A = [C[1 + K * (l - 1):1 + K * l].T for l in range(1, L + 1)]
        Z = np.column_stack([d] + [-A[l - 1] @ d for l in range(1, L + 1)])
        a = np.full(n, self.m0); P = 4.0 * np.ones((n, n)) + q * np.minimum.outer(np.arange(n), np.arange(n))
        Tm = self.Tm; Q = np.zeros((n, n)); Q[0, 0] = q; Si = np.linalg.inv(S); ll = 0.0
        ap, Pp, af, Pf = [], [], [], []
        for i in range(self.T):
            a = Tm @ a; P = Tm @ P @ Tm.T + Q; ap.append(a); Pp.append(P)
            if self.obs[i]:
                t = i + L; wv = self.Y[t] - c0 - sum(A[l - 1] @ self.Y[t - l] for l in range(1, L + 1))
                v = wv - Z @ a; F = Z @ P @ Z.T + S; Fi = np.linalg.inv(F); Kg = P @ Z.T @ Fi
                a = a + Kg @ v; P = P - Kg @ Z @ P; P = (P + P.T) / 2
                ll += -0.5 * (K * np.log(2 * np.pi) + np.linalg.slogdet(F)[1] + v @ Fi @ v)
            af.append(a); Pf.append(P)
        if not smooth: return np.array(af), np.array(Pf), ll
        as_, Ps = [None] * self.T, [None] * self.T; as_[-1], Ps[-1] = af[-1], Pf[-1]
        for i in range(self.T - 2, -1, -1):
            J = Pf[i] @ Tm.T @ np.linalg.pinv(Pp[i + 1]); as_[i] = af[i] + J @ (as_[i + 1] - ap[i + 1]); Ps[i] = Pf[i] + J @ (Ps[i + 1] - Pp[i + 1]) @ J.T
        return np.array(af), np.array(Pf), ll, np.array(as_), np.array(Ps)
    def mstep(self, as_, Ps):
        K = self.K; Ex = self.A_ + as_ @ self.B.T; o = self.obs
        M2 = np.einsum("ti,tj->ij", Ex[o], Ex[o]) + np.einsum("ik,tkl,jl->ij", self.B, Ps[o], self.B)
        yy, yx, xx = M2[:K, :K], M2[:K, K:], M2[K:, K:]
        C = np.linalg.solve(xx, yx.T); S = (yy - yx @ C) / o.sum()
        dr = as_[:, 0] - as_[:, 1]; q = float(np.mean(dr ** 2 + Ps[:, 0, 0] + Ps[:, 1, 1] - 2 * Ps[:, 0, 1]))
        return C, S, q
    def fit(self, q=None, r_init=None, tol=1e-7, maxit=2000):
        r = (r_init if r_init is not None else D0["rstar LW"]).reindex(pd.period_range(self.per[0] - L, END, freq="M")).ffill().values
        G = self.Y - np.outer(r, self.d); X = np.column_stack([np.ones(self.T)] + [G[L - l:L - l + self.T] for l in range(1, L + 1)])[self.obs]
        C = np.linalg.lstsq(X, G[L:][self.obs], rcond=None)[0]; S = np.cov((G[L:][self.obs] - X @ C).T); qq = q if q is not None else 0.005
        old = -np.inf
        for it in range(maxit):
            af, Pf, ll, as_, Ps = self.kalman(C, S, qq); C, S, qn = self.mstep(as_, Ps)
            if q is None: qq = max(qn, 1e-10)
            if abs(ll - old) < tol * max(1, abs(ll)): break
            old = ll
        af, Pf, ll, as_, Ps = self.kalman(C, S, qq)
        self.C, self.S, self.q, self.ll, self.it = C, S, qq, ll, it
        self.rf = pd.Series(af[:, 0], index=self.per); self.rs = pd.Series(as_[:, 0], index=self.per); return self
    def irf_we(self, win):
        T = MV.ma(self.C, self.K, L); b = np.r_[0, 0, win[:self.K - 2]]
        return {(v, h): float(MV.row_of(T, v, h) @ b) for v in ("u", "P") for h in (6, 12, 18, 24, 36)}

def var_fixed(fci, start, r):
    """The same monthly VAR estimated by OLS with a given r* path (LW, or constant = the real case), window-impact IRFs."""
    m = RW(fci, start); rr = r.reindex(pd.period_range(m.per[0] - L, END, freq="M")).ffill().values
    G = m.Y - np.outer(rr, m.d); X = np.column_stack([np.ones(m.T)] + [G[L - l:L - l + m.T] for l in range(1, L + 1)])[m.obs]
    m.C = np.linalg.lstsq(X, G[L:][m.obs], rcond=None)[0]; return m

t0 = time.time(); WIN = {fci: MV.window_column("rstar", "rstar" if fci else 0, "out") for fci in (0, 1)}
import os
QGRID = [float(x) for x in os.environ.get("RW_QGRID", "0.0004,0.0016,0.0036,0.0064").split(",")]   # sd per month 0.02, 0.04, 0.06, 0.08 (LW: quarterly-change sd 0.145, about 0.084 per month)
MAXIT = int(os.environ.get("RW_MAXIT", "400")); HS = (6, 12, 18, 24, 36)
prof, irf, paths = [], [], {}
def plug(key, r):
    """Note B's mixed-frequency model with r in place of LW: 2-year = real 2-year - r; FCI = real FCI - c r (daily: the daily real index plus the monthly offset, as the package)."""
    r = r.reindex(D0.index); r = r.bfill().ffill()
    M.IDXM[key] = (M.IDXM["real"] - CFCI * r.reindex(M.IDXM["real"].index)); M.FCI[key] = M._daily_fci(M.IDXM[key])
    for R in (M.RATE, M.RATE2): R[key] = POL - interp_monthly(M._e2 + r)
    for R in (M.RATEM, M.RATEM2): R[key] = M.Y2M - M._e2m - r
def model_irf(key, fci, start):
    est = next(M.estimate(key, key if fci else 0, "u,pi", start, None, "out", "none", 2, lags=(12,)))
    return {(n, h): float(est["s0"][h, j]) for j, n in enumerate(est["names"]) for h in HS}
for start in ("1996-01", "1973-01"):
    for fci in (0, 1):
        lab = f"{start[:4]}, {'with' if fci else 'no'} FCI"
        cand = [("MLE", None)] + [(f"sd {np.sqrt(q):.2f}", q) for q in QGRID]
        for qlab, q in cand:
            m = RW(fci, start).fit(q=q, maxit=MAXIT, tol=1e-8); paths[(lab, qlab)] = m
            prof.append(dict(case=lab, q=qlab, sd_eta=np.sqrt(m.q), loglik=m.ll, iters=m.it, sd_dr=m.rf.diff().std(), corr_LW=m.rf.corr(D0["rstar LW"].reindex(m.per)),
                             corr_dLW=m.rf.diff().corr(D0["rstar LW"].reindex(m.per).diff())))
            A = m.irf_we(WIN[fci]); key = f"rw_{start[:4]}_{fci}_{qlab.replace(' ', '')}"; plug(key, m.rf); B = model_irf(key, fci, start)
            for (v, h), x in A.items(): irf.append(dict(case=lab, rstar=f"RW {qlab}", method="A monthly VAR", var=v, h=h, r=x))
            for (v, h), x in B.items(): irf.append(dict(case=lab, rstar=f"RW {qlab}", method="B Note B model", var=v, h=h, r=x))
            print(lab, qlab, m.per[0], "sd_eta", round(np.sqrt(m.q), 4), "ll", round(m.ll, 1), "its", m.it, f"{time.time() - t0:.0f}s", flush=True)
        for rl, r in (("LW", D0["rstar LW"]), ("constant (real case)", D0["rstar LW"] * 0 + 2.0)):
            A = var_fixed(fci, start, r).irf_we(WIN[fci])
            for (v, h), x in A.items(): irf.append(dict(case=lab, rstar=rl, method="A monthly VAR", var=v, h=h, r=x))
            key = "rstar" if rl == "LW" else "real"; B = model_irf(key, fci, start) if rl == "LW" else None
            if rl != "LW":
                plug("rwconst", r); B = model_irf("rwconst", fci, start)
            for (v, h), x in B.items(): irf.append(dict(case=lab, rstar=rl, method="B Note B model", var=v, h=h, r=x))
P = pd.DataFrame(prof); I = pd.DataFrame(irf)
P.to_csv(HERE / "rw_rstar_profile.csv", index=False, float_format="%.5f"); I.to_csv(HERE / "rw_rstar_irf.csv", index=False, float_format="%.4f")
pd.DataFrame({f"{k[0]} | {k[1]}": v.rf for k, v in paths.items()}).to_csv(HERE / "rw_rstar_paths.csv", float_format="%.4f")
md = ["# Real case with a random-walk r* filtered inside the VAR (point estimates, 12 lags, no trend)", "",
      f"Gaps: real 2-year - r*, real FCI - c r* with c = {CFCI:.3f}; r* a random walk with innovation sd per month sd_eta (MLE or fixed). Exact EM (Kalman smoother inside the VAR). "
      "IRFs per +1 pp on the 2-year in the window: A = the monthly gap VAR with Note B's window impact; B = Note B's mixed-frequency model with the one-sided filtered r* (r_t|t). "
      "Rows LW: the same monthly VAR (A) or the package's r*-gap model (B; its FCI uses Note A's r*-gap formula); constant = the real case.", "",
      "## Likelihood and the filtered r*", "", "| case | q | sd_eta | log-likelihood | EM iterations | sd of monthly change of r*_t|t | corr with LW | corr of changes with LW |", "|---|---|---|---|---|---|---|---|"]
for _, r in P.iterrows(): md.append(f"| {r.case} | {r.q} | {r.sd_eta:.4f} | {r.loglik:.1f} | {r.iters} | {r.sd_dr:.3f} | {r.corr_LW:.2f} | {r.corr_dLW:.2f} |")
for meth in ("A monthly VAR", "B Note B model"):
    md += ["", f"## IRFs, method {meth}", "", "| case | r* | " + " | ".join(f"u {h}m" for h in HS) + " | " + " | ".join(f"P {h}m" for h in HS) + " |", "|---|---|" + "---|" * 10]
    for (c, rs), g in I[I.method == meth].groupby(["case", "rstar"], sort=False):
        q = g.set_index(["var", "h"]).r; md.append(f"| {c} | {rs} | " + " | ".join(f"{q[('u', h)]:+.2f}" for h in HS) + " | " + " | ".join(f"{q[('P', h)]:+.2f}" for h in HS) + " |")
(HERE / "rw_rstar.md").write_text("\n".join(md)); print("\n".join(md))
