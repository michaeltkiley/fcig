"""Step 4. Is K1's Gamma spurious? Simulate Note B's estimated model (r*-gap with the FCI, 12 lags; true Gamma = 0, S_nu = 0) on the actual calendar
(same daily rows and months, 1996-2026; pre-1996 history from the data), with monthly and daily residuals resampled from Note B's fit, and estimate K1 on each
simulated sample by ECME (from Gamma = 0, S_nu = S_m / 50, as on the data). Usage: python 04_k1_sim.py <first seed> <number of samples>.
Logs to output/k1_sim_<seed>.log; one row per sample appended to output/k1_sim.csv (Gamma, S_nu, LR vs Note B's model, cycles)."""
import os, sys, time, copy
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"): os.environ.setdefault(_v, "1")
import numpy as np, pandas as pd
from scipy.optimize import minimize
from kf import noteb as N, k1
from kf.inputs import OUT

HAR = N.HAR
ds0 = N.Design("rstar", "rstar", 12); K, L, nd = ds0.K, ds0.L, ds0.nd
Cm, Sm, Cd, Sd = N.ols_fit(ds0); par = N.unpack(Cm, Cd, K, L, nd)
res_m = ds0.Mm - ds0.Xm() @ Cm; res_d = ds0.Fd - ds0.Xd() @ Cd
I = N.inputs(); F = I.daily("rstar", "rstar").loc["1990-01-02":].dropna()
pre = F.loc[:ds0.dates[0]].values[:-1][-66:]                                                        # the 66 rows before the first sample row (data)
nm = len(ds0.P); mo = ds0.mon_of_row


def simulate(rng):
    """One sample: daily f on the sample rows, monthly macro, in Note B's model (macro first in each month)."""
    f = np.vstack([pre, np.zeros((len(ds0.Fd), nd))]); o = len(pre)
    m = np.zeros((nm, K)); ml = ds0.mlags.copy(); fl = ds0.flags.copy(); fbar = np.zeros((nm, nd))
    em = res_m[rng.integers(0, nm, nm)]; ed = res_d[rng.integers(0, len(res_d), len(ds0.Fd))]
    t_row = 0
    for t in range(nm):
        for l in range(1, L + 1):
            if t - l >= 0: ml[t, K * (l - 1):K * l] = m[t - l]; fl[t, nd * (l - 1):nd * l] = fbar[t - l]
        m[t] = np.r_[1.0, ml[t], fl[t]] @ Cm + em[t]
        mprev = ml[t, :K]
        rows = np.where(mo == t)[0]
        for r in rows:
            x = np.r_[1.0, np.concatenate([f[o + r - h:o + r].mean(0) for h in HAR]), mprev, m[t]]
            f[o + r] = x @ Cd + ed[r]
        fbar[t] = f[o + rows].mean(0)
    d = copy.copy(ds0)
    d.Fd = f[o:]; d.Mm = m; d.mlags = ml; d.flags = fl
    d.Wd = np.column_stack([np.ones(len(d.Fd))] + [np.array([f[o + r - h:o + r].mean(0) for r in range(len(d.Fd))]) for h in HAR])
    d.Md = (ml[mo, :K], m[mo])
    return d


def ecme(kd, th, ll_ref, logf, tag):
    path = [k1.loglik(kd, th)]
    for it in range(300):
        _, t1 = k1.em_step(kd, th); th = t1[:4] + th[4:]
        r = minimize(lambda p: -k1.loglik(kd, th[:4] + k1._from_phi(p, K, nd)), k1._phi(*th[4:]), method="L-BFGS-B", options=dict(maxiter=200))
        th = th[:4] + k1._from_phi(r.x, K, nd); path.append(-r.fun); G = th[4]
        logf(f"{time.strftime('%H:%M:%S')} {tag} cycle {it:3d} loglik {path[-1]:.4f} gain {path[-1] - path[-2]:.5f} LR {2 * (path[-1] - ll_ref):.2f} "
             f"Gamma u:[{G[0,0]:+.3f},{G[0,1]:+.3f}] pi:[{G[1,0]:+.3f},{G[1,1]:+.3f}]")
        if path[-1] - path[-2] < 1e-4: break
    return th, path, it + 1


if __name__ == "__main__":
    s0, ns = int(sys.argv[1]), int(sys.argv[2]); log = open(OUT / f"k1_sim_{s0}.log", "a")
    def say(s): log.write(s + "\n"); log.flush()
    for s in range(s0, s0 + ns):
        rng = np.random.default_rng(1000 + s); d = simulate(rng); kd = k1.K1Data(d)
        kd.df = np.vstack([d.Fd[0] - pre[-1], np.diff(d.Fd, axis=0)])
        c = N.ols_fit(d); ll_ref = N.closed_form_loglik(d, *c)                                   # Note B's model fitted to the simulated sample (the null)
        say(f"{time.strftime('%H:%M:%S')} sample {s}: Note B loglik {ll_ref:.4f}")
        th, path, cyc = ecme(kd, (*c, np.zeros((K, K if nd == 2 else nd)), np.diag(np.diag(c[1])) / 50), ll_ref, say, f"sample {s}")
        G, S = th[4], th[5]; b = np.array([1.0, 0.9917])
        row = dict(sample=s, LR=2 * (path[-1] - ll_ref), cycles=cyc, G_u_pol=G[0, 0], G_u_idx=G[0, 1], G_pi_pol=G[1, 0], G_pi_idx=G[1, 1],
                   sameday_u=float((G @ b)[0]), sameday_pi=float((G @ b)[1]), sd_nu_u=np.sqrt(S[0, 0]), sd_nu_pi=np.sqrt(S[1, 1]))
        pd.DataFrame([row]).to_csv(OUT / "k1_sim.csv", mode="a", header=not (OUT / "k1_sim.csv").exists(), index=False)
        say(f"{time.strftime('%H:%M:%S')} sample {s} done: {row}")
