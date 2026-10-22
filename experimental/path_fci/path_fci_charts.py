"""
EXPERIMENTAL add-on (path_fci.py unchanged): two clean charts, one for the MS-style index and one for the GS-style index, each against the GS FCI.

Path-surprise index = forward-regression (GLS) weights, each variable regressed individually on the path surprise (path_fci.py), BBB spread excluded:
    MS-style: 10-year, ln CAPE, real dollar, real oil        GS-style: fed funds, 10-year, ln CAPE, dollar
The right axis (GS FCI) is scaled so that its standard deviation and mean line up with the index on the left (same zero line, same spread), so the two
move together on the page exactly as far as their correlation says.

Usage:  python experimental/path_fci/path_fci_charts.py [--sample full|nonzlb] [--real10]
(--real10: the 10-year is the real yield, DGS10 less Cleveland Fed expected inflation. The dollar is the real dollar and CAPE a real valuation in all versions.)
Outputs: path_fci_chart_ms_<sample>[_real10].png, path_fci_chart_gs_<sample>[_real10].png
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
SETS = {"ms": ["10-yr", "Equities (ln CAPE)", "Dollar (ln real)", "Oil (ln real)"],
        "gs": ["Fed funds", "10-yr", "Equities (ln CAPE)", "Dollar (ln real)"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("--real10", action="store_true", help="10-year = DGS10 less Cleveland Fed 10-year expected inflation"); ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    P.L.REAL10 = a.real10
    X, G = P.L.build()
    ev = ev[ev.Date.isin(X.index)].reset_index(drop=True)
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    dx = P.event_changes(X, ev)
    B = P.fit(dx, ev)
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    fr = {"10-yr": sens.rg10, "Equities (ln CAPE)": -sens.req, "Dollar (ln real)": sens.fpxr, "Oil (ln real)": sens.poil}
    lev = lambda w, names: sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
    tag = "_real10" if a.real10 else ""
    ten = "real 10-yr" if a.real10 else "10-yr"
    gs = G.fci.reindex(X.index)
    req = float(pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0).loc["req", "unit_size"])
    ms_frbus = P.L.level(X, sens.to_dict(), req).Total      # the MS-style index as built in experimental/ms_fci: five variables, FRB/US q4 weights
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for key, names in SETS.items():
        w = P.weights(B, names)                              # forward regressions, one variable at a time against the path surprise (GLS weights)
        idx = lev(w, names)
        other = ms_frbus if key == "ms" else gs
        print(f"\n[{key.upper()}-style] path weights (pp of path-rate per unit): " + ", ".join(f"{n} {w[n]:+.3f}" for n in names))
        print(f"  correlation with {'MS FRB/US index' if key == 'ms' else 'GS FCI'}: levels {np.corrcoef(idx, other)[0, 1]:.2f}, daily changes {idx.diff().corr(other.diff()):.2f}; "
              f"latest {idx.iloc[-1]:+.2f} pp" + (f" vs {ms_frbus.iloc[-1]:+.2f}" if key == "ms" else ""))
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(idx.index, idx, color="#1f5fa8", lw=1.8, label=f"{key.upper()}-style index, path-surprise weights, no BBB, {ten} (left axis, pp of funds rate)")
        ax.axhline(0, color="gray", lw=0.8)
        ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
        if key == "ms":
            ax.plot(ms_frbus.index, ms_frbus, color="#d62728", lw=1.8, label=f"MS-style index, FRB/US weights, all five variables, {ten} (left axis)")
            ax.set_ylim(min(idx.min(), ms_frbus.min()) - 0.3, max(idx.max(), ms_frbus.max()) + 0.3)
            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
            title = f"MS-style index ({ten}): path-surprise weights vs FRB/US weights (corr {np.corrcoef(idx, ms_frbus)[0, 1]:.2f} levels, {idx.diff().corr(ms_frbus.diff()):.2f} daily changes)"
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
            title = f"GS-style index ({ten}): path-surprise weights vs GS FCI (corr {np.corrcoef(idx, gs)[0, 1]:.2f} levels, {idx.diff().corr(gs.diff()):.2f} daily changes)"
        ax.set_title(title, fontsize=13); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_chart_{key}_{a.sample}{tag}.png"), dpi=130)


if __name__ == "__main__":
    main()
