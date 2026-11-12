"""Shared helpers: scalars written by the computation scripts (results/scalars_<script>.csv) and figure style."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from .config import RES, REP

COLORS = {"market": "#1f4e9c", "gs": "#2a9d4b", "frbus": "#d95f02", "fcig": "#222222", "anfci": "#7b4fa0", "grey": "#888888"}
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 8, "font.family": "serif"})


class Scalars:
    """Named numbers from one script, saved to results/scalars_<script>.csv; 07_report.py turns them into LaTeX macros."""
    def __init__(self, script):
        self.script, self.items = script, {}

    def add(self, name, value):
        self.items[name] = value

    def save(self):
        pd.Series(self.items, dtype=object).rename_axis("name").rename("value").to_csv(RES / f"scalars_{self.script}.csv")


def load_scalars():
    out = {}
    for f in sorted(RES.glob("scalars_*.csv")):
        for k, v in pd.read_csv(f, index_col=0).value.items():
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = v
    return out


def axes(ax, ylabel=None, legend=True, zero=True):
    if zero:
        ax.axhline(0, color="#999999", lw=0.8)
    ax.grid(alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if ylabel:
        ax.set_ylabel(ylabel)
    if legend:
        ax.legend(frameon=False)


def figure(name, fig):
    fig.tight_layout()
    fig.savefig(REP / f"{name}.pdf")
    plt.close(fig)
