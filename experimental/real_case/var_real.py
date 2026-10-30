"""
Market output VAR on the real market index (REAL_QA R14): same design as market_macro/mkt_dynamic_full.py, only the market index changes.
    VAR: unemployment gap (UNRATE - NROU) and the real market index (market_real.py, MKT_real), 1973-01..latest common month, 12 monthly 2020 dummies (exogenous),
    Cholesky with unemployment first; 4 lags (main) and 12 (check), BIC reported. Bootstrap 95% bands (500 reps, recursive, dummies fixed).
    Phi(m) = unemployment response m months after a 1-unit shock to M; yardstick Phi(12).
    Indexes (real market-index units, pp of the 2-year yield per NS unit; 1-year lookback):
      eventual pressure  EP = MKT_real
      current pressure   CP(t) = sum_{m=0}^{12} [Phi(m) - Phi(m-1)] / Phi(12) * M(t-m)
      forward impetus    GI(t) = sum_{m=0}^{11} [Phi(m+12) - Phi(m)] / Phi(12) * dM(t-m)
      realized impetus   CP(t) - CP(t-12)
Usage: python experimental/real_case/var_real.py
Outputs: var_real_phi.csv, var_real_monthly.csv, var_real_12lag.png
"""
import os, sys, warnings
import numpy as np, pandas as pd
from statsmodels.tsa.api import VAR
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experimental", "market_macro"))
import mkt_output as MO
import mkt_dynamic_full as MF


def main():
    mk = pd.read_csv(os.path.join(HERE, "market_real_monthly.csv"), index_col=0); mk.index = pd.PeriodIndex(mk.index, freq="M")
    M = mk.MKT_real
    u = MO.V.macro_data(False)["unemployment gap"]
    D = pd.DataFrame({"u": u, "M": M}).loc["1973-01":].dropna()
    end = D.index[-1]
    dum = pd.DataFrame({f"d2020_{m:02d}": (D.index == pd.Period(f"2020-{m:02d}", "M")).astype(float) for m in range(1, 13)}, index=D.index)
    D.index = D.index.to_timestamp(); dum.index = D.index
    sel = VAR(D, exog=dum).select_order(12)
    print(f"sample {D.index[0]:%Y-%m}..{end} ({len(D)} months), 2020 dummied; BIC lag order {sel.bic}, AIC {sel.aic}")
    nom = pd.read_csv(os.path.join(ROOT, "experimental", "market_macro", "mkt_dynamic_full_phi.csv"), index_col=0)
    res, out = {}, {"EP (real market index)": M}
    for p in sorted({4, 12, int(sel.bic)}):
        r = VAR(D, exog=dum).fit(p)
        gc = r.test_causality("u", ["M"], kind="f")
        irf = r.irf(36); oi = irf.orth_irfs; sc = oi[0, 1, 1]
        Phi = oi[:, 0, 1] / sc; se = irf.stderr(orth=True)[:, 0, 1] / sc
        blo, bhi = MF.boot_bands(r, D, dum, p)
        print(f"\n[p={p}{' (BIC)' if p == sel.bic else ''}] M Granger-causes u: F {gc.test_statistic:.2f}, p {gc.pvalue:.5f}")
        print(f"   {'month':>5} {'resp':>7} {'t':>5} {'bootstrap 95%':>17} {'nominal':>8}")
        for h in (1, 3, 6, 9, 12, 18, 24, 36):
            nv = nom[str(p)].iloc[h] if str(p) in nom else np.nan
            print(f"   {h:>5} {Phi[h]:+7.3f} {Phi[h] / se[h]:5.1f} [{blo[h]:+.3f},{bhi[h]:+.3f}] {nv:+8.3f}")
        sig = [h for h in range(1, 37) if blo[h] > 0]
        print(f"   bootstrap 95% band above zero in months {sig[0] if sig else '-'}..{sig[-1] if sig else '-'} ({len(sig)} of 36); M own response m12 {oi[12, 1, 1] / sc:+.2f}, m24 {oi[24, 1, 1] / sc:+.2f}")
        print(f"   yardstick Phi(12) {Phi[12]:+.3f} u pp per unit (output {-2 * Phi[12]:+.2f}%)")
        wcp = np.array([Phi[m] - (Phi[m - 1] if m > 0 else 0.0) for m in range(13)]) / Phi[12]
        wgi = np.array([Phi[m + 12] - Phi[m] for m in range(12)]) / Phi[12]
        CP = sum(wcp[m] * M.shift(m) for m in range(13))
        GI = sum(wgi[m] * M.diff().shift(m) for m in range(12))
        out.update({f"CP p{p}": CP, f"forward impetus p{p}": GI, f"realized impetus p{p}": CP.diff(12)})
        res[p] = Phi
    pd.DataFrame(res).to_csv(os.path.join(HERE, "var_real_phi.csv"), float_format="%.5f", index_label="month")
    O = pd.DataFrame(out).loc["1974-01":]
    O.to_csv(os.path.join(HERE, "var_real_monthly.csv"), float_format="%.4f", index_label="month")
    fg = pd.read_csv(os.path.join(HERE, "fcig_real_monthly.csv"), index_col=0)["1yr all real"]; fg.index = pd.PeriodIndex(fg.index, freq="M")
    print("\ncorrelations with the all-real FCI-G (1-year lookback), 1975-2026:")
    for c in O.columns:
        j = pd.concat([O[c], fg], axis=1).loc["1975-01":].dropna()
        print(f"   {c:26s} {j.corr().iloc[0, 1]:+.2f}   latest {O[c].dropna().iloc[-1]:+.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    t = O.index.to_timestamp()
    for c, col, lab in (("EP (real market index)", "#ff7f0e", "Eventual pressure: real market index"), ("CP p12", "#1f5fa8", "Current pressure (12-lag VAR, 1-year lookback)"),
                        ("forward impetus p12", "#d62728", "Forward impetus (12-lag VAR)")):
        ax.plot(t, O[c], color=col, lw=1.3, label=lab)
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(fontsize=9, frameon=False, loc="upper right")
    ax.set_ylabel("pp of 2-year yield per NS unit; tighter above zero (vs 1973-2026 average)")
    ax.set_title("Real market-index output lens, VAR 1973-2026 (2020 dummied), 12 lags", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "var_real_12lag.png"), dpi=130)


if __name__ == "__main__":
    main()
