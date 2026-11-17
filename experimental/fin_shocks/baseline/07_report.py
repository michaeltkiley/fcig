"""Step 7. Tables and figures of the results document from results/ (12-lag main tables by section, 3/6/12-lag appendix tables by panel, the response
figures, the weights table and the trade-off table). Compile report/baseline_robustness.tex with pdflatex (twice).   python3 05_report.py"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cases as CS
from lib.paths import RESULTS, REPORT, OUT, DATA

R = {CS.case_id(c): pd.read_csv(RESULTS / f"{CS.case_id(c)}.csv") for c in CS.unique_cases()}
MAIN_LAGS = 12
B96 = dict(macro="u,pi", start="1996-01", end=None, t2020="out", trend="none")          # the two baselines (FS-A76): monthly equations from 1996 and from 1973, March-December 2020 dropped
B73 = {**B96, "start": "1973-01"}
STARTS = (("1996-01", ""), ("1973-01", "73"))
CORE_TESTS = [("base", "Baseline", "B", {}, 12), ("t2020", "2020 left in", "R1a", dict(form="rstar"), 12), ("kiley", "Kiley $r^*$", "R2a", {}, 12),
              ("spline", "Real yield and FCI, spline trend (no $r^*$)", "R2c", {}, 12), ("ebp", "Excess bond premium added", "R3a", {}, 12),
              ("cmpE", "FCI components, equities free", "R4c", dict(form="rstar", fci="cmpE"), 12), ("bs", "Bauer--Swanson surprise", "R5a", {}, 12),
              ("L3", "3 lags", "B", {}, 3), ("L6", "6 lags", "B", {}, 6), ("ip", "Industrial production added", "R7", dict(form="rstar"), 12), ("ff", "Federal funds rate in the daily block", "R8", dict(form="rstar"), 12)]
def core_row(pid, sel, sx, L):
    """The r*-gap (or the panel's own version) case with the FCI of a core robustness test, from 1996 (sx = '') or 1973 (sx = '73'); rows of its 12-month results at L lags."""
    p_ = CS.panel_by_id(pid + sx); c = next(c for c in p_["cases"] if c["fci"] != 0 and all(c.get(k) == v for k, v in sel.items()) and (sel or c["form"] in ("rstar", "kiley", "real")) and (pid != "B" or c["form"] == "rstar"))
    d = R[CS.case_id(c)]; return d[d.lags == L]
def blocks_of(p, lab=None):
    """Rows of a panel's table: one block per version when the panel has more than one (or the components), else one block."""
    forms = list(dict.fromkeys(c["form"] for c in p["cases"])); lab = lab or CS.SHORT.get(p["id"], p["title"])
    if len(forms) > 1 or p["id"].startswith("R4"): return [(f"{lab}: {CS.FORMS[f]}", [c for c in p["cases"] if c["form"] == f]) for f in forms]
    return [(lab, p["cases"])]
def _wt():
    w = pd.read_csv(RESULTS / "weights_test.csv"); return w[w.test == "all"] if "test" in w else w

# ---------------------------------------------------------------- tables
def num(x):
    s = f"{abs(x):.2f}"; return ("$-$" if x < 0 and s != "0.00" else "") + s
def stars(r, h):
    """Significance of a response: two stars if the 95% interval excludes zero (5 percent level), one if the 90% interval does (10 percent level)."""
    return "$^{**}$" if r[f"lo95_{h}"] * r[f"hi95_{h}"] > 0 else ("$^{*}$" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "")
def cell(r, h):
    star = stars(r, h)
    return num(r[f"r{h}"]) + star, f"[{num(r[f'lo{h}'])}, {num(r[f'hi{h}'])}]"
def get(c, L):
    d = R[CS.case_id(c)]; g = d[d.lags == L]; return g[g["var"] == "u"].iloc[0], g[g["var"] == "P"].iloc[0]
def two_lines(c, L):
    u, p = get(c, L); cells = [cell(r, h) for r in (u, p) for h in (12, 24, 36)]
    return int(u.nobs), [x[0] for x in cells], [x[1] for x in cells]

HEAD = (r"\begin{tabular}{llcrrrrrrr}\toprule" "\n" r" & & & & \multicolumn{3}{c}{Unemployment gap (pp)} & \multicolumn{3}{c}{Price level (\%)}\\ \cmidrule(lr){5-7}\cmidrule(lr){8-10}" "\n"
        r"Case & FCI & Lags & Obs & 12 m & 24 m & 36 m & 12 m & 24 m & 36 m\\ \midrule")
NOTE = r"Per +1 pp on the 2-year yield. $^{**}$ and $^{*}$: significant at the 5 and 10 percent levels (the 95\% and 90\% bootstrap intervals exclude zero); 90\% intervals in brackets. Obs = monthly observations in the equations."

FIT = r"\resizebox{\ifdim\width>\textwidth\textwidth\else\width\fi}{!}{%"
def longtab(title, label, spec, head_rows, body, note):
    """Tall appendix table: longtable with the header repeated on every page, notes below."""
    return "\n".join([r"\begingroup\scriptsize\setlength{\tabcolsep}{0.9pt}", rf"\begin{{longtable}}{{{spec}}}", rf"\caption{{{title}}}\label{{{label}}}\\", r"\toprule", head_rows, r"\midrule\endfirsthead",
                       r"\toprule", head_rows, r"\midrule\endhead", r"\bottomrule\endfoot", *body, r"\end{longtable}", rf"\begin{{flushleft}}\footnotesize\textit{{Notes:}} {note}\end{{flushleft}}", r"\endgroup"])

def table(title, label, groups, lags, note, place="H"):
    """groups: list of (row label, [cases]); one block per label; lags: tuple of lag lengths shown for each case."""
    body = []
    for gi, (lab, cs) in enumerate(groups):
        if gi: body.append(r"\addlinespace")
        for ci, c in enumerate(cs):
            for li, L in enumerate(lags):
                n, pts, ivs = two_lines(c, L)
                a = (lab if ci == 0 and li == 0 else ""); f = CS.FCI_LABEL[c["fci"]] if li == 0 else ""
                body += [f"{a} & {f} & {L} & {n} & " + " & ".join(pts) + r"\\", r" & & & & " + " & ".join(rf"{{\scriptsize {x}}}" for x in ivs) + r"\\"]
    if place == "p":
        head_rows = HEAD.split("\\toprule\n", 1)[1].replace(r"\midrule", "")
        return longtab(title, label, "llcrrrrrrr", head_rows.rstrip(), body, f"{note} {NOTE}")
    out = [r"\begin{table}[H]\centering\footnotesize\setlength{\tabcolsep}{2.2pt}", rf"\caption{{{title}}}\label{{{label}}}", FIT, HEAD, *body, r"\bottomrule\end{tabular}}", rf"\par\smallskip\parbox{{0.96\linewidth}}{{\scriptsize {note} {NOTE}}}", r"\end{table}"]
    return "\n".join(out)

for g, pids in CS.GROUPS.items():                                                  # 12 lags, by section
    blocks = sum([blocks_of(CS.panel_by_id(pid)) for pid in pids], [])
    (REPORT / f"tab_main_{g}.tex").write_text(table(CS.GROUP_TITLE[g] + " (12 lags)", f"tab:main{g}", blocks, (MAIN_LAGS,), CS.GROUP_NOTE[g]) + "\n")
for p in CS.PANELS:                                                                  # appendix: 3, 6, 12 lags, per panel
    (REPORT / f"tab_app_{p['id']}.tex").write_text(table(p["title"], f"tab:app{p['id']}", blocks_of(p, CS.FORMS[p["cases"][0]["form"]] if len(set(c["form"] for c in p["cases"])) == 1 and not p["id"].startswith("R4") else ""), (3, 6, 12), p["notes"], "p") + "\n")

# ---------------------------------------------------------------- monthly VAR benchmark tables
MON = {CS.monthly_id(m): pd.read_csv(RESULTS / f"{CS.monthly_id(m)}.csv") for m in CS.MONTHLY}
IDENT = {"P1": "Proxy VAR", "WE": "Window impact"}
def mcells(d, L, ident):
    g = d[(d.lags == L) & (d.ident == ident)]; pts, ivs = [], []
    for v in ("u", "P"):
        for h in (12, 24, 36):
            r = g[(g["var"] == v) & (g.h == h)].iloc[0]
            if r.unbounded: pts.append(num(r.r)); ivs.append("unbounded")
            else: pts.append(num(r.r) + ("$^{*}$" if r.lo * r.hi > 0 else "")); ivs.append(f"[{num(r.lo)}, {num(r.hi)}]")
    return int(g.nobs.iloc[0]), pts, ivs
def monthly_table(title, label, lags, note, start, place="H"):
    spec = "lllcrrrrrrr"
    head = (r" & & & & & \multicolumn{3}{c}{Unemployment gap (pp)} & \multicolumn{3}{c}{Price level (\%)}\\ \cmidrule(lr){6-8}\cmidrule(lr){9-11}" "\n"
            r"2-year & FCI & Identification & Lags & Obs & 12 m & 24 m & 36 m & 12 m & 24 m & 36 m\\")
    body = []
    for si, step in enumerate(("nom", "real", "rstar")):
        if si: body.append(r"\addlinespace")
        for fci in (0, step):
            d = MON[CS.monthly_id(dict(step=step, fci=fci, start=start))]
            for ident in ("P1", "WE"):
                for L in lags:
                    n, pts, ivs = mcells(d, L, ident)
                    a = CS.FORMS[step] if (fci == 0 and ident == "P1" and L == lags[0]) else ""; f = CS.FCI_LABEL[fci] if (ident == "P1" and L == lags[0]) else ""
                    body += [f"{a} & {f} & {IDENT[ident] if L == lags[0] else ''} & {L} & {n} & " + " & ".join(pts) + r"\\", r" & & & & & " + " & ".join(rf"{{\tiny {x}}}" for x in ivs) + r"\\"]
    if place == "p": return longtab(title, label, spec, head, body, note)
    out = [r"\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{2pt}", rf"\caption{{{title}}}\label{{{label}}}", FIT, rf"\begin{{tabular}}{{{spec}}}\toprule", head, r"\midrule", *body, r"\bottomrule\end{tabular}}", rf"\par\smallskip\parbox{{0.96\linewidth}}{{\scriptsize {note}}}", r"\end{table}"]
    return "\n".join(out)
MNOTE = (r"Monthly VAR in the unemployment gap, core PCE inflation, the monthly average of the 2-year yield and, when included, of the FCI (same version), to September 2026, no trend, March--December 2020 dropped. "
         r"Proxy VAR: Nakamura--Steinsson surprise as instrument; sets are exact 90\% Anderson--Rubin sets, ``unbounded'' when the instrument cannot reject large effects. "
         r"Window impact: impact vector taken from the daily model (the month-average response to a window surprise); 90\% bootstrap intervals. Unit in both: +1 pp on the 2-year yield in the announcement window.")
for st, sx in STARTS:
    yr = st[:4]
    (REPORT / f"tab_main_monthly{sx}.tex").write_text(monthly_table(f"Monthly VAR benchmark from {yr} (12 lags)", f"tab:mainmonthly{sx}", (12,), MNOTE, st) + "\n")
    (REPORT / f"tab_app_monthly{sx}.tex").write_text(monthly_table(f"Monthly VAR benchmark from {yr} (3, 6 and 12 lags)", f"tab:appmonthly{sx}", (3, 6, 12), MNOTE, st, "p") + "\n")
frows = []
for st, sx in STARTS:
  frows.append(rf"\multicolumn{{7}}{{l}}{{\textit{{Monthly equations from {st[:4]}}}}}\\")
  for step in ("nom", "real", "rstar"):
    for fci in (0, step):
        d = MON[CS.monthly_id(dict(step=step, fci=fci, start=st))]; g = d[(d.ident == "P1") & (d["var"] == "u") & (d.h == 12)].set_index("lags")
        frows.append(f"{CS.FORMS[step] if fci == 0 else ''} & {CS.FCI_LABEL[fci]} & " + " & ".join(f"{g.F[L]:.1f}" for L in (3, 6, 12)) + " & " + (f"{num(g.impact_fci[12])} & {num(g.win_fci[12] / g.win_pol[12])}" if fci else " & ") + r"\\")
(REPORT / "tab_monthly_F.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Monthly proxy VAR: first-stage strength and impact on the FCI}\label{tab:monthlyF}",
    r"\begin{tabular}{llrrrrr}\toprule 2-year & FCI & $F$ (3 lags) & $F$ (6) & $F$ (12) & Proxy impact on FCI & Model impact on FCI\\ \midrule", *frows, r"\bottomrule\end{tabular}",
    r"\par\smallskip\parbox{0.92\linewidth}{\scriptsize $F$: robust first-stage statistic of the policy-variable residual on the instrument (instrument months only, 1996--2026; monthly equations from 1996 or from 1973). Impact on FCI: response of the month's average FCI per +1 pp on the month's average 2-year yield, estimated from monthly residuals (proxy VAR, 12 lags) and implied by the daily model.}", r"\end{table}"]) + "\n")

