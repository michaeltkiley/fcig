"""Tables and figures for Part B5 (Route 2 with the proposed baselines).   python3 F_route2_base.py -> results_route2_base/tables.md, figures/B5_*.png|pdf"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent; R5 = HERE / "results_route2_base"; FIG = HERE / "figures"
BLUE, VIOLET, ORANGE, GRAY, INK = "#2a78d6", "#6250d6", "#eb6834", "#8a8984", "#52514e"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK, "axes.grid": True, "grid.color": "#e4e3df", "lines.linewidth": 1.4})
ma12 = lambda x: pd.Series(x).rolling(12).mean().values
import sys
MODE = sys.argv[1] if len(sys.argv) > 1 else "infer"
S = pd.read_csv(R5 / "shares.csv"); B = pd.read_csv(R5 / "bands_shares.csv"); O = pd.read_csv(R5 / "overlap.csv")
S = S[S["mode"] == MODE]; B = B[B["mode"] == MODE]
SRC = [("1974-1989", "spliced", "1974-89: monthly-recovered (scaled)"), ("1990-2026", "daily_all", "1990-2026: daily-recovered, all days"), ("1990-2026", "daily_other", "  non-announcement days"),
       ("1990-2026", "daily_ann", "  announcement days"), ("1990-2026", "measured", "  measured surprises (Route 1)"), ("1996-2026", "daily_all", "1996-2026: daily-recovered, all days"),
       ("1996-2026", "measured", "  measured surprises (Route 1)")]
VN = {"u": "unemployment gap", "pi": "core inflation", "pol": "2-year yield", "idx": "FCI"}
out = [f"### Splice (May 1990 - Sept 2026, March-December 2020 excluded)\n\n" + O.round(3).to_markdown(index=False)]
for fci in ("rstar", "0"):
    for h in (24, 12, 36):
        rows = []
        for model in (1973, 1996):
            for era, src, name in SRC:
                g = S[(S.fci.astype(str) == fci) & (S.model == model) & (S.h == h) & (S.era == era) & (S.source == src)]
                if g.empty: continue
                r = {"model from": model, "shocks": name}
                for v in ("u", "pi", "pol", "idx"):
                    if v not in g or pd.isna(g[v].iloc[0]): continue
                    b = B[(B.fci.astype(str) == fci) & (B.model == model) & (B.h == h) & (B.era == era) & (B.source == src) & (B["var"] == v)]
                    r[VN[v]] = f"{100 * g[v].iloc[0]:.1f}" + (f" [{100 * b.p5.iloc[0]:.1f}, {100 * b.p95.iloc[0]:.1f}]" if len(b) else "")
                rows.append(r)
        out.append(f"### Variance shares at {h} months, percent: r*-gap {'with the FCI' if fci != '0' else 'yield alone'} (12 lags, March-December 2020 dropped from estimation, 2020 {'decomposed with the estimated coefficients' if MODE == 'infer' else 'absorbed by the dummies'}; 90% bands from Note B's draws)\n\n" + pd.DataFrame(rows).to_markdown(index=False))
# episodes
MONTHS = ["1979-12", "1980-12", "1982-06", "1984-06", "1986-12", "1989-06", "1992-06", "1995-06", "1998-12", "2001-12", "2003-06", "2008-12", "2009-10", "2013-12", "2019-12", "2020-04", "2020-12", "2021-06", "2022-06", "2022-12", "2023-12", "2024-12", "2026-09"]
rows = []
for model in (1973, 1996):
    h = pd.read_csv(R5 / f"hd_rstar_rstar_model{model}_{MODE}.csv")
    for v in ("u", "pi", "pol", "idx"):
        g = h[h["var"] == v].set_index("month").drop(columns="var")
        if v == "pi": g = g.rolling(12).mean()
        for m in MONTHS: rows.append(dict(model=model, var="core infl. 12m" if v == "pi" else v, month=m, all_shocks=g.loc[m, "all_shocks_var"], route2=g.loc[m, "spliced"], measured=g.loc[m, "measured"]))
E = pd.DataFrame(rows); E.to_csv(R5 / f"episodes_{MODE}.csv", index=False, float_format="%.3f")
P = E.pivot_table(index="month", columns=["var", "model"], values="route2", sort=False).round(2)
out.append("### Route 2 historical contributions at selected months, r*-gap with FCI (policy-direction shocks; columns: variable and propagation model)\n\n" + P.to_markdown())
(R5 / f"tables_{MODE}.md").write_text("\n\n".join(out) + "\n")
# figure: historical decomposition, both propagation models
names = [("u", "Unemployment gap (pp)"), ("pi", "Core PCE inflation, 12-month (pp)"), ("pol", "2-year yield, r*-gap (pp)"), ("idx", "FCI, r*-gap (index points)")]
fig, ax = plt.subplots(2, 2, figsize=(10.5, 6.6), sharex=True); ax = ax.ravel()
for k, (v, lab) in enumerate(names):
    a = ax[k]
    for model, col in ((1973, BLUE), (1996, VIOLET)):
        h = pd.read_csv(R5 / f"hd_rstar_rstar_model{model}_{MODE}.csv"); g = h[h["var"] == v]; t = pd.PeriodIndex(g.month, freq="M").to_timestamp(); f = ma12 if v == "pi" else np.asarray
        if model == 1973:
            a.plot(t, f(g.all_shocks_var.values), color=GRAY, lw=1.0, label="all shocks (monthly VAR)")
            z = np.load(R5 / f"bands_hd_rstar_rstar_model1973_{MODE}.npz", allow_pickle=True)["hd"][:, :, k].astype(float)
            if v == "pi": z = np.array([ma12(r) for r in z])
            a.fill_between(t, np.nanpercentile(z, 5, axis=0), np.nanpercentile(z, 95, axis=0), color=BLUE, alpha=0.15, lw=0, label="90% band, model from 1973")
        a.plot(t, f(g.spliced.values), color=col, label=f"policy-direction shocks, model from {model}")
        if model == 1973: a.plot(t, f(g.measured.values), color=ORANGE, lw=1.1, label="measured surprises, model from 1973")
    a.axhline(0, color=INK, lw=0.6); a.set_title(lab, loc="left", fontsize=9)
    if v == "u": a.set_ylim(-3, 5)
hh, ll = ax[0].get_legend_handles_labels(); fig.suptitle(f"Route 2 with the proposed baselines: r*-gap with FCI, 12 lags, 2020 dropped from estimation ({MODE})", x=0.01, ha="left", fontsize=10)
fig.tight_layout(rect=(0, 0.1, 1, 0.97)); fig.legend(hh, ll, frameon=False, fontsize=8, loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=2)
for ext in ("png", "pdf"): fig.savefig(FIG / f"B5_hd_rstar_{MODE}.{ext}", dpi=160, bbox_inches="tight")
plt.close(fig)
print("\n\n".join(out)[:6000])
