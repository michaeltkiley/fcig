"""Figures and tables for Part A4 (industrial production added).   python3 F_ip.py -> figures/A4_irf_ip_<sample>.png|pdf, results_ip/tables_ip.md"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).resolve().parent; RI = HERE / "results_ip"; RC = HERE / "results_core"; FIG = HERE / "figures"
BLUE, GRAY, INK = "#2a78d6", "#8a8984", "#52514e"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.grid": True, "grid.color": "#e4e3df", "grid.linewidth": 0.6, "lines.linewidth": 1.5})
STEP = {"nom": "Nominal", "real": "Real", "rstar": "r*-gap"}; VAR = {"u": "Unemployment gap (pp)", "P": "Price level (%)", "ip": "Industrial production (%)"}
def paths(f, x, s): p = pd.read_csv(RI / f"{f}_{x}_upipip_{s}_all_in_paths.csv"); return p[(p.kind == "macro") & (p.lags == 12)]

def fig(start):
    fig, ax = plt.subplots(3, 3, figsize=(11, 8), sharex=True)
    for j, f in enumerate(("nom", "real", "rstar")):
        for i, v in enumerate(("u", "P", "ip")):
            a = ax[i, j]
            for x, col, lab in ((0, GRAY, "yield alone"), (f, BLUE, "yield + FCI")):
                p = paths(f, x, start); p = p[p["var"] == v]
                a.fill_between(p.h, p.lo, p.hi, color=col, alpha=0.15, lw=0, label=f"{lab}: 90% band"); a.fill_between(p.h, p.lo68, p.hi68, color=col, alpha=0.18, lw=0)
                a.plot(p.h, p.r, color=col, label=lab)
            a.axhline(0, color=INK, lw=0.6); a.set_title(f"{STEP[f]}: {VAR[v]}", loc="left", fontsize=9)
            if i == 2: a.set_xlabel("months after a +1 pp window surprise")
    h, l = ax[0, 0].get_legend_handles_labels(); fig.suptitle(f"Note B's model with industrial production, monthly equations from {start[:4]} (12 lags; bands 68 and 90 percent)", x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97)); fig.legend(h, l, frameon=False, ncol=4, loc="lower left", bbox_to_anchor=(0.01, 0.0), fontsize=8)
    for ext in ("png", "pdf"): fig.savefig(FIG / f"A4_irf_ip_{start[:4]}.{ext}", dpi=160, bbox_inches="tight")
    plt.close(fig)

def star(r, h):
    return "**" if r[f"lo95_{h}"] * r[f"hi95_{h}"] > 0 else ("*" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "")
def cell(r, h): return f"{r[f'r{h}']:+.2f}{star(r, h)} [{r[f'lo{h}']:+.2f}, {r[f'hi{h}']:+.2f}]"

def tables():
    out = []
    for v in ("u", "P", "ip"):
        rows = []
        for s in ("1996-01", "1973-01"):
            for f in ("nom", "real", "rstar"):
                for x in ("0", f):
                    d = pd.read_csv(RI / f"{f}_{x}_upipip_{s}_all_in.csv"); r = d[d["var"] == v].iloc[0]
                    row = {"sample": s[:4], "yield": STEP[f], "FCI": "yes" if x != "0" else "no", **{f"{h} m": cell(r, h) for h in (12, 24, 36)}}
                    if v in ("u", "P"):
                        b = pd.read_csv(RC / f"{f}_{x}_upi_{s}_all_in.csv"); b = b[(b.lags == 12) & (b["var"] == v)].iloc[0]
                        row["24 m without IP in the model"] = f"{b.r24:+.2f}"
                    rows.append(row)
        out.append(f"### A4 ({VAR[v]}). Note B's model with industrial production; per +1 pp window surprise, 12 lags, 90% intervals, ** and * 5 and 10 percent\n\n" + pd.DataFrame(rows).to_markdown(index=False))
    (RI / "tables_ip.md").write_text("\n\n".join(out) + "\n"); print("\n\n".join(out))

if __name__ == "__main__":
    fig("1973-01"); fig("1996-01"); tables()