# ---------------------------------------------------------------- how noisy is the monthly proxy VAR if the model is true?
SIM = pd.read_csv(RESULTS / "proxy_sim_summary.csv")
def sim_table():
    lab = {("proxy_fci", "F"): "First-stage $F$", ("proxy_fci", "u12"): "Unemployment gap, 12 m", ("proxy_fci", "P24"): "Price level, 24 m", ("proxy_nofci", "u12"): "Unemployment gap, 12 m", ("window", "u12"): "Unemployment gap, 12 m"}
    out = [r"\begin{table}[H]\centering\small", r"\caption{A monthly proxy VAR when the r*-gap model is the true process}\label{tab:proxysim}",
           r"\begin{tabular}{lrrrr}\toprule Estimate & Data & True & Simulated median & 5th--95th percentile\\ \midrule"]
    for system, head in (("proxy_fci", "A. Proxy VAR with the FCI"), ("proxy_nofci", "B. Proxy VAR without the FCI"), ("window", "C. Monthly VAR with the window impact and the FCI")):
        out.append(rf"\multicolumn{{5}}{{l}}{{\textit{{{head}}}}}\\")
        for _, r in SIM[SIM.system == system].iterrows():
            f = "{:.1f}" if r.quantity == "F" else "{:.2f}"; sg = lambda x: ("$-$" if x < 0 and f.format(abs(x)) != "0.00" else "") + f.format(abs(x))
            out.append(f"\\quad {lab[(system, r.quantity)]} & {sg(r.data)} & {sg(r.truth) if pd.notna(r.truth) else ''} & {sg(r.sim_median)} & [{sg(r.sim_p05)}, {sg(r.sim_p95)}]\\\\")
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize 1,000 samples of 369 months generated by the estimated r*-gap model with the FCI (12 lags), with the data's calendar and announcement days; policy reaches unemployment and prices only through the 2-year yield and the FCI. Data: the 1996 sample, 12 lags, r*-gap measures, March--December 2020 dropped; monthly averages in the monthly VAR. True: the model's response per +1 pp on the 2-year yield in the announcement window (the unit of every panel). Simulated: median and 5th--95th percentiles of the estimates.}", r"\end{table}"]
    return "\n".join(out)
(REPORT / "tab_proxy_sim.tex").write_text(sim_table() + "\n")

def monthly_compact():
    """Table in Section 3.5: r*-gap yield and FCI; proxy VAR, window-impact VAR and the main model; unemployment at 12 and 24 months, price level at 12 and 24 months."""
    m = MON[CS.monthly_id(dict(step="rstar", fci="rstar", start="1996-01"))]; m = m[m.lags == 12]
    def mrow(ident, lab):
        cs_ = []
        for v in ("u", "P"):
            for h in (12, 24):
                r = m[(m.ident == ident) & (m["var"] == v) & (m.h == h)].iloc[0]; cs_.append((num(r.r) + ("$^{*}$" if r.lo * r.hi > 0 else ""), f"[{num(r.lo)}, {num(r.hi)}]"))
        return [f"{lab} & " + " & ".join(c[0] for c in cs_) + r"\\", " & " + " & ".join(rf"{{\scriptsize {c[1]}}}" for c in cs_) + r"\\"]
    dd = R[CS.case_id(dict(form="rstar", fci="rstar", **B96))]; dd = dd[dd.lags == MAIN_LAGS]; cs_ = []
    for v in ("u", "P"):
        for h in (12, 24):
            r = dd[dd["var"] == v].iloc[0]; cs_.append((num(r[f"r{h}"]) + ("$^{*}$" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else ""), f"[{num(r[f'lo{h}'])}, {num(r[f'hi{h}'])}]"))
    main = [r"Main model (daily block) & " + " & ".join(c[0] for c in cs_) + r"\\", " & " + " & ".join(rf"{{\scriptsize {c[1]}}}" for c in cs_) + r"\\"]
    out = [r"\begin{table}[H]\centering\small", r"\caption{Monthly VARs with the FCI and the main model ($r^*$-gap two-year yield and FCI; 12 lags)}\label{tab:monthlycompact}",
           r"\begin{tabular}{lrrrr}\toprule & \multicolumn{2}{c}{Unemployment gap (pp)} & \multicolumn{2}{c}{Price level (\%)}\\ \cmidrule(lr){2-3}\cmidrule(lr){4-5} & 12 m & 24 m & 12 m & 24 m\\ \midrule",
           *mrow("P1", "Proxy VAR"), *mrow("WE", "Window-impact VAR"), *main, r"\bottomrule\end{tabular}",
           r"\par\smallskip\parbox{0.8\linewidth}{\scriptsize Per +1 pp on the two-year yield. $^{*}$: the 90\% interval excludes zero; intervals in brackets (Anderson--Rubin sets for the proxy VAR; bootstrap for the others). Monthly VARs use monthly averages; unit +1 pp on the two-year yield in the announcement window.}", r"\end{table}"]
    (REPORT / "tab_monthly_compact.tex").write_text("\n".join(out) + "\n")
monthly_compact()


