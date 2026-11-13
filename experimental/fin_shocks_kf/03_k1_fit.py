"""Step 3. K1 on the data (r*-gap with the FCI, 12 lags): ECME to convergence (kf/k1.py fit). Starts from the saved SQUAREM point if given, else from Note B with
Gamma = 0, S_nu = S_m / 50. Logs every cycle (time, log-likelihood, Gamma, S_nu) to output/k1_fit.log; saves the estimate each cycle to output/k1_theta.npz."""
import os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"): os.environ.setdefault(_v, "1")
import numpy as np
from kf import noteb as N, k1
from kf.inputs import OUT

ds = N.Design("rstar", "rstar", 12); kd = k1.K1Data(ds); Cm, Sm, Cd, Sd = N.ols_fit(ds)
ll0 = N.closed_form_loglik(ds, Cm, Sm, Cd, Sd)
th = tuple(np.load(sys.argv[1], allow_pickle=True)) if len(sys.argv) > 1 else (Cm, Sm, Cd, Sd, np.zeros((2, 2)), np.diag(np.diag(Sm)) / 50)
log = open(OUT / "k1_fit.log", "a"); t0 = time.time()
def say(s): print(s, flush=True); log.write(s + "\n"); log.flush()
say(f"{time.strftime('%H:%M:%S')} start; Note B log-likelihood {ll0:.4f}; start log-likelihood {k1.loglik(kd, th):.4f}")
from scipy.optimize import minimize
path = [k1.loglik(kd, th)]
for it in range(500):
    _, t1 = k1.em_step(kd, th); th = t1[:4] + th[4:]
    r = minimize(lambda p: -k1.loglik(kd, th[:4] + k1._from_phi(p, 2, 2)), k1._phi(*th[4:]), method="L-BFGS-B", options=dict(maxiter=200))
    th = th[:4] + k1._from_phi(r.x, 2, 2); path.append(-r.fun)
    G, S = th[4], th[5]
    say(f"{time.strftime('%H:%M:%S')} cycle {it:3d}  loglik {path[-1]:.4f}  gain {path[-1] - path[-2]:.5f}  LR vs Note B {2 * (path[-1] - ll0):.2f}  "
        f"Gamma u:[{G[0,0]:+.3f},{G[0,1]:+.3f}] pi:[{G[1,0]:+.3f},{G[1,1]:+.3f}]  sd(nu) u {np.sqrt(S[0,0]):.4f} pi {np.sqrt(S[1,1]):.4f}")
    np.savez(OUT / "k1_theta.npz", *th, path=np.array(path))
    if path[-1] - path[-2] < 1e-4: break
say(f"{time.strftime('%H:%M:%S')} done: converged after {it + 1} cycles, {(time.time() - t0) / 60:.1f} minutes")
