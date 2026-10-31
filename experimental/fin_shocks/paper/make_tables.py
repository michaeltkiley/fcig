"""Tables and figure for the LaTeX note (mp_transmission.tex), built from the midas_core.py outputs (FS-A21).
Run from this folder: python3 make_tables.py   Output: tables/*.tex, figures/fig1_steps.pdf
Markers: ** = 90% interval excludes zero; * = 68% interval excludes zero (but not the 90%)."""
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); UP = os.path.dirname(HERE)
FILES = ["nom-0_nom-1", "real-0_real-1", "rstar-0_rstar-1", "kiley-0_kiley-1", "ma8-0_ma8-nom_ma8-real_ma8-rstar", "nom-0_nom-1_nom-real_trend"]
d = pd.concat([pd.read_csv(os.path.join(UP, f"midas_core_{f}.csv")) for f in FILES]); d["fci"] = d.fci.astype(str)
irf = pd.concat([pd.read_csv(os.path.join(UP, f"midas_core_{f}_irf.csv")) for f in FILES]); irf["fci"] = irf.fci.astype(str)
if "trend" not in d: d["trend"] = 0
d["trend"] = d.trend.fillna(0).astype(int); irf["trend"] = irf.trend.fillna(0).astype(int)
os.makedirs(os.path.join(HERE, "tables"), exist_ok=True); os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
d.to_csv(os.path.join(HERE, "tables", "all_results.csv"), index=False, float_format="%.4f")

def cell(r, h):
    v = f"{r[f'r{h}']:.2f}".replace("-", "$-$")
    if r[f"lo{h}"] > 0 or r[f"hi{h}"] < 0: return v + "$^{**}$"
    if r[f"lo68_{h}"] > 0 or r[f"hi68_{h}"] < 0: return v + "$^{*}$"
    return v

def table(rows, var, macro="u,pi", name=""):
    """rows: list of (label, rate, fci, trend). Columns: 12/24/36 months x 3/6/12 lags."""
    out = ["\\begin{tabular}{llccccccccc}", "\\toprule", " & & \\multicolumn{3}{c}{12 months} & \\multicolumn{3}{c}{24 months} & \\multicolumn{3}{c}{36 months}\\\\",
           "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}\\cmidrule(lr){9-11}", "Rate & FCI & 3 & 6 & 12 & 3 & 6 & 12 & 3 & 6 & 12 \\\\", "\\midrule"]
    for lab, rate, fci, tr in rows:
        if lab is None: out.append("\\midrule"); continue
        g = d[(d.macro == macro) & (d["var"] == var) & (d.rate == rate) & (d.fci == fci) & (d.trend == tr)].sort_values("lags")
        fl = {"0": "no", "1": "yes"}.get(fci, fci.replace("rstar", "$r^*$-gap").replace("nom", "nominal"))
        out.append(f"{lab} & {fl} & " + " & ".join(cell(r, h) for h in (12, 24, 36) for _, r in g.iterrows()) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}"]
    open(os.path.join(HERE, "tables", name + ".tex"), "w").write("\n".join(out) + "\n")

CORE = [("Nominal", "nom", "0", 0), ("Nominal", "nom", "1", 0), (None,) * 4, ("Real", "real", "0", 0), ("Real", "real", "1", 0), (None,) * 4,
        ("$r^*$-gap", "rstar", "0", 0), ("$r^*$-gap", "rstar", "1", 0)]
for var, nm in (("u", "tab1_u"), ("P", "tab2_p")): table(CORE, var, "u,pi", nm)
for var, nm in (("u", "tab3_ip_u"), ("P", "tab3_ip_p"), ("ip", "tab3_ip_ip")): table(CORE, var, "u,pi,ip", nm)
ROB = [("$r^*$-gap (LW), baseline", "rstar", "1", 0), (None,) * 4, ("$r^*$-gap (Kiley)", "kiley", "0", 0), ("$r^*$-gap (Kiley)", "kiley", "1", 0), (None,) * 4,
       ("Nominal + quadratic trend", "nom", "0", 1), ("Nominal + quadratic trend", "nom", "1", 1), ("Nominal + quadratic trend", "nom", "real", 1), (None,) * 4,
       ("2-year $-$ 8-year average", "ma8", "0", 0), ("2-year $-$ 8-year average", "ma8", "nom", 0), ("2-year $-$ 8-year average", "ma8", "real", 0), ("2-year $-$ 8-year average", "ma8", "rstar", 0)]
for var, nm in (("u", "tab4_rob_u"), ("P", "tab4_rob_p")): table(ROB, var, "u,pi", nm)

# Figure 1: the four key cases, 6 lags, with 68% and 90% bands; Bauer-Swanson benchmark (read from their Fig. 8) as markers
BS = {"u": ([10, 12, 24, 36], [0.22, 0.19, 0.17, 0.15]), "P": ([12, 24, 36], [-0.36, -0.48, -0.6])}
cases = [("nom", "0", "Nominal 2-year, no FCI"), ("nom", "1", "Nominal 2-year and FCI"), ("rstar", "0", "$r^*$-gap 2-year, no FCI"), ("rstar", "1", "$r^*$-gap 2-year and FCI")]
fig, ax = plt.subplots(2, 4, figsize=(11, 5), sharey="row")
for j, (rate, fci, title) in enumerate(cases):
    for i, (var, ylab) in enumerate((("u", "Unemployment gap (pp)"), ("P", "Core PCE price level (%)"))):
        g = irf[(irf.macro == "u,pi") & (irf["var"] == var) & (irf.rate == rate) & (irf.fci == fci) & (irf.lags == 6) & (irf.trend == 0)].sort_values("h")
        a = ax[i, j]; a.fill_between(g.h, g.lo, g.hi, color="0.85", lw=0); a.fill_between(g.h, g.lo68, g.hi68, color="0.65", lw=0)
        a.plot(g.h, g.r, color="k", lw=1.6); a.axhline(0, color="k", lw=0.6)
        a.plot(*BS[var], "o", ms=4, mfc="none", mec="tab:red", label="Bauer-Swanson (2023)" if (i == 0 and j == 0) else None)
        if i == 0: a.set_title(title, fontsize=9)
        if j == 0: a.set_ylabel(ylab, fontsize=9)
        if i == 1: a.set_xlabel("Months", fontsize=9)
        a.tick_params(labelsize=8)
ax[0, 0].legend(fontsize=7, frameon=False, loc="lower left")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "figures", "fig1_steps.pdf")); print("tables and figure written")
