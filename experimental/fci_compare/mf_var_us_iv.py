"""
ECB-method VAR (mf_var_us.py) with the funds-rate yardstick identified by Nakamura-Steinsson surprises as an external instrument (INDEX_QA.md answer 37).
    VAR and index as in mf_var_us.py (main version: core PCE inflation gap, unemployment gap, six financial variables; alpha by ML).
    Identification: same-month effects of a policy shock = Cov(e_t, z_t) / Cov(e_ffr,t, z_t), where e_t are the VAR residuals and z_t the monthly sum of NS surprises
                    (1994-2025, excluding 2020); the funds-rate effect is normalized to 1. Later effects: VAR dynamics.
    Yardstick: funds rate held +1 pp for 12 months by a sequence of identified policy shocks; effect = -2 x unemployment gap at month 12.
    Weights: variable j held +1 for 12 months, others at baseline (as mf_var_us.py), divided by the yardstick.
Run for 1 lag (BIC) and 6 lags.
Usage: python experimental/fci_compare/mf_var_us_iv.py
Output: mf_var_us_iv.csv
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


def residuals(v):
    Xm, Xz = v.regressors(v.alpha)
    Xs = [Xm] * v.nm + [Xz] * v.nz
    E = np.column_stack([v.Yd[:, i] - Xs[i] @ v.B[i] for i in range(len(Xs))])
    return pd.DataFrame(E, index=pd.PeriodIndex(v.idx, freq="M"), columns=v.names)


def main():
    x, _ = DL.levels_data()
    M = V.macro_data(False); Z = x[V.FIN0]
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    _, ns, _, _ = Q.gss_ns(d)
    z = pd.Series(ns).groupby(pd.PeriodIndex(d.Date, freq="M")).sum()
    s0 = np.array([0.009, 0.57, 0.42, 0.13, -0.032, 0.10]); s0 /= np.linalg.norm(s0)
    starts = [s0, np.array([0.1, 0.1, 0.85, 0.5, -0.02, 0.0])]
    rows = []
    for p in (1, 6):
        v = V.MFVAR(M, Z, p, first="1990-07").fit(starts)
        E = residuals(v)
        zz = z.reindex(E.index).fillna(0.0)
        E = E.loc["1994-02":]; zz = zz.loc["1994-02":]
        k = v.names.index("policy rate"); ui = v.names.index("unemployment gap"); nm = v.nm
        fs = sm.OLS(E["policy rate"], sm.add_constant(zz)).fit(cov_type="HC1")
        imp = np.array([np.cov(E[c], zz)[0, 1] for c in v.names]); imp = imp / imp[k]
        A = v.companion(); n = len(v.names); H = 36
        y = np.zeros((H + p, n))
        for t in range(H):
            pred = sum(A[l] @ y[p + t - 1 - l] for l in range(p))
            eps = (1.0 - pred[k]) if t < 12 else 0.0
            y[p + t] = pred + imp * eps
        y = y[p:]
        du = y[11, ui]
        print(f"\n[p={p}] alpha: " + ", ".join(f"{c} {a:+.3f}" for c, a in zip(Z.columns, v.alpha)))
        print(f"   first stage: policy-rate residual on NS surprises, coef {fs.params.iloc[1]:+.3f} (t {fs.tvalues.iloc[1]:.1f}), F {fs.tvalues.iloc[1] ** 2:.1f}, months {len(zz)}")
        print("   identified same-month effects per 1 pp funds rate: " + ", ".join(f"{c} {imp[i]:+.3f}" for i, c in enumerate(v.names)))
        print("   yardstick: u gap months 1,6,12,18,24,36:", np.round(y[[0, 5, 11, 17, 23, 35], ui], 3), "| index F months 1,6,12,24:", np.round(y[[0, 5, 11, 23], nm:] @ v.alpha, 3))
        print("   financial variables at month 12:", dict(zip(v.names[nm:], np.round(y[11, nm:], 3))))
        w = {c: float(v.partial(j)[11, ui] / du) for j, c in enumerate(Z.columns)}
        print(f"   output equivalent of the yardstick at month 12: {-2 * du:+.3f}% (FRB/US: -0.45%);  weights: " + ", ".join(f"{c} {wj:+.4f}" for c, wj in w.items()))
        for c, wj in w.items():
            rows.append(dict(lags=p, variable=c, alpha=v.alpha[list(Z.columns).index(c)], weight=wj, yardstick_u_m12=du, first_stage_F=fs.tvalues.iloc[1] ** 2))
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "mf_var_us_iv.csv"), float_format="%.5f", index=False)


if __name__ == "__main__":
    main()
