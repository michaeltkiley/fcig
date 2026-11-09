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
        if "mstart" not in z: z["mstart"] = "1994-02"
        out.append(z)
    z = pd.concat(out); z["fci"] = z.fci.astype(str); z["trend"] = z.trend.fillna(0).astype(int)
    z["shock"] = z.shock.fillna("NS"); z["bootd"] = z.bootd.fillna(0).astype(int)
    keys = ["macro", "rate", "fci", "trend", "mstart", "sample", "shock", "bootd", "lags", "var"] + (["h"] if irf_files else [])
    return z.drop_duplicates(keys, keep="last")
D_FULL = _load(False); D_ALL = D_FULL[D_FULL.mstart == "1994-02"]; IRF_ALL = _load(True); IRF_ALL = IRF_ALL[IRF_ALL.mstart == "1994-02"]   # long-sample rows (FS-A29) only enter through sel(ms=...)
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
def sel(rate, fci, var, macro="u,pi", tr=TR, smp="", shock="NS", bootd=0, ms="1994-02"):
    return D_FULL[(D_FULL.macro == macro) & (D_FULL["var"] == var) & (D_FULL.rate == rate) & (D_FULL.fci == fci) & (D_FULL.trend == tr)
                 & (D_FULL["sample"] == smp) & (D_FULL.shock == shock) & (D_FULL.bootd == bootd) & (D_FULL.mstart == ms)].sort_values("lags")
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

STEPS = [("Nominal", "none", ("nom", "0")), ("", "included", ("nom", "1")), ("Real", "none", ("real", "0")), ("", "included", ("real", "1")), ("$r^*$-gap", "none", ("rstar", "0")), ("", "included", ("rstar", "1"))]
def core_rows(var, macro="u,pi", **kw): return [(a, b, dict(rate=r, fci=f, var=var, macro=macro, **kw)) for a, b, (r, f) in STEPS]
ptable([("A. Unemployment gap (percentage points)", core_rows("u")), ("B. Core PCE price level (percent)", core_rows("P"))], "tab1_core")
ptable([("A. Unemployment gap (percentage points)", core_rows("u", "u,pi,ip")), ("B. Industrial production (percent)", core_rows("ip", "u,pi,ip"))], "tabA_ip")
ptable([("A. Unemployment gap (percentage points)", core_rows("u", tr=0)), ("B. Core PCE price level (percent)", core_rows("P", tr=0))], "tabA_notrend")
ptable([("A. Unemployment gap (percentage points)", core_rows("u", bootd=3)), ("B. Core PCE price level (percent)", core_rows("P", bootd=3))], "tabA_boot")
# FS-A29: long-sample dynamics (monthly equations from 1973 / 1977 / 1982; shocks and daily model unchanged)
LONGP = [("1973", dict(ms="1973-01")), ("1977", dict(ms="1977-01")), ("1982", dict(ms="1982-01")), ("1973, no trend", dict(ms="1973-01", tr=0))]
for var, nm, ttl in (("u", "tabA_long_u", "Unemployment gap (percentage points)"), ("P", "tabA_long_p", "Core PCE price level (percent)")):
    ptable([(f"Monthly equations estimated from {lab}: {ttl.lower() if False else ttl}", core_rows(var, **kw)) for lab, kw in LONGP], nm)
FCI4 = [("none", "0"), ("nominal", "nom"), ("real", "real"), ("$r^*$-gap", "rstar")]
def adj_rows(rate, var):
    same = {"rstar": "rstar", "nom": "nom"}.get(rate)
    return [("", lab, dict(rate=rate, fci=("1" if f == same else f), var=var)) for lab, f in FCI4]
ADJ = [("Two-year yield: nominal", "nom"), ("Two-year yield: Laubach--Williams $r^*$-gap (baseline)", "rstar"), ("Two-year yield: Kiley $r^*$-gap", "kiley"),
       ("Two-year yield: minus 9--10-year forward rate", "fwd"), ("Two-year yield: minus average over past 8 years", "ma8")]
