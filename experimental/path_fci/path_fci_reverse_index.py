"""
EXPERIMENTAL add-on (path_fci.py unchanged): index with rescaled reverse-regression weights, BBB spread excluded.

Weights: regress the path surprise on the event-day changes of the variables together (path_fci_reverse.py), then rescale all weights by one factor so that
sum_j w_j b_j = 1, with b_j the forward responses to a 1 pp path surprise (path_fci.py): a 1 pp path surprise then moves the index 1 pp, like the GLS
weights. (The raw reverse coefficients are shrunk by noise in the event-day changes; the rescaling removes the shrinkage but keeps the relative weights.)
Sets: MS-style (10-year, CAPE, real dollar, real oil) and Core (10-year, CAPE, dollar). Compared with the GLS weights without BBB, FRB/US weights and the GS FCI.

Usage:  python experimental/path_fci/path_fci_reverse_index.py [--sample full|nonzlb]
Outputs: path_fci_reverse_index_<sample>.png, path_fci_reverse_index_daily_<sample>.csv
"""
import os, argparse
import numpy as np, pandas as pd
import statsmodels.api as sm
import path_fci as P

HERE, ROOT = P.HERE, P.ROOT
SETS = {"MS-style (10-yr, CAPE, dollar, oil)": ["10-yr", "Equities (ln CAPE)", "Dollar (ln real)", "Oil (ln real)"],
        "Core (10-yr, CAPE, dollar)": ["10-yr", "Equities (ln CAPE)", "Dollar (ln real)"]}


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
    D, rows = {}, {}
    for s, names in SETS.items():
        r = sm.OLS(ev.path, sm.add_constant(dx[names])).fit(cov_type="HC1")
        raw = r.params[names]
        k = float((raw * B.loc[names, "b"].astype(float)).sum())
        w = raw / k
        rows[s] = pd.DataFrame({"raw reverse": raw, "rescaled (used)": w, "GLS no BBB": P.weights(B, names), "FRB/US q4": pd.Series(fr)[names]})
        print(f"\n[{s}] reverse-regression R2 {r.rsquared:.2f}; rescale factor 1/{k:.2f}\n", rows[s].round(3).to_string())
        D[s + ", reverse (rescaled)"] = lev(w, names)
        D[s + ", GLS"] = lev(P.weights(B, names), names)
    D["Core (10-yr, CAPE, dollar), FRB/US weights"] = lev(fr, SETS["Core (10-yr, CAPE, dollar)"])
    D["GS FCI"] = G.fci.reindex(X.index)
    D = pd.DataFrame(D)
    D.to_csv(os.path.join(HERE, f"path_fci_reverse_index_daily_{a.sample}.csv"), float_format="%.4f", index_label="date")
    short = {c: c.split(" (")[0] + (", " + c.split(", ")[-1] if ", " in c else "") for c in D.columns}
    print("\nCorrelation of daily changes (1990-2026):\n", D.diff().rename(columns=short).corr().round(2).to_string())
    print("Correlation of levels (1990-2026):\n", D.rename(columns=short).corr().round(2).to_string())
    print("\nlatest (20 Oct), pp:", {short[k]: round(float(v), 2) for k, v in D.iloc[-1].items()})
    for lab, dt in (("2009-03", "2009-03-31"), ("2012-12", "2012-12-31"), ("2021-12", "2021-12-31"), ("2023-10", "2023-10-31")):
        print(f"  {lab}:", {short[k]: round(float(v), 2) for k, v in D.loc[:dt].iloc[-1].drop("GS FCI").items()})
    print("sd of daily change:", {short[k]: round(float(v), 3) for k, v in D.diff().std().items()})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(11, 9), gridspec_kw={"height_ratios": [3, 2]})
    a0 = ax[0]
    m = "MS-style (10-yr, CAPE, dollar, oil)"
    a0.plot(D.index, D[m + ", reverse (rescaled)"], color="#1f77b4", lw=1.3, label="Reverse-regression weights, rescaled (left, pp)")
    a0.plot(D.index, D[m + ", GLS"], color="#2ca02c", lw=0.9, alpha=0.8, label="Forward (GLS) weights, no BBB (left, pp)")
    a0.plot(D.index, D["Core (10-yr, CAPE, dollar), FRB/US weights"], color="#d62728", lw=0.9, label="FRB/US weights, same variables (left, pp)")
    a0.axhline(0, color="gray", lw=0.6); a0.set_ylabel("pp funds-rate equivalent vs 1990-2026 mean")
    b = a0.twinx(); b.plot(D.index, D["GS FCI"], color="k", lw=0.8, alpha=0.6, label="GS FCI (right)"); b.set_ylabel("GS FCI")
    h1, l1 = a0.get_legend_handles_labels(); h2, l2 = b.get_legend_handles_labels(); a0.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
    a0.set_title(f"MS-style index (no BBB) with rescaled reverse-regression weights (betas: {a.sample} sample)")
    t = rows[m]; names = list(t.index); x = np.arange(len(names)); a1 = ax[1]
    for off, col, c in ((-0.27, "rescaled (used)", "#1f77b4"), (0.0, "GLS no BBB", "#2ca02c"), (0.27, "FRB/US q4", "#d62728")):
        a1.bar(x + off, t[col], 0.27, label=col, color=c)
    a1.set_xticks(x); a1.set_xticklabels(names, fontsize=9); a1.axhline(0, color="gray", lw=0.6)
    a1.set_ylabel("pp per unit (pp; per 1% for CAPE, dollar, oil)"); a1.legend(fontsize=8); a1.set_title("Weights")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, f"path_fci_reverse_index_{a.sample}.png"), dpi=130)


if __name__ == "__main__":
    main()
