"""Tables and figure for the LaTeX note (mp_transmission.tex), built from the midas_core.py outputs (FS-A21).
Run from this folder: python3 make_tables.py   Output: tables/*.tex, figures/fig1_steps.pdf
Markers: ** = 90% interval excludes zero; dagger = 68% interval excludes zero (but not the 90%)."""
import os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); UP = os.path.dirname(HERE)
import glob
def _load(irf_files):
    """All midas_core outputs; the sample tag comes from the file name; duplicates (same case run twice) keep the newest file."""
    out = []
    for fn in sorted(glob.glob(os.path.join(UP, "midas_core_*.csv")), key=os.path.getmtime):
        if fn.endswith("_irf.csv") != irf_files or os.path.basename(fn) in ("midas_core.csv", "midas_core_irf.csv"): continue
        smp = "drop2021" if "drop2021" in fn else ("end2019" if "end2019" in fn else "")
        z = pd.read_csv(fn).assign(sample=smp)
        if "trend" not in z: z["trend"] = 0
        if "shock" not in z: z["shock"] = "NS"
        if "bootd" not in z: z["bootd"] = 0
        out.append(z)
    z = pd.concat(out); z["fci"] = z.fci.astype(str); z["trend"] = z.trend.fillna(0).astype(int)
    z["shock"] = z.shock.fillna("NS"); z["bootd"] = z.bootd.fillna(0).astype(int)
    keys = ["macro", "rate", "fci", "trend", "sample", "shock", "bootd", "lags", "var"] + (["h"] if irf_files else [])
    return z.drop_duplicates(keys, keep="last")
D_ALL = _load(False); IRF_ALL = _load(True)
d = D_ALL[(D_ALL.shock == "NS") & (D_ALL.bootd == 0)]; irf = IRF_ALL[(IRF_ALL.shock == "NS") & (IRF_ALL.bootd == 0)]
TR = 1   # FS-A24: quadratic time trend in every monthly equation is the baseline assumption for all results
os.makedirs(os.path.join(HERE, "tables"), exist_ok=True); os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
d.to_csv(os.path.join(HERE, "tables", "all_results.csv"), index=False, float_format="%.4f")

def cell(r, h):
    v = f"{r[f'r{h}']:.2f}".replace("-", "$-$")
    if r[f"lo{h}"] > 0 or r[f"hi{h}"] < 0: return v + "$^{**}$"
    if r[f"lo68_{h}"] > 0 or r[f"hi68_{h}"] < 0: return v + "$^{\\dagger}$"
    return v

def table(rows, var, macro="u,pi", name=""):
    """rows: list of (label, rate, fci, trend). Columns: 12/24/36 months x 3/6/12 lags."""
    out = ["\\begin{tabular}{llccccccccc}", "\\toprule", " & & \\multicolumn{3}{c}{12 months} & \\multicolumn{3}{c}{24 months} & \\multicolumn{3}{c}{36 months}\\\\",
           "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}\\cmidrule(lr){9-11}", "Rate & FCI & 3 & 6 & 12 & 3 & 6 & 12 & 3 & 6 & 12 \\\\", "\\midrule"]
    for row in rows:
        lab = row[0]
        if lab is None: out.append("\\midrule"); continue
        rate, fci, tr = row[1:4]; smp = row[4] if len(row) > 4 else ""; fl = row[5] if len(row) > 5 else {"0": "no", "1": "yes"}[fci]
        g = d[(d.macro == macro) & (d["var"] == var) & (d.rate == rate) & (d.fci == fci) & (d.trend == tr) & (d["sample"] == smp)].sort_values("lags")
        if len(g) < 3: continue
        out.append(f"{lab} & {fl} & " + " & ".join(cell(r, h) for h in (12, 24, 36) for _, r in g.iterrows()) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}"]
    open(os.path.join(HERE, "tables", name + ".tex"), "w").write("\n".join(out) + "\n")

CORE = [("Nominal", "nom", "0", TR), ("Nominal", "nom", "1", TR), (None,) * 4, ("Real", "real", "0", TR), ("Real", "real", "1", TR), (None,) * 4,
        ("$r^*$-gap", "rstar", "0", TR), ("$r^*$-gap", "rstar", "1", TR)]
for var, nm in (("u", "tab1_u"), ("P", "tab2_p")): table(CORE, var, "u,pi", nm)
for var, nm in (("u", "tab3_ip_u"), ("P", "tab3_ip_p"), ("ip", "tab3_ip_ip")): table(CORE, var, "u,pi,ip", nm)
FL = (("0", "none"), ("nom", "nominal"), ("real", "real"), ("rstar", "$r^*$-gap"))
def block(lab, rate, tr=TR):
    out = []
    for f, fl in FL:
        ff = "1" if f == {"rstar": "rstar", "nom": "nom"}.get(rate) else f      # same-form FCI is stored as fci = 1
        out.append((lab, rate, ff, tr, "", fl))
    return out + [(None,)]
# FCI held at the note's three indexes (nominal, real, r*-gap); only the 2-year adjustment changes (user, FS-A23)
ROB = (block("2-year $r^*$-gap, Laubach--Williams (baseline)", "rstar") + block("2-year $r^*$-gap, Kiley", "kiley")
       + block("2-year $-$ 9--10y forward rate", "fwd") + block("2-year $-$ 8-year average", "ma8"))[:-1]