for var, nm in (("u", "tab2_rob_u"), ("P", "tab2_rob_p")):
    ptable([(t, adj_rows(r, var)) for t, r in ADJ], nm, h1="", h2="FCI")
SMPS = [("Baseline (excl.\\ Mar--Dec 2020)", ""), ("Also drop 2021", "drop2021"), ("End in 2022", "end2022"), ("End in 2019", "end2019")]
def smp_rows(var): return [(lab if i == 0 else "", fl, dict(rate="rstar", fci=f, var=var, smp=sm)) for lab, sm in SMPS for i, (fl, f) in enumerate((("none", "0"), ("$r^*$-gap", "1")))]
ptable([("A. Unemployment gap (percentage points)", smp_rows("u")), ("B. Core PCE price level (percent)", smp_rows("P"))], "tab3_smp", h1="Sample", h2="FCI")
SHK = [("Nakamura--Steinsson", "NS"), ("Nakamura--Steinsson, Greenbook part removed", "NS-GB"), ("Bauer--Swanson, predictable part removed", "BS-ORTH"), ("Jaroci\\'nski--Karadi pure policy", "NS-JK")]
def shk_rows(var): return [(lab if i == 0 else "", st, dict(rate=r, fci="1", var=var, shock=sk)) for lab, sk in SHK for i, (st, r) in enumerate((("Nominal", "nom"), ("$r^*$-gap", "rstar")))]
ptable([("A. Unemployment gap (percentage points)", shk_rows("u")), ("B. Core PCE price level (percent)", shk_rows("P"))], "tabA_shocks", h1="Shock", h2="Step")

# FS-A31: relaxing the key assumptions: daily Baa-10-year spread added (responds on impact); FCI replaced by its three components
def cc_rows(var):
    out = []
    for st, r in (("Nominal", "nom"), ("Real", "real"), ("$r^*$-gap", "rstar")):
        out += [(st, "FCI (baseline)", dict(rate=r, fci="1", var=var)), ("", "FCI and Baa spread", dict(rate=r, fci="baa", var=var)), ("", "Components instead of FCI", dict(rate=r, fci="cmp", var=var))]
    return out
ptable([("A. Unemployment gap (percentage points)", cc_rows("u")), ("B. Core PCE price level (percent)", cc_rows("P"))], "tabA_cc", h1="Step", h2="Financial block")
# FS-A32: monthly excess bond premium added to the monthly block (third variable, treated like u and inflation)
def ebp_rows(var):
    out = []
    for st, r in (("Nominal", "nom"), ("Real", "real"), ("$r^*$-gap", "rstar")):
        out += [(st, "No FCI", dict(rate=r, fci="0", var=var)), ("", "No FCI, with EBP", dict(rate=r, fci="0", var=var, macro="u,pi,ebp")),
                ("", "FCI", dict(rate=r, fci="1", var=var)), ("", "FCI, with EBP", dict(rate=r, fci="1", var=var, macro="u,pi,ebp"))]
    return out
ptable([("A. Unemployment gap (percentage points)", ebp_rows("u")), ("B. Core PCE price level (percent)", ebp_rows("P")), ("C. Excess bond premium (percentage points)", [(st if k == 0 else "", lab, dict(rate=r, fci=f, var="ebp", macro="u,pi,ebp")) for st, r in (("Nominal", "nom"), ("Real", "real"), ("$r^*$-gap", "rstar")) for k, (lab, f) in enumerate((("No FCI", "0"), ("FCI", "1")))])], "tabA_ebp", h1="Step", h2="Model")
# F tests of the proportional-weights restriction (prop_test.py): p-values, FCI versus its three components
_pt = pd.read_csv(os.path.join(UP, "prop_test.csv"))
_o = ["\\begin{tabular}{llccc}", "\\toprule", "Step & Equation & 3 lags & 6 lags & 12 lags \\\\", "\\midrule"]
for st, r in (("Nominal", "nom"), ("Real", "real"), ("$r^*$-gap", "rstar")):
    for k, (eq, lab) in enumerate((("u", "Unemployment gap"), ("pi", "Core PCE inflation"))):
        g = _pt[(_pt["step"] == r) & (_pt["eq"] == eq)].sort_values("lags")
        _o.append((st if k == 0 else "") + f" & {lab} & " + " & ".join(f"{v:.2f}" for v in g.p) + " \\\\")
