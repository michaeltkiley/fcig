"""Linear Gaussian state space with time-varying system matrices, exogenous inputs and missing observations: Kalman filter (log-likelihood) and
Rauch-Tung-Striebel smoother (moments for the EM step). General code; the Note B structure is in noteb.py.

    a_{t+1} = T_t a_t + c_t + R_t eta_t,   eta_t ~ N(0, Q_t)          (transition from t to t+1)
    y_t     = Z_t a_t + d_t + eps_t,       eps_t ~ N(0, H_t)          (y_t may contain NaN: those rows are skipped)
Step t supplies (T, c, RQR', Z, d, H) through a callback so that only the matrices of the current step are in memory."""
import numpy as np

LOG2PI = np.log(2 * np.pi)


def kfilter(a0, P0, nsteps, step, store=False):
    """Returns log-likelihood and, if store, the filtered and predicted moments and the transition matrices (for the smoother).
    step(t) -> dict(Z, d, H, y, T, c, RQR). Observation at t is applied to the predicted state a_t|t-1; then the state is moved to t+1."""
    a, P = a0.copy(), P0.copy(); ll = 0.0
    keep = dict(af=[], Pf=[], ap=[], Pp=[], T=[]) if store else None
    for t in range(nsteps):
        s = step(t)
        if store: keep["ap"].append(a.copy()); keep["Pp"].append(P.copy())
        y = s["y"]
        if y is not None:
            ok = ~np.isnan(y)
            if ok.any():
                Z, d, H, y = s["Z"][ok], s["d"][ok], s["H"][np.ix_(ok, ok)], y[ok]
                v = y - Z @ a - d; F = Z @ P @ Z.T + H; F = (F + F.T) / 2
                L = np.linalg.cholesky(F); w = np.linalg.solve(L, v)
                ll += -0.5 * (len(v) * LOG2PI + 2 * np.log(np.diag(L)).sum() + w @ w)
                PZ = P @ Z.T; K = np.linalg.solve(F, PZ.T).T
                a = a + K @ v; P = P - K @ PZ.T; P = (P + P.T) / 2
        if store: keep["af"].append(a.copy()); keep["Pf"].append(P.copy()); keep["T"].append(s["T"])
        a = s["T"] @ a + s["c"]; P = s["T"] @ P @ s["T"].T + s["RQR"]
    return ll, keep


def smoother(keep):
    """RTS smoother on the stored filter output: smoothed means and covariances of a_t (t = 0..n-1), and lag-one cross covariances Cov(a_{t+1}, a_t | all)."""
    af, Pf, ap, Pp, T = keep["af"], keep["Pf"], keep["ap"], keep["Pp"], keep["T"]; n = len(af)
    a_s = [None] * n; P_s = [None] * n; C = [None] * (n - 1)
    a_s[-1], P_s[-1] = af[-1], Pf[-1]
    for t in range(n - 2, -1, -1):
        J = np.linalg.lstsq(Pp[t + 1].T, (Pf[t] @ T[t].T).T, rcond=None)[0].T          # J = Pf_t T_t' Pp_{t+1}^+ (pseudo-inverse: Pp can be singular)
        a_s[t] = af[t] + J @ (a_s[t + 1] - ap[t + 1])
        P_s[t] = Pf[t] + J @ (P_s[t + 1] - Pp[t + 1]) @ J.T
        C[t] = P_s[t + 1] @ J.T
    return np.array(a_s), np.array(P_s), C