for var, nm in (("u", "tab4_rob_u"), ("P", "tab4_rob_p")): table(ROB, var, "u,pi", nm)
SMP = [("Baseline sample", "rstar", "1", TR, "", "$r^*$-gap (LW)"), ("Also drop 2021", "rstar", "1", TR, "drop2021", "$r^*$-gap (LW)"), ("End in 2019", "rstar", "1", TR, "end2019", "$r^*$-gap (LW)"),
       (None,), ("Baseline sample", "rstar", "0", TR, "", "none"), ("Also drop 2021", "rstar", "0", TR, "drop2021", "none"), ("End in 2019", "rstar", "0", TR, "end2019", "none")]
for var, nm in (("u", "tab5_smp_u"), ("P", "tab5_smp_p")): table(SMP, var, "u,pi", nm)


# Table 7: fuller bootstrap (daily block re-estimated in each draw, 1000 draws); Table 8: alternative shocks (FS-A25)
def with_data(dd, fn):
    global d
    keep = d; d = dd; fn(); d = keep
CORE2 = [r for r in CORE]
if ((D_ALL.bootd == 1)).any():
    with_data(D_ALL[(D_ALL.shock == "NS") & (D_ALL.bootd == 1)], lambda: [table(CORE2, v, "u,pi", nm) for v, nm in (("u", "tab7_boot_u"), ("P", "tab7_boot_p"))])
for sk, tag in (("BS-ORTH", "bs"), ("NS-JK", "jk")):
    if (D_ALL.shock == sk).any():
        with_data(D_ALL[(D_ALL.shock == sk) & (D_ALL.bootd == 0)], lambda: [table(CORE2, v, "u,pi", nm) for v, nm in (("u", f"tab8_{tag}_u"), ("P", f"tab8_{tag}_p"))])

# Figure 1: the four key cases, 6 lags, with 68% and 90% bands; Bauer-Swanson benchmark (read from their Fig. 8) as markers
BS = {"u": ([10, 12, 24, 36], [0.22, 0.19, 0.17, 0.15]), "P": ([12, 24, 36], [-0.36, -0.48, -0.6])}
cases = [("nom", "0", "Nominal 2-year, no FCI"), ("nom", "1", "Nominal 2-year and FCI"), ("rstar", "0", "$r^*$-gap 2-year, no FCI"), ("rstar", "1", "$r^*$-gap 2-year and FCI")]
fig, ax = plt.subplots(2, 4, figsize=(11, 5), sharey="row")
for j, (rate, fci, title) in enumerate(cases):
    for i, (var, ylab) in enumerate((("u", "Unemployment gap (pp)"), ("P", "Core PCE price level (%)"))):
        g = irf[(irf.macro == "u,pi") & (irf["var"] == var) & (irf.rate == rate) & (irf.fci == fci) & (irf.lags == 6) & (irf.trend == TR) & (irf["sample"] == "")].sort_values("h")
        a = ax[i, j]; a.fill_between(g.h, g.lo, g.hi, color="0.85", lw=0); a.fill_between(g.h, g.lo68, g.hi68, color="0.65", lw=0)
        a.plot(g.h, g.r, color="k", lw=1.6); a.axhline(0, color="k", lw=0.6)
        a.plot(*BS[var], "o", ms=4, mfc="none", mec="tab:red", label="Bauer-Swanson (2023; CPI for prices)" if (i == 0 and j == 0) else None)
        if i == 0: a.set_title(title, fontsize=9)
        if j == 0: a.set_ylabel(ylab, fontsize=9)
        if i == 1: a.set_xlabel("Months", fontsize=9)
        a.tick_params(labelsize=8)
ax[0, 0].legend(fontsize=7, frameon=False, loc="lower left")
fig.tight_layout(); fig.savefig(os.path.join(HERE, "figures", "fig1_steps.pdf")); print("tables and figure written")

# Table 8 (compact): alternative shocks, with the FCI (nominal and r*-gap steps); rows labelled by shock (FS-A25)
def shock_table(var, name):
    out = ["\\begin{tabular}{llccccccccc}", "\\toprule", " & & \\multicolumn{3}{c}{12 months} & \\multicolumn{3}{c}{24 months} & \\multicolumn{3}{c}{36 months}\\\\",
           "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}\\cmidrule(lr){9-11}", "Shock & Step (with FCI) & 3 & 6 & 12 & 3 & 6 & 12 & 3 & 6 & 12 \\\\", "\\midrule"]
    for k, (sk, lab) in enumerate((("NS", "Nakamura--Steinsson (baseline)"), ("BS-ORTH", "Bauer--Swanson orthogonalized"), ("NS-JK", "Jaroci\\'nski--Karadi pure policy"))):
        if k: out.append("\\midrule")
        for rate, step in (("nom", "Nominal"), ("rstar", "$r^*$-gap")):
            g = D_ALL[(D_ALL.shock == sk) & (D_ALL.bootd == 0) & (D_ALL.macro == "u,pi") & (D_ALL["var"] == var) & (D_ALL.rate == rate) & (D_ALL.fci == "1") & (D_ALL.trend == TR) & (D_ALL["sample"] == "")].sort_values("lags")
            if len(g) < 3: continue
            out.append(f"{lab} & {step} & " + " & ".join(cell(r, h) for h in (12, 24, 36) for _, r in g.iterrows()) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}"]
    open(os.path.join(HERE, "tables", name + ".tex"), "w").write("\n".join(out) + "\n")
for var, nm in (("u", "tab8_shocks_u"), ("P", "tab8_shocks_p")): shock_table(var, nm)
