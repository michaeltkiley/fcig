"""Figures for the second report: core results from 1973 (A) and Route 2 (B).   python3 D_figures.py -> figures/A*.png|pdf, figures/B*.png|pdf"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).resolve().parent; FIG = HERE / "figures"; C = HERE / "results_core"; R2 = HERE / "results_route2"
BLUE, ORANGE, AQUA, GRAY, INK, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#52514e", "#6250d6"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.grid": True, "grid.color": "#e4e3df", "grid.linewidth": 0.6, "lines.linewidth": 1.4})
def save(fig, name): fig.savefig(FIG / f"{name}.png", dpi=160, bbox_inches="tight"); fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight"); plt.close(fig)
def dt(m): return pd.PeriodIndex(m, freq="M").to_timestamp()
ma12 = lambda x: pd.Series(x).rolling(12).mean().values
STEP = {"nom": "nominal", "real": "real", "rstar": "r*-gap"}

def figA():
    fig, ax = plt.subplots(2, 3, figsize=(11, 5.6), sharex=True)
    for j, f in enumerate(("nom", "real", "rstar")):
        for i, v in enumerate(("u", "P")):
            a = ax[i, j]
            for start, ls in (("1973-01", "-"), ("1996-01", "--")):
                for fci, col, lab in ((0, GRAY, "yield alone"), (f, BLUE, "yield + FCI")):
                    p = pd.read_csv(C / f"{f}_{fci}_upi_{start}_all_in_paths.csv"); p = p[(p.lags == 12) & (p.kind == "macro") & (p["var"] == v)]
                    if start == "1973-01": a.fill_between(p.h, p.lo, p.hi, color=col, alpha=0.12, lw=0)
                    a.plot(p.h, p.r, ls, color=col, label=f"{lab}, from {start[:4]}")
            a.axhline(0, color=INK, lw=0.6); a.set_title(f"{STEP[f]}: {'unemployment gap (pp)' if v == 'u' else 'price level (%)'}", loc="left", fontsize=9)
            if i == 1: a.set_xlabel("months after a +1 pp window surprise")
    h, l = ax[0, 0].get_legend_handles_labels(); fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.legend(h, l, frameon=False, ncol=4, loc="lower left", bbox_to_anchor=(0.01, 0.0), fontsize=8); save(fig, "A1_core_paths")

def figB_shocks(step="rstar", fci="rstar"):
    d = pd.read_csv(R2 / f"daily_shocks_{step}_{fci}.csv"); d["mp"] = pd.PeriodIndex(d.month, freq="M")
    m_all = d.groupby("mp").s.sum(); m_ns = d.groupby("mp").ns.sum()
    h = pd.read_csv(R2 / f"hd_{step}_{fci}.csv")
    fig, ax = plt.subplots(2, 1, figsize=(10, 5.4))
    a = ax[0]; a.plot(m_all.index.to_timestamp(), m_all.values, color=BLUE, lw=0.8, label="recovered from daily innovations, month's sum")
    a.plot(m_ns.index.to_timestamp(), m_ns.values, color=ORANGE, lw=1.0, label="measured window surprises, month's sum")
    a.set_title("Policy shocks since 1990 (pp, window 2-year units), r*-gap with FCI", loc="left", fontsize=9); a.legend(frameon=False, fontsize=8, loc="upper right")
    import lib_r2 as R
    c = R.run(step, fci, "avg", "1973-01", 12, "WE", "in"); ov = pd.read_csv(R2 / "overlap.csv"); sc = float(ov[(ov.step == step) & (ov.fci.astype(str) == str(fci))].scale.iloc[0])
    e = pd.Series(c["e"], index=c["per"]); b = ax[1]
    b.plot(e.loc[:"1990-04"].index.to_timestamp(), sc * e.loc[:"1990-04"].values, color=VIOLET, lw=0.8, label=f"1974-1990: recovered from monthly VAR innovations (x {sc:.2f})")
    b.plot(m_all.loc["1990-05":].index.to_timestamp(), m_all.loc["1990-05":].values, color=BLUE, lw=0.8, label="1990-2026: recovered from daily innovations")
    b.set_title("Spliced policy-shock series, 1974-2026", loc="left", fontsize=9); b.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout(); save(fig, "B1_shocks")

def figB_hd(step="rstar", fci="rstar", name="B2_hd_rstar"):
    h = pd.read_csv(R2 / f"hd_{step}_{fci}.csv"); Bz = np.load(R2 / f"bands_hd_{step}_{fci}.npz", allow_pickle=True) if (R2 / f"bands_hd_{step}_{fci}.npz").exists() else None
    names = [("u", "Unemployment gap (pp)"), ("pi", "Core PCE inflation, 12-month (pp)"), ("pol", f"2-year yield, {STEP[step]} (pp)"), ("idx", f"FCI, {STEP[step]} (index points)")]
    fig, ax = plt.subplots(2, 2, figsize=(10.5, 6.6), sharex=True); ax = ax.ravel()
    for k, (v, lab) in enumerate(names):
        a = ax[k]; g = h[h["var"] == v].reset_index(drop=True)
        if g.empty: a.axis("off"); ax[k - 2].tick_params(labelbottom=True); continue
        t = dt(g.month); f = ma12 if v == "pi" else (lambda x: np.asarray(x))
        a.plot(t, f(g.all_shocks_var.values), color=GRAY, lw=1.0, label="all shocks (monthly VAR, deviation from the deterministic path)")
        if Bz is not None:
            dd = Bz["spliced"][:, :, k].astype(float)
            if v == "pi": dd = np.array([ma12(r) for r in dd])
            a.fill_between(t, np.nanpercentile(dd, 5, axis=0), np.nanpercentile(dd, 95, axis=0), color=BLUE, alpha=0.16, lw=0, label="90% band (Note B's draws; month-aggregated shocks, 36-month responses)")
        a.plot(t, f(g.spliced.values), color=BLUE, lw=1.4, label="policy-direction shocks: daily from 1990, monthly before (Route 2)")
        a.plot(t, f(g.daily_ann.values + 0 * g.measured.values), color=AQUA, lw=1.0, label="of which announcement days")
        a.plot(t, f(g.measured.values), color=ORANGE, lw=1.2, label="measured window surprises (Route 1)")
        a.axhline(0, color=INK, lw=0.6); a.set_title(lab, loc="left", fontsize=9)
        if v == "u": a.set_ylim(-3, 5)
    hh, ll = ax[0].get_legend_handles_labels(); fig.tight_layout(rect=(0, 0.13, 1, 1))
    fig.legend(hh, ll, frameon=False, fontsize=8, loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=1); save(fig, name)

def figB_shares():
    s = pd.read_csv(R2 / "shares.csv"); s = s[(s.h == 24) & (s.step == "rstar") & (s.fci == "rstar")]
    order = [("1974-1989", "spliced", "1974-89: monthly-recovered (scaled)"), ("1990-2026", "daily_all", "1990-2026: daily-recovered, all days"),
             ("1990-2026", "daily_other", "   non-announcement days"), ("1990-2026", "daily_ann", "   announcement days"), ("1990-2026", "measured", "   measured surprises")]
    fig, ax = plt.subplots(1, 4, figsize=(11, 3.2), sharey=True)
    for a, (v, lab) in zip(ax, (("u", "Unemployment gap"), ("pi", "Core inflation"), ("pol", "2-year yield"), ("idx", "FCI"))):
        y = np.arange(len(order))[::-1]; vals = [100 * float(s[(s.era == e) & (s.source == src)][v].iloc[0]) for e, src, _ in order]
        a.barh(y, vals, color=[VIOLET, BLUE, BLUE, AQUA, ORANGE], height=0.6); a.set_yticks(y); a.set_yticklabels([o[2] for o in order]); a.set_title(lab, loc="left", fontsize=9)
        for yy, vv in zip(y, vals): a.text(vv, yy, f" {vv:.1f}", va="center", fontsize=7.5, color=INK)
    fig.supxlabel("percent of the 24-month forecast-error variance (r*-gap with FCI)", fontsize=9, color=INK)
    fig.tight_layout(); save(fig, "B3_shares")

if __name__ == "__main__":
    figA(); figB_shocks(); figB_hd(); figB_hd("nom", 0, "B4_hd_nom_nofci"); figB_shares()
