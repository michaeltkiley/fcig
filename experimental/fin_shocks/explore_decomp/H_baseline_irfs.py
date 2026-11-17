"""Proposed baseline IRFs (D-A21): Note B's model, r*-gap, 12 lags, March-December 2020 dropped, monthly equations from 1996 and from 1973, without and with the FCI
(stored results of Note B's robustness R1b/R1c, 500 block-bootstrap draws; read only).   python3 H_baseline_irfs.py -> figures/H_baseline_irfs.png|pdf, results_core/baseline_irfs.md"""
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent; RES = HERE.parent / "baseline" / "results"; FIG = HERE / "figures"
BLUE, GRAY, INK = "#2a78d6", "#8a8984", "#52514e"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK, "axes.grid": True, "grid.color": "#e4e3df", "lines.linewidth": 1.6})
fig, ax = plt.subplots(2, 2, figsize=(10, 6.4), sharex=True)
rows = []
for j, start in enumerate(("1996-01", "1973-01")):
    for i, (v, lab) in enumerate((("u", "Unemployment gap (pp)"), ("P", "Core PCE price level (%)"))):
        a = ax[i, j]
        for fci, col, name in (("0", GRAY, "2-year yield alone"), ("rstar", BLUE, "2-year yield + FCI")):
            p = pd.read_csv(RES / f"rstar_{fci}_upi_{start}_all_out_paths.csv"); p = p[(p.lags == 12) & (p.kind == "macro") & (p["var"] == v)]
            a.fill_between(p.h, p.lo, p.hi, color=col, alpha=0.13, lw=0); a.fill_between(p.h, p.lo68, p.hi68, color=col, alpha=0.2, lw=0); a.plot(p.h, p.r, color=col, label=name)
            for h in (12, 24, 36):
                q = p[p.h == h].iloc[0]; rows.append(dict(sample=f"{start[:4]}-2026", FCI=name, var=v, h=h, response=q.r, lo90=q.lo, hi90=q.hi, lo68=q.lo68, hi68=q.hi68))
        a.axhline(0, color=INK, lw=0.6); a.set_title(f"{lab}, monthly equations from {start[:4]}", loc="left", fontsize=9)
        if i == 1: a.set_xlabel("months after a +1 pp window surprise in the 2-year yield")
h, l = ax[0, 0].get_legend_handles_labels()
fig.suptitle("Proposed baselines: r*-gap, 12 lags, March-December 2020 dropped (bands 68 and 90 percent)", x=0.01, ha="left", fontsize=10)
fig.tight_layout(rect=(0, 0.05, 1, 0.97)); fig.legend(h, l, frameon=False, ncol=2, loc="lower left", bbox_to_anchor=(0.01, 0.0), fontsize=8)
for ext in ("png", "pdf"): fig.savefig(FIG / f"H_baseline_irfs.{ext}", dpi=160, bbox_inches="tight")
T = pd.DataFrame(rows); (HERE / "results_core" / "baseline_irfs.md").write_text(T.round(3).to_markdown(index=False) + "\n"); print(T.round(2).to_string())
