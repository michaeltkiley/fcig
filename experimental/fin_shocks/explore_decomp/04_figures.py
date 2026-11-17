"""Figures and tables for REPORT.md (reads results/ from 01-03).
   python3 04_figures.py"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).resolve().parent; RES = HERE / "results"; FIG = HERE / "figures"; FIG.mkdir(exist_ok=True)
BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#8a8984", "#52514e"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.grid": True, "grid.color": "#e4e3df", "grid.linewidth": 0.6, "lines.linewidth": 1.4})
LAB = {"u": "Unemployment gap (pp)", "pi12": "Core PCE inflation, 12-month (pp)", "pol": "2-year yield, r*-gap (pp)", "idx": "FCI, r*-gap (index points)"}

def to_dt(m): return pd.PeriodIndex(m, freq="M").to_timestamp()
def save(fig, name): fig.savefig(FIG / f"{name}.png", dpi=160, bbox_inches="tight"); fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight"); plt.close(fig)
def ma12(x): return pd.Series(x).rolling(12).mean().values          # 12-month inflation from monthly annualized contributions

# ---------------------------------------------------------------- 1. recovered shock vs measured surprises
def fig_shocks(case="rstar_rstar_avg1973_L12_WE_in", case2="rstar_rstar_eom1990_L12_WE_in"):
    fig, ax = plt.subplots(2, 2, figsize=(10, 5.6), gridspec_kw=dict(width_ratios=[2.4, 1]))
    for row, (c, lab) in enumerate(((case, "monthly averages, VAR from 1973"), (case2, "end of month, VAR from 1990"))):
        s = pd.read_csv(RES / f"shocks_{c}.csv"); t = to_dt(s.month)
        a = ax[row, 0]; a.plot(t, s.e, color=BLUE, lw=0.8, label="Recovered from VAR innovations (Route 2)")
        a.plot(t, s.z, color=ORANGE, lw=1.0, label="Measured window surprises (monthly sum)")
        a.set_title(f"Policy shock, r*-gap with FCI, {lab}", loc="left", fontsize=9); a.set_ylabel("pp, window 2-year units")
        if row == 0: a.legend(frameon=False, loc="upper right", fontsize=8)
        b = ax[row, 1]; ok = pd.PeriodIndex(s.month, freq="M") >= pd.Period("1996-01", "M")
        b.scatter(s.z[ok], s.e[ok], s=9, color=BLUE, alpha=0.6, edgecolor="none")
        rho = np.corrcoef(s.z[ok], s.e[ok])[0, 1]
        b.set_title(f"1996-2026: correlation {rho:.2f}", loc="left", fontsize=9); b.set_xlabel("measured surprise"); b.set_ylabel("recovered shock")
    fig.tight_layout(); save(fig, "fig1_shocks")

# ---------------------------------------------------------------- 2. historical decomposition
def hd_frame(case):
    d = pd.read_csv(RES / f"hd_{case}.csv"); return {v: g.reset_index(drop=True) for v, g in d.groupby("var")}

def band(npz, j, pi=False, lo=5, hi=95):
    x = (npz["draws"] if "draws" in npz.files else npz["hd"])[:, :, j].astype(float)
    if pi: x = np.array([ma12(r) for r in x])
    return np.nanpercentile(x, lo, axis=0), np.nanpercentile(x, hi, axis=0)

def fig_hd(case="rstar_rstar_avg1973_L12_WE_in", boot="boot_hd_rstar_rstar_avg_WE.npz", r1="route1_rstar_rstar_1996.npz", name="fig2_hd_rstar_avg", title=""):
    H = hd_frame(case); B = np.load(RES / boot, allow_pickle=True) if (RES / boot).exists() else None; R1 = np.load(RES / r1, allow_pickle=True) if (RES / r1).exists() else None
    fig, ax = plt.subplots(2, 2, figsize=(10, 6.4), sharex=True); ax = ax.ravel()
    for k, (v, j) in enumerate((("u", 0), ("pi12", 1), ("pol", 2), ("idx", 3))):
        src = "pi" if v == "pi12" else v
        if src not in H: ax[k].axis("off"); ax[k - 2].tick_params(labelbottom=True); continue
        h = H[src]; t = to_dt(h.month); f = ma12 if v == "pi12" else (lambda x: np.asarray(x))
        a = ax[k]
        a.plot(t, f(h.stochastic.values), color=GRAY, lw=1.0, label="All shocks (deviation from the deterministic path)")
        if B is not None:
            lo, hi = band(B, j, pi=(v == "pi12")); a.fill_between(t, lo, hi, color=BLUE, alpha=0.18, lw=0)
        a.plot(t, f(h.route2.values), color=BLUE, lw=1.3, label="Policy shocks, Route 2 (upper: shocks recovered from innovations; 90% band)")
        if R1 is not None:
            t1 = to_dt(R1["months"]); p = R1["point"][:, j]; p = ma12(p) if v == "pi12" else p
            lo, hi = band(R1, j, pi=(v == "pi12")); a.fill_between(t1, lo, hi, color=ORANGE, alpha=0.25, lw=0)
            a.plot(t1, p, color=ORANGE, lw=1.3, label="Policy shocks, Route 1 (lower: measured window surprises in Note B's model; 90% band)")
        a.axhline(0, color=INK, lw=0.6); a.set_title(LAB[v] if case.startswith("rstar") or v in ("u", "pi12") else LAB[v].replace("r*-gap", case.split("_")[0].replace("nom", "nominal")), loc="left", fontsize=9)
    ax[0].set_ylim(-3, 5)                               # 2020 spike in the all-shocks line (to 10 pp) cut off
    hdl, lbl = ax[0].get_legend_handles_labels()
    if title: fig.suptitle(title, x=0.01, ha="left", fontsize=10)
    fig.tight_layout(rect=(0, 0.1, 1, 0.97)); fig.legend(hdl, lbl, frameon=False, fontsize=8, loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=1); save(fig, name)

# ---------------------------------------------------------------- 3. variance shares: bounds
def fig_fevd():
    f = pd.read_csv(RES / "fevd.csv"); f = f[(f.L == 12) & (f.t2020 == "in") & (f.ident == "WE") & (f.h == 24)]
    rows = []
    for (kind, start) in (("avg", "1973-01"), ("eom", "1990-01")):
        for step in ("nom", "real", "rstar"):
            for fci in ("0", step):
                g = f[(f.kind == kind) & (f.start == start) & (f.step == step) & (f.fci.astype(str) == fci)]
                rows.append(dict(sample=f"{kind} {start[:4]}", case=f"{step}{' + FCI' if fci != '0' else ''}",
                                 **{f"{b}_{v}": float(g[g.bound == b][v].iloc[0]) for b in ("full_upper", "post_upper", "post_lower") for v in ("u", "pi")}))
    T = pd.DataFrame(rows); T.to_csv(RES / "fevd_table_h24.csv", index=False, float_format="%.4f")
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for a, v, lab in ((ax[0], "u", "Unemployment gap"), (ax[1], "pi", "Core PCE inflation")):
        y = np.arange(len(T))[::-1]
        a.hlines(y, 100 * T[f"post_lower_{v}"], 100 * T[f"post_upper_{v}"], color=BLUE, lw=2.2, label="1996-2026: bounds (lower = measured surprises, upper = invertibility)")
        a.plot(100 * T[f"post_lower_{v}"], y, "o", color=ORANGE, ms=5, label="lower bound")
        a.plot(100 * T[f"full_upper_{v}"], y, "D", color=BLUE, ms=5, mfc="white", label="full sample, upper bound (invertibility)")
        a.set_yticks(y); a.set_yticklabels(T["sample"] + "  " + T["case"]); a.set_xlabel("share of 24-month forecast-error variance, percent")
        a.set_title(lab, loc="left", fontsize=9); a.set_xlim(left=-0.5)
    hdl, lbl = ax[0].get_legend_handles_labels()
    fig.tight_layout(rect=(0, 0.12, 1, 1)); fig.legend(hdl, lbl, frameon=False, fontsize=8, loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=3); save(fig, "fig3_fevd")

if __name__ == "__main__":
    fig_shocks(); fig_fevd()
    fig_hd(title="r*-gap 2-year yield and FCI: VAR in monthly averages from 1973 (window column)")
    fig_hd("rstar_rstar_eom1990_L12_WE_in", "boot_hd_rstar_rstar_eom_WE.npz", "route1_rstar_rstar_1996.npz", "fig4_hd_rstar_eom", "r*-gap 2-year yield and FCI: VAR in end-of-month values from 1990 (window column)")
    fig_hd("nom_0_avg1973_L12_WE_in", "boot_hd_nom_0_avg_WE.npz", "route1_nom_0_1996.npz", "fig5_hd_nom_avg", "Nominal 2-year yield, no FCI: VAR in monthly averages from 1973 (window column)")
    fig_hd("rstar_rstar_avg1973_L12_WE2_in", "none.npz", "route1_rstar_rstar_1996.npz", "fig6_hd_rstar_avg_WE2", "r*-gap with FCI, monthly averages from 1973, two-month recovery (WE2)")
    fig_hd("rstar_rstar_avg1973_L12_P1_in", "boot_hd_rstar_rstar_avg_P1.npz", "route1_rstar_rstar_1996.npz", "fig7_hd_rstar_avg_P1", "r*-gap with FCI, monthly averages from 1973, proxy column (P1)")
