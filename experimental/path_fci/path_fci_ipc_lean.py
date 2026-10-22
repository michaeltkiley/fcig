"""
EXPERIMENTAL add-on (path_fci.py, path_fci_ipc.py unchanged): instrumental principal component with a lean instrument set.

Instruments Z (event window), none of them the three variables themselves:
    R: ED1, UST2Y                                  (rate indicators only)
    S: ED1, UST2Y, SPFUT, EURUSD, USDJPY           (adds the S&P futures return and the two exchange rates as other measures of the equity and dollar moves)
Step 1  principal components F of standardised Z (k = 1 for R, 2 for S): the common policy news in the instruments, free of the measurement error specific to each.
Step 2  instrumented path: f = fitted value of the raw path surprise (ED4 residual) on F, with MP1 as a control (the part of the path surprise the instruments explain).
        f is in pp of path surprise.  Purge each variable:  x_j = a_j + b_j f + c_j MP1 + e_j  (this is 2SLS of x_j on the path surprise with F as instruments); b_j = true response per 1 pp.
Step 3  weights from the error covariance Psi of e (full, 3 x 3):  w = Psi^-1 b / (b' Psi^-1 b), so w'b = 1: pp of path surprise per unit of x_j, no double counting.
Index = sum_j w_j (x_j - mean_j): real 10-year (--real10), 100 ln CAPE, 100 ln real dollar. Weights are estimated once, in the event window.
Caution for S: SPFUT and the FX rates share news with SP500 and DXY themselves (their errors are not independent), which biases the purged responses of those two variables.

Usage:  python experimental/path_fci/path_fci_ipc_lean.py [--sample full|nonzlb] [--real10]
Outputs: path_fci_ipc_lean_{ms,gs}_<set>_<sample>[_real10].png
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
ENDOG = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}
SETS = {"R": (["ED1", "UST2Y"], 1), "S": (["ED1", "UST2Y", "SPFUT", "EURUSD", "USDJPY"], 2)}


def estimate(d, zcols, k):
    Z = d[zcols].values
    Z = (Z - Z.mean(0)) / Z.std(0)
    U, S, Vt = np.linalg.svd(Z, full_matrices=False)
    F = U[:, :k] * S[:k]
    first = sm.OLS(d.path.values, np.column_stack([np.ones(len(d)), d.MP1.values, F])).fit()
    f = F @ first.params[2:]                                  # instrumented path (excludes the constant and the MP1 part)
    X2 = sm.add_constant(pd.DataFrame({"f": f, "MP1": d.MP1.values}))
    cols = list(ENDOG.values())
    res = [sm.OLS(d[c].values, X2).fit(cov_type="HC1") for c in cols]
    b = np.array([r.params["f"] for r in res])
    R = np.array([r.resid for r in res]).T
    Pi = np.linalg.inv(np.cov(R.T, ddof=3))
    w = Pi @ b
    return w / (b @ w), b, [r.bse["f"] for r in res], first, res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true")
    ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    tag = "_real10" if a.real10 else ""
    ten = "real 10-yr" if a.real10 else "10-yr"
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms_frbus = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    gs = G.fci.reindex(X.index)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = list(ENDOG)
    for sname, (zcols, k) in SETS.items():
        d = ev.dropna(subset=zcols + list(ENDOG.values())).reset_index(drop=True)
        if a.sample == "nonzlb":
            d = d[~P.in_zlb(d.Date)].reset_index(drop=True)
        w, b, se, first, res = estimate(d, zcols, k)
        print(f"\n[{sname}: {', '.join(zcols)}; {k} PC] {len(d)} events ({a.sample}). Instruments explain {first.rsquared:.0%} of the path surprise (incl. MP1 control); F-test of the PCs: {first.f_pvalue:.1e}")
        print("  purged response to +1 pp path (se): " + ", ".join(f"{n} {b[i]:+.3f} ({se[i]:.3f})" for i, n in enumerate(names)))
        rng = np.random.default_rng(3); bs = np.array([estimate(d.iloc[rng.integers(0, len(d), len(d))].reset_index(drop=True), zcols, k)[0] for _ in range(300)])
        print("  weights: " + ", ".join(f"{n} {w[i]:+.4f} [{np.percentile(bs[:, i], 5):+.3f}, {np.percentile(bs[:, i], 95):+.3f}]" for i, n in enumerate(names)) + f"; shares {', '.join(f'{x:.0%}' for x in w * b)}")
        ww = pd.Series(w, index=names)
        idx = sum(ww[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
        print(f"  index: level sd {idx.std():.2f}, daily sd {idx.diff().std():.3f}; vs MS FRB/US: levels {np.corrcoef(idx, ms_frbus)[0, 1]:.2f}, daily {idx.diff().corr(ms_frbus.diff()):.2f}; "
              f"vs GS FCI: levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily {idx.diff().corr(gs.diff()):.2f}; latest {idx.iloc[-1]:+.2f}")
        for key in ("ms", "gs"):
            fig, ax = plt.subplots(figsize=(13, 6.5))
            ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"Instrumental-PC weights, instruments {'+'.join(zcols)}; {ten}, CAPE, real dollar (left axis, pp of path surprise)")
            ax.axhline(0, color="gray", lw=0.8); ax.set_ylabel("tighter above zero (vs 1990-2026 average)", fontsize=11)
            if key == "ms":
                ax.plot(ms_frbus.index, ms_frbus, color="#d62728", lw=1.8, label=f"MS-style index, FRB/US weights, all five variables, {ten} (left axis, pp of funds rate)")
                ax.set_ylim(min(idx.min(), ms_frbus.min()) - 0.3, max(idx.max(), ms_frbus.max()) + 0.3)
                ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=9, frameon=False)
                title = f"vs MS-style index: corr {np.corrcoef(idx, ms_frbus)[0, 1]:.2f} levels, {idx.diff().corr(ms_frbus.diff()):.2f} daily changes"
            else:
                kk = gs.std() / idx.std(); gl = (gs - gs.mean()) / kk
                allv = pd.concat([idx, gl]); pad = 0.04 * (allv.max() - allv.min()); lo, hi = allv.min() - pad, allv.max() + pad
                ax.set_ylim(lo, hi)
                bb = ax.twinx(); bb.plot(gs.index, gs, color="#d62728", lw=1.8, label="GS FCI, Goldman-style weights (right axis, scaled to the same spread)")
                bb.set_ylim(gs.mean() + kk * lo, gs.mean() + kk * hi); bb.set_ylabel("GS FCI", fontsize=11); bb.tick_params(labelsize=11)
                h1, l1 = ax.get_legend_handles_labels(); h2, l2 = bb.get_legend_handles_labels()
                ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=9, frameon=False)
                title = f"vs GS FCI: corr {np.corrcoef(idx, gs)[0, 1]:.2f} levels, {idx.diff().corr(gs.diff()):.2f} daily changes"
            ax.set_title(f"Lean instrumental-PC index {title}", fontsize=12); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
            fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_ipc_lean_{key}_{sname}_{a.sample}{tag}.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
