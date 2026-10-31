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
        import re as _re
        m_ = _re.search(r"_((?:drop|end)\d{4})", os.path.basename(fn)); smp = m_.group(1) if m_ else ""
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

COLS = ["\\begin{tabular}{llccccccccc}", "\\toprule", " & & \\multicolumn{3}{c}{12 months} & \\multicolumn{3}{c}{24 months} & \\multicolumn{3}{c}{36 months}\\\\",
        "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}\\cmidrule(lr){9-11}"]
def sel(rate, fci, var, macro="u,pi", tr=TR, smp="", shock="NS", bootd=0):
    return D_ALL[(D_ALL.macro == macro) & (D_ALL["var"] == var) & (D_ALL.rate == rate) & (D_ALL.fci == fci) & (D_ALL.trend == tr)
                 & (D_ALL["sample"] == smp) & (D_ALL.shock == shock) & (D_ALL.bootd == bootd)].sort_values("lags")
def ptable(panels, name, h1="Step", h2="FCI"):
    """panels: list of (title, rows); row = (col1, col2, dict of sel() arguments)."""
    out = COLS + [f"{h1} & {h2} & 3 & 6 & 12 & 3 & 6 & 12 & 3 & 6 & 12 \\\\"]
    for title, rows in panels:
        out += ["\\midrule", f"\\multicolumn{{11}}{{l}}{{\\textit{{{title}}}}}\\\\"]
        for c1, c2, kw in rows:
            g = sel(**kw)
            if len(g) < 3: continue
            out.append(f"{c1} & {c2} & " + " & ".join(cell(r, h) for h in (12, 24, 36) for _, r in g.iterrows()) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}"]
    open(os.path.join(HERE, "tables", name + ".tex"), "w").write("\n".join(out) + "\n")

STEPS = [("Nominal", "no", ("nom", "0")), ("", "yes", ("nom", "1")), ("Real", "no", ("real", "0")), ("", "yes", ("real", "1")), ("$r^*$-gap", "no", ("rstar", "0")), ("", "yes", ("rstar", "1"))]
def core_rows(var, macro="u,pi", **kw): return [(a, b, dict(rate=r, fci=f, var=var, macro=macro, **kw)) for a, b, (r, f) in STEPS]
ptable([("A. Unemployment gap (percentage points)", core_rows("u")), ("B. Core PCE price level (percent)", core_rows("P"))], "tab1_core")
ptable([("A. Unemployment gap (percentage points)", core_rows("u", "u,pi,ip")), ("B. Industrial production (percent)", core_rows("ip", "u,pi,ip"))], "tabA_ip")
ptable([("A. Unemployment gap (percentage points)", core_rows("u", tr=0)), ("B. Core PCE price level (percent)", core_rows("P", tr=0))], "tabA_notrend")
ptable([("A. Unemployment gap (percentage points)", core_rows("u", bootd=3)), ("B. Core PCE price level (percent)", core_rows("P", bootd=3))], "tabA_boot")
FCI4 = [("none", "0"), ("nominal", "nom"), ("real", "real"), ("$r^*$-gap", "rstar")]
def adj_rows(rate, var):
    same = {"rstar": "rstar", "nom": "nom"}.get(rate)
    return [("", lab, dict(rate=rate, fci=("1" if f == same else f), var=var)) for lab, f in FCI4]
ADJ = [("2-year: nominal", "nom"), ("2-year: Laubach--Williams $r^*$-gap (baseline)", "rstar"), ("2-year: Kiley $r^*$-gap", "kiley"),
       ("2-year: minus 9--10-year forward rate", "fwd"), ("2-year: minus trailing 8-year average", "ma8")]
for var, nm in (("u", "tab2_rob_u"), ("P", "tab2_rob_p")):
    ptable([(t, adj_rows(r, var)) for t, r in ADJ], nm, h1="", h2="FCI")