_o += ["\\bottomrule", "\\end{tabular}"]
open(os.path.join(HERE, "tables", "tabA_prop.tex"), "w").write("\n".join(_o) + "\n")

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

# ---------------------------------------------------------------------------------------------------------------------------------------------
# FS-A40: implied policy trade-off (Phillips multiplier, tradeoff.py), the headline figure with the shock's financial paths, and the long view
# of nominal versus r*-gap rates. PAPER_* = values stated in the text; checked below (OK / MISMATCH).
def _tload(name):
    fn = os.path.join(UP, name)
    return pd.read_csv(fn) if os.path.exists(fn) else None
TB = _tload("tradeoff_nom-0_nom-1_real-0_real-1_rstar-0_rstar-1.csv")
TF = _tload("tradeoff_nom-0_nom-1_real-0_real-1_rstar-0_rstar-1_fin.csv")
TS = {"end2019": _tload("tradeoff_nom-1_rstar-0_rstar-1_end2019.csv"), "drop2021": _tload("tradeoff_nom-1_rstar-1_drop2021.csv"),
      "m1973": _tload("tradeoff_nom-1_rstar-1_m197301.csv")}
def kcell(r):
    """Point estimate with its 90% Anderson-Rubin-type set; ** when the set excludes zero; open-ended sets shown with infinity."""
    if r is None: return "", ""
    lo_inf = not bool(r.bounded) and r.k_lo <= -5.99; hi_inf = not bool(r.bounded) and r.k_hi >= 2.99
    v = "---" if (lo_inf and hi_inf) else f"{r.kappa:.2f}".replace("-", "$-$")      # set covers the whole grid: point estimate not informative
    if r.k_hi < 0 or r.k_lo > 0: v += "$^{**}$"
    lo = "$-\\infty$" if lo_inf else f"{r.k_lo:.2f}".replace("-", "$-$")
    hi = "$\\infty$" if hi_inf else f"{r.k_hi:.2f}".replace("-", "$-$")
    return v, f"{{\\scriptsize [{lo}, {hi}]}}"
def krows(T, case, label, lab2):
    out1, out2 = [f"{label} & {lab2}"], [" & "]
    for Hh in (24, 36):
        for L in (3, 6, 12):
            g = T[(T.case == case) & (T.H == Hh) & (T.lags == L)]
            a, b = kcell(g.iloc[0]) if len(g) else ("", ""); out1.append(a); out2.append(b)
    return [" & ".join(out1) + " \\\\", " & ".join(out2) + " \\\\[2pt]"]
if TB is not None:
    o = ["\\begin{tabular}{llcccccc}", "\\toprule", " & & \\multicolumn{3}{c}{24 months} & \\multicolumn{3}{c}{36 months}\\\\", "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}",
         "Step & FCI & 3 & 6 & 12 & 3 & 6 & 12 \\\\", "\\midrule", "\\multicolumn{8}{l}{\\textit{A. Baseline sample}}\\\\"]
    for lab, lab2, c in (("Nominal", "none", "nom-0"), ("", "included", "nom-1"), ("Real", "none", "real-0"), ("", "included", "real-1"), ("$r^*$-gap", "none", "rstar-0"), ("", "included", "rstar-1")):
        o += krows(TB, c, lab, lab2)
    o += ["\\midrule", "\\multicolumn{8}{l}{\\textit{B. Other samples, with the FCI}}\\\\"]
    for sk, slab in (("end2019", "End in 2019"), ("drop2021", "Also drop 2021"), ("m1973", "Monthly equations from 1973")):
        if TS[sk] is None: continue
        o += krows(TS[sk], "nom-1", slab, "nominal") + krows(TS[sk], "rstar-1", "", "$r^*$-gap")
    o += ["\\midrule", "\\multicolumn{8}{l}{\\textit{C. Difference, $r^*$-gap minus nominal (both with the FCI), baseline sample}}\\\\"]
    o += krows(TB, "diff rstar-1 minus nom-1", "", "")
    o += ["\\bottomrule", "\\end{tabular}"]
    open(os.path.join(HERE, "tables", "tab_tradeoff.tex"), "w").write("\n".join(o) + "\n")

