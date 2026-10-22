"""
EXPERIMENTAL add-on (path_fci.py unchanged): IV reverse regression with a lean instrument set.

    path_e = a + w_10y UST10Y_e + w_eq SP500_e + w_usd DXY_e + g MP1_e + u_e     (event window; UST10Y, SP500, DXY endogenous; MP1 = target surprise, exogenous control)
Instruments (excluded):
    L1: ED1 (the one rate futures contract), SPFUT (S&P E-mini futures return), EURUSD, USDJPY (other measures of the dollar move)
    L2: L1 + UST2Y
Why: the path surprise is the ED4 residual, so ED2-ED4 share contract noise with it and cannot be excluded. ED1 has its own noise; SPFUT and the two exchange rates are alternative
measures of the equity and dollar moves whose errors should be independent of the 10-year's. Each endogenous variable then has its own instrument group, which is the classical
errors-in-variables set-up. 2SLS, robust errors (linearmodels); Wooldridge robust overidentification test.
Index = sum_j w_j (x_j - mean_j) with the real 10-year, 100 ln CAPE, 100 ln real dollar (weights are pp of path surprise per unit; no rescaling).

Usage:  python experimental/path_fci/path_fci_iv_lean.py [--sample full|nonzlb] [--real10]
Outputs: path_fci_iv_lean_{ms,gs}_<sample>[_real10].png (L1 weights)
"""
import os, argparse
import numpy as np, pandas as pd
from linearmodels.iv import IV2SLS
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
ENDOG = {"10-yr": "UST10Y", "Equities (ln CAPE)": "SP500", "Dollar (ln real)": "DXY"}
SETS = {"L1: ED1, SPFUT, EURUSD, USDJPY": ["ED1", "SPFUT", "EURUSD", "USDJPY"], "L2: L1 + UST2Y": ["ED1", "SPFUT", "EURUSD", "USDJPY", "UST2Y"]}


def fit(ev, inst):
    d = ev.dropna(subset=list(ENDOG.values()) + inst).reset_index(drop=True).assign(const=1.0)
    m = IV2SLS(d.path, d[["const", "MP1"]], d[list(ENDOG.values())], d[inst]).fit(cov_type="robust")
    return d, m


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true")
    ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    W = {}
    for lab, inst in SETS.items():
        d, m = fit(ev, inst)
        fs = m.first_stage.diagnostics
        j = m.wooldridge_overid
        print(f"\n[{lab}] {len(d)} events ({a.sample})")
        print(pd.DataFrame({"w": [m.params[c] for c in ENDOG.values()], "se": [m.std_errors[c] for c in ENDOG.values()],
                            "first-stage partial F": [float(fs.loc[c, "f.stat"]) for c in ENDOG.values()]}, index=list(ENDOG)).round(4).to_string())
        print(f"  overid (Wooldridge robust): stat {j.stat:.2f}, df {j.df}, p = {j.pval:.3f}")
        W[lab] = pd.Series({n: m.params[c] for n, c in ENDOG.items()})
    tag = "_real10" if a.real10 else ""
    ten = "real 10-yr" if a.real10 else "10-yr"
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)
    ms_frbus = P.L.level(X, sens["ffr_eq_q4"].to_dict(), float(sens.loc["req", "unit_size"])).Total
    gs = G.fci.reindex(X.index)
    idxs = {}
    for lab, w in W.items():
        idx = sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in ENDOG)
        idxs[lab] = idx
        print(f"index [{lab}]: level sd {idx.std():.2f}, daily sd {idx.diff().std():.3f}; vs MS FRB/US corr levels {np.corrcoef(idx, ms_frbus)[0, 1]:.2f}, daily {idx.diff().corr(ms_frbus.diff()):.2f}; "
              f"vs GS FCI levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily {idx.diff().corr(gs.diff()):.2f}; latest {idx.iloc[-1]:+.2f}")
    idx = idxs[list(SETS)[0]]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for key in ("ms", "gs"):
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"IV reverse regression, ED1 + SPFUT + FX instruments, {ten}, CAPE, real dollar (left axis, pp of path surprise)")
        ax.axhline(0, color="gray", lw=0.8); ax.set_ylabel("tighter above zero (vs 1990-2026 average)", fontsize=11)
        if key == "ms":
            ax.plot(ms_frbus.index, ms_frbus, color="#d62728", lw=1.8, label=f"MS-style index, FRB/US weights, all five variables, {ten} (left axis, pp of funds rate)")
            ax.set_ylim(min(idx.min(), ms_frbus.min()) - 0.3, max(idx.max(), ms_frbus.max()) + 0.3)
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"vs MS-style index: corr {np.corrcoef(idx, ms_frbus)[0, 1]:.2f} levels, {idx.diff().corr(ms_frbus.diff()):.2f} daily changes"
        else:
            k = gs.std() / idx.std(); gl = (gs - gs.mean()) / k
            allv = pd.concat([idx, gl]); pad = 0.04 * (allv.max() - allv.min()); lo, hi = allv.min() - pad, allv.max() + pad
            ax.set_ylim(lo, hi)
            b = ax.twinx(); b.plot(gs.index, gs, color="#d62728", lw=1.8, label="GS FCI, Goldman-style weights (right axis, scaled to the same spread)")
            b.set_ylim(gs.mean() + k * lo, gs.mean() + k * hi); b.set_ylabel("GS FCI", fontsize=11); b.tick_params(labelsize=11)
            h1, l1 = ax.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels()
            ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"vs GS FCI: corr {np.corrcoef(idx, gs)[0, 1]:.2f} levels, {idx.diff().corr(gs.diff()):.2f} daily changes"
        ax.set_title(f"Index with lean-IV reverse-regression weights {title}", fontsize=12); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_iv_lean_{key}_{a.sample}{tag}.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
