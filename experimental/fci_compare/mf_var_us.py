"""
Index estimated by the method of the ECB Macro-Finance FCI (Bletzinger, Martorana and Mistak 2026, ECB WP 3193), on our US data and with our design choices
(experimental/INDEX_QA.md answers 17-27, approved 29 Oct 2026). Inspired by and citing their method; not their index.

Model (monthly):
    M_t = [core PCE inflation gap (12-month, less 2), unemployment gap (UNRATE less CBO NROU, interpolated to months)]  (headline PCE: robustness)
    Z_t = financial variables of the macro-model index, demeaned levels: policy rate, 10-year, mortgage spread, BBB spread, equities (100 ln CAPE), real dollar (100 ln);
          version +HP adds house prices (100 ln price-to-rent)
    macro equations:      M_t = c + sum_l A_l M_{t-l} + sum_l b_l (alpha' Z_{t-l}) + e_t      (financial variables only through the index F = alpha'Z; same alpha at every lag)
    financial equations:  Z_t = c + sum_l [B_l M_{t-l} + C_l Z_{t-l}] + e_t                (unrestricted)
    Estimation: Gaussian maximum likelihood, alpha jointly with all coefficients (iterated SUR given alpha; alpha by numerical optimization, ||alpha|| = 1, alpha_policy > 0);
                no ridge penalty (answer 23); sample 1990-2025 with every 2020 month excluded from the likelihood; lag length by BIC (1-6).
    Standard errors for alpha: inverse Hessian of the profile log-likelihood.
Funds-rate equivalents (output lens, model-consistent):
    yardstick  funds rate held +100 bp for 12 months: each month a funds-rate innovation chosen to keep it there; within-month effects on all variables are generalized impulse
               responses (residual covariance with the funds rate / its variance); later effects through the VAR. Effect = -2 x unemployment-gap response at month 12 (Okun).
    weight_j   variable j held +1 unit for 12 months, all other financial variables at baseline (effect only through the index), same measurement, divided by the yardstick.
    index      sum_j weight_j x~_j (pp of funds rate)
Inputs not in git: raw/PCEPILFE.csv, PCEPI.csv, UNRATE.csv, NROU.csv (FRED).
Usage: python experimental/fci_compare/mf_var_us.py
Outputs: mf_var_us_results.csv (weights), mf_var_us_monthly.csv (indexes)
"""
import os, sys, time
import numpy as np, pandas as pd
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
import macro_model_dl as DL

FIN0 = ["policy rate", "10-year", "mortgage spread", "BBB spread", "equities", "dollar"]


