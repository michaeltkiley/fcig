"""
EXPERIMENTAL add-on (path_fci.py unchanged): two clean charts, one for the MS-style index and one for the GS-style index, each against the GS FCI.

Path-surprise index = rescaled reverse-regression weights (path_fci_reverse_index.py), BBB spread excluded:
    MS-style: 10-year, ln CAPE, real dollar, real oil        GS-style: fed funds, 10-year, ln CAPE, dollar
The right axis (GS FCI) is scaled so that its standard deviation and mean line up with the index on the left (same zero line, same spread), so the two
move together on the page exactly as far as their correlation says. MS chart also shows the same variables with FRB/US weights.

Usage:  python experimental/path_fci/path_fci_charts.py [--sample full|nonzlb]
Outputs: path_fci_chart_ms_<sample>.png, path_fci_chart_gs_<sample>.png
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
SETS = {"ms": ["10-yr", "Equities (ln CAPE)", "Dollar (ln real)", "Oil (ln real)"],
        "gs": ["Fed funds", "10-yr", "Equities (ln CAPE)", "Dollar (ln real)"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    X, G = P.L.build()
    ev = ev[ev.Date.isin(X.index)].reset_index(drop=True)
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    dx = P.event_changes(X, ev)
    B = P.fit(dx, ev)
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    fr = {"10-yr": sens.rg10, "Equities (ln CAPE)": -sens.req, "Dollar (ln real)": sens.fpxr, "Oil (ln real)": sens.poil}
    lev = lambda w, names: sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
    gs = G.fci.reindex(X.index)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for key, names in SETS.items():
        r = sm.OLS(ev.path, sm.add_constant(dx[names])).fit(cov_type="HC1")
        w = r.params[names] / float((r.params[names] * B.loc[names, "b"].astype(float)).sum())
        idx = lev(w, names)
        print(f"\n[{key.upper()}-style] weights (pp of path-rate per unit): " + ", ".join(f"{n} {w[n]:+.3f}" for n in names))
        print(f"  correlation with GS FCI: levels {np.corrcoef(idx, gs)[0, 1]:.2f}, daily changes {idx.diff().corr(gs.diff()):.2f}; latest {idx.iloc[-1]:+.2f} pp; "
              f"2012-12 {idx.loc[:'2012-12-31'].iloc[-1]:+.1f}, 2021-12 {idx.loc[:'2021-12-31'].iloc[-1]:+.1f}, 2009-03 {idx.loc[:'2009-03-31'].iloc[-1]:+.1f}")
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"{key.upper()}-style index, path-surprise weights (left axis, pp of funds rate)")
        if key == "ms":
            f = lev(fr, names)
            ax.plot(f.index, f, color="#d62728", lw=1.4, ls="--", label="same variables, FRB/US weights (left axis)")
        ax.axhline(0, color="gray", lw=0.8)
        ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
        k = gs.std() / idx.std()
        gl = (gs - gs.mean()) / k                       # GS FCI in left-axis units
        allv = pd.concat([idx, gl] + ([f] if key == "ms" else []))
        pad = 0.04 * (allv.max() - allv.min())
        lo, hi = allv.min() - pad, allv.max() + pad
        ax.set_ylim(lo, hi)
        b = ax.twinx(); b.plot(gs.index, gs, color="black", lw=1.2, alpha=0.75, label="GS FCI (right axis, scaled to the same spread)")
        b.set_ylim(gs.mean() + k * lo, gs.mean() + k * hi); b.set_ylabel("GS FCI", fontsize=11)
        h1, l1 = ax.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
        ax.set_title(f"{key.upper()}-style index (no BBB spread) vs GS FCI: corr {np.corrcoef(idx, gs)[0, 1]:.2f} in levels, {idx.diff().corr(gs.diff()):.2f} in daily changes", fontsize=13)
        ax.grid(alpha=0.25); ax.tick_params(labelsize=11); b.tick_params(labelsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_chart_{key}_{a.sample}.png"), dpi=130)


if __name__ == "__main__":
    main()