# ---------------------------------------------------------------- numbers quoted in the text of the note (macros)
def write_numbers():
    """report/numbers.tex: one macro per number quoted in the text, so the prose cannot drift from the tables.  \bl{step:fci:var:h} = estimate, \blabs{..} = absolute value,
    \blsig{..} = 'significant' / 'not significant' (90% interval), \bllo{..}, \blhi{..}; step in nom/real/rstar, fci in no/yes, var in u/P (unemployment gap pp / price level %), h in 12/24/36 months.
    Baseline panel, 12 lags."""
    L = [r"% generated by baseline/07_report.py: do not edit", r"\newcommand{\bl}[1]{\csname bl:#1\endcsname}", r"\newcommand{\blabs}[1]{\csname blabs:#1\endcsname}",
         r"\newcommand{\blsig}[1]{\csname blsig:#1\endcsname}", r"\newcommand{\bllo}[1]{\csname bllo:#1\endcsname}", r"\newcommand{\blhi}[1]{\csname blhi:#1\endcsname}"]
    d = lambda name, val: L.append(r"\expandafter\gdef\csname " + name + r"\endcsname{" + val + "}")
    for (st, sx), f in [(a, b) for a in STARTS for b in ("nom", "real", "rstar")]:
        for fci, fk in ((0, "no"), (f, "yes")):
            dd = R[CS.case_id(dict(form=f, fci=fci, **{**B96, "start": st}))]; g = dd[dd.lags == MAIN_LAGS]
            for v in ("u", "P"):
                r = g[g["var"] == v].iloc[0]
                for h in (12, 24, 36):
                    k = ("b73:" if sx else "") + f"{f}:{fk}:{v}:{h}"; d("bl:" + k, num(r[f"r{h}"])); d("blabs:" + k, f"{abs(r[f'r{h}']):.2f}"); d("blsig:" + k, "significant" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "not significant")
                    d("bllo:" + k, num(r[f"lo{h}"])); d("blhi:" + k, num(r[f"hi{h}"]))
    n = R[CS.case_id(dict(form="rstar", fci="rstar", **B96))]; d("bl:nobs", str(int(n[n.lags == MAIN_LAGS].nobs.iloc[0])))
    n = R[CS.case_id(dict(form="rstar", fci="rstar", **B73))]; d("bl:b73:nobs", str(int(n[n.lags == MAIN_LAGS].nobs.iloc[0])))
    BASE = B96
    pth = lambda f, fci: (lambda d: d[d.lags == MAIN_LAGS])(pd.read_csv(RESULTS / f"{CS.case_id(dict(form=f, fci=fci, **BASE))}_paths.csv"))
    u = pth("nom", 0); u = u[(u.kind == "macro") & (u["var"] == "u")]; i = u.r.idxmin(); d("bl:path:nom:no:u:min", num(u.r[i])); d("bl:path:nom:no:u:minh", str(int(u.h[i])))
    u = pth("rstar", "rstar"); u = u[(u.kind == "macro") & (u["var"] == "u")]; i = u.r.idxmax(); d("bl:path:rstar:yes:u:max", num(u.r[i])); d("bl:path:rstar:yes:u:maxh", str(int(u.h[i])))
    LS = pd.read_csv(RESULTS / "lit_style.csv").query("lags == 12"); LSI = pd.read_csv(RESULTS / "lit_style_info.csv").query("lags == 12").set_index("case")
    for key, case in (("c2y96", "chol_2y_1996"), ("c2y84", "chol_2y_1984"), ("cffr", "chol_ffr_1984_2007"), ("c2ycom", "chol_2y_1996_com"), ("cffrcom", "chol_ffr_1984_2007_com"), ("prox", "proxy_2y_1996"), ("c2y73", "chol_2y_1973"), ("prox73", "proxy_2y_1973")):
        for v in ("u", "P"):
            for h in (0, 12, 24, 36):
                r = LS[(LS.case == case) & (LS["var"] == v) & (LS.h == h)].iloc[0]; k = f"st:{key}:{v}:{h}"
                d("bl:" + k, num(r.point)); d("blabs:" + k, f"{abs(r.point):.2f}"); d("bllo:" + k, num(r.lo)); d("blhi:" + k, num(r.hi)); d("blsig:" + k, "significant" if r.lo * r.hi > 0 else "not significant")
        d("bl:st:" + key + ":nobs", str(int(LSI.nobs[case])))
    d("bl:st:prox:F", f"{LSI.F['proxy_2y_1996']:.1f}"); d("bl:st:prox73:F", f"{LSI.F['proxy_2y_1973']:.1f}")
    # monthly VARs on monthly averages (12 lags), from 1996 (mo:) and from 1973 (mo73:)
    for (st, sx), f in [(a, b) for a in STARTS for b in ("nom", "real", "rstar")]:
        for fci, fk in ((0, "no"), (f, "yes")):
            m = MON[CS.monthly_id(dict(step=f, fci=fci, start=st))]; m = m[m.lags == MAIN_LAGS]; d(f"bl:mo{sx}:{f}:{fk}:F", f"{m.F.iloc[0]:.1f}")
            if fci: d(f"bl:mo{sx}:{f}:{fk}:impf", num(m.impact_fci.iloc[0])); d(f"bl:mo{sx}:{f}:{fk}:modf", num(m.win_fci.iloc[0] / m.win_pol.iloc[0]))
            d(f"bl:mo{sx}:win", f"{m.win_pol.iloc[0]:.2f}")
            for ident in ("P1", "WE"):
                for v in ("u", "P"):
                    for h in (12, 24, 36):
                        r = m[(m.ident == ident) & (m["var"] == v) & (m.h == h)].iloc[0]; k = f"mo{sx}:{f}:{fk}:{ident}:{v}:{h}"
                        d("bl:" + k, num(r.r)); d("blabs:" + k, f"{abs(r.r):.2f}"); d("bllo:" + k, "$-\\infty$" if np.isinf(r.lo) else num(r.lo)); d("blhi:" + k, "$+\\infty$" if np.isinf(r.hi) else num(r.hi))
                        d("blsig:" + k, "unbounded" if r.unbounded else ("significant" if r.lo * r.hi > 0 else "not significant"))
    # simulation (r*-gap model as the true process)
    for _, r in SIM.iterrows():
        k = f"sim:{r.system}:{r.quantity}"; f = "{:.1f}" if r.quantity == "F" else "{:.2f}"; sg = lambda x: ("$-$" if x < 0 and f.format(abs(x)) != "0.00" else "") + f.format(abs(x))
        d("bl:" + k + ":data", sg(r.data)); d("bl:" + k + ":med", sg(r.sim_median)); d("bl:" + k + ":lo", sg(r.sim_p05)); d("bl:" + k + ":hi", sg(r.sim_p95)); d("bl:" + k + ":share", f"{100 * r.share_le_data:.0f}")
        if pd.notna(r.truth): d("bl:" + k + ":truth", sg(r.truth))
    # trade-off (Phillips multiplier)
    TT = pd.read_csv(RESULTS / "tradeoff.csv"); TT["fci"] = TT.fci.astype(str); TD = pd.read_csv(RESULTS / "tradeoff_diff.csv")
    for (st, sx), f in [(a, b) for a in STARTS for b in ("nom", "real", "rstar")]:
        for fci, fk in ((0, "no"), (f, "yes")):
            t = TT[(TT.form == f) & (TT.fci == str(fci)) & (TT.macro == "u,pi") & (TT.start == st) & TT.end.isna() & (TT.t2020 == "out") & (TT.trend == "none") & (TT.lags == MAIN_LAGS) & (TT["shock"] == "ns") & (TT.get("ext", pd.Series("", index=TT.index)).fillna("") == "")]
            for H in (12, 24, 36):
                r = t[t.H == H].iloc[0]; k = f"tr{sx}:{f}:{fk}:{H}"
                d("bl:" + k, num(r.kappa)); d("blabs:" + k, f"{abs(r.kappa):.2f}"); d("bl:" + k + ":sac", f"{abs(1 / r.kappa):.1f}")
                d("bllo:" + k, "$-\\infty$" if np.isinf(r.k_lo) else num(r.k_lo)); d("blhi:" + k, "$+\\infty$" if np.isinf(r.k_hi) else num(r.k_hi))
                d("blsig:" + k, "bounded away from zero" if (not np.isinf(r.k_lo) and not np.isinf(r.k_hi) and r.k_lo * r.k_hi > 0) or (np.isinf(r.k_lo) != np.isinf(r.k_hi) and (r.k_hi < 0 if np.isinf(r.k_lo) else r.k_lo > 0)) else "includes zero")
    # robustness panels (12 lags): rb:<panel>[:<form>]:<no|yes|fci>:<u|P>:<h>; panel ids as in cases.py (<id> from 1996, <id>73 from 1973); the form is added when a panel has several
    for p_ in CS.PANELS:
        if p_["id"] in ("B", "B73"): continue
        multi = len(set(c["form"] for c in p_["cases"])) > 1 or p_["id"].startswith("R4")
        for cs in p_["cases"]:
            fk = "no" if cs["fci"] == 0 else ("yes" if cs["fci"] in (cs["form"], "baa") else str(cs["fci"])); form_tag = f":{cs['form']}" if multi else ""
            g_ = R[CS.case_id(cs)]; g_ = g_[g_.lags == MAIN_LAGS]
            for v in ("u", "P"):
                r = g_[g_["var"] == v].iloc[0]
                for h in (12, 24, 36):
                    k = f"rb:{p_['id']}{form_tag}:{fk}:{v}:{h}"; d("bl:" + k, num(r[f"r{h}"])); d("blabs:" + k, f"{abs(r[f'r{h}']):.2f}"); d("blsig:" + k, "significant" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "not significant")
                    d("bllo:" + k, num(r[f"lo{h}"])); d("blhi:" + k, num(r[f"hi{h}"]))
    WT = _wt()
    for _, r in WT[(WT.lags == MAIN_LAGS) & (WT.start == "1996-01")].iterrows(): e_ = r["eq"]; d(f"bl:wt:{r.step}:{e_}:p", f"{r.p_boot:.3f}"); d(f"bl:wt:{r.step}:{e_}:W", f"{r.wald:.1f}"); d(f"bl:wt:{r.step}:{e_}:q", str(int(r.restrictions)))
    for _, r in WT[(WT.lags == MAIN_LAGS) & (WT.start == "1973-01")].iterrows(): d(f"bl:wt73:{r.step}:{r['eq']}:p", f"{r.p_boot:.3f}")
    w73 = WT[(WT.lags == MAIN_LAGS) & (WT.start == "1973-01")].p_boot; d("bl:wt73:min", f"{w73.min():.2f}"); d("bl:wt73:max", f"{w73.max():.2f}")
    from lib import daily as DD
    for nm in ("bs", "jk"): DD.use_surprise(nm); d(f"bl:ev:{nm}", str(len(DD.event_index())))
    DD.use_surprise("ns")
    from lib.daily import window_impact, event_index, EV
    from lib import monthly as MO
    from lib.model import MAC
    d("bl:bF", f"{window_impact(event_index())[1]:.2f}")
    for f in ("nom", "real", "rstar"):                                  # FCI innovation per unit of 2-year-yield innovation in ordinary months (monthly VAR residuals, 12 lags, 1996+, monthly averages, 2020 dropped)
        X, Y, P_ = MO.design(MO.data(f, f), 12, "1996-01", MO.END); k_ = ~P_.isin(MO.C2020); X, Y = X[k_], Y[k_]; r = Y - X @ np.linalg.lstsq(X, Y, rcond=None)[0]
        d(f"bl:ord:{f}", f"{np.cov(r[:, 3], r[:, 2])[0, 1] / np.var(r[:, 2], ddof=1):.2f}")
    ie = event_index(); s_ = EV.ns.values[ie]                           # share of each window move explained by the policy-news surprise (R-squared)
    for col, k in (("UST2Y", "y2"), ("UST10Y", "y10"), ("SP500", "sp"), ("DXY", "usd"), ("idx_win", "fci")): d(f"bl:r2:{k}", f"{100 * np.corrcoef(s_, EV[col].values[ie])[0, 1] ** 2:.0f}")
    (REPORT / "numbers.tex").write_text("\n".join(L) + "\n")
write_numbers()

def paths(c, L=MAIN_LAGS):
    d = pd.read_csv(RESULTS / f"{CS.case_id(c)}_paths.csv"); return d[d.lags == L]
