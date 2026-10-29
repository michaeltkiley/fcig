"""
ECB-method VAR (mf_var_us.py) with a Gertler-Karadi-style policy indicator (INDEX_QA.md answers 41-42).
    VAR: core PCE inflation gap, unemployment gap, the six index variables (policy rate, 10-year, mortgage spread, BBB spread, equities, real dollar; demeaned levels,
         end of month) and the 2-year Treasury yield (DGS2, end of month, demeaned) as the policy indicator.
    The 2-year yield is NOT in the index: it enters only the financial equations (all financial equations unrestricted); the macro equations see financial variables
         only through F = alpha'Z over the six index variables.
    Identification: the monthly sum of raw NS surprises (1994-2025, excluding 2020) instruments the 2-year residual; same-month effects of a policy shock on every variable =
         Cov(e_t, z_t) / Cov(e_2y,t, z_t) (2-year effect = 1).
    Yardstick: 2-year yield held +1 pp for 12 months by a sequence of identified shocks; later effects through the VAR; effect = -2 x unemployment gap at month 12.
         (Unit: pp of the 2-year yield, the NS unit.)
    Weights: index variable j held +1 for 12 months, others at baseline, divided by the yardstick.
    Sample 1990-2025, all 2020 months excluded from the likelihood; lags by BIC (1-6), 6 lags as a check.
Usage: python experimental/fci_compare/mf_var_us_gk.py
Outputs: mf_var_us_gk.csv (weights), mf_var_us_gk_monthly.csv (index in 2-year-yield pp)
"""
import os, sys
import numpy as np, pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
sys.path.insert(0, os.path.join(ROOT, "experimental", "path_fci"))
import mf_var_us as V
import macro_model_dl as DL
import path_fci as P
import path_fci_gss_ns as Q


class MFVARX(V.MFVAR):
    """MFVAR whose last `ne` financial variables are outside the index (they enter only the financial equations)."""
    def __init__(self, M, Z, p, ne=1, **kw):
        super().__init__(M, Z, p, **kw); self.ne = ne; self.ni = self.nz - ne

    def regressors(self, alpha):
        T, p, nm = self.T, self.p, self.nm
        LM = self.Lags[:, :, :nm].reshape(T, -1)
        LF = self.Lags[:, :, nm:nm + self.ni] @ alpha
        return np.column_stack([np.ones(T), LM, LF]), np.column_stack([np.ones(T), self.Lags.reshape(T, -1)])

    def nparams(self):
        n, nm, nz, p = self.nm + self.nz, self.nm, self.nz, self.p
        return nm * (1 + p * nm + p) + nz * (1 + p * n) + (self.ni - 1) + n * (n + 1) // 2

    def companion(self):
        n, nm, p = self.nm + self.nz, self.nm, self.p
        A = np.zeros((p, n, n))
        for i in range(nm):
            b = self.B[i]
            for l in range(p):
                A[l, i, :nm] = b[1 + l * nm:1 + (l + 1) * nm]
                A[l, i, nm:nm + self.ni] = b[1 + p * nm + l] * self.alpha
        for j in range(self.nz):
            b = self.B[nm + j]
            for l in range(p):
                A[l, nm + j, :] = b[1 + l * n:1 + (l + 1) * n]
        return A


def residuals(v):
    Xm, Xz = v.regressors(v.alpha)
    Xs = [Xm] * v.nm + [Xz] * v.nz
    E = np.column_stack([v.Yd[:, i] - Xs[i] @ v.B[i] for i in range(len(Xs))])
    return pd.DataFrame(E, index=pd.PeriodIndex(v.idx, freq="M"), columns=v.names)