SMPS = [("Baseline", ""), ("Also drop 2021", "drop2021"), ("End in 2022", "end2022"), ("End in 2019", "end2019")]
def smp_rows(var): return [(lab if i == 0 else "", fl, dict(rate="rstar", fci=f, var=var, smp=sm)) for lab, sm in SMPS for i, (fl, f) in enumerate((("none", "0"), ("$r^*$-gap", "1")))]
ptable([("A. Unemployment gap (percentage points)", smp_rows("u")), ("B. Core PCE price level (percent)", smp_rows("P"))], "tab3_smp", h1="Sample", h2="FCI")
SHK = [("Nakamura--Steinsson", "NS"), ("Greenbook-purged NS", "NS-GB"), ("Bauer--Swanson orth.", "BS-ORTH"), ("Jaroci\\'nski--Karadi", "NS-JK")]
def shk_rows(var): return [(lab if i == 0 else "", st, dict(rate=r, fci="1", var=var, shock=sk)) for lab, sk in SHK for i, (st, r) in enumerate((("nominal", "nom"), ("$r^*$-gap", "rstar")))]
ptable([("A. Unemployment gap (percentage points)", shk_rows("u")), ("B. Core PCE price level (percent)", shk_rows("P"))], "tabA_shocks", h1="Shock", h2="Step")

# Figure 2: the r*-gap 2-year, the r*-gap FCI and core inflation, 2015-2026 (monthly)
import sys; sys.path.insert(0, os.path.join(UP, "..", "mp_var_fci")); sys.path.insert(0, UP)
from mf_common import M as _M
_e2 = pd.read_csv(os.path.join(UP, "..", "mp_var_fci", "data", "EXPINF2YR.csv")); _e2 = pd.Series(_e2.iloc[:, 1].values, index=pd.PeriodIndex(pd.to_datetime(_e2.iloc[:, 0]), freq="M"))
from mf_common import D0 as _D0
_d0 = _D0.load()
gap2 = (_M.gs2 - _e2.reindex(_M.index) - _d0["rstar LW"].reindex(_M.index))
Z = pd.DataFrame({"r*-gap 2-year yield": gap2, "r*-gap FCI (market index)": _M.market_rstar, "Core PCE inflation, 12-month (%)": _M.pi_core.rolling(12).mean()}).loc["2015-01":"2026-09"]
fig, a = plt.subplots(figsize=(8, 3.2)); x = Z.index.to_timestamp()
for c, st in zip(Z.columns, ("-", "--", ":")): a.plot(x, Z[c], st, color="k", lw=1.5, label=c)
a.axhline(0, color="0.5", lw=0.6); a.legend(fontsize=8, frameon=False); a.tick_params(labelsize=8); a.set_ylabel("Percent / index units", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "figures", "fig2_recent.pdf")); plt.close(fig)

# Figure 3: leave-one-year-out (baseline, 6 lags): u at 12 months and price level at 24 months with 90% intervals
L1 = D_ALL[(D_ALL["sample"].str.startswith("drop")) & (D_ALL["sample"] != "drop2021") & (D_ALL.rate == "rstar") & (D_ALL.fci == "1") & (D_ALL.lags == 6) & (D_ALL.trend == TR) & (D_ALL.shock == "NS")]
if len(L1):
    base = sel("rstar", "1", "u").query("lags == 6"); baseP = sel("rstar", "1", "P").query("lags == 6")
    fig, ax = plt.subplots(1, 2, figsize=(9, 3))
    for a, (var, h, lab, b0) in zip(ax, (("u", 12, "Unemployment gap, 12 months (pp)", base), ("P", 24, "Core PCE price level, 24 months (%)", baseP))):
        g = L1[L1["var"] == var].copy(); g["yr"] = g["sample"].str[4:].astype(int); g = g.sort_values("yr")
        a.errorbar(g.yr, g[f"r{h}"], yerr=[g[f"r{h}"] - g[f"lo{h}"], g[f"hi{h}"] - g[f"r{h}"]], fmt="o", ms=3, color="k", lw=0.8)
        a.axhline(float(b0[f"r{h}"].iloc[0]), color="tab:red", lw=1, ls="--"); a.axhline(0, color="0.5", lw=0.6)
        a.set_title(lab, fontsize=9); a.set_xlabel("Year dropped", fontsize=8); a.tick_params(labelsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "figures", "fig3_loyo.pdf")); plt.close(fig)

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
