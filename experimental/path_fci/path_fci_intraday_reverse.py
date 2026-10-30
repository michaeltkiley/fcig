"""
EXPERIMENTAL add-on (path_fci.py unchanged): reverse regression on the INTRADAY (USMPD event-window) surprises, raw coefficients used as weights.

    path_e = a + w_10y * UST10Y_e + w_eq * SP500_e + w_usd * DXY_e + u_e       (UST10Y in pp, SP500 and DXY returns in %)
    index  = sum_j w_j (x_j - mean_j),   x = 10-year yield (nominal or real: DGS10 less Cleveland Fed expected inflation), 100 ln CAPE, 100 ln real dollar
No rescaling: w_j is pp of path surprise per unit of x_j, and the index is the best linear predictor of the path surprise from these variables (the regression R2 says how
much of the surprise they explain). The weights are estimated once, on the event-window data, and are not re-estimated for the real 10-year.

Usage:  python experimental/path_fci/path_fci_intraday_reverse.py [--sample full|nonzlb] [--real10]
Outputs: path_fci_intraday_reverse_{ms,gs}_<sample>[_real10].png
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
COLS = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true")
    ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    ev = ev.dropna(subset=list(COLS.values())).reset_index(drop=True)
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    names = list(COLS)
    r = sm.OLS(ev.path, sm.add_constant(ev[list(COLS.values())])).fit(cov_type="HC1")
    w = pd.Series({n: r.params[c] for n, c in COLS.items()})
    print(f"{len(ev)} events ({a.sample}); R2 {r.rsquared:.2f}. Weights (pp of path surprise per unit; se): " + ", ".join(f"{n} {w[n]:+.4f} ({r.bse[c]:.4f})" for n, c in COLS.items()))
    tag = "_real10" if a.real10 else ""
    ten = "real 10-yr" if a.real10 else "10-yr"
    idx = sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms_frbus = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    gs = G.fci.reindex(X.index)
    print(f"sd of index {idx.std():.2f} pp (level), daily change {idx.diff().std():.3f}; MS FRB/US index sd {ms_frbus.std():.2f}, daily {ms_frbus.diff().std():.3f}")
    print(f"vs MS FRB/US index: corr levels {np.corrcoef(idx, ms_frbus)[0, 1]:.2f}, daily changes {idx.diff().corr(ms_frbus.diff()):.2f}; latest {idx.iloc[-1]:+.2f} vs {ms_frbus.iloc[-1]:+.2f}")
    print(f"vs GS FCI: corr levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily changes {idx.diff().corr(gs.diff()):.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for key in ("ms", "gs"):
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"Reverse-regression weights (intraday event-window, unscaled), {ten}, CAPE, real dollar (left axis, pp of path surprise)")
        ax.axhline(0, color="gray", lw=0.8)
        ax.set_ylabel("tighter above zero (vs 1990-2026 average)", fontsize=11)
        if key == "ms":
            ax.plot(ms_frbus.index, ms_frbus, color="#d62728", lw=1.8, label=f"MS-style index, FRB/US weights, all five variables, {ten} (left axis, pp of funds rate)")
            ax.set_ylim(min(idx.min(), ms_frbus.min()) - 0.3, max(idx.max(), ms_frbus.max()) + 0.3)
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"vs MS-style index ({ten}): corr {np.corrcoef(idx, ms_frbus)[0, 1]:.2f} levels, {idx.diff().corr(ms_frbus.diff()):.2f} daily changes"
        else:
            k = gs.std() / idx.std()
            gl = (gs - gs.mean()) / k
            allv = pd.concat([idx, gl]); pad = 0.04 * (allv.max() - allv.min())
            lo, hi = allv.min() - pad, allv.max() + pad
            ax.set_ylim(lo, hi)
            b = ax.twinx(); b.plot(gs.index, gs, color="#d62728", lw=1.8, label="GS FCI, Goldman-style weights (right axis, scaled to the same spread)")
            b.set_ylim(gs.mean() + k * lo, gs.mean() + k * hi); b.set_ylabel("GS FCI", fontsize=11); b.tick_params(labelsize=11)
            h1, l1 = ax.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels()
            ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"vs GS FCI: corr {np.corrcoef(idx, gs)[0, 1]:.2f} levels, {idx.diff().corr(gs.diff()):.2f} daily changes"
        ax.set_title(f"Index with intraday reverse-regression weights {title}", fontsize=12); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_intraday_reverse_{key}_{a.sample}{tag}.png"), dpi=130)


if __name__ == "__main__":
    main()