def main():
    x, _ = DL.levels_data()
    d2 = V.fred_m("DGS2").resample("ME").last(); d2.index = d2.index.to_period("M")
    Z = pd.concat([x[V.FIN0], (d2 - d2.loc["1990-01":"2025-12"].mean()).rename("2-year")], axis=1)
    M = V.macro_data(False)
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    _, ns, _, _ = Q.gss_ns(d)
    z = pd.Series(ns).groupby(pd.PeriodIndex(d.Date, freq="M")).sum()
    s0 = np.array([0.009, 0.57, 0.42, 0.13, -0.032, 0.10]); s0 /= np.linalg.norm(s0)
    starts = [s0, np.array([0.1, 0.1, 0.85, 0.5, -0.02, 0.0])]
    bic, fits = {}, {}
    for p in range(1, 7):
        v = MFVARX(M, Z, p, ne=1, first="1990-07").fit(starts)
        bic[p] = -2 * v.ll + v.nparams() * np.log(v.T); fits[p] = v
        print(f"p={p}: T {v.T}, logL {v.ll:.1f}, BIC {bic[p]:.1f}", flush=True)
    pb = min(bic, key=bic.get)
    rows, idx = [], {}
    for p in sorted({pb, 6}):
        v = fits[p]
        se = v.alpha_se()
        E = residuals(v)
        zz = z.reindex(E.index).fillna(0.0)
        E = E.loc["1994-02":]; zz = zz.loc["1994-02":]
        k = v.names.index("2-year"); ui = v.names.index("unemployment gap"); nm = v.nm
        fs = sm.OLS(E["2-year"], sm.add_constant(zz)).fit(cov_type="HC1")
        imp = np.array([np.cov(E[c], zz)[0, 1] for c in v.names]); imp = imp / imp[k]
        A = v.companion(); n = len(v.names); H = 36
        y = np.zeros((H + p, n))
        for t in range(H):
            pred = sum(A[l] @ y[p + t - 1 - l] for l in range(p))
            eps = (1.0 - pred[k]) if t < 12 else 0.0
            y[p + t] = pred + imp * eps
        y = y[p:]
        du = y[11, ui]
        w = {c: float(v.partial(j)[11, ui] / du) for j, c in enumerate(V.FIN0)}
        tag = "BIC" if p == pb else "6 lags"
        print(f"\n[p={p} ({tag})] alpha: " + ", ".join(f"{c} {a:+.3f} ({s:.3f})" for c, a, s in zip(V.FIN0, v.alpha, se)))
        print(f"   first stage: 2-year residual on NS surprises, coef {fs.params.iloc[1]:+.3f} (t {fs.tvalues.iloc[1]:.1f}), F {fs.tvalues.iloc[1] ** 2:.1f}, months {len(zz)}")
        print("   identified same-month effects per 1 pp on the 2-year: " + ", ".join(f"{c} {imp[i]:+.3f}" for i, c in enumerate(v.names)))
        print("   yardstick: unemployment gap months 1,6,12,18,24,36:", np.round(y[[0, 5, 11, 17, 23, 35], ui], 3),
              "| index F months 1,6,12,24:", np.round(y[[0, 5, 11, 23], nm:nm + v.ni] @ v.alpha, 3))
        print("   financial variables at month 12:", dict(zip(v.names[nm:], np.round(y[11, nm:], 3))))
        print(f"   output equivalent at month 12: {-2 * du:+.3f}% ; weights (pp of 2-year per unit): " + ", ".join(f"{c} {wj:+.4f}" for c, wj in w.items()))
        for c in V.FIN0:
            rows.append(dict(lags=p, choice=tag, variable=c, alpha=v.alpha[V.FIN0.index(c)], alpha_se=se[V.FIN0.index(c)], weight=w[c], yardstick_u_m12=du, first_stage_F=fs.tvalues.iloc[1] ** 2))
        idx[f"p={p}"] = (x[V.FIN0] * pd.Series(w)).sum(axis=1, min_count=6)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "mf_var_us_gk.csv"), float_format="%.5f", index=False)
    I = pd.DataFrame(idx).loc["1990-01":]
    I.to_csv(os.path.join(HERE, "mf_var_us_gk_monthly.csv"), float_format="%.4f", index_label="month")
    print("\nindex (pp of 2-year): sd", I.std().round(2).to_dict(), "latest", I.dropna().iloc[-1].round(2).to_dict())


if __name__ == "__main__":
    main()
