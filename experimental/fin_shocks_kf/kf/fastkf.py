"""Compiled Kalman filter (log-likelihood only) for a state space given as arrays: step t uses transition type typ[t] (T[typ], RQR[typ]),
constant c[t], observation y[t] (NaN = missing), Z, d[t], H. Same conventions as ssm.kfilter (observe at t, then move to t+1)."""
import numpy as np
from numba import njit


@njit(cache=True)
def loglik(a0, P0, y, d, c, typ, T, Q, Z, H):
    a = a0.copy(); P = P0.copy(); ll = 0.0; ns = y.shape[0]
    for t in range(ns):
        ok = np.where(~np.isnan(y[t]))[0]
        if ok.size > 0:
            Zo = Z[ok]; v = y[t][ok] - Zo @ a - d[t][ok]
            Ho = np.empty((ok.size, ok.size))
            for i in range(ok.size):
                for j in range(ok.size): Ho[i, j] = H[ok[i], ok[j]]
            PZ = P @ Zo.T; F = Zo @ PZ + Ho; F = (F + F.T) / 2
            L = np.linalg.cholesky(F); w = np.linalg.solve(L, v)
            ll += -0.5 * (ok.size * np.log(2 * np.pi) + 2 * np.sum(np.log(np.diag(L))) + w @ w)
            K = np.linalg.solve(F, PZ.T).T
            a = a + K @ v; P = P - K @ PZ.T; P = (P + P.T) / 2
        Tt = T[typ[t]]; a = Tt @ a + c[t]; P = Tt @ P @ Tt.T + Q[typ[t]]
    return ll