def check_claims():
    """The qualitative claims of the note's Sections 3.1-3.3 (integration of 17 Nov 2026: two baselines, 2020 dropped, monthly averages); raises an error if any stops being true."""
    def g(f, fk, v, h, st="1996-01"):
        dd = R[CS.case_id(dict(form=f, fci=0 if fk == "no" else f, **{**B96, "start": st}))]; r = dd[(dd.lags == MAIN_LAGS) & (dd["var"] == v)].iloc[0]
        return r[f"r{h}"], r[f"lo{h}"] * r[f"hi{h}"] > 0, r[f"lo95_{h}"] * r[f"hi95_{h}"] > 0
    est = lambda *k, **kw: g(*k, **kw)[0]; sig = lambda *k, **kw: g(*k, **kw)[1]; sig5 = lambda *k, **kw: g(*k, **kw)[2]; S = ("nom", "real", "rstar"); bad = []
    chk = lambda name, ok: None if ok else bad.append(name); H3 = (12, 24, 36); T73 = "1973-01"
    # baseline from 1996
    for f in ("nom", "real"): chk(f"1996 {f}: yield alone, unemployment falls significantly (5%) at 12 and 24 m; price level not significant at 24 m", all(est(f, "no", "u", h) < 0 and sig5(f, "no", "u", h) for h in (12, 24)) and not sig(f, "no", "P", 24))
    chk("1996 r*-gap yield alone: unemployment negative and not significant at 12, 24, 36 m; price level significant at 12 m only", all(est("rstar", "no", "u", h) < 0 and not sig("rstar", "no", "u", h) for h in H3) and sig("rstar", "no", "P", 12) and not sig("rstar", "no", "P", 24) and not sig("rstar", "no", "P", 36))
    for f in S: chk(f"1996 {f} with FCI: unemployment positive and price level negative at 12, 24, 36 m", all(est(f, "yes", "u", h) > 0 and est(f, "yes", "P", h) < 0 for h in H3))
    chk("1996 r*-gap with FCI: unemployment significant at 5% at 12 and 24 m, not at 36 m; price level at 5% at 12, 24, 36 m", sig5("rstar", "yes", "u", 12) and sig5("rstar", "yes", "u", 24) and not sig("rstar", "yes", "u", 36) and all(sig5("rstar", "yes", "P", h) for h in H3))
    chk("1996 real with FCI: unemployment significant at 10% at 12 and 24 m; price level at 10% at 12, 24, 36 m", sig("real", "yes", "u", 12) and sig("real", "yes", "u", 24) and all(sig("real", "yes", "P", h) for h in H3))
    chk("1996 nominal with FCI: no response significant", not any(sig("nom", "yes", v, h) for v in ("u", "P") for h in H3))
    chk("1996: r*-gap with FCI has the largest price fall and unemployment rise at 24 m", est("rstar", "yes", "P", 24) < min(est("nom", "yes", "P", 24), est("real", "yes", "P", 24)) and est("rstar", "yes", "u", 24) > max(est("nom", "yes", "u", 24), est("real", "yes", "u", 24)))
    # baseline from 1973
    chk("1973 r*-gap yield alone: unemployment rises (significant at 12 m), price level falls significantly at 12, 24, 36 m", est("rstar", "no", "u", 12, st=T73) > 0 and sig("rstar", "no", "u", 12, st=T73) and all(est("rstar", "no", "P", h, st=T73) < 0 and sig5("rstar", "no", "P", h, st=T73) for h in H3))
    chk("1973: every version, the FCI raises the 12 m unemployment response and deepens the 24 m price fall", all(est(f, "yes", "u", 12, st=T73) > est(f, "no", "u", 12, st=T73) and est(f, "yes", "P", 24, st=T73) < est(f, "no", "P", 24, st=T73) for f in S))
    chk("1973 r*-gap with FCI: unemployment significant at 5% at 12 m, not at 24 or 36 m; price level at 5% at 12, 24, 36 m", sig5("rstar", "yes", "u", 12, st=T73) and not sig("rstar", "yes", "u", 24, st=T73) and not sig("rstar", "yes", "u", 36, st=T73) and all(sig5("rstar", "yes", "P", h, st=T73) for h in H3))
    chk("1973: with FCI no significant fall in unemployment and no significant rise in prices in any version", not any((est(f, "yes", "u", h, st=T73) < 0 and sig(f, "yes", "u", h, st=T73)) or (est(f, "yes", "P", h, st=T73) > 0 and sig(f, "yes", "P", h, st=T73)) for f in S for h in H3))
    # standard methods (monthly averages)
    LS = pd.read_csv(RESULTS / "lit_style.csv").query("lags == 12"); ls = lambda c, v, h: LS[(LS.case == c) & (LS["var"] == v) & (LS.h == h)].iloc[0]; lsig = lambda c, v, h: ls(c, v, h).lo * ls(c, v, h).hi > 0
    for c in ("chol_2y_1996", "proxy_2y_1996"):
        chk(f"{c}: unemployment falls significantly at 12 and 24 m; price level not significant at 12, 24, 36 m", all(ls(c, "u", h).point < 0 and lsig(c, "u", h) for h in (12, 24)) and not any(lsig(c, "P", h) for h in H3))
    chk("chol_2y_1984: unemployment negative at 12, 24 m, not significant; price level not significant", all(ls("chol_2y_1984", "u", h).point < 0 and not lsig("chol_2y_1984", "u", h) for h in (12, 24)) and not any(lsig("chol_2y_1984", "P", h) for h in H3))
    chk("1973 standard methods: Cholesky unemployment positive, price level negative, none significant; proxy VAR not significant (first-stage F below 5)", all(ls("chol_2y_1973", "u", h).point > 0 and ls("chol_2y_1973", "P", h).point < 0 for h in H3) and not any(lsig(c, v, h) for c in ("chol_2y_1973", "proxy_2y_1973") for v in ("u", "P") for h in H3) and pd.read_csv(RESULTS / "lit_style_info.csv").query("lags == 12").set_index("case").F["proxy_2y_1973"] < 5)
    chk("chol_ffr_1984_2007: unemployment falls significantly at 12 m only", ls("chol_ffr_1984_2007", "u", 12).point < 0 and lsig("chol_ffr_1984_2007", "u", 12) and not lsig("chol_ffr_1984_2007", "u", 24))
    chk("commodity-price control: 2-year Cholesky unemployment fall at 12 m still significant; funds-rate version negative at 12 m", ls("chol_2y_1996_com", "u", 12).point < 0 and lsig("chol_2y_1996_com", "u", 12) and ls("chol_ffr_1984_2007_com", "u", 12).point < 0)
    # monthly VAR benchmarks (monthly averages)
    mo = lambda f, fk, i, v, h, st="1996-01": (lambda m: m[(m.lags == MAIN_LAGS) & (m.ident == i) & (m["var"] == v) & (m.h == h)].iloc[0])(MON[CS.monthly_id(dict(step=f, fci=0 if fk == "no" else f, start=st))])
    msig = lambda r: (not r.unbounded) and r.lo * r.hi > 0
    chk("monthly proxy VAR with the FCI: first-stage F below 5 from both starts", mo("rstar", "yes", "P1", "u", 12).F < 5 and mo("rstar", "yes", "P1", "u", 12, T73).F < 5)
    chk("monthly window-impact VAR r*-gap with FCI: unemployment up and price level down at 12-36 m from both starts; price level significant at 24 m in both", all(mo("rstar", "yes", "WE", "u", h, st).r > 0 and mo("rstar", "yes", "WE", "P", h, st).r < 0 for h in H3 for st in ("1996-01", T73)) and all(msig(mo("rstar", "yes", "WE", "P", 24, st)) for st in ("1996-01", T73)))
    chk("monthly window-impact VAR from 1996: about half the model's response (0.35 to 0.7 of it; r*-gap with FCI, u 12 m and P 24 m)", all(0.35 < mo("rstar", "yes", "WE", v, h).r / est("rstar", "yes", v, h) < 0.7 for v, h in (("u", 12), ("P", 24))))
    chk("monthly window-impact VAR: responses smaller than the model's (r*-gap with FCI, u 12 m and P 24 m, both starts)", all(abs(mo("rstar", "yes", "WE", v, h, st).r) < abs(est("rstar", "yes", v, h, st=st)) for v, h in (("u", 12), ("P", 24)) for st in ("1996-01", T73)))
    chk("monthly proxy VAR nominal without FCI from 1996: unemployment falls significantly at 12 m", mo("nom", "no", "P1", "u", 12).r < 0 and msig(mo("nom", "no", "P1", "u", 12)))
    # simulation with the model as the true process
    sm = lambda s, q: SIM[(SIM.system == s) & (SIM.quantity == q)].iloc[0]
    chk("simulation: proxy VAR with FCI is noisy (90% range of u at 12 m wider than 1 pp and covering zero)", sm("proxy_fci", "u12").sim_p95 - sm("proxy_fci", "u12").sim_p05 > 1 and sm("proxy_fci", "u12").sim_p05 < 0 < sm("proxy_fci", "u12").sim_p95)
    chk("simulation: window-impact range narrower than the proxy-with-FCI range (u, 12 m)", sm("window", "u12").sim_p95 - sm("window", "u12").sim_p05 < sm("proxy_fci", "u12").sim_p95 - sm("proxy_fci", "u12").sim_p05)
    chk("simulation: data values inside the simulated 5-95 ranges (proxy with FCI: F and u12; proxy without FCI: u12; window u12)", all(sm(a, b).sim_p05 <= sm(a, b).data <= sm(a, b).sim_p95 for a, b in (("proxy_fci", "F"), ("proxy_fci", "u12"), ("proxy_nofci", "u12"), ("window", "u12"))))
    chk("simulation: the monthly window-impact VAR is biased toward zero (median between a third and two thirds of the truth; temporal aggregation)", 0.33 * sm("window", "u12").truth < sm("window", "u12").sim_median < 0.67 * sm("window", "u12").truth)
    chk("simulation: proxy VAR with the FCI centred below the truth", sm("proxy_fci", "u12").sim_median < sm("proxy_fci", "u12").truth)
    chk("simulation: proxy VAR without FCI biased toward zero (median below half the truth)", sm("proxy_nofci", "u12").sim_median < 0.5 * sm("proxy_nofci", "u12").truth)
    WT = _wt(); chk("weights test results present for both starts", set(WT.start) >= {"1996-01", T73})
    allr = [c for p_ in CS.PANELS for c in p_["cases"] if c["fci"] != 0 and c["form"] in ("rstar", "kiley", "real") and (c["form"] == "rstar" or p_["id"].startswith(("R2", "B")))]
    chk("introduction: with the FCI, every robustness case (all panels, both starts) has unemployment up and the price level down after 12 months", all((lambda d: d[d["var"] == "u"].iloc[0].r12 > 0 and d[d["var"] == "P"].iloc[0].r12 < 0)(R[CS.case_id(c)].query("lags == 12")) for c in allr))
    pth_u = lambda f, fc: (lambda d: d[(d.kind == "macro") & (d["var"] == "u")].sort_values("h").r.values)(paths(dict(form=f, fci=fc, **B96)))
    chk("Section 3.2: from 1996 the FCI moves the unemployment path above the yield-alone path from month 1 through 36 in every version", all((pth_u(f, f)[1:] > pth_u(f, 0)[1:]).all() for f in S))
    if __import__("os").environ.get("CLAIMS_REPORT") and bad: print("FAILED CLAIMS:", *bad, sep="\n  ")
    else: assert not bad, "claims in the note no longer hold: " + "; ".join(bad)
check_claims()

# test of the proportional-weights restriction: tab_weights_test.tex and tab_wt_full.tex are written by 07b_report_extensions.py

