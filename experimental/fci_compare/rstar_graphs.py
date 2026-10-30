"""
Separate charts of the r*-gap versions (Kiley and Laubach-Williams one-sided r*; Richmond dropped) for the macro-model (with house prices), market-based (NS) and GS indexes, with the plain real-rate
version (no r* adjustment) as a reference. Reads rstar_sets_daily.csv (rstar_sets.py). Monthly, funds-rate pp, tighter above zero (vs the 1990-2026 average).
Usage: python experimental/fci_compare/rstar_graphs.py     Outputs: rstar_graph_{macro,market,gs}.png
"""
import os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FAM = {"macro": "Macro-model levels index (FRB/US weights, with house prices)", "market": "Market-based index (NS-shock weights)", "GS": "GS (replication; NS-shock conversion)"}


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    D = pd.read_csv(os.path.join(HERE, "rstar_sets_daily.csv"), parse_dates=["date"]).set_index("date")
    M = D.resample("ME").last()
    for fam, title in FAM.items():
        fig, ax = plt.subplots(figsize=(13, 6.5))
        ax.plot(M.index, M[f"{fam} | Kiley"], color="#1f5fa8", lw=1.8, label="real rates less Kiley r* (one-sided)")
        ax.plot(M.index, M[f"{fam} | Laubach-Williams"], color="#2ca02c", lw=1.8, label="real rates less Laubach-Williams r* (one-sided)")
        ax.plot(M.index, M[f"{fam} | none (real rates)"], color="black", lw=1.0, ls="--", label="real rates, no r* adjustment")
        ax.axhline(0, color="gray", lw=0.8); ax.grid(alpha=0.25); ax.tick_params(labelsize=11)
        ax.set_ylabel("pp of funds rate, tighter above zero (vs 1990-2026 average)", fontsize=11)
        k, l, n = (M[f"{fam} | {c}"] for c in ("Kiley", "Laubach-Williams", "none (real rates)"))
        ax.set_title(f"{title}: r*-gap versions (monthly corr of levels Kiley/LW {k.corr(l):.2f}; 12-month changes {k.diff(12).corr(l.diff(12)):.2f})", fontsize=11)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=1, fontsize=10, frameon=False)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, f"rstar_graph_{fam.lower()}.png"), dpi=130); plt.close(fig)
        print(f"{fam}: latest Kiley {k.iloc[-1]:+.2f}, LW {l.iloc[-1]:+.2f}, no r* {n.iloc[-1]:+.2f}; sd Kiley {k.std():.2f}, LW {l.std():.2f}, none {n.std():.2f}; corr Kiley/LW {k.corr(l):.2f}; "
              f"mean abs gap LW-Kiley {(l - k).abs().mean():.2f}, max {(l - k).abs().max():.2f}")


if __name__ == "__main__":
    main()
