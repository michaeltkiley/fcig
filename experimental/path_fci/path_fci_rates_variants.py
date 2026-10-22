"""
EXPERIMENTAL add-on: the GSS-path and Nakamura-Steinsson indexes (path_fci_gss_ns.py, full-covariance weights) with three versions of the 10-year in the index data.
Weights are estimated once, from the event-window surprise in the (nominal) 10-year, the S&P 500 and the dollar index, and are NOT re-estimated for the real versions.
    nominal   DGS10
    real      DGS10 less Cleveland Fed 10-year expected inflation (FRED EXPINF10YR)
    r* gap    real 10-year less Kiley's one-sided r* (experimental/ms_fci/kiley_rstar.csv)
CAPE and the real dollar are the same in all three. Each version is a deviation from its own 1990-2026 daily mean.
Comparators: the MS-style FRB/US-weighted index with the same 10-year version, and the GS FCI.

Usage:  python experimental/path_fci/path_fci_rates_variants.py
Outputs: path_fci_rates_{gss,ns}.png, path_fci_rates_daily.csv
"""
import os
import numpy as np, pandas as pd
import path_fci as P
import path_fci_gss_ns as Q

HERE, ROOT = P.HERE, P.ROOT


def main():
    ev = P.events(P.USMPD)
    d = ev.dropna(subset=Q.FUT + ["UST2Y"] + list(Q.ENDOG.values())).reset_index(drop=True)
    gss, ns, _, _ = Q.gss_ns(d)
    W = {}
    for fname, fac in (("gss", gss), ("ns", ns)):
        W[fname] = pd.Series(Q.estimate(d, fac, True)[0], index=list(Q.ENDOG))
    print("weights (pp of factor per unit): \n" + pd.DataFrame(W).round(4).to_string())
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    req = float(sens.loc["req", "unit_size"])
    versions = {"nominal 10-yr": (False, False), "real 10-yr": (True, False), "real 10-yr gap to r*": (False, True)}
    series, msf = {}, {}
    for vlab, (real, rstar) in versions.items():
        P.L.REAL10, P.L.RSTAR = real, rstar
        X, G = P.L.build()
        msf[vlab] = P.L.level(X, sens["ffr_eq_q4"].to_dict(), req).Total
        for fname in W:
            series[(fname, vlab)] = sum(W[fname][n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in W[fname].index)
    gs = G.fci.reindex(X.index)
    D = pd.DataFrame({f"{k[0]} | {k[1]}": v for k, v in series.items()})
    D.to_csv(os.path.join(HERE, "path_fci_rates_daily.csv"), float_format="%.4f", index_label="date")
    names = {"gss": "GSS path factor", "ns": "Nakamura-Steinsson policy news"}
    print("\n                                        latest | corr with matching MS FRB/US (levels / daily) | corr with GS FCI (levels / daily) | level sd")
    for fname in W:
        for vlab in versions:
            s = series[(fname, vlab)]
            print(f"{names[fname][:5]:5s} {vlab:22s} {s.iloc[-1]:+6.2f} | {np.corrcoef(s, msf[vlab])[0, 1]:.2f} / {s.diff().corr(msf[vlab].diff()):.2f} | {np.corrcoef(s, gs)[0, 1]:.2f} / {s.diff().corr(gs.diff()):.2f} | {s.std():.2f}")
    print("MS FRB/US latest:", {k: round(float(v.iloc[-1]), 2) for k, v in msf.items()})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cols = {"nominal 10-yr": "#d62728", "real 10-yr": "#1f5fa8", "real 10-yr gap to r*": "#2ca02c"}
    for fname in W:
        fig, ax = plt.subplots(figsize=(13, 6.5))
        for vlab in versions:
            ax.plot(series[(fname, vlab)].index, series[(fname, vlab)], color=cols[vlab], lw=1.6, label=f"{vlab} (latest {series[(fname, vlab)].iloc[-1]:+.2f})")
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        ax.set_ylabel(f"tighter above zero (vs 1990-2026 average); pp of {'GSS path (1 pp on ED4)' if fname == 'gss' else 'NS policy news (1 pp on the 2-year)'}", fontsize=10)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=3, fontsize=10, frameon=False)
        ax.set_title(f"{names[fname]} index: nominal, real and r*-adjusted 10-year (same weights; CAPE and real dollar unchanged)", fontsize=12)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_rates_{fname}.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
