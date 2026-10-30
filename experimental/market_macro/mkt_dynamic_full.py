"""
Market-index output lens estimated through the end of the data, excluding 2020 (12 monthly dummies for 2020 as exogenous regressors; 2021 onward kept).
Same two-variable VAR (unemployment gap, market index M; Cholesky, u first), sample 1973-01..latest common month. Lags: 4 and 12 (user), and the BIC choice.
Reports: Granger test, unemployment response to a 1-unit M shock with asymptotic 95% bands and bootstrap 95% bands where available, the yardstick Phi(12),
and the dynamic indexes (current pressure, forward impetus, realized impetus; 1-year lookback) with their correlation with FCI-G (1-year lookback),
compared with the 1973-2019 estimates (mkt_dynamic_lags.py).
Usage: python experimental/market_macro/mkt_dynamic_full.py
"""
import os, sys
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import mkt_output as MO
LL, V = MO.LL, MO.V


def boot_bands(r, D, ex, p, H=36, reps=500, seed=7):
    """Residual bootstrap (recursive design, 2020 dummies held fixed), 95% percentile bands for the scaled u response."""
    rs = np.random.default_rng(seed)
    Y = D.values; T = len(Y); k = 2
    coefs, inter = r.coefs, r.params.values
    resid = r.resid.values
    exv = ex.values if ex is not None else None
    out = []
    for _ in range(reps):
        Yb = Y.copy()
        e = resid[rs.integers(0, len(resid), size=T - p)]
        for t in range(p, T):
            x = inter[0].copy()
            if exv is not None:
                x = x + exv[t] @ inter[1:1 + exv.shape[1]]
            for l in range(p):
                x = x + coefs[l] @ Yb[t - 1 - l]
            Yb[t] = x + e[t - p]
        rb = VAR(pd.DataFrame(Yb, index=D.index, columns=D.columns), exog=ex).fit(p)
        oi = rb.irf(H).orth_irfs
        out.append(oi[:, 0, 1] / oi[0, 1, 1])
    out = np.array(out)
    return np.percentile(out, 2.5, axis=0), np.percentile(out, 97.5, axis=0)


def main():
    F = LL.financial()[MO.VARS]
    u = V.macro_data(False)["unemployment gap"]
    J0 = pd.concat([u.rename("u"), F], axis=1).loc["1973-01":].dropna()
    end = J0.index[-1]
    base = J0[MO.VARS].loc[[t for t in J0.index if t.year != 2020]]
    Ml = pd.Series((J0[MO.VARS] - base.mean()).values @ MO.W, index=J0.index)
    D = pd.DataFrame({"u": J0.u, "M": Ml})
    dum = pd.DataFrame({f"d2020_{m:02d}": (D.index == pd.Period(f"2020-{m:02d}", "M")).astype(float) for m in range(1, 13)}, index=D.index)
    D.index = D.index.to_timestamp(); dum.index = D.index
    sel = VAR(D, exog=dum).select_order(12)
    print(f"sample {D.index[0]:%Y-%m}..{end} ({len(D)} months), 2020 dummied; BIC lag order {sel.bic}, AIC {sel.aic}")
    tr = pd.read_csv(os.path.join(ROOT, "experimental", "fci_compare", "transmission_v3_monthly.csv"), index_col=0); tr.index = pd.PeriodIndex(tr.index, freq="M")
    M = tr["MKT"]
    f1 = pd.read_csv(os.path.join(ROOT, "raw", "fed_monthly_1yr.csv"), parse_dates=["date"]).set_index("date").iloc[:, 0]; f1.index = f1.index.to_period("M")
    rep = pd.read_csv(os.path.join(ROOT, "fcig_replication_monthly.csv")); rep.index = pd.PeriodIndex(rep["month"], freq="M")
    fg = pd.concat([f1, rep["1yr|FCI-G"].loc[f1.index[-1] + 1:]]) / 0.4525
    res = {}
    for p in sorted({4, 12, int(sel.bic)}):
        r = VAR(D, exog=dum).fit(p)
        gc = r.test_causality("u", ["M"], kind="f")
        irf = r.irf(36); oi = irf.orth_irfs; sc = oi[0, 1, 1]
        Phi = oi[:, 0, 1] / sc; se = irf.stderr(orth=True)[:, 0, 1] / sc
        blo, bhi = boot_bands(r, D, dum, p)
        print(f"\n[p={p}{' (BIC)' if p == sel.bic else ''}] M Granger-causes u: F {gc.test_statistic:.2f}, p {gc.pvalue:.5f}")
        print(f"   {'month':>5} {'resp':>7} {'t':>5} {'asy 95%':>17} {'bootstrap 95%':>17}")
        for h in (1, 3, 6, 9, 12, 18, 24, 36):
            print(f"   {h:>5} {Phi[h]:+7.3f} {Phi[h] / se[h]:5.1f} [{Phi[h] - 1.96 * se[h]:+.3f},{Phi[h] + 1.96 * se[h]:+.3f}] [{blo[h]:+.3f},{bhi[h]:+.3f}]")
        sig = [h for h in range(1, 37) if blo[h] > 0]
        print(f"   bootstrap 95% band above zero in months {sig[0] if sig else '-'}..{sig[-1] if sig else '-'} ({len(sig)} of 36); M own response m12 {oi[12, 1, 1] / sc:+.2f}, m24 {oi[24, 1, 1] / sc:+.2f}")
        print(f"   yardstick Phi(12) {Phi[12]:+.3f} u pp per unit (output {-2 * Phi[12]:+.2f}%)")
        wcp = np.array([Phi[m] - (Phi[m - 1] if m > 0 else 0.0) for m in range(13)]) / Phi[12]
        wgi = np.array([Phi[m + 12] - Phi[m] for m in range(12)]) / Phi[12]
        CP = sum(wcp[m] * M.shift(m) for m in range(13))
        GI = sum(wgi[m] * M.diff().shift(m) for m in range(12))
        Jx = pd.DataFrame({"CP": CP, "forward impetus": GI, "realized impetus": CP.diff(12), "FCI-G 1yr": fg, "M": M}).loc["1991-01":]
        print("   corr with FCI-G 1yr: " + ", ".join(f"{c} {Jx[c].corr(Jx['FCI-G 1yr']):.2f}" for c in ("M", "CP", "forward impetus", "realized impetus"))
              + f";  corr(CP, M) {Jx.CP.corr(Jx.M):.2f};  latest: " + ", ".join(f"{c} {Jx[c].dropna().iloc[-1]:+.2f}" for c in ("M", "CP", "forward impetus", "realized impetus")))
        res[p] = Phi
    pd.DataFrame(res).to_csv(os.path.join(HERE, "mkt_dynamic_full_phi.csv"), float_format="%.5f", index_label="month")


if __name__ == "__main__":
    main()
