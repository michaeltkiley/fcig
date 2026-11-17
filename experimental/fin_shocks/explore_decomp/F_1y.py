"""Figures for Part A6 (1-year yield in place of the 2-year; point estimates; 1-year responses rescaled to the same-size surprise as the 2-year, i.e. x 0.78).
   python3 F_1y.py -> figures/A6_irf_1y_<start>.png|pdf"""
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
import A6_1y as A
HERE = Path(__file__).resolve().parent; P = pd.read_csv(HERE / "results_1y" / "point_paths.csv"); FIG = HERE / "figures"
BLUE, GRAY, INK = "#2a78d6", "#8a8984", "#52514e"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK, "axes.grid": True, "grid.color": "#e4e3df", "lines.linewidth": 1.5})
STEP = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap"}; V = {"u": "Unemployment gap (pp)", "P": "Price level (%)", "pol": "Policy yield (pp, monthly average)"}
for start in ("1996-01", "1973-01"):
    fig, ax = plt.subplots(3, 3, figsize=(11, 8), sharex=True)
    for j, f in enumerate(("nom", "real", "rstar")):
        for i, v in enumerate(("u", "P", "pol")):
            a = ax[i, j]
            for fci, col in (("0", GRAY), (f, BLUE)):
                for rate, ls, sc in (("2-year", "--", 1.0), ("1-year", "-", A.RATIO)):
                    g = P[(P.start == start) & (P.form == f) & (P.fci.astype(str) == fci) & (P.rate == rate)]
                    a.plot(g.h, g[v] * sc, ls, color=col, label=f"{'yield + FCI' if fci != '0' else 'yield alone'}, {rate}")
            a.axhline(0, color=INK, lw=0.6); a.set_title(f"{STEP[f]}: {V[v]}", loc="left", fontsize=9)
            if i == 2: a.set_xlabel("months after the surprise")
    h, l = ax[0, 0].get_legend_handles_labels()
    fig.suptitle(f"2-year (dashed) vs 1-year (solid) as the policy yield, from {start[:4]}; same-size surprise (+1 pp 2-year in the window = +{A.RATIO:.2f} pp 1-year); point estimates", x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97)); fig.legend(h, l, frameon=False, ncol=4, loc="lower left", bbox_to_anchor=(0.01, 0.0), fontsize=8)
    for ext in ("png", "pdf"): fig.savefig(FIG / f"A6_irf_1y_{start[:4]}.{ext}", dpi=160, bbox_inches="tight")
    plt.close(fig)