# ---------------------------------------------------------------- weights table (window responses)
w = pd.read_csv(OUT / "market_weights.csv", index_col=0)
names = {"y10": "10-year Treasury yield (pp)", "equities": "Equity valuation, 100 ln CAPE (\\%)", "dollar": "Real broad dollar, 100 ln (\\%)"}
sg = lambda x, f: (("$-$" if x < 0 else "$+$") + f.format(abs(x)))
rows = [f"{names[k]} & {sg(w.response[k], '{:.2f}')} ({w.se[k]:.2f}) & {sg(w.weight[k], '{:.3f}')} & {w.weight[k] * w.response[k]:.2f}\\\\" for k in w.index]
(REPORT / "tab_weights.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Market-index weights from policy news}\label{tab:weights}",
    r"\begin{tabular}{lrrr}\toprule Component & Response to policy news & Weight & Share of a policy move\\ \midrule", *rows, r"\bottomrule\end{tabular}",
    r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize Response of each 30-minute announcement-window change to the policy-news factor (scaled so the 2-year yield moves 1 pp), with robust standard errors; weights from the one-factor GLS of Kiley (2026); share = weight $\times$ response (the three shares sum to 1).}", r"\end{table}"]) + "\n")

# ---------------------------------------------------------------- trade-off table
try:
    T = pd.read_csv(RESULTS / "tradeoff.csv"); T["fci"] = T.fci.astype(str); D = pd.read_csv(RESULTS / "tradeoff_diff.csv")
    def kset(r):
        if np.isinf(r.k_lo) or np.isinf(r.k_hi):
            s68 = "undefined" if (np.isinf(r.k68_lo) or np.isinf(r.k68_hi)) else f"[{num(r.k68_lo)}, {num(r.k68_hi)}]"
            return f"{num(r.kappa)} (undefined; 68\\%: {s68})"
        return f"{num(r.kappa)} [{num(r.k_lo)}, {num(r.k_hi)}]"
    lines = []
    def trow(lab, c):
        t = T[(T.form == c["form"]) & (T.fci == str(c["fci"])) & (T.macro == c["macro"]) & (T.start == c["start"]) & (T.end.fillna("").astype(str).str.replace(".0", "", regex=False) == (str(c["end"]) if c["end"] else ""))
              & (T.t2020 == c["t2020"]) & (T.trend == c["trend"]) & (T.lags == MAIN_LAGS) & (T["shock"] == c.get("shock", "ns")) & (T["ext"].fillna("") == c.get("ext", "") if "ext" in T else True)]
        return f"{lab} & {CS.FCI_LABEL[c['fci']]} & " + " & ".join(kset(t[t.H == h].iloc[0]) for h in (24, 36)) + r"\\"
    for pb in ("B", "B73"):
        lines.append(rf"\multicolumn{{4}}{{l}}{{\textit{{{CS.SHORT[pb]}}}}}\\")
        for f in ("nom", "real", "rstar"):
            lines += [trow(CS.FORMS[f] if c["fci"] == 0 else "", c) for c in CS.panel_by_id(pb)["cases"] if c["form"] == f]
        lines.append(r"\addlinespace")
    lines.append(r"\multicolumn{4}{l}{\textit{Variations, $r^*$-gap with the FCI}}\\")
    for pid in CS._both("R1a", "R1c", "R2a", "R2c"):
        p_ = CS.panel_by_id(pid); lines.append(trow(CS.SHORT[pid], next(c for c in p_["cases"] if c["fci"] != 0 and c["form"] in ("rstar", "kiley", "real") and (pid not in ("R1a", "R1a73") or c["form"] == "rstar"))))
    d = D[D.lags == MAIN_LAGS].set_index("H")
    lines += [r"\addlinespace", "r*-gap minus nominal, with FCI & & " + " & ".join(f"[{num(d.lo[h])}, {num(d.hi[h])}]" for h in (24, 36)) + r"\\"]
    (REPORT / "tab_tradeoff_full.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Implied trade-off: Phillips multiplier $\kappa_H$ (12 lags), all cases}\label{tab:tradefull}",
        r"\begin{tabular}{llrr}\toprule Case & FCI & $H=24$ months & $H=36$ months\\ \midrule", *lines, r"\bottomrule\end{tabular}",
        r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize $\kappa_H$ = core PCE price level at month $H$ (percent) per percentage-point year of cumulative unemployment-gap response (Barnichon and Mesters 2021); the sacrifice ratio is $-1/\kappa_H$. Point estimate and 90\% confidence set (Anderson--Rubin type) in brackets, computed exactly (a wide grid refined by bisection), so a finite end is never an artifact of the grid. An infinite end means that the 90\% interval of the cumulative unemployment response includes zero: the data then cannot rule out arbitrarily steep trade-offs on that side; ``unbounded'': both sides. Last row: paired difference over common announcement draws.}", r"\end{table}"]) + "\n")
except FileNotFoundError:
    print("tradeoff.csv missing: run 04_tradeoff.py first")


