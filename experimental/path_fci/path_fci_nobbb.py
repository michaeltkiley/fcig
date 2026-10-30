"""
EXPERIMENTAL add-on to path_fci.py (unchanged): the path-surprise indexes without the BBB spread.

Same event regressions and one-factor GLS weights as path_fci.py, re-estimated on the reduced sets (the weights change when a variable is dropped,
because they are normalised so that a 1 pp path surprise moves the index 1 pp):
    GS-style, no BBB:  fed funds, 10-year, ln CAPE, dollar
    MS-style, no BBB:  10-year, ln CAPE, real dollar, real oil
Comparison: the same sets with FRB/US q4 weights (no re-normalisation), and the GS FCI.

Usage:  python experimental/path_fci/path_fci_nobbb.py [--sample full|nonzlb]
Outputs: path_fci_nobbb_<sample>.png, path_fci_nobbb_daily_<sample>.csv
"""
import os, sys, argparse
import numpy as np, pandas as pd
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
SETS = {"GS-style (no BBB)": ["Fed funds", "10-yr", "Equities (ln CAPE)", "Dollar (ln real)"],
        "MS-style (no BBB)": ["10-yr", "Equities (ln CAPE)", "Dollar (ln real)", "Oil (ln real)"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="full", choices=["full", "nonzlb"]); ap.add_argument("usmpd", nargs="?", default=P.USMPD)
    a = ap.parse_args()
    ev = P.events(a.usmpd)
    X, G = P.L.build()
    ev = ev[ev.Date.isin(X.index)].reset_index(drop=True)
    if a.sample == "nonzlb":
        ev = ev[~P.in_zlb(ev.Date)].reset_index(drop=True)
    B = P.fit(P.event_changes(X, ev), ev)
    sens = pd.read_csv(os.path.join(ROOT, "experimental", "ms_fci", "frbus_sensitivities.csv"), index_col=0)["ffr_eq_q4"]
    fr = {"10-yr": sens.rg10, "Equities (ln CAPE)": -sens.req, "Dollar (ln real)": sens.fpxr, "Oil (ln real)": sens.poil, "Fed funds": 0.0}
    D, W = {}, {}
    for s, names in SETS.items():
        w = P.weights(B, names); W[s] = w
        D[f"{s}, path weights"] = sum(w[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in names)
    D["MS-style (no BBB), FRB/US weights"] = sum(fr[n] * P.VARS[n][1] * (X[P.VARS[n][0]] - X[P.VARS[n][0]].mean()) for n in SETS["MS-style (no BBB)"])
    D = pd.DataFrame(D)
    D["GS FCI"] = G.fci.reindex(X.index)
    D.to_csv(os.path.join(HERE, f"path_fci_nobbb_daily_{a.sample}.csv"), float_format="%.4f", index_label="date")
    print(f"sample {a.sample}, {len(ev)} events. Weights (pp of path-rate per unit of x; FRB/US q4 in last column):")
    Wt = pd.DataFrame(W); Wt["FRB/US q4"] = pd.Series(fr)
    print(Wt.round(3).to_string())
    print("\nSum of w*b (should be 1):", {s: round(float((W[s] * B.loc[W[s].index, "b"].astype(float)).sum()), 3) for s in W})
    for per, (p0, p1) in {"1990-2026": ("1990", "2026"), "2009-2026": ("2009", "2026")}.items():
        print(f"\n{per} correlation of levels\n", D[p0:p1].corr().round(2).to_string(), f"\n{per} correlation of daily changes\n", D[p0:p1].diff().corr().round(2).to_string())
    print("\nlatest (20 Oct), pp:", D.iloc[-1].round(2).to_dict())
    for lab, dt in (("2009-03", "2009-03-31"), ("2012-12", "2012-12-31"), ("2021-12", "2021-12-31"), ("2023-10", "2023-10-31")):
        print(f"  {lab}:", D.loc[:dt].iloc[-1].drop("GS FCI").round(2).to_dict())
    print("sd of daily change:", D.diff().std().round(3).to_dict())
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(D.index, D["MS-style (no BBB), path weights"], color="#1f77b4", lw=1.2, label="MS-style, no BBB, path weights (left, pp)")
    ax.plot(D.index, D["GS-style (no BBB), path weights"], color="#2ca02c", lw=1.0, alpha=0.8, label="GS-style, no BBB, path weights (left, pp)")
    ax.plot(D.index, D["MS-style (no BBB), FRB/US weights"], color="#d62728", lw=1.0, label="MS-style, no BBB, FRB/US weights (left, pp)")
    ax.axhline(0, color="gray", lw=0.6); ax.set_ylabel("pp funds-rate equivalent vs 1990-2026 mean")
    b = ax.twinx(); b.plot(D.index, D["GS FCI"], color="k", lw=0.8, alpha=0.6, label="GS FCI (right)"); b.set_ylabel("GS FCI")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
    ax.set_title(f"Path-surprise-weighted indexes without the BBB spread (betas: {a.sample} sample)")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_nobbb_{a.sample}.png"), dpi=130)


if __name__ == "__main__":
    main()