# Figure 1 (headline): baseline (r*-gap 2-year and FCI) vs the standard approach (nominal 2-year alone), 6 lags; financial paths from tradeoff.py
if TF is not None and TB is not None:
    fig, ax = plt.subplots(2, 3, figsize=(11, 5.6))
    def band(a, g, col, lab, fill=True):
        if fill: a.fill_between(g.h, g.lo, g.hi, color=col, alpha=0.18, lw=0)
        a.plot(g.h, g.r, color=col, lw=1.6, ls="-" if fill else "--", label=lab)
    spec = (("rstar-1", "rstar", "1", "k", "$r^*$-gap two-year yield and FCI (baseline)", True), ("nom-0", "nom", "0", "tab:red", "Nominal two-year yield alone", False))
    for case, rate, fci, col, lab, fill in spec:
        g = TF[(TF.case == case) & (TF.lags == 6) & (TF["var"] == "pol")].sort_values("h"); band(ax[0, 0], g, col, lab, fill)
        if fci == "1": g = TF[(TF.case == case) & (TF.lags == 6) & (TF["var"] == "idx")].sort_values("h"); band(ax[0, 1], g, col, lab, fill)
        for a, var, mac in ((ax[0, 2], "u", "u,pi"), (ax[1, 0], "P", "u,pi"), (ax[1, 1], "ip", "u,pi,ip")):
            g = irf[(irf.macro == mac) & (irf["var"] == var) & (irf.rate == rate) & (irf.fci == fci) & (irf.lags == 6) & (irf.trend == TR) & (irf["sample"] == "")].sort_values("h")
            if len(g): band(a, g, col, lab, fill)
    # tradeoff path: price level against cumulative unemployment (pp-years), months 0-36
    for case, col, lab in (("rstar-1", "k", "$r^*$-gap, with FCI"), ("nom-1", "tab:blue", "Nominal, with FCI")):
        ru = irf[(irf.macro == "u,pi") & (irf["var"] == "u") & (irf.rate == case[:-2]) & (irf.fci == "1") & (irf.lags == 6) & (irf.trend == TR) & (irf["sample"] == "")].sort_values("h")
        rp = irf[(irf.macro == "u,pi") & (irf["var"] == "P") & (irf.rate == case[:-2]) & (irf.fci == "1") & (irf.lags == 6) & (irf.trend == TR) & (irf["sample"] == "")].sort_values("h")
        cu = np.cumsum(ru.r.values) / 12; ax[1, 2].plot(cu, rp.r.values, color=col, lw=1.6, label=lab)
        for hh in (12, 24, 36): ax[1, 2].plot(cu[hh], rp.r.values[hh], "o", ms=3.5, color=col)
    ax[1, 2].set_xlabel("Cumulative unemployment gap (pp-years)", fontsize=8); ax[1, 2].legend(fontsize=7, frameon=False, loc="lower left")
    titles = ("Two-year yield (pp)", "FCI (index units)", "Unemployment gap (pp)", "Core PCE price level (%)", "Industrial production (%)", "Price level against cumulative unemployment")
    for a, t in zip(ax.ravel(), titles):
        a.set_title(t, fontsize=9); a.axhline(0, color="0.4", lw=0.6); a.tick_params(labelsize=8)
    for a in list(ax[0]) + list(ax[1, :2]): a.set_xlabel("Months", fontsize=8)
    ax[0, 0].legend(fontsize=7, frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "figures", "fig0_headline.pdf")); plt.close(fig)