# ---------------------------------------------------------------- appendix: the main results at 3, 6 and 12 lags (same sample, announcements and bootstrap)
def lag_summary():
    """tab_lags.tex, macros bl:lag:* appended to numbers.tex, and the claims of the appendix on lag length."""
    LG = (3, 6, 12); BASEC = B96; ml = []; bad = []
    dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:lag:" + k + r"\endcsname{" + v + "}")
    chk = lambda name, ok: None if ok else bad.append(name)
    sg = lambda r, h: r[f"lo{h}"] * r[f"hi{h}"] > 0
    pi = lambda pt, lo, hi: (num(pt) + ("$^{*}$" if lo * hi > 0 else "") + f" [{num(lo)}, {num(hi)}]")
    LSL = pd.read_csv(RESULTS / "lit_style.csv"); LSL["sig"] = LSL.lo * LSL.hi > 0
    lit = lambda c, v, h, L: LSL[(LSL.lags == L) & (LSL.case == c) & (LSL["var"] == v) & (LSL.h == h)].iloc[0]
    mod = lambda f, fci, L, ident, v, h: (lambda m: m[(m.lags == L) & (m.ident == ident) & (m["var"] == v) & (m.h == h)].iloc[0])(MON[CS.monthly_id(dict(step=f, fci=fci, start="1996-01"))])
    def bl(f, fk, v, h, L):
        dd = R[CS.case_id(dict(form=f, fci=0 if fk == "no" else f, **BASEC))]; return dd[(dd.lags == L) & (dd["var"] == v)].iloc[0]
    rows = []
    def line(label, cells): rows.append(f"{label} & " + " & ".join(cells) + r"\\")
    rows.append(r"\multicolumn{4}{l}{\textit{Standard methods (per +1 pp on the policy rate)}}\\")
    line("Cholesky, 2-year yield: unemployment gap, 12 m", [pi(lit("chol_2y_1996", "u", 12, L).point, lit("chol_2y_1996", "u", 12, L).lo, lit("chol_2y_1996", "u", 12, L).hi) for L in LG])
    line("Cholesky, 2-year yield: price level, 36 m", [pi(lit("chol_2y_1996", "P", 36, L).point, lit("chol_2y_1996", "P", 36, L).lo, lit("chol_2y_1996", "P", 36, L).hi) for L in LG])
    line("Proxy VAR: unemployment gap, 24 m", [pi(lit("proxy_2y_1996", "u", 24, L).point, lit("proxy_2y_1996", "u", 24, L).lo, lit("proxy_2y_1996", "u", 24, L).hi) for L in LG])
    rows.append(r"\addlinespace\multicolumn{4}{l}{\textit{FCI model, $r^*$-gap 2-year yield (baseline)}}\\")
    for fk, v, h, lab in (("yes", "u", 24, "With FCI: unemployment gap, 24 m"), ("yes", "P", 24, "With FCI: price level, 24 m"), ("yes", "P", 36, "With FCI: price level, 36 m"), ("no", "u", 12, "Without FCI: unemployment gap, 12 m")):
        line(lab, [(lambda r: pi(r[f"r{h}"], r[f"lo{h}"], r[f"hi{h}"]))(bl("rstar", fk, v, h, L)) for L in LG])
    try:
        TL = pd.read_csv(RESULTS / "tradeoff.csv"); tt = lambda L, H: TL[(TL.form == "rstar") & (TL.fci == "rstar") & (TL.macro == "u,pi") & (TL.start == "1996-01") & TL.end.isna() & (TL.t2020 == "out") & (TL.trend == "none") & (TL.lags == L) & (TL.H == H) & (TL["shock"] == "ns") & (TL["ext"].fillna("") == "" if "ext" in TL else True)].iloc[0]
        kc = lambda t: f"{num(t.kappa)} " + ("[unbounded]" if not np.isfinite(t.k_lo) or not np.isfinite(t.k_hi) else f"[{num(t.k_lo)}, {num(t.k_hi)}]")
        line("Phillips multiplier, 24 m", [kc(tt(L, 24)) for L in LG]); mult_bounded = {L: bool(np.isfinite(tt(L, 24).k_lo) and np.isfinite(tt(L, 24).k_hi)) for L in LG}
    except FileNotFoundError: mult_bounded = {}
    CORE_C = [next(c for c in CS.panel_by_id(pid + sx)["cases"] if c["fci"] != 0 and all(c.get(k) == v for k, v in sel.items()) and (sel or c["form"] in ("rstar", "kiley", "real")) and (pid != "B" or c["form"] == "rstar"))
              for _, _, pid, sel, L_ in CORE_TESTS if L_ == 12 for sx in ("", "73")]
    rows.append(r"\addlinespace\multicolumn{4}{l}{\textit{Baselines and core tests with the FCI, both samples (%d cases, 3 horizons)}}\\" % len(CORE_C))
    cnt = {L: dict(Pneg=0, Psig=0, upos=0, usig=0, n=0, usigneg=0, Psigpos=0) for L in LG}
    for c in CORE_C:
            for L in LG:
                g = R[CS.case_id(c)]; g = g[g.lags == L]
                for v in ("u", "P"):
                    r = g[g["var"] == v].iloc[0]
                    for h in (12, 24, 36):
                        x = r[f"r{h}"]
                        if v == "P": cnt[L]["n"] += 1; cnt[L]["Pneg"] += x < 0; cnt[L]["Psig"] += bool(sg(r, h)); cnt[L]["Psigpos"] += bool(sg(r, h) and x > 0)
                        else: cnt[L]["upos"] += x > 0; cnt[L]["usig"] += bool(sg(r, h)); cnt[L]["usigneg"] += bool(sg(r, h) and x < 0)
    n_ = cnt[12]["n"]
    line("Price level falls", [f"{cnt[L]['Pneg']} of {n_}" for L in LG]); line("Price level falls significantly", [f"{cnt[L]['Psig']} of {n_}" for L in LG])
    line("Unemployment gap rises", [f"{cnt[L]['upos']} of {n_}" for L in LG]); line("Unemployment gap rises significantly", [f"{cnt[L]['usig']} of {n_}" for L in LG])
    rows.append(r"\addlinespace\multicolumn{4}{l}{\textit{Financial weights and simulation ($r^*$-gap)}}\\")
    WTL = _wt(); wt = lambda st, eq, L: WTL[(WTL.start == st) & (WTL.step == "rstar") & (WTL["eq"] == eq) & (WTL.lags == L)].iloc[0].p_boot
    line("Proportional weights, 1996: bootstrap $p$, unemployment equation", [f"{wt('1996-01', 'u', L):.3f}" for L in LG]); line("Proportional weights, 1996: bootstrap $p$, inflation equation", [f"{wt('1996-01', 'pi', L):.3f}" for L in LG])
    line("Proportional weights, 1973: bootstrap $p$, inflation equation", [f"{wt('1973-01', 'pi', L):.3f}" for L in LG])
    sm = {L: pd.read_csv(RESULTS / ("proxy_sim_summary.csv" if L == 12 else f"proxy_sim_summary_L{L}.csv")).set_index(["system", "quantity"]) for L in LG}
    line("Proxy VAR with FCI, simulated: median unemployment, 12 m (true value)", [f"{sm[L].loc[('proxy_fci', 'u12')].sim_median:.2f} ({sm[L].loc[('proxy_fci', 'u12')].truth:.2f})" for L in LG])
    line("Proxy VAR with FCI, simulated: first-stage $F$, median", [f"{sm[L].loc[('proxy_fci', 'F')].sim_median:.1f}" for L in LG])
    (REPORT / "tab_lags.tex").write_text("\n".join([r"\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}", r"\caption{The main results with 3, 6 and 12 monthly lags}\label{tab:lags}",
        r"\begin{tabular}{p{5.3cm}ccc}\toprule & 3 lags & 6 lags & 12 lags\\ \midrule", *rows, r"\bottomrule\end{tabular}",
        r"\par\smallskip\parbox{0.96\linewidth}{\scriptsize Same sample (1996 to 2026), announcements and block bootstrap (500 draws) at every lag length. Responses per +1 pp on the policy rate; $^{**}$, $^{*}$: 95\% and 90\% intervals exclude zero; 90\% intervals in brackets. Counts (at the 10 percent level): the 16 cases with the FCI in the baseline and Section 4.1, 2, 3 and 5 (components excluded), responses at 12, 24 and 36 months.}", r"\end{table}"]) + "\n")
    for L in LG:
        for k in ("Pneg", "Psig", "upos", "usig", "usigneg", "Psigpos"): dm(f"{k}:{L}", str(int(cnt[L][k])))
        dm(f"med:P:{L}", num(np.median([R[CS.case_id(c)].query("lags == @L and `var` == 'P'").iloc[0][f"r{h}"] for c in CORE_C for h in (12, 24, 36)])))
    dm("n", str(int(n_)))
    for L in LG:
        t = lit("chol_2y_1996", "u", 12, L); dm(f"chol:u12:{L}", num(t.point))
        b = bl("rstar", "yes", "P", 36, L); dm(f"rstar:P36:{L}", num(b.r36)); b = bl("rstar", "yes", "u", 24, L); dm(f"rstar:u24:{L}", num(b.r24))
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
    for L in LG:
        chk(f"lags {L}: with the FCI the price level falls in all core cases and horizons but one (12 lags: Kiley r* from 1996 at 36 m, not significant; 3 lags: components with equities free from 1973 at 12-36 m, significant at 24 m; 6 lags: none)",
            cnt[L]["Pneg"] == n_ - {3: 3, 6: 0, 12: 1}[L] and cnt[L]["Psigpos"] == (1 if L == 3 else 0))
        chk(f"lags {L}: with the FCI no significant fall in unemployment in any core case", cnt[L]["usigneg"] == 0)
        chk(f"lags {L}: unemployment rises in a large majority of responses with the FCI", cnt[L]["upos"] >= 0.7 * n_)
        t = lit("chol_2y_1996", "u", 12, L); chk(f"lags {L}: Cholesky unemployment falls at 12 m (significantly at 12 lags only)", t.point < 0 and t.sig == (L == 12))
        pr = lit("proxy_2y_1996", "u", 24, L); chk(f"lags {L}: proxy VAR unemployment falls at 24 m", pr.point < 0)
        chk(f"lags {L}: without the FCI the r*-gap unemployment gap is not significantly positive", not any(sg(bl("rstar", "no", "u", h, L), h) and bl("rstar", "no", "u", h, L)[f"r{h}"] > 0 for h in (12, 24, 36)))
        chk(f"lags {L}: weights, 1996: inflation equation rejects proportional weights at 10% in every step, unemployment equation not at 5%", all(WTL[(WTL.start == "1996-01") & (WTL.lags == L) & (WTL["eq"] == "pi")].p_boot < 0.10) and all(WTL[(WTL.start == "1996-01") & (WTL.lags == L) & (WTL["eq"] == "u")].p_boot > 0.05))
    chk("weights, 1973: no rejection of proportional weights at 5% at any lag length, step or equation", all(WTL[(WTL.start == "1973-01") & (WTL.lags.isin(LG))].p_boot > 0.05))
    chk("simulation: the median proxy-VAR estimate with the FCI lies below the true response at every lag length", all(sm[L].loc[("proxy_fci", "u12")].sim_median < sm[L].loc[("proxy_fci", "u12")].truth for L in LG))
    chk("price level significant in more cases with more lags", cnt[3]["Psig"] < cnt[6]["Psig"] < cnt[12]["Psig"])
    chk("point estimates of the baseline price response grow with the lag length", abs(bl("rstar", "yes", "P", 36, 3).r36) < abs(bl("rstar", "yes", "P", 36, 6).r36) < abs(bl("rstar", "yes", "P", 36, 12).r36))
    if mult_bounded: chk("the multiplier set at 24 m (from 1996) is bounded at every lag length; it excludes zero at 6 and 12 lags", mult_bounded == {3: True, 6: True, 12: True} and all(tt(L, 24).k_hi < 0 for L in (6, 12)) and tt(3, 24).k_hi > 0)
    if __import__("os").environ.get("CLAIMS_REPORT") and bad: print("FAILED CLAIMS:", *bad, sep="\n  ")
    else: assert not bad, "claims on lag length no longer hold: " + "; ".join(bad)
lag_summary()


# ---------------------------------------------------------------- appendix: the default bootstrap against independent resampling
def boot_summary():
    """Macros bl:bs:* (appended to numbers.tex) and claims for the appendix paragraph on the bootstrap."""
    if not (RESULTS / "boot_sens.csv").exists(): print("boot_sens.csv missing: run 10_bootstrap_sensitivity.py"); return
    B_ = pd.read_csv(RESULTS / "boot_sens.csv"); B_["fci"] = B_.fci.astype(str); key = ["form", "fci", "var", "h"]
    a = B_[B_.variant == "j12r"].set_index(key); b = B_[B_.variant == "iid"].set_index(key); a = a.loc[b.index]
    wr = ((b.hi - b.lo) / (a.hi - a.lo)); s10 = lambda x: (x.lo * x.hi > 0); s5 = lambda x: (x.lo95 * x.hi95 > 0); n = len(a)
    ml = []; dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:bs:" + k + r"\endcsname{" + v + "}")
    dm("n", str(n)); dm("wr:med", f"{wr.median():.2f}"); dm("wr:min", f"{wr.min():.2f}"); dm("wr:max", f"{wr.max():.2f}"); dm("wider", str(int((wr > 1).sum())))
    dm("same10", str(int((s10(a) == s10(b)).sum()))); dm("same5", str(int((s5(a) == s5(b)).sum()))); dm("sig10:block", str(int(s10(a).sum()))); dm("sig10:iid", str(int(s10(b).sum())))
    k = ("rstar", "rstar", "u", 24); dm("u24:lo", num(b.loc[k].lo)); dm("u24:hi", num(b.loc[k].hi)); dm("u24:lo5", num(a.loc[k].lo)); dm("u24:hi5", num(a.loc[k].hi))
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
    bad = []; chk = lambda name, ok: None if ok else bad.append(name)
    chk("independent resampling gives wider 90% intervals than the block bootstrap in most of the responses", (wr > 1).mean() > 0.5)
    chk("price level of the r*-gap FCI baseline significant at 5% at 12, 24, 36 m under both bootstraps", all(s5(x).loc[("rstar", "rstar", "P", h)] for x in (a, b) for h in (12, 24, 36)))
    chk("nominal and real yield alone: unemployment at 12 m significantly negative at 5% under both bootstraps", all(s5(x).loc[(f, "0", "u", 12)] and x.loc[(f, "0", "u", 12)].r < 0 for x in (a, b) for f in ("nom", "real")))
    if __import__("os").environ.get("CLAIMS_REPORT") and bad: print("FAILED CLAIMS:", *bad, sep="\n  ")
    else: assert not bad, "claims on the bootstrap no longer hold: " + "; ".join(bad)
boot_summary()


