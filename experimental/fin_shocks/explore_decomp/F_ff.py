"""Figures for Part A5 (funds rate added; point estimates).   python3 F_ff.py -> figures/A5_irf_ff_<start>.png|pdf"""
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent; P = pd.read_csv(HERE / "results_ff" / "point_paths.csv"); FIG = HERE / "figures"
BLUE, GRAY, INK = "#2a78d6", "#8a8984", "#52514e"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK, "axes.grid": True, "grid.color": "#e4e3df", "lines.linewidth": 1.5})
STEP = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap"}; V = {"u": "Unemployment gap (pp)", "P": "Price level (%)", "ff": "Funds rate (pp, monthly average)"}
for start in ("1996-01", "1973-01"):
    fig, ax = plt.subplots(3, 3, figsize=(11, 8), sharex=True)
    for j, f in enumerate(("nom", "real", "rstar")):
        for i, v in enumerate(("u", "P", "ff")):
            a = ax[i, j]
            for fci, col in (("0", GRAY), (f, BLUE)):
                for model, ls in (("no funds rate", "--"), ("funds rate, impact MP1", "-")):
                    g = P[(P.start == start) & (P.form == f) & (P.fci.astype(str) == fci) & (P.model == model)]
                    if v in g and g[v].notna().any():
                        a.plot(g.h, g[v], ls, color=col, label=f"{'yield + FCI' if fci != '0' else 'yield alone'}, {model.replace(', impact MP1', '')}")
            a.axhline(0, color=INK, lw=0.6); a.set_title(f"{STEP[f]}: {V[v]}", loc="left", fontsize=9)
            if i == 2: a.set_xlabel("months after a +1 pp window surprise")
    h, l = ax[0, 0].get_legend_handles_labels(); fig.suptitle(f"Note B's model with the federal funds rate, monthly equations from {start[:4]} (12 lags; point estimates)", x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97)); fig.legend(h, l, frameon=False, ncol=4, loc="lower left", bbox_to_anchor=(0.01, 0.0), fontsize=8)
    for ext in ("png", "pdf"): fig.savefig(FIG / f"A5_irf_ff_{start[:4]}.{ext}", dpi=160, bbox_inches="tight")
    plt.close(fig)
