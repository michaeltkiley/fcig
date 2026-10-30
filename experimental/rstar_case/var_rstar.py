"""
Market output VAR on the r*-gap market index (RSTAR_QA S5): same design as real_case/var_real.py (unemployment gap and M; 1973-01..2026-09; 2020 dummied;
Cholesky with unemployment first; 4 lags main, 12 check; bootstrap 95% bands), M = MKT LW (main) or MKT Ki (check) from rstar_indexes_monthly.csv.
Also: fit of the unemployment equation (residual sd) against the real-case VAR with the same lags (does the r*-gap index predict unemployment better or worse?).
Usage: python experimental/rstar_case/var_rstar.py      Outputs: var_rstar_phi.csv, var_rstar_monthly.csv, var_rstar_12lag.png
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


def rd(p):
    d = pd.read_csv(p, index_col=0); d.index = pd.PeriodIndex(d.index, freq="M"); return d


def setup(M, u):
    D = pd.DataFrame({"u": u, "M": M}).loc["1973-01":"2026-09"].dropna()
    dum = pd.DataFrame({f"d2020_{m:02d}": (D.index == pd.Period(f"2020-{m:02d}", "M")).astype(float) for m in range(1, 13)}, index=D.index)
    D.index = D.index.to_timestamp(); dum.index = D.index
    return D, dum


def main():
    R = rd(os.path.join(HERE, "rstar_indexes_monthly.csv"))
    real = rd(os.path.join(ROOT, "experimental", "real_case", "market_real_monthly.csv")).MKT_real
    u = MO.V.macro_data(False)["unemployment gap"]
    out, phis = {}, {}
    for lab in ("LW", "Ki"):
        M = R[f"MKT {lab}"]
        D, dum = setup(M, u)
        sel = VAR(D, exog=dum).select_order(12)
        print(f"\n===== M = r*-gap market index ({lab}); {D.index[0]:%Y-%m}..{D.index[-1]:%Y-%m} ({len(D)} months); BIC lag {sel.bic}, AIC {sel.aic} =====")
        out[f"EP {lab}"] = M
        for p in (4, 12):
            r = VAR(D, exog=dum).fit(p)
            Dr, dr = setup(real, u); rr = VAR(Dr, exog=dr).fit(p)
            gc = r.test_causality("u", ["M"], kind="f")
            irf = r.irf(36); oi = irf.orth_irfs; sc = oi[0, 1, 1]
            Phi = oi[:, 0, 1] / sc; se = irf.stderr(orth=True)[:, 0, 1] / sc
            blo, bhi = MF.boot_bands(r, D, dum, p)
            sig = [h for h in range(1, 37) if blo[h] > 0]
            print(f"[p={p}] Granger F {gc.test_statistic:.2f}, p {gc.pvalue:.5f};  u-equation residual sd {r.resid['u'].std():.4f} (real case {rr.resid['u'].std():.4f})")
            print("   Phi: " + "  ".join(f"m{h} {Phi[h]:+.3f} [{blo[h]:+.3f},{bhi[h]:+.3f}]" for h in (3, 6, 12, 24, 36)))
            print(f"   band above zero months {sig[0] if sig else '-'}..{sig[-1] if sig else '-'} ({len(sig)} of 36); yardstick Phi(12) {Phi[12]:+.3f}")
            wcp = np.array([Phi[m] - (Phi[m - 1] if m > 0 else 0.0) for m in range(13)]) / Phi[12]
            wgi = np.array([Phi[m + 12] - Phi[m] for m in range(12)]) / Phi[12]
            CP = sum(wcp[m] * M.shift(m) for m in range(13))
            GI = sum(wgi[m] * M.diff().shift(m) for m in range(12))
            out.update({f"CP p{p} {lab}": CP, f"forward impetus p{p} {lab}": GI, f"realized impetus p{p} {lab}": CP.diff(12)})
            phis[f"{lab} p{p}"] = Phi
    pd.DataFrame(phis).to_csv(os.path.join(HERE, "var_rstar_phi.csv"), float_format="%.5f", index_label="month")
    O = pd.DataFrame(out).loc["1974-01":"2026-09"]
    O.to_csv(os.path.join(HERE, "var_rstar_monthly.csv"), float_format="%.4f", index_label="month")
    fg = R["FCI-G 1yr LW"]
    print("\ncorrelation with the r*-gap FCI-G (1-year, LW), 1975-2026, and latest:")
    for c in [c for c in O.columns if c.endswith("LW")]:
        j = pd.concat([O[c], fg], axis=1).loc["1975-01":].dropna()
        print(f"   {c:28s} {j.corr().iloc[0, 1]:+.2f}   latest {O[c].dropna().iloc[-1]:+.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 6.5))
    t = O.index.to_timestamp()
    for c, col, lb in (("EP LW", "#ff7f0e", "Eventual pressure: r*-gap market index (LW)"), ("CP p12 LW", "#1f5fa8", "Current pressure (12-lag VAR)"),
                       ("forward impetus p12 LW", "#d62728", "Forward impetus (12-lag VAR)")):
        ax.plot(t, O[c], color=col, lw=1.3, label=lb)
    ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.legend(fontsize=9, frameon=False, loc="upper right")
    ax.set_ylabel("pp of 2-year yield per NS unit; tighter above zero (vs 1973-2026 average)")
    ax.set_title("r*-gap market-index output lens (Laubach-Williams r*), VAR 1973-2026 (2020 dummied), 12 lags", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "var_rstar_12lag.png"), dpi=130)


if __name__ == "__main__":
    main()