# ---------------------------------------------------------------- Section 4: summary table of the robustness variations, macros and claims
def rob_summary():
    """tab_rob_summary.tex (Section 5, author FS-A78: 12 months): baseline and the nine core tests, r*-gap with the FCI, unemployment gap and price level at 12 months, from 1996 and from 1973; macros bl:rob:*; claims."""
    lines = []; res = {}; ml = []; dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:rob:" + k + r"\endcsname{" + str(v) + "}")
    for key, lab, pid, sel, L in CORE_TESTS:
        pts, ivs = [], []
        for st, sx in STARTS:
            d = core_row(pid, sel, sx, L)
            for v in ("u", "P"):
                r = d[d["var"] == v].iloc[0]; res[(key, sx, v)] = (r.r12, r.lo12 * r.hi12 > 0, r.lo95_12 * r.hi95_12 > 0)
                pts.append(num(r.r12) + stars(r, 12)); ivs.append(f"[{num(r.lo12)}, {num(r.hi12)}]")
                dm(f"{key}{sx}:{v}", num(r.r12)); dm(f"{key}{sx}:{v}:sig", "significant" if r.lo12 * r.hi12 > 0 else "not significant")
        lines += [f"{lab} & " + " & ".join(pts) + r"\\", " & " + " & ".join(rf"{{\scriptsize {x}}}" for x in ivs) + r"\\"]
        if key == "base": lines.append(r"\midrule")
    tests = [k for k, *_ in CORE_TESTS if k != "base"]
    for sx in ("", "73"):
        for v in ("u", "P"): dm(f"nsig{sx}:{v}", sum(res[(k, sx, v)][1] for k in tests))
    dm("ntests", len(tests))
    OUTL = {"": ("kiley", "spline"), "73": ("L3", "kiley")}                         # the two tests whose responses differ in size from the rest (named in the text)
    for sx in ("", "73"):
        mid = [k for k in tests if k not in OUTL[sx]]
        for v in ("u", "P"):
            xs = [abs(res[(k, sx, v)][0]) for k in mid]; dm(f"mid{sx}:{v}:lo", f"{min(xs):.2f}"); dm(f"mid{sx}:{v}:hi", f"{max(xs):.2f}")
            for k in tests: dm(f"{k}{sx}:{v}:abs", f"{abs(res[(k, sx, v)][0]):.2f}")
    out = [r"\begin{table}[tp]\centering\small", r"\caption{Robustness: Responses at 12 Months}\label{tab:robsummary}",
           r"\begin{tabular}{lcccc}\toprule & \multicolumn{2}{c}{Monthly equations from 1996} & \multicolumn{2}{c}{Monthly equations from 1973}\\ \cmidrule(lr){2-3}\cmidrule(lr){4-5} & Unemployment gap & Price level & Unemployment gap & Price level\\ \midrule",
           *lines, r"\bottomrule\end{tabular}",
           r"\begin{flushleft}\footnotesize\textit{Notes:} $r^*$-gap two-year yield and FCI; responses 12 months after a policy move that raises the two-year yield 1 percentage point in the announcement window; unemployment gap in percentage points, price level in percent; 12 lags unless stated; March--December 2020 dropped unless stated. $^{**}$ and $^{*}$: the 95\% and 90\% bootstrap intervals exclude zero; 90\% intervals in brackets. The tests are described in Section 5; full results at 12, 24 and 36 months for every version are in the appendix.\end{flushleft}", r"\end{table}"]
    (REPORT / "tab_rob_summary.tex").write_text("\n".join(out) + "\n")
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
    bad = []; chk = lambda name, ok: None if ok else bad.append(name)
    chk("every core test, both samples: unemployment rises and the price level falls at 12 m", all(res[(k, sx, "u")][0] > 0 and res[(k, sx, "P")][0] < 0 for k, *_ in CORE_TESTS for sx in ("", "73")))
    NOT_SIG = {("t2020", "", "u"), ("kiley", "", "u"), ("kiley", "", "P"), ("spline", "", "u"), ("spline", "", "P"), ("L3", "", "P"), ("t2020", "73", "u"), ("kiley", "73", "u"), ("cmpE", "73", "u"), ("L3", "73", "u"), ("L3", "73", "P")}
    chk("significance pattern at 10% (the text names the exceptions: 2020 left in and Kiley r* for unemployment; Kiley r* and the spline trend from 1996; 3 lags; components from 1973 for unemployment)",
        all(res[(k, sx, v)][1] == ((k, sx, v) not in NOT_SIG) for k, *_ in CORE_TESTS for sx in ("", "73") for v in ("u", "P")))
    chk("the baseline: significant at 5% for both variables and both samples", all(res[("base", sx, v)][2] for sx in ("", "73") for v in ("u", "P")))
    ratio_ = lambda k, sx, v: res[(k, sx, v)][0] / res[("base", sx, v)][0]
    chk("Kiley r* and the spline trend from 1996: same sign, a quarter to a half of the baseline's size (u and P)", all(0.2 < ratio_(k, "", v) < 0.5 for k in ("kiley", "spline") for v in ("u", "P")))
    chk("6 lags: from 1996 unemployment close to the baseline (within 15 percent) and the price fall about a fifth smaller; from 1973 both smaller", 0.85 < ratio_("L6", "", "u") <= 1.0 and 0.7 < ratio_("L6", "", "P") < 0.85 and all(ratio_("L6", "73", v) < 0.85 for v in ("u", "P")))
    chk("Bauer-Swanson surprise: responses at least as large as the baseline's in both samples", all(ratio_("bs", sx, v) >= 1.0 for sx in ("", "73") for v in ("u", "P")))
    from lib import model as M_
    for sx in ("", "73"):
        r9 = core_row("R9", dict(form="rstar"), sx, 12); b_ = core_row("B", {}, sx, 12)
        rat = [r9[r9["var"] == v].iloc[0].r12 / b_[b_["var"] == v].iloc[0].r12 for v in ("u", "P")]
        chk(f"1-year yield ({sx or '96'}): responses per pp of its own window move 1.0 to 1.6 times the baseline's, in line with 1/RATIO_1Y = {1 / M_.RATIO_1Y:.2f}", all(1.0 < x < 1.6 for x in rat))
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + r"\expandafter\gdef\csname bl:rob:ratio1y\endcsname{" + f"{M_.RATIO_1Y:.2f}" + "}\n")
    for sx in ("", "73"):
        mid = [k for k in tests if k not in OUTL[sx]]; srt = sorted(tests, key=lambda k: res[(k, sx, "u")][0])
        chk(f"robustness {sx or '96'}: the two named departures are the two smallest unemployment responses", set(srt[:2]) == set(OUTL[sx]))
        chk(f"robustness {sx or '96'}: the other eight lie around the baseline (baseline inside their range for both variables)", all(min(res[(k, sx, v)][0] for k in mid) <= res[("base", sx, v)][0] <= max(res[(k, sx, v)][0] for k in mid) for v in ("u", "P")))
    if __import__("os").environ.get("CLAIMS_REPORT") and bad: print("FAILED CLAIMS:", *bad, sep="\n  ")
    else: assert not bad, "claims on the robustness section no longer hold: " + "; ".join(bad)
rob_summary()

# ---------------------------------------------------------------- figures
BLUE, ORANGE, INK, GREY = "#2a78d6", "#eb6834", "#0b0b0b", "#6b6a66"      # validated pair (dataviz skill, light surface); ink for text and neutral series
plt.rcParams.update({"font.size": 8, "axes.edgecolor": GREY, "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": 0.6, "axes.axisbelow": True})
def paths(c, L=MAIN_LAGS):
    d = pd.read_csv(RESULTS / f"{CS.case_id(c)}_paths.csv"); return d[d.lags == L]
def line(ax, d, color, ls, label, lo="lo", hi="hi", alpha=0.14):
    ax.fill_between(d.h, d[lo], d[hi], color=color, alpha=alpha, lw=0)
    if "lo68" in d: ax.fill_between(d.h, d.lo68, d.hi68, color=color, alpha=min(2 * alpha, 0.4), lw=0)                  # 68% band inside the 90% band
    ax.plot(d.h, d.r, color=color, ls=ls, lw=1.8, label=label)

base = CS.PANELS[0]["cases"]
fig, axs = plt.subplots(2, 3, figsize=(7.2, 3.9), sharex=True)
for j, f in enumerate(("nom", "real", "rstar")):
    cs = {c["fci"]: c for c in base if c["form"] == f}
    for i, v in enumerate(("u", "P")):
        ax = axs[i, j]; ax.axhline(0, color=GREY, lw=0.8)
        for c, col, ls, lab in ((cs[0], ORANGE, "--", "2-year yield only"), (cs[f], BLUE, "-", "with FCI")):
            d = paths(c); d = d[(d.kind == "macro") & (d["var"] == v)]; line(ax, d, col, ls, lab)
        if i == 0: ax.set_title(CS.FORMS[f] + " 2-year yield", fontsize=8.5)
        if j == 0: ax.set_ylabel("Unemployment gap (pp)" if v == "u" else "Core PCE price level (%)")
        if i == 1: ax.set_xlabel("Months after the policy move")
axs[0, 0].legend(frameon=False, loc="upper left", fontsize=7.5)
fig.suptitle("Response to a policy move that raises the 2-year yield 1 percentage point (12 lags; bands: 68 and 90 percent intervals)", fontsize=8.5, y=0.995)
fig.tight_layout(); fig.savefig(REPORT / "fig_steps.pdf"); plt.close(fig)

fig, ax = plt.subplots(1, 1, figsize=(4.4, 2.8)); ax.axhline(0, color=GREY, lw=0.8)
c = next(c for c in base if c["form"] == "rstar" and c["fci"] == "rstar"); d = paths(c); d = d[d.kind == "fin"]
line(ax, d[d["var"] == "pol"], INK, "-", "2-year yield, r*-gap form", alpha=0.10); line(ax, d[d["var"] == "idx"], GREY, "--", "FCI (2-year-yield units)", alpha=0.10)
ax.set_xlabel("Months after the policy move"); ax.set_ylabel("Percentage points"); ax.legend(frameon=False, fontsize=7.5)
ax.set_title("Financial response (monthly averages; 12 lags; 68 and 90% bands)", fontsize=8)
fig.tight_layout(); fig.savefig(REPORT / "fig_financial.pdf"); plt.close(fig)

# ---------------------------------------------------------------- standard methods (Section 3.1) and the baseline figure (Section 3.2)
LSR = pd.read_csv(RESULTS / "lit_style.csv").query("lags == 12")
def ls_path(case, v): return LSR[(LSR.case == case) & (LSR["var"] == v) & (LSR.h <= 36)]
def fig_standard():
    """Cholesky VAR and monthly proxy VAR on the 1996 sample, 2-year yield, no FCI: the puzzles that motivate the model."""
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.4)); H_ = []
    for ax, v, ylab in ((axs[0], "u", "Unemployment gap (pp)"), (axs[1], "P", "Core PCE price level (%)")):
        ax.axhline(0, color=GREY, lw=0.8)
        for case, col, ls_, ci in (("chol_2y_1996", ORANGE, "-", True), ("proxy_2y_1996", BLUE, "--", True)):
            d = ls_path(case, v); lo, hi = d.lo.clip(-4, 4), d.hi.clip(-4, 4)
            ax.fill_between(d.h, lo, hi, color=col, alpha=0.13, lw=0); H_.append(ax.plot(d.h, d.point, color=col, ls=ls_, lw=1.9)[0])
        ax.set_xlabel("Months after the policy move"); ax.set_ylabel(ylab); ax.set_xlim(0, 36)
    axs[0].set_ylim(-2.2, 1.2); axs[1].set_ylim(-2.5, 2.5)
    fig.legend([H_[0], H_[1]], ["Recursive (Cholesky) VAR; 90% bootstrap band", "Proxy VAR, Nakamura-Steinsson instrument; 90% Anderson-Rubin set"], loc="lower center", ncol=1, frameon=False, fontsize=7.5)
    fig.tight_layout(rect=[0, 0.13, 1, 1]); fig.savefig(REPORT / "fig_standard.pdf"); plt.close(fig)
fig_standard()