# Figure: nominal versus r*-gap two-year yield and FCI, with the unemployment gap, 1994-2026
_Z = pd.DataFrame({"y2n": _M.gs2, "y2r": gap2, "fn": _M.market_nominal, "fr": _M.market_rstar, "u": _M.u_gap}).loc["1994-01":"2026-09"]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.2), sharey=False); x = _Z.index.to_timestamp()
ax[0].plot(x, _Z.y2n, color="tab:red", lw=1.3, label="Nominal two-year yield"); ax[0].plot(x, _Z.y2r, color="k", lw=1.5, label="$r^*$-gap two-year yield")
ax[1].plot(x, _Z.fn, color="tab:red", lw=1.3, label="Nominal FCI"); ax[1].plot(x, _Z.fr, color="k", lw=1.5, label="$r^*$-gap FCI")
for a in ax:
    a.plot(x, _Z.u, color="0.55", lw=1.0, ls=":", label="Unemployment gap"); a.axhline(0, color="0.5", lw=0.6); a.legend(fontsize=7, frameon=False); a.tick_params(labelsize=8)
ax[0].set_ylabel("Percent / index units", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(HERE, "figures", "fig_long.pdf")); plt.close(fig)

# PAPER checks for FS-A40 (values stated in mp_transmission.tex, section 4.2 and 4.4)
PAPER_TRADE = {  # (file key, case, H): (min, max) over lags 3/6/12 of the multiplier, as stated in the text
    ("base", "rstar-1", 24): (-1.06, -0.77), ("base", "rstar-1", 36): (-0.84, -0.52),
    ("base", "nom-1", 24): (-0.49, -0.29), ("base", "nom-1", 36): (-0.36, -0.20),
    ("end2019", "rstar-1", 24): (-0.15, 0.03), ("end2019", "rstar-1", 36): (-0.16, 0.03),
    ("drop2021", "rstar-1", 24): (-1.13, -0.45)}
PAPER_FIN = {0: 0.46, 1: 0.97, 12: 0.61, 24: 0.28}     # r*-gap 2-year path (monthly average), r*-gap + FCI, 6 lags
if TB is not None:
    src = {"base": TB, **TS}
    for (fk, case, Hh), (a, b) in PAPER_TRADE.items():
        g = src[fk][(src[fk].case == case) & (src[fk].H == Hh)].kappa
        ok = abs(g.min() - a) < 0.006 and abs(g.max() - b) < 0.006
        print(f"PAPER multiplier {fk} {case} H{Hh}: text [{a}, {b}] data [{g.min():.2f}, {g.max():.2f}] {'OK' if ok else 'MISMATCH'}")
    allex = TB[(TB.case == "rstar-1") & (TB.H.isin([24, 36]))]
    print("PAPER r*-gap+FCI sets exclude zero and -0.15:", "OK" if ((allex.k_hi < -0.15) & allex.bounded).all() else "MISMATCH")
    nomin = TB[(TB.case == "nom-1") & (TB.H.isin([24, 36]))]
    print("PAPER nominal+FCI sets include zero:", "OK" if ((nomin.k_lo < 0) & (nomin.k_hi > 0)).all() else "MISMATCH")
    dd = TB[(TB.case == "diff rstar-1 minus nom-1") & (TB.H.isin([24, 36]))]
    print("PAPER difference interval includes zero:", "OK" if ((dd.k_lo < 0) & (dd.k_hi > 0)).all() else "MISMATCH")
if TF is not None:
    g = TF[(TF.case == "rstar-1") & (TF.lags == 6) & (TF["var"] == "pol")].set_index("h").r
    for h, v in PAPER_FIN.items(): print(f"PAPER 2-year path h{h}: text {v} data {g[h]:.2f} {'OK' if abs(g[h] - v) < 0.006 else 'MISMATCH'}")