def fred_m(name):
    d = pd.read_csv(os.path.join(ROOT, "raw", f"{name}.csv"))
    s = pd.Series(pd.to_numeric(d.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(d.iloc[:, 0])).dropna()
    return s


def macro_data(headline=False):
    p = fred_m("PCEPI" if headline else "PCEPILFE"); p.index = p.index.to_period("M")
    infl = 100 * np.log(p / p.shift(12)) - 2.0
    u = fred_m("UNRATE"); u.index = u.index.to_period("M")
    n = fred_m("NROU")                                            # quarterly, dated first month of the quarter
    nm = n.copy(); nm.index = (n.index + pd.offsets.MonthBegin(1)).to_period("M")    # centre on the middle month
    idx = pd.period_range(nm.index[0], nm.index[-1], freq="M")
    nm = nm.reindex(idx).interpolate()
    return pd.DataFrame({"inflation gap": infl, "unemployment gap": u - nm.reindex(u.index)})


class MFVAR:
    def __init__(self, M, Z, p, start="1990-01", end="2025-12", exclude=("2020-01", "2020-12"), first=None):
        Y = pd.concat([M, Z], axis=1).dropna()
        self.nm, self.nz, self.p = M.shape[1], Z.shape[1], p
        self.names = list(M.columns) + list(Z.columns)
        t0 = pd.Period(first or start, "M")
        rows = [t for t in Y.index if t0 <= t <= pd.Period(end, "M") and not (pd.Period(exclude[0], "M") <= t <= pd.Period(exclude[1], "M"))]
        rows = [t for t in rows if all((t - l) in Y.index for l in range(1, p + 1))]
        self.idx = rows
        V = Y.values; pos = {t: i for i, t in enumerate(Y.index)}
        self.Yd = np.array([V[pos[t]] for t in rows])                              # T x n
        self.Lags = np.stack([np.array([V[pos[t - l]] for t in rows]) for l in range(1, p + 1)], axis=1)   # T x p x n
        self.T = len(rows)

    def regressors(self, alpha):
        T, p, nm = self.T, self.p, self.nm
        LM = self.Lags[:, :, :nm].reshape(T, -1)
        LF = self.Lags[:, :, nm:] @ alpha                                          # T x p
        Xm = np.column_stack([np.ones(T), LM, LF])
        Xz = np.column_stack([np.ones(T), self.Lags.reshape(T, -1)])
        return Xm, Xz

    def sur(self, alpha, iters=50, tol=1e-10):
        Xm, Xz = self.regressors(alpha)
        n, nm = self.nm + self.nz, self.nm
        Xs = [Xm] * nm + [Xz] * self.nz
        Y = self.Yd
        B = [np.linalg.lstsq(X, Y[:, i], rcond=None)[0] for i, X in enumerate(Xs)]
        E = np.column_stack([Y[:, i] - X @ B[i] for i, X in enumerate(Xs)])
        ll_old = None
        for _ in range(iters):
            Om = E.T @ E / self.T
            Oi = np.linalg.inv(Om)
            # GLS: block system
            ks = [X.shape[1] for X in Xs]; off = np.concatenate([[0], np.cumsum(ks)])
            A = np.zeros((off[-1], off[-1])); c = np.zeros(off[-1])
            for i in range(n):
                for j in range(n):
                    A[off[i]:off[i + 1], off[j]:off[j + 1]] = Oi[i, j] * Xs[i].T @ Xs[j]
                c[off[i]:off[i + 1]] = sum(Oi[i, j] * Xs[i].T @ Y[:, j] for j in range(n))
            beta = np.linalg.solve(A, c)
            B = [beta[off[i]:off[i + 1]] for i in range(n)]
            E = np.column_stack([Y[:, i] - Xs[i] @ B[i] for i in range(n)])
            Om = E.T @ E / self.T
            ll = -0.5 * self.T * (n * np.log(2 * np.pi) + np.linalg.slogdet(Om)[1] + n)
            if ll_old is not None and abs(ll - ll_old) < tol: break
            ll_old = ll
        return ll, B, Om

    @staticmethod
    def alpha_from(v):
        u = np.concatenate([[1.0], v]); return u / np.linalg.norm(u)

    def fit(self, starts):
        best = None
        for s in starts:
            v0 = s[1:] / s[0]
            f = lambda v: -self.sur(self.alpha_from(v), iters=8)[0]
            r = minimize(f, v0, method="Nelder-Mead", options={"maxiter": 4000, "xatol": 1e-6, "fatol": 1e-6})
            r = minimize(f, r.x, method="BFGS")
            ll = -self.sur(self.alpha_from(r.x))[0] * -1
            if best is None or ll > best[0]:
                best = (ll, r.x)
        self.v = best[1]; self.alpha = self.alpha_from(self.v)
        self.ll, self.B, self.Om = self.sur(self.alpha)
        return self

    def alpha_se(self, h=1e-4):
        f = lambda v: self.sur(self.alpha_from(v))[0]
        k = len(self.v); H = np.zeros((k, k))
        for i in range(k):
            for j in range(i, k):
                ei = np.zeros(k); ej = np.zeros(k); ei[i] = h; ej[j] = h
                H[i, j] = H[j, i] = (f(self.v + ei + ej) - f(self.v + ei - ej) - f(self.v - ei + ej) + f(self.v - ei - ej)) / (4 * h * h)
        Cv = np.linalg.inv(-H)
        J = np.zeros((k + 1, k)); a0 = self.alpha
        for i in range(k):
            e = np.zeros(k); e[i] = 1e-6
            J[:, i] = (self.alpha_from(self.v + e) - self.alpha_from(self.v - e)) / 2e-6
        return np.sqrt(np.diag(J @ Cv @ J.T))

    def nparams(self):
        n, nm, nz, p = self.nm + self.nz, self.nm, self.nz, self.p
        return nm * (1 + p * nm + p) + nz * (1 + p * n) + (nz - 1) + n * (n + 1) // 2

    def companion(self):
        n, nm, p = self.nm + self.nz, self.nm, self.p
        A = np.zeros((p, n, n))
        for i in range(nm):
            b = self.B[i]
            for l in range(p):
                A[l, i, :nm] = b[1 + l * nm:1 + (l + 1) * nm]
                A[l, i, nm:] = b[1 + p * nm + l] * self.alpha
        for j in range(self.nz):
            b = self.B[nm + j]
            for l in range(p):
                A[l, nm + j, :] = b[1 + l * n:1 + (l + 1) * n]
        return A

    def yardstick(self, months=12, H=12, ffr="policy rate"):
        A = self.companion(); n = A.shape[1]; k = self.names.index(ffr)
        g = self.Om[:, k] / self.Om[k, k]
        y = np.zeros((H + self.p, n))
        for t in range(H):
            pred = sum(A[l] @ y[self.p + t - 1 - l] for l in range(self.p))
            eps = (1.0 - pred[k]) if t < months else 0.0
            y[self.p + t] = pred + g * eps
        return y[self.p:]

    def partial(self, j, months=12, H=12):
        """variable j held +1 for `months`, other financial variables at baseline: macro block driven by F = alpha_j."""
        A = self.companion(); nm = self.nm
        m = np.zeros((H + self.p, nm))
        for t in range(H):
            acc = np.zeros(nm)
            for l in range(self.p):
                acc += A[l][:nm, :nm] @ m[self.p + t - 1 - l]
                if t - 1 - l >= 0 and t - 1 - l < months:
                    acc += A[l][:nm, nm + j]                       # Z_j = 1 at lag date, others 0
            m[self.p + t] = acc
        return m[self.p:]


def run(label, M, Z, p, starts, first):
    t0 = time.time()
    v = MFVAR(M, Z, p, first=first).fit(starts)
    se = v.alpha_se()
    y = v.yardstick()
    ui = v.names.index("unemployment gap")
    du_y = y[11, ui]
    w = np.array([v.partial(j)[11, ui] / du_y for j in range(v.nz)])
    print(f"\n[{label}] p={p}, T={v.T}, logL {v.ll:.1f} ({time.time() - t0:.0f}s)")
    print("  alpha (||alpha|| = 1; se): " + ", ".join(f"{n} {a:+.3f} ({s:.3f})" for n, a, s in zip(Z.columns, v.alpha, se)))
    print(f"  yardstick: funds rate +1 pp for 12 months -> unemployment gap at month 12 {du_y:+.3f} pp, output equivalent {-2 * du_y:+.3f}% "
          f"(FRB/US hike at 4 quarters: -0.45%); index F moves {float(y[0, len(v.names) - v.nz:] @ v.alpha):+.3f} on impact")
    print("  funds-rate-equivalent weights per unit: " + ", ".join(f"{n} {wj:+.4f}" for n, wj in zip(Z.columns, w)))
    return v, se, w, du_y


def main():
    x, comp = DL.levels_data()
    out_w, out_i = [], {}
    first = "1990-07"                                           # common first month so BIC compares like with like (max lag 6)
    for label, headline, cols in (("main: core PCE, no house prices", False, FIN0), ("headline PCE", True, FIN0), ("core PCE, + house prices", False, FIN0 + ["house prices"])):
        M = macro_data(headline)
        Z = x[cols]
        s0 = np.array([0.009, 0.57, 0.42, 0.13, -0.032, 0.10, -0.029][:len(cols)]); s0 = s0 / np.linalg.norm(s0)
        starts = [s0, np.r_[1.0, np.zeros(len(cols) - 1)] + 0.05, np.r_[0.6, 0.5, 0.1, 0.1, -0.05, 0.05, -0.02][:len(cols)]]
        if label.startswith("main"):
            bic = {}
            for p in range(1, 7):
                vv = MFVAR(M, Z, p, first=first).fit(starts[:1])
                bic[p] = -2 * vv.ll + vv.nparams() * np.log(vv.T)
                print(f"  p={p}: logL {vv.ll:.1f}, BIC {bic[p]:.1f}", flush=True)
            P_ = min(bic, key=bic.get)
            print(f"BIC chooses p = {P_}")
        v, se, w, du = run(label, M, Z, P_, starts, first)
        for n, a, s, wj in zip(cols, v.alpha, se, w):
            out_w.append(dict(version=label, variable=n, alpha=a, alpha_se=s, ffr_weight=wj, p=P_, yardstick_u_m12=du, yardstick_output=-2 * du))
        out_i[label] = (Z.loc["1990-01":] * w).sum(axis=1, min_count=len(cols))
    pd.DataFrame(out_w).to_csv(os.path.join(HERE, "mf_var_us_results.csv"), float_format="%.5f", index=False)
    I = pd.DataFrame(out_i)
    I.to_csv(os.path.join(HERE, "mf_var_us_monthly.csv"), float_format="%.4f", index_label="month")
    print("\nindex (pp of funds rate): sd", I.std().round(2).to_dict(), "| latest", I.dropna().iloc[-1].round(2).to_dict())


if __name__ == "__main__":
    main()