def standard_table(rows, fname, label, caption, extra=""):
    out = [r"\begin{table}[H]\centering\footnotesize\setlength{\tabcolsep}{2.4pt}", rf"\caption{{{caption}}}\label{{{label}}}",
           r"\begin{tabular}{llrrrrrrr}\toprule" "\n" r" & & & \multicolumn{3}{c}{Unemployment gap (pp)} & \multicolumn{3}{c}{Price level (\%)}\\ \cmidrule(lr){4-6}\cmidrule(lr){7-9}" "\n" r"Method & Sample & Obs & 12 m & 24 m & 36 m & 12 m & 24 m & 36 m\\ \midrule"]
    info = pd.read_csv(RESULTS / "lit_style_info.csv").query("lags == 12").set_index("case")
    for case, lab, smp in rows:
        cells = []
        for v in ("u", "P"):
            for h in (12, 24, 36):
                r = LSR[(LSR.case == case) & (LSR["var"] == v) & (LSR.h == h)].iloc[0]; cells.append((num(r.point) + ("$^{*}$" if r.lo * r.hi > 0 else ""), f"[{num(r.lo)}, {num(r.hi)}]"))
        out += [f"{lab} & {smp} & {int(info.nobs[case])} & " + " & ".join(c[0] for c in cells) + r"\\", r" & & & " + " & ".join(rf"{{\scriptsize {c[1]}}}" for c in cells) + r"\\"]
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.96\linewidth}{\scriptsize Monthly data, 12 lags, constant, no trend; unemployment gap, core PCE inflation and the monthly average of the policy rate (the 2-year Treasury yield, or the effective federal funds rate where stated), policy rate ordered last in the Cholesky VARs; price level = cumulated inflation/12. " 
            + extra + r" Unit: +1 pp on the policy rate on impact. Brackets: 90\% intervals (residual bootstrap for the Cholesky VARs; exact Anderson--Rubin sets for the proxy VAR). $^{*}$ = excludes zero.}", r"\end{table}"]
    (REPORT / fname).write_text("\n".join(out) + "\n")
_LI = pd.read_csv(RESULTS / "lit_style_info.csv").query("lags == 12").set_index("case"); _F = _LI.F["proxy_2y_1996"]
def standard_compact():
    """Table 2 (Part 2A): standard methods without the FCI, monthly averages; rows = method and response, columns = samples from 1996 and from 1973."""
    out = [r"\begin{table}[tp]\centering\small", r"\caption{Standard Methods: Responses to a 1 Percentage Point Rise in the Two-Year Yield}\label{tab:standard}",
           r"\begin{tabular}{llcc}\toprule Method & Response & 1996--2026 & 1973--2026\\ \midrule"]
    for mi, (m, lab) in enumerate((("chol", "Recursive (Cholesky) VAR"), ("proxy", "Proxy VAR"))):
        if mi: out.append(r"\addlinespace")
        for ri, (v, h, rl) in enumerate((("u", 12, "Unemployment gap, 12 m"), ("u", 24, "Unemployment gap, 24 m"), ("P", 24, "Price level, 24 m"), ("P", 36, "Price level, 36 m"))):
            cs_ = [LSR[(LSR.case == f"{m}_2y_{yr}") & (LSR["var"] == v) & (LSR.h == h)].iloc[0] for yr in ("1996", "1973")]
            out += [f"{lab if ri == 0 else ''} & {rl} & " + " & ".join(num(r.point) + ("$^{*}$" if r.lo * r.hi > 0 else "") for r in cs_) + r"\\",
                    " & & " + " & ".join(rf"{{\scriptsize [{num(r.lo)}, {num(r.hi)}]}}" for r in cs_) + r"\\"]
    out += [r"\bottomrule\end{tabular}", rf"\begin{{flushleft}}\footnotesize\textit{{Notes:}} Monthly VARs in the unemployment gap, core PCE inflation and the monthly average of the nominal two-year yield; 12 lags, constant, no trend, March--December 2020 dropped. Cholesky: the yield ordered last, per +1 pp innovation in the yield. Proxy VAR: Nakamura--Steinsson policy news summed within the month as instrument (first-stage $F$ = {_F:.1f} from 1996, {_LI.F['proxy_2y_1973']:.1f} from 1973), per +1 pp on the yield in the announcement window. Brackets: 90\% intervals (block bootstrap for the Cholesky VARs; exact Anderson--Rubin sets for the proxy VAR). $^{{*}}$ = excludes zero.\end{{flushleft}}", r"\end{table}"]
    (REPORT / "tab_standard.tex").write_text("\n".join(out) + "\n")
standard_compact()
standard_table([("chol_2y_1996", "Cholesky, 2-year yield", "1996--2026"), ("chol_2y_1984", "Cholesky, 2-year yield", "1984--2026"), ("chol_2y_1973", "Cholesky, 2-year yield", "1973--2026"), ("chol_ffr_1984_2007", "Cholesky, federal funds rate", "1984--2007"), ("proxy_2y_1996", "Proxy VAR, 2-year yield", "1996--2026"), ("proxy_2y_1973", "Proxy VAR, 2-year yield", "1973--2026")],
               "tab_standard_all.tex", "tab:standardall", "Standard methods with other samples and the federal funds rate", f"Proxy VAR: Nakamura--Steinsson policy news summed within the month as instrument; first-stage $F$ = {_F:.1f}.")
standard_table([("chol_2y_1996_com", "Cholesky + commodity prices, 2-year yield", "1996--2026"), ("chol_ffr_1984_2007_com", "Cholesky + commodity prices, federal funds rate", "1984--2007")],
               "tab_standard_com.tex", "tab:standardcom", "Standard methods with a commodity price index in the first block", "The log PPI for all commodities (monthly average) is added to the system and ordered before the policy rate.")

def fig_size():
    """Baseline figure: r*-gap 2-year yield with the FCI (bands), the nominal yield alone and with the FCI in the same model, and the Cholesky VAR of Section 3.1."""
    base = B96
    cs = dict(rstar=dict(form="rstar", fci="rstar", **base), nom0=dict(form="nom", fci=0, **base), nom1=dict(form="nom", fci="nom", **base))
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.9)); H_ = {}
    for ax, v, ylab in ((axs[0], "u", "Unemployment gap (pp)"), (axs[1], "P", "Core PCE price level (%)")):
        ax.axhline(0, color=GREY, lw=0.8)
        d = paths(cs["rstar"]); d = d[(d.kind == "macro") & (d["var"] == v)]
        ax.fill_between(d.h, d.lo, d.hi, color=BLUE, alpha=0.13, lw=0); ax.fill_between(d.h, d.lo68, d.hi68, color=BLUE, alpha=0.25, lw=0)
        H_["b"] = ax.plot(d.h, d.r, color=BLUE, lw=2.0)[0]
        for key, ls_ in (("nom0", "--"), ("nom1", ":")):
            e = paths(cs[key]); e = e[(e.kind == "macro") & (e["var"] == v)]; H_[key] = ax.plot(e.h, e.r, color=ORANGE, ls=ls_, lw=1.9)[0]
        c = ls_path("chol_2y_1996", v); H_["chol"] = ax.plot(c.h, c.point, color=INK, ls="-.", lw=1.5)[0]
        ax.set_xlabel("Months after the policy move"); ax.set_ylabel(ylab); ax.set_xlim(0, 36)
    labs = ["r*-gap 2-year yield and FCI (baseline; bands: 68 and 90 percent)", "Nominal 2-year yield alone (same model)", "Nominal 2-year yield and FCI (same model)", "Recursive (Cholesky) VAR, 2-year yield (Section 3.1)"]
    fig.legend([H_["b"], H_["nom0"], H_["nom1"], H_["chol"]], labs, loc="lower center", ncol=2, frameon=False, fontsize=7.2)
    fig.tight_layout(rect=[0, 0.13, 1, 1]); fig.savefig(REPORT / "fig_size.pdf"); plt.close(fig)
fig_size()

def fig_intro():
    """Figure 1 (introduction; Part 2A): the two baselines, r*-gap two-year yield alone and with the FCI; columns = monthly equations from 1996 and from 1973, rows = unemployment gap and price level
    (same surprise, normalization and bootstrap; 68 and 90 percent bands)."""
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 5.2), sharex=True)
    for j, (st, title) in enumerate((("1996-01", "Monthly equations from 1996"), ("1973-01", "Monthly equations from 1973"))):
        base = {**B96, "start": st}
        for i, (v, ylab) in enumerate((("u", "Unemployment gap (pp)"), ("P", "Core PCE price level (%)"))):
            ax = axs[i, j]; ax.axhline(0, color=GREY, lw=0.8)
            e = paths(dict(form="rstar", fci=0, **base)); e = e[(e.kind == "macro") & (e["var"] == v)]
            ax.fill_between(e.h, e.lo, e.hi, color=ORANGE, alpha=0.10, lw=0); ax.fill_between(e.h, e.lo68, e.hi68, color=ORANGE, alpha=0.20, lw=0); h2 = ax.plot(e.h, e.r, color=ORANGE, ls="--", lw=1.9)[0]
            d = paths(dict(form="rstar", fci="rstar", **base)); d = d[(d.kind == "macro") & (d["var"] == v)]
            ax.fill_between(d.h, d.lo, d.hi, color=BLUE, alpha=0.13, lw=0); ax.fill_between(d.h, d.lo68, d.hi68, color=BLUE, alpha=0.25, lw=0); h1 = ax.plot(d.h, d.r, color=BLUE, lw=2.0)[0]
            ax.set_xlim(0, 36)
            if i == 0: ax.set_title(title, fontsize=8.5)
            if j == 0: ax.set_ylabel(ylab)
            if i == 1: ax.set_xlabel("Months after the policy move")
    for i in range(2):                                                                # common vertical scale within a row
        lo = min(axs[i, 0].get_ylim()[0], axs[i, 1].get_ylim()[0]); hi = max(axs[i, 0].get_ylim()[1], axs[i, 1].get_ylim()[1]); axs[i, 0].set_ylim(lo, hi); axs[i, 1].set_ylim(lo, hi)
    fig.legend([h1, h2], ["Yield and FCI, both relative to the neutral rate", "Yield alone, relative to the neutral rate"], loc="lower center", ncol=2, frameon=False, fontsize=7.5)
    fig.tight_layout(rect=[0, 0.05, 1, 1]); fig.savefig(REPORT / "fig_intro.pdf"); plt.close(fig)
fig_intro()
from lib import latex_style as LST
LST.restyle_dir(REPORT)                                                              # house LaTeX style: [tp] floats, Title Case captions, notes below the table
print("report inputs written to", REPORT)
