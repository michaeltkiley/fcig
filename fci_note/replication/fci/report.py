"""Writing results for the paper: numbers as LaTeX macros, tables as LaTeX, figures as PDF."""
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .data import OUT

(OUT / "figures").mkdir(parents=True, exist_ok=True); (OUT / "tables").mkdir(parents=True, exist_ok=True)


class Numbers:
    """Collects named numbers and writes them as \\newcommand macros (output/numbers_<script>.tex), so the text of the paper cites computed values."""
    def __init__(self, script):
        self.script, self.items = script, {}

    def add(self, name, value, fmt="{:.2f}"):
        name = re.sub(r"[^A-Za-z]", "", name)
        self.items[name] = fmt.format(value) if not isinstance(value, str) else value
        print(f"  \\{name} = {self.items[name]}")

    def write(self):
        with open(OUT / f"numbers_{self.script}.tex", "w") as f:
            for k, v in self.items.items():
                f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")


def table(name, df, fmt="{:.2f}", caption=None, index=True):
    """Simple booktabs table body (tabular only), written to output/tables/<name>.tex."""
    cols = list(df.columns)
    lines = ["\\begin{tabular}{" + ("l" if index else "") + "r" * len(cols) + "}", "\\toprule",
             (" & " if index else "") + " & ".join(map(str, cols)) + " \\\\", "\\midrule"]
    for i, row in df.iterrows():
        cells = [fmt.format(v) if isinstance(v, (int, float)) and v == v else ("" if v != v else str(v)) for v in row.values]
        lines.append((str(i) + " & " if index else "") + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    (OUT / "tables" / f"{name}.tex").write_text("\n".join(lines) + "\n")


def figure(name, fig):
    fig.tight_layout()
    fig.savefig(OUT / "figures" / f"{name}.pdf"); fig.savefig(OUT / "figures" / f"{name}.png", dpi=130)
    plt.close(fig)


COLORS = {"market": "#d95f02", "frbus": "#1b4f8a", "gs": "#2a9d4b", "fcig": "#222222", "anfci": "#7b4fa0", "grey": "#888888"}


def axes(ax, ylabel=None):
    ax.axhline(0, color="#999999", lw=0.8); ax.grid(alpha=0.25)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.legend(frameon=False, fontsize=8)
