"""Step 7. Tables and figures of the results document from results/ (12-lag main tables by section, 6/12-lag appendix tables by panel, the response
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
HEAD_FORM = "real"          # baseline_real (FS-A85 D1): the headline version
# The six core robustness tests (FS-A85 D6 as revised by D10-D11); the 1985 start has no 1973 counterpart (sx73 = None)
CORE_TESTS = [("base", "Baseline", "B", {}, 12), ("t2020", "2020 left in", "R1", {}, 12), ("ebpip", "Excess bond premium and industrial production added", "R2", {}, 12),
              ("bs", "Bauer--Swanson surprise", "R3", {}, 12), ("L6", "6 lags", "B", {}, 6), ("noff", "Without the funds rate", "R5", {}, 12), ("s85", "Monthly equations from 1985", "R6", {}, 12)]
def core_row(pid, sel, sx, L, form=HEAD_FORM):
    """The case with the FCI of a core robustness test in the given version (default: the headline real version), from 1996 (sx = '') or 1973 (sx = '73'); rows of its results at L lags.
    The 1985 start (R6) has one sample: its row is returned for both columns."""
    pid_ = pid if pid == "R6" else pid + sx
    p_ = CS.panel_by_id(pid_); c = next(c for c in p_["cases"] if c["fci"] != 0 and c["form"] == form and all(c.get(k) == v for k, v in sel.items()))
    d = R[CS.case_id(c)]; return d[d.lags == L]
def blocks_of(p, lab=None, version_only=False):
    """Rows of a panel's table: one block per version when the panel has more than one (or the components), else one block.
    version_only: label each block by its version alone (appendix tables, whose caption names the panel)."""
    forms = list(dict.fromkeys(c["form"] for c in p["cases"])); lab = lab or CS.SHORT.get(p["id"], p["title"])
    if len(forms) > 1 : return [(CS.FORMS[f] if version_only else f"{lab}: {CS.FORMS[f]}", [c for c in p["cases"] if c["form"] == f]) for f in forms]
    return [(lab, p["cases"])]

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
    (REPORT / f"tab_app_{p['id']}.tex").write_text(table(p["title"], f"tab:app{p['id']}", blocks_of(p, CS.FORMS[p["cases"][0]["form"]] if len(set(c["form"] for c in p["cases"])) == 1 else "", version_only=True), (6, 12), p["notes"], "p") + "\n")

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
    for si, step in enumerate(("nom", "real")):
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
MNOTE = (r"Monthly VAR in the unemployment gap, core PCE inflation, the monthly averages of the 2-year yield, of the FCI when included, and of the federal funds rate (same version), to September 2026, no trend, March--December 2020 dropped. "
         r"Proxy VAR: Nakamura--Steinsson surprise as instrument; sets are exact 90\% Anderson--Rubin sets, ``unbounded'' when the instrument cannot reject large effects. "
         r"Window impact: impact vector taken from the daily model (the month-average response to a window surprise); 90\% bootstrap intervals. Unit in both: +1 pp on the 2-year yield in the announcement window.")
for st, sx in STARTS:
    yr = st[:4]
    (REPORT / f"tab_main_monthly{sx}.tex").write_text(monthly_table(f"Monthly VAR benchmark from {yr} (12 lags)", f"tab:mainmonthly{sx}", (12,), MNOTE, st) + "\n")
    (REPORT / f"tab_app_monthly{sx}.tex").write_text(monthly_table(f"Monthly VAR benchmark from {yr} (6 and 12 lags)", f"tab:appmonthly{sx}", (6, 12), MNOTE, st, "p") + "\n")
frows = []
for st, sx in STARTS:
  frows.append(rf"\multicolumn{{6}}{{l}}{{\textit{{Monthly equations from {st[:4]}}}}}\\")
  for step in ("nom", "real"):
    for fci in (0, step):
        d = MON[CS.monthly_id(dict(step=step, fci=fci, start=st))]; g = d[(d.ident == "P1") & (d["var"] == "u") & (d.h == 12)].set_index("lags")
        frows.append(f"{CS.FORMS[step] if fci == 0 else ''} & {CS.FCI_LABEL[fci]} & " + " & ".join(f"{g.F[L]:.1f}" for L in (6, 12)) + " & " + (f"{num(g.impact_fci[12])} & {num(g.win_fci[12] / g.win_pol[12])}" if fci else " & ") + r"\\")
(REPORT / "tab_monthly_F.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Monthly proxy VAR: first-stage strength and impact on the FCI}\label{tab:monthlyF}",
    r"\begin{tabular}{llrrrr}\toprule 2-year & FCI & $F$ (6 lags) & $F$ (12) & Proxy impact on FCI & Model impact on FCI\\ \midrule", *frows, r"\bottomrule\end{tabular}",
    r"\par\smallskip\parbox{0.92\linewidth}{\scriptsize $F$: robust first-stage statistic of the policy-variable residual on the instrument (instrument months only, 1996--2026; monthly equations from 1996 or from 1973). Impact on FCI: response of the month's average FCI per +1 pp on the month's average 2-year yield, estimated from monthly residuals (proxy VAR, 12 lags) and implied by the daily model.}", r"\end{table}"]) + "\n")

# ---------------------------------------------------------------- how noisy is the monthly proxy VAR if the model is true?
SIM = pd.read_csv(RESULTS / "proxy_sim_summary.csv")
SIMM = pd.read_csv(RESULTS / "sim_matched_summary.csv")      # step 14: the main model without and with the FCI on the same simulated samples (FS-A92)
SIM = pd.concat([SIM, SIMM.assign(system="main_" + SIMM.system)], ignore_index=True)
def sim_table():
    lab = {("proxy_fci", "F"): "First-stage $F$", ("proxy_fci", "u12"): "Unemployment gap, 12 m", ("proxy_fci", "P24"): "Price level, 24 m", ("proxy_nofci", "u12"): "Unemployment gap, 12 m", ("window", "u12"): "Unemployment gap, 12 m",
           **{(f"main_{s_}", q): t for s_ in ("fci", "nofci", "diff") for q, t in (("u12", "Unemployment gap, 12 m"), ("u24", "Unemployment gap, 24 m"), ("P24", "Price level, 24 m"))}}
    out = [r"\begin{table}[H]\centering\small", r"\caption{Monthly VARs and the main model when the real model is the true process}\label{tab:proxysim}",
           r"\begin{tabular}{lrrrr}\toprule Estimate & Data & True & Simulated median & 5th--95th percentile\\ \midrule"]
    for system, head in (("proxy_fci", "A. Proxy VAR with the FCI"), ("proxy_nofci", "B. Proxy VAR without the FCI"), ("window", "C. Monthly VAR with the window impact and the FCI"),
                         ("main_fci", "D. Main model with the FCI"), ("main_nofci", "E. Main model without the FCI"), ("main_diff", "F. Difference, D less E")):
        out.append(rf"\multicolumn{{5}}{{l}}{{\textit{{{head}}}}}\\")
        for _, r in SIM[(SIM.system == system) & SIM.apply(lambda x: (x.system, x.quantity) in lab, axis=1)].iterrows():
            f = "{:.1f}" if r.quantity == "F" else "{:.2f}"; sg = lambda x: ("$-$" if x < 0 and f.format(abs(x)) != "0.00" else "") + f.format(abs(x))
            out.append(f"\\quad {lab[(system, r.quantity)]} & {sg(r.data)} & {sg(r.truth) if pd.notna(r.truth) else ''} & {sg(r.sim_median)} & [{sg(r.sim_p05)}, {sg(r.sim_p95)}]\\\\")
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize 1,000 samples of 369 months generated by the estimated real model with the FCI and the funds rate (12 lags), with the data's calendar and announcement days; policy reaches unemployment and prices only through the 2-year yield, the FCI and the funds rate. Data: the 1996 sample, 12 lags, real measures, March--December 2020 dropped; monthly averages in the monthly VAR. True: the model's response per +1 pp on the 2-year yield in the announcement window (the unit of every panel). Simulated: median and 5th--95th percentiles of the estimates. Panels D--F: on each sample the main model (daily block and monthly equations) is estimated with the two rates and the FCI and with the two rates alone, both started from the true window impact; the difference is computed sample by sample.}", r"\end{table}"]
    return "\n".join(out)
(REPORT / "tab_proxy_sim.tex").write_text(sim_table() + "\n")

def monthly_compact():
    """Table in Section 3.5: r*-gap yield and FCI; proxy VAR, window-impact VAR and the main model; unemployment at 12 and 24 months, price level at 12 and 24 months."""
    m = MON[CS.monthly_id(dict(step=HEAD_FORM, fci=HEAD_FORM, start="1996-01"))]; m = m[m.lags == 12]
    def mrow(ident, lab):
        cs_ = []
        for v in ("u", "P"):
            for h in (12, 24):
                r = m[(m.ident == ident) & (m["var"] == v) & (m.h == h)].iloc[0]; cs_.append((num(r.r) + ("$^{*}$" if r.lo * r.hi > 0 else ""), f"[{num(r.lo)}, {num(r.hi)}]"))
        return [f"{lab} & " + " & ".join(c[0] for c in cs_) + r"\\", " & " + " & ".join(rf"{{\scriptsize {c[1]}}}" for c in cs_) + r"\\"]
    dd = R[CS.case_id(dict(form=HEAD_FORM, fci=HEAD_FORM, **B96))]; dd = dd[dd.lags == MAIN_LAGS]; cs_ = []
    for v in ("u", "P"):
        for h in (12, 24):
            r = dd[dd["var"] == v].iloc[0]; cs_.append((num(r[f"r{h}"]) + ("$^{*}$" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else ""), f"[{num(r[f'lo{h}'])}, {num(r[f'hi{h}'])}]"))
    main = [r"Main model (daily block) & " + " & ".join(c[0] for c in cs_) + r"\\", " & " + " & ".join(rf"{{\scriptsize {c[1]}}}" for c in cs_) + r"\\"]
    out = [r"\begin{table}[H]\centering\small", r"\caption{Monthly VARs with the FCI and the main model (real two-year yield, FCI and funds rate; 12 lags)}\label{tab:monthlycompact}",
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
    for (st, sx), f in [(a, b) for a in STARTS for b in ("nom", "real")]:
        for fci, fk in ((0, "no"), (f, "yes")):
            dd = R[CS.case_id(dict(form=f, fci=fci, **{**B96, "start": st}))]; g = dd[dd.lags == MAIN_LAGS]
            for v in ("u", "P"):
                r = g[g["var"] == v].iloc[0]
                for h in (12, 24, 36):
                    k = ("b73:" if sx else "") + f"{f}:{fk}:{v}:{h}"; d("bl:" + k, num(r[f"r{h}"])); d("blabs:" + k, f"{abs(r[f'r{h}']):.2f}"); d("blsig:" + k, "significant" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "not significant")
                    d("bllo:" + k, num(r[f"lo{h}"])); d("blhi:" + k, num(r[f"hi{h}"]))
    n = R[CS.case_id(dict(form=HEAD_FORM, fci=HEAD_FORM, **B96))]; d("bl:nobs", str(int(n[n.lags == MAIN_LAGS].nobs.iloc[0])))
    n = R[CS.case_id(dict(form=HEAD_FORM, fci=HEAD_FORM, **B73))]; d("bl:b73:nobs", str(int(n[n.lags == MAIN_LAGS].nobs.iloc[0])))
    BASE = B96
    pth = lambda f, fci: (lambda d: d[d.lags == MAIN_LAGS])(pd.read_csv(RESULTS / f"{CS.case_id(dict(form=f, fci=fci, **BASE))}_paths.csv"))
    u = pth("nom", 0); u = u[(u.kind == "macro") & (u["var"] == "u")]; i = u.r.idxmin(); d("bl:path:nom:no:u:min", num(u.r[i])); d("bl:path:nom:no:u:minh", str(int(u.h[i])))
    u = pth("real", "real"); u = u[(u.kind == "macro") & (u["var"] == "u")]; i = u.r.idxmax(); d("bl:path:real:yes:u:max", num(u.r[i])); d("bl:path:real:yes:u:maxh", str(int(u.h[i])))
    LS = pd.read_csv(RESULTS / "lit_style.csv").query("lags == 12"); LSI = pd.read_csv(RESULTS / "lit_style_info.csv").query("lags == 12").set_index("case")
    for key, case in (("c2y96", "chol_2y_1996"), ("c2y84", "chol_2y_1984"), ("cffr", "chol_ffr_1984_2007"), ("c2ycom", "chol_2y_1996_com"), ("cffrcom", "chol_ffr_1984_2007_com"), ("prox", "proxy_2y_1996"), ("c2y73", "chol_2y_1973"), ("prox73", "proxy_2y_1973")):
        for v in ("u", "P"):
            for h in (0, 12, 24, 36):
                r = LS[(LS.case == case) & (LS["var"] == v) & (LS.h == h)].iloc[0]; k = f"st:{key}:{v}:{h}"
                d("bl:" + k, num(r.point)); d("blabs:" + k, f"{abs(r.point):.2f}"); d("bllo:" + k, num(r.lo)); d("blhi:" + k, num(r.hi)); d("blsig:" + k, "significant" if r.lo * r.hi > 0 else "not significant")
        d("bl:st:" + key + ":nobs", str(int(LSI.nobs[case])))
    d("bl:st:prox:F", f"{LSI.F['proxy_2y_1996']:.1f}"); d("bl:st:prox73:F", f"{LSI.F['proxy_2y_1973']:.1f}")
    # monthly VARs on monthly averages (12 lags), from 1996 (mo:) and from 1973 (mo73:)
    for (st, sx), f in [(a, b) for a in STARTS for b in ("nom", "real")]:
        for fci, fk in ((0, "no"), (f, "yes")):
            m = MON[CS.monthly_id(dict(step=f, fci=fci, start=st))]; m = m[m.lags == MAIN_LAGS]; d(f"bl:mo{sx}:{f}:{fk}:F", f"{m.F.iloc[0]:.1f}")
            if fci: d(f"bl:mo{sx}:{f}:{fk}:impf", num(m.impact_fci.iloc[0])); d(f"bl:mo{sx}:{f}:{fk}:modf", num(m.win_fci.iloc[0] / m.win_pol.iloc[0]))
            d(f"bl:mo{sx}:{f}:{fk}:impff", num(m.impact_ff.iloc[0])); d(f"bl:mo{sx}:{f}:{fk}:modff", num(m.win_ff.iloc[0] / m.win_pol.iloc[0]))
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
        if "share_wrong_sign" in r and pd.notna(r.share_wrong_sign): d("bl:" + k + ":wrong", f"{100 * r.share_wrong_sign:.0f}"); d("bl:" + k + ":right", f"{100 * (1 - r.share_wrong_sign):.0f}")
        if pd.notna(r.truth): d("bl:" + k + ":truth", sg(r.truth))
    # trade-off (Phillips multiplier)
    TT = pd.read_csv(RESULTS / "tradeoff.csv"); TT["fci"] = TT.fci.astype(str); TD = pd.read_csv(RESULTS / "tradeoff_diff.csv")
    for (st, sx), f in [(a, b) for a in STARTS for b in ("nom", "real")]:
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
        multi = len(set(c["form"] for c in p_["cases"])) > 1
        for cs in p_["cases"]:
            fk = "no" if cs["fci"] == 0 else ("yes" if cs["fci"] in (cs["form"], "baa") else str(cs["fci"])); form_tag = f":{cs['form']}" if multi else ""
            g_ = R[CS.case_id(cs)]; g_ = g_[g_.lags == MAIN_LAGS]
            for v in ("u", "P"):
                r = g_[g_["var"] == v].iloc[0]
                for h in (12, 24, 36):
                    k = f"rb:{p_['id']}{form_tag}:{fk}:{v}:{h}"; d("bl:" + k, num(r[f"r{h}"])); d("blabs:" + k, f"{abs(r[f'r{h}']):.2f}"); d("blsig:" + k, "significant" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "not significant")
                    d("bllo:" + k, num(r[f"lo{h}"])); d("blhi:" + k, num(r[f"hi{h}"]))
    from lib import daily as DD
    for nm in ("bs", "jk"): DD.use_surprise(nm); d(f"bl:ev:{nm}", str(len(DD.event_index())))
    DD.use_surprise("ns")
    from lib.daily import window_impact, event_index, EV
    from lib import monthly as MO
    from lib.model import MAC
    from lib import model as M_
    d("bl:ff:b", f"{M_.B_FF:.2f}")                                                      # funds-rate window impact per +1 pp on the two-year yield (MP1), FS-A89
    ev_ = EV.iloc[event_index()]; xs_ = ev_.ns.values - ev_.ns.values.mean(); sl_ = lambda y: float(np.sum((y - np.nanmean(y)) * xs_) / np.sum(xs_ * xs_)); s2_ = sl_(ev_.UST2Y.values)
    for k_ in (1, 5, 22):                                                                # realized change in the effective funds rate, day before to k days after, per +1 pp on the two-year window move
        ch_ = np.array([M_._dff[t:].iloc[min(k_, len(M_._dff[t:]) - 1)] - M_._dff[:t - pd.Timedelta(days=1)].iloc[-1] for t in pd.DatetimeIndex(ev_.d)]); d(f"bl:ff:dff{k_}", f"{sl_(ch_) / s2_:.2f}")
    zl_ = M_.DFFM < 0.25                                                                 # zero lower bound: monthly average funds rate below 0.25 (FS-A88)
    for nm_, a_ in (("96", "1996-01"), ("74", "1974-01")): z_ = zl_.loc[a_:"2026-09"]; d(f"bl:zlb:share{nm_}", f"{100 * z_.mean():.0f}")
    d("bl:zlb:n", str(int(zl_.loc["1996-01":"2026-09"].sum())))
    zd_ = pd.DatetimeIndex(ev_.d); zm_ = zl_.reindex(zd_.to_period("M")).fillna(False).values; d("bl:zlb:ev", str(int(zm_.sum())))
    d("bl:bF", f"{window_impact(event_index())[1]:.2f}")
    ie = event_index(); s_ = EV.ns.values[ie]                           # share of each window move explained by the policy-news surprise (R-squared)
    for col, k in (("UST2Y", "y2"), ("UST10Y", "y10"), ("SP500", "sp"), ("DXY", "usd"), ("idx_win", "fci")): d(f"bl:r2:{k}", f"{100 * np.corrcoef(s_, EV[col].values[ie])[0, 1] ** 2:.0f}")
    (REPORT / "numbers.tex").write_text("\n".join(L) + "\n")
write_numbers()

def paths(c, L=MAIN_LAGS):
    d = pd.read_csv(RESULTS / f"{CS.case_id(c)}_paths.csv"); return d[d.lags == L]
def check_claims():
    """The qualitative claims of the results (baseline_real, FS-A85), written from the new results (claims_real.py); the text quotes only claims listed there.
    Raises an error if any stops being true (CLAIMS_REPORT=1: list the failures instead)."""
    import claims_real as CR
    bad = CR.check(R, MON, SIM, B96, ROB)
    if __import__("os").environ.get("CLAIMS_REPORT") and bad: print("FAILED CLAIMS:", *bad, sep="\n  ")
    else: assert not bad, "claims no longer hold: " + "; ".join(bad)


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
        for f in ("nom", "real"):
            lines += [trow(CS.FORMS[f] if c["fci"] == 0 else "", c) for c in CS.panel_by_id(pb)["cases"] if c["form"] == f]
        lines.append(r"\addlinespace")
    lines.append(r"\multicolumn{4}{l}{\textit{Robustness tests and the final section, real with the FCI}}\\")
    for pid in CS._both("R1", "R2", "R3", "R5") + ["R6"] + CS._both("F2"):
        p_ = CS.panel_by_id(pid); lines.append(trow(CS.SHORT[pid], next(c for c in p_["cases"] if c["fci"] != 0 and c["form"] == "real")))
    for pid in CS._both("F1"):
        p_ = CS.panel_by_id(pid); lines.append(trow(CS.SHORT[pid], next(c for c in p_["cases"] if c["fci"] != 0)))
    d = D[D.lags == MAIN_LAGS].set_index("H")
    lines += [r"\addlinespace", "Real minus nominal, with FCI & & " + " & ".join(f"[{num(d.lo[h])}, {num(d.hi[h])}]" for h in (24, 36)) + r"\\"]
    (REPORT / "tab_tradeoff_full.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Implied trade-off: Phillips multiplier $\kappa_H$ (12 lags), all cases}\label{tab:tradefull}",
        r"\begin{tabular}{llrr}\toprule Case & FCI & $H=24$ months & $H=36$ months\\ \midrule", *lines, r"\bottomrule\end{tabular}",
        r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize $\kappa_H$ = core PCE price level at month $H$ (percent) per percentage-point year of cumulative unemployment-gap response (Barnichon and Mesters 2021); the sacrifice ratio is $-1/\kappa_H$. Point estimate and 90\% confidence set (Anderson--Rubin type) in brackets, computed exactly (a wide grid refined by bisection), so a finite end is never an artifact of the grid. An infinite end means that the 90\% interval of the cumulative unemployment response includes zero: the data then cannot rule out arbitrarily steep trade-offs on that side; ``unbounded'': both sides. Last row: paired difference over common announcement draws.}", r"\end{table}"]) + "\n")
except FileNotFoundError:
    print("tradeoff.csv missing: run 04_tradeoff.py first")


# ---------------------------------------------------------------- appendix: the main results at 6 and 12 lags (same sample, announcements and bootstrap; FS-A85 D9: 3 lags dropped)
def lag_summary():
    """tab_lags.tex and macros bl:lag:* appended to numbers.tex."""
    LG = (6, 12); BASEC = B96; ml = []
    dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:lag:" + k + r"\endcsname{" + v + "}")
    sg = lambda r, h: r[f"lo{h}"] * r[f"hi{h}"] > 0
    pi = lambda pt, lo, hi: (num(pt) + ("$^{*}$" if lo * hi > 0 else "") + f" [{num(lo)}, {num(hi)}]")
    LSL = pd.read_csv(RESULTS / "lit_style.csv"); LSL["sig"] = LSL.lo * LSL.hi > 0
    lit = lambda c, v, h, L: LSL[(LSL.lags == L) & (LSL.case == c) & (LSL["var"] == v) & (LSL.h == h)].iloc[0]
    def bl(f, fk, v, h, L):
        dd = R[CS.case_id(dict(form=f, fci=0 if fk == "no" else f, **BASEC))]; return dd[(dd.lags == L) & (dd["var"] == v)].iloc[0]
    rows = []
    def line(label, cells): rows.append(f"{label} & " + " & ".join(cells) + r"\\")
    rows.append(r"\multicolumn{3}{l}{\textit{Standard methods (per +1 pp on the policy rate)}}\\")
    line("Cholesky, 2-year yield: unemployment gap, 12 m", [pi(lit("chol_2y_1996", "u", 12, L).point, lit("chol_2y_1996", "u", 12, L).lo, lit("chol_2y_1996", "u", 12, L).hi) for L in LG])
    line("Cholesky, 2-year yield: price level, 36 m", [pi(lit("chol_2y_1996", "P", 36, L).point, lit("chol_2y_1996", "P", 36, L).lo, lit("chol_2y_1996", "P", 36, L).hi) for L in LG])
    line("Proxy VAR: unemployment gap, 24 m", [pi(lit("proxy_2y_1996", "u", 24, L).point, lit("proxy_2y_1996", "u", 24, L).lo, lit("proxy_2y_1996", "u", 24, L).hi) for L in LG])
    for f in ("real", "nom"):
        rows.append(r"\addlinespace\multicolumn{3}{l}{\textit{FCI model, %s 2-year yield and funds rate}}\\" % CS.FORMS[f].lower())
        for fk, v, h, lab in (("yes", "u", 24, "With FCI: unemployment gap, 24 m"), ("yes", "P", 24, "With FCI: price level, 24 m"), ("yes", "P", 36, "With FCI: price level, 36 m"), ("no", "u", 12, "Without FCI: unemployment gap, 12 m")):
            line(lab, [(lambda r: pi(r[f"r{h}"], r[f"lo{h}"], r[f"hi{h}"]))(bl(f, fk, v, h, L)) for L in LG])
    try:
        TL = pd.read_csv(RESULTS / "tradeoff.csv"); tt = lambda L, H: TL[(TL.form == HEAD_FORM) & (TL.fci == HEAD_FORM) & (TL.macro == "u,pi") & (TL.start == "1996-01") & TL.end.isna() & (TL.t2020 == "out") & (TL.trend == "none") & (TL.lags == L) & (TL.H == H) & (TL["shock"] == "ns") & (TL["ext"].fillna("") == "" if "ext" in TL else True)].iloc[0]
        kc = lambda t: f"{num(t.kappa)} " + ("[unbounded]" if not np.isfinite(t.k_lo) or not np.isfinite(t.k_hi) else f"[{num(t.k_lo)}, {num(t.k_hi)}]")
        line("Phillips multiplier, real with FCI, 24 m", [kc(tt(L, 24)) for L in LG])
    except FileNotFoundError: pass
    CORE_C = []
    for _, _, pid, sel, L_ in CORE_TESTS:
        if L_ != 12: continue
        for sx in (("",) if pid == "R6" else ("", "73")):
            for f in ("nom", "real"):
                pid_ = pid if pid == "R6" else pid + sx; CORE_C.append(next(c for c in CS.panel_by_id(pid_)["cases"] if c["fci"] != 0 and c["form"] == f))
    rows.append(r"\addlinespace\multicolumn{3}{l}{\textit{Baselines and core tests with the FCI, nominal and real, both samples (%d cases, 3 horizons)}}\\" % len(CORE_C))
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
    rows.append(r"\addlinespace\multicolumn{3}{l}{\textit{Simulation (real model as the true process)}}\\")
    sm = {L: pd.read_csv(RESULTS / ("proxy_sim_summary.csv" if L == 12 else f"proxy_sim_summary_L{L}.csv")).set_index(["system", "quantity"]) for L in LG if (RESULTS / ("proxy_sim_summary.csv" if L == 12 else f"proxy_sim_summary_L{L}.csv")).exists()}
    if len(sm) == len(LG):
        line("Proxy VAR with FCI, simulated: median unemployment, 12 m (true value)", [f"{sm[L].loc[('proxy_fci', 'u12')].sim_median:.2f} ({sm[L].loc[('proxy_fci', 'u12')].truth:.2f})" for L in LG])
        line("Proxy VAR with FCI, simulated: first-stage $F$, median", [f"{sm[L].loc[('proxy_fci', 'F')].sim_median:.1f}" for L in LG])
    (REPORT / "tab_lags.tex").write_text("\n".join([r"\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}", r"\caption{The main results with 6 and 12 monthly lags}\label{tab:lags}",
        r"\begin{tabular}{p{6.3cm}cc}\toprule & 6 lags & 12 lags\\ \midrule", *rows, r"\bottomrule\end{tabular}",
        r"\par\smallskip\parbox{0.96\linewidth}{\scriptsize Same sample (1996 to 2026), announcements and block bootstrap (500 draws) at both lag lengths. Responses per +1 pp on the policy rate; $^{*}$: 90\% interval excludes zero; 90\% intervals in brackets. Counts (at the 10 percent level): the cases with the FCI in the baselines and the robustness tests (nominal and real), responses at 12, 24 and 36 months.}", r"\end{table}"]) + "\n")
    for L in LG:
        for k in ("Pneg", "Psig", "upos", "usig", "usigneg", "Psigpos"): dm(f"{k}:{L}", str(int(cnt[L][k])))
        dm(f"med:P:{L}", num(np.median([R[CS.case_id(c)].query("lags == @L and `var` == 'P'").iloc[0][f"r{h}"] for c in CORE_C for h in (12, 24, 36)])))
    dm("n", str(int(n_)))
    for L in LG:
        t = lit("chol_2y_1996", "u", 12, L); dm(f"chol:u12:{L}", num(t.point))
        b = bl(HEAD_FORM, "yes", "P", 36, L); dm(f"real:P36:{L}", num(b.r36)); b = bl(HEAD_FORM, "yes", "u", 24, L); dm(f"real:u24:{L}", num(b.r24))
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
lag_summary()


# ---------------------------------------------------------------- appendix: the default bootstrap against independent resampling
def boot_summary():
    """Macros bl:bs:* (appended to numbers.tex) for the appendix paragraph on the bootstrap."""
    if not (RESULTS / "boot_sens.csv").exists(): print("boot_sens.csv missing: run 10_bootstrap_sensitivity.py"); return
    B_ = pd.read_csv(RESULTS / "boot_sens.csv"); B_["fci"] = B_.fci.astype(str); key = ["form", "fci", "var", "h"]
    a = B_[B_.variant == "j12r"].set_index(key); b = B_[B_.variant == "iid"].set_index(key); a = a.loc[b.index]
    wr = ((b.hi - b.lo) / (a.hi - a.lo)); s10 = lambda x: (x.lo * x.hi > 0); s5 = lambda x: (x.lo95 * x.hi95 > 0); n = len(a)
    ml = []; dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:bs:" + k + r"\endcsname{" + v + "}")
    dm("n", str(n)); dm("wr:med", f"{wr.median():.2f}"); dm("wr:min", f"{wr.min():.2f}"); dm("wr:max", f"{wr.max():.2f}"); dm("wider", str(int((wr > 1).sum())))
    dm("same10", str(int((s10(a) == s10(b)).sum()))); dm("same5", str(int((s5(a) == s5(b)).sum()))); dm("sig10:block", str(int(s10(a).sum()))); dm("sig10:iid", str(int(s10(b).sum())))
    k = (HEAD_FORM, HEAD_FORM, "u", 24); dm("u24:lo", num(b.loc[k].lo)); dm("u24:hi", num(b.loc[k].hi)); dm("u24:lo5", num(a.loc[k].lo)); dm("u24:hi5", num(a.loc[k].hi))
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
boot_summary()


# ---------------------------------------------------------------- Section 5: summary table of the robustness tests (FS-A85 D6), macros
ROB = {}
def rob_summary():
    """tab_rob_summary.tex: the baseline and the six core tests, real (headline) and nominal with the FCI, unemployment gap and price level at 12 months, from 1996 and from 1973
    (the 1985 start in the 1996 columns only); macros bl:rob:<form>:<key><sx>:<u|P>. ROB holds (estimate, 10% significant, 5% significant) for the claims."""
    out_rows = []; ml = []; dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:rob:" + k + r"\endcsname{" + str(v) + "}")
    for fi, f in enumerate(("real", "nom")):
        out_rows.append((r"\addlinespace" if fi else "") + rf"\multicolumn{{5}}{{l}}{{\textit{{{CS.FORMS[f]} 2-year yield, funds rate and FCI}}}}\\")
        for key, lab, pid, sel, L in CORE_TESTS:
            pts, ivs = [], []
            for st, sx in STARTS:
                if pid == "R6" and sx: pts += ["", ""]; ivs += ["", ""]; continue
                d = core_row(pid, sel, sx, L, f)
                for v in ("u", "P"):
                    r = d[d["var"] == v].iloc[0]; ROB[(f, key, sx, v)] = (r.r12, r.lo12 * r.hi12 > 0, r.lo95_12 * r.hi95_12 > 0)
                    pts.append(num(r.r12) + stars(r, 12)); ivs.append(f"[{num(r.lo12)}, {num(r.hi12)}]")
                    dm(f"{f}:{key}{sx}:{v}", num(r.r12)); dm(f"{f}:{key}{sx}:{v}:abs", f"{abs(r.r12):.2f}"); dm(f"{f}:{key}{sx}:{v}:sig", "significant" if r.lo12 * r.hi12 > 0 else "not significant")
            out_rows += [f"{lab} & " + " & ".join(pts) + r"\\", " & " + " & ".join(rf"{{\scriptsize {x}}}" if x else "" for x in ivs) + r"\\"]
        if f == "real":                                                              # FS-A94: the index restriction (step 15), real version only; not in ROB (the claims on the core tests)
            pts, ivs = [], []
            for st, sx in STARTS:
                d = pd.read_csv(RESULTS / f"{CS.case_id(dict(form='real', fci='cmp', macro='u,pi', start=st, end=None, t2020='out', trend='none'))}.csv").query("lags == 12")
                for v in ("u", "P"):
                    r = d[d["var"] == v].iloc[0]; pts.append(num(r.r12) + stars(r, 12)); ivs.append(f"[{num(r.lo12)}, {num(r.hi12)}]")
            out_rows += ["FCI components free & " + " & ".join(pts) + r"\\", " & " + " & ".join(rf"{{\scriptsize {x}}}" for x in ivs) + r"\\"]
    tests = [k for k, *_ in CORE_TESTS if k != "base"]; dm("ntests", len(tests))
    for f in ("real", "nom"):
        for sx in ("", "73"):
            for v in ("u", "P"): dm(f"{f}:nsig{sx}:{v}", sum(ROB[(f, k, sx, v)][1] for k in tests if (f, k, sx, v) in ROB))
    out = [r"\begin{table}[tp]\centering\small", r"\caption{Robustness: Responses at 12 Months}\label{tab:robsummary}",
           r"\begin{tabular}{lcccc}\toprule & \multicolumn{2}{c}{Monthly equations from 1996} & \multicolumn{2}{c}{Monthly equations from 1973}\\ \cmidrule(lr){2-3}\cmidrule(lr){4-5} & Unemployment gap & Price level & Unemployment gap & Price level\\ \midrule",
           *out_rows, r"\bottomrule\end{tabular}",
           r"\begin{flushleft}\footnotesize\textit{Notes:} Two-year yield, federal funds rate and FCI in the stated version; responses 12 months after a policy move that raises the two-year yield 1 percentage point in the announcement window; unemployment gap in percentage points, price level in percent; 12 lags unless stated; March--December 2020 dropped unless stated. The 1985 start has monthly equations from January 1985 (1996 columns). $^{**}$ and $^{*}$: the 95\% and 90\% bootstrap intervals exclude zero; 90\% intervals in brackets. FCI components free (real version only): the three weighted components of the FCI replace it in the daily block and enter the monthly equations separately; the daily block then differs slightly from the baseline's, and the like-for-like comparison, with the FCI built from the components, is in the text. Full results at 12, 24 and 36 months for both versions are in the appendix.\end{flushleft}", r"\end{table}"]
    from lib import model as M_; dm("ratio1y", f"{M_.RATIO_1Y:.2f}")                 # 1-year / 2-year announcement-day response (appendix A4)
    (REPORT / "tab_rob_summary.tex").write_text("\n".join(out) + "\n")
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
rob_summary()


# ---------------------------------------------------------------- final section (FS-A85 D11): slow-moving rates and financial conditions
def final_section():
    """tab_slow_shares.tex: the share of the variance of the FCI, the 2-year yield, the funds rate, the unemployment gap and core inflation that a natural cubic spline in time fits (knots at the
    first and last estimation months and the NBER peaks inside), nominal and real, both samples; tab_slow_resp.tex: the baseline, the LW r*-gap step and the spline trend, nominal and real beside,
    responses at 12 and 24 months, both samples. Macros bl:slow:*."""
    from lib import model as M_
    ml = []; dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:slow:" + k + r"\endcsname{" + str(v) + "}")
    srows = []; series = (("idx", "FCI"), ("pol", "Two-year yield"), ("ff", "Federal funds rate"), ("u", "Unemployment gap"), ("pi", "Core PCE inflation"))
    for f in ("nom", "real", "rstar"):
        cells = []
        for st, sx in STARTS:
            X, Y, P_ = M_.macro_data(f, f, ["u", "pi"], 12, st, None, "out", "none", periods=True); FB = M_.fin_monthly(f, f).reindex(P_)
            Z = np.c_[np.ones(len(P_)), M_.trend_cols(P_, str(P_[0]), None)]
            for k, _ in series:
                y = (FB[k].values if k in FB else M_.MAC[k].reindex(P_).values); ok = ~np.isnan(y); b_ = np.linalg.lstsq(Z[ok], y[ok], rcond=None)[0]; e_ = y[ok] - Z[ok] @ b_
                r2 = 1 - e_ @ e_ / ((y[ok] - y[ok].mean()) @ (y[ok] - y[ok].mean())); cells.append(f"{100 * r2:.0f}"); dm(f"{f}{sx}:{k}", f"{100 * r2:.0f}")
        srows.append(f"{CS.FORMS[f] if f != 'rstar' else 'Relative to $r^*$'} & " + " & ".join(cells) + r"\\")
    head = " & ".join(lab for _, lab in series)
    (REPORT / "tab_slow_shares.tex").write_text("\n".join([r"\begin{table}[tp]\centering\scriptsize\setlength{\tabcolsep}{3pt}", r"\caption{Variance Fitted by a Spline Trend}\label{tab:slowshares}",
        r"\begin{tabular}{l" + "r" * (2 * len(series)) + r"}\toprule & \multicolumn{%d}{c}{Monthly equations from 1996} & \multicolumn{%d}{c}{Monthly equations from 1973}\\ \cmidrule(lr){2-%d}\cmidrule(lr){%d-%d}" % (len(series), len(series), 1 + len(series), 2 + len(series), 1 + 2 * len(series)),
        "Version & " + head + " & " + head + r"\\ \midrule", *srows, r"\bottomrule\end{tabular}",
        r"\begin{flushleft}\footnotesize\textit{Notes:} Percent of the variance of each monthly series (monthly averages over the estimation months of the model, 12 lags, March--December 2020 dropped) fitted by a natural cubic spline in time with knots at the first and last estimation months and at the NBER business-cycle peaks inside the sample. The unemployment gap and inflation do not depend on the version. $r^*$-gap: Laubach--Williams $r^*$.\end{flushleft}", r"\end{table}"]) + "\n")
    rows = []
    for st, sx in STARTS:
        rows.append(rf"\multicolumn{{9}}{{l}}{{\textit{{Monthly equations from {st[:4]}}}}}\\")
        specs = [("Baseline (no trend)", lambda f: dict(form=f, fci=f, **{**B96, "start": st})), ("Spline trend", lambda f: dict(form=f, fci=f, **{**B96, "start": st, "trend": "spline"}))]
        for lab, mk in specs:
            pts, ivs = [], []
            for f in ("nom", "real"):
                g = R[CS.case_id(mk(f))]; g = g[g.lags == MAIN_LAGS]
                for v in ("u", "P"):
                    r = g[g["var"] == v].iloc[0]
                    for h in (12, 24): pts.append(num(r[f"r{h}"]) + stars(r, h)); ivs.append(f"[{num(r[f'lo{h}'])}, {num(r[f'hi{h}'])}]"); dm(f"{'spl' if 'Spline' in lab else 'base'}{sx}:{f}:{v}:{h}", num(r[f"r{h}"]))
            rows += [f"{lab} & " + " & ".join(pts) + r"\\", " & " + " & ".join(rf"{{\tiny {x}}}" for x in ivs) + r"\\"]
        g = R[CS.case_id(dict(form="rstar", fci="rstar", **{**B96, "start": st}))]; g = g[g.lags == MAIN_LAGS]; pts, ivs = [], []
        for v in ("u", "P"):
            r = g[g["var"] == v].iloc[0]
            for h in (12, 24): pts.append(num(r[f"r{h}"]) + stars(r, h)); ivs.append(f"[{num(r[f'lo{h}'])}, {num(r[f'hi{h}'])}]"); dm(f"rstar{sx}:{v}:{h}", num(r[f"r{h}"])); dm(f"rstar{sx}:{v}:{h}:abs", f"{abs(r[f'r{h}']):.2f}")
        rows += [r"$r^*$-gap (LW) & \multicolumn{4}{c}{} & " + " & ".join(pts) + r"\\", r" & \multicolumn{4}{c}{} & " + " & ".join(rf"{{\tiny {x}}}" for x in ivs) + r"\\", r"\addlinespace"]
    (REPORT / "tab_slow_resp.tex").write_text("\n".join([r"\begin{table}[tp]\centering\scriptsize\setlength{\tabcolsep}{2.5pt}", r"\caption{Slow-Moving Rates: The $r^*$-Gap Step and a Spline Trend}\label{tab:slowresp}",
        r"\begin{tabular}{lrrrrrrrr}\toprule & \multicolumn{4}{c}{Nominal} & \multicolumn{4}{c}{Real (last row: relative to $r^*$)}\\ \cmidrule(lr){2-5}\cmidrule(lr){6-9} & \multicolumn{2}{c}{Unemployment gap} & \multicolumn{2}{c}{Price level} & \multicolumn{2}{c}{Unemployment gap} & \multicolumn{2}{c}{Price level}\\ & 12 m & 24 m & 12 m & 24 m & 12 m & 24 m & 12 m & 24 m\\ \midrule",
        *rows[:-1], r"\bottomrule\end{tabular}",
        r"\begin{flushleft}\footnotesize\textit{Notes:} Two-year yield, funds rate and FCI with the FCI, 12 lags, March--December 2020 dropped. Spline trend: natural cubic spline in time in every monthly equation (knots at the first and last estimation months and at NBER peaks inside). $r^*$-gap: rates less expected inflation and Laubach--Williams $r^*$, the FCI in the $r^*$-gap form. $^{**}$, $^{*}$: 95\% and 90\% bootstrap intervals exclude zero; 90\% intervals below.\end{flushleft}", r"\end{table}"]) + "\n")
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
final_section()

def components_test():
    """Robustness: the index restriction in the monthly equations (step 15, FS-A93; real version, 12 lags). tab_components.tex (appendix) and macros bl:cm:* appended to numbers.tex:
    bl:cm:<sx>:<R|F|D>:<u|P>:<h>[:lo|:hi|:abs] (R restricted = FCI built from the components, F all free, D paired difference F less R; sx '' = 1996, '73' = 1973),
    bl:cm:<sx>:p:<u|pi> (bootstrap p of equal coefficients), bl:cm:<sx>:aic:<u|pi>, bl:cm:<sx>:bic:<u|pi>."""
    ml = []; dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:cm:" + k + r"\endcsname{" + v + "}")
    Dif = pd.read_csv(RESULTS / "components_diff.csv"); Wt = pd.read_csv(RESULTS / "components_wald.csv"); rows = []
    for st, sx in (("1996-01", ""), ("1973-01", "73")):
        cs = {k: pd.read_csv(RESULTS / f"{CS.case_id(dict(form='real', fci=f, macro='u,pi', start=st, end=None, t2020='out', trend='none'))}.csv").query("lags == 12").set_index("var") for k, f in (("R", "cmpR"), ("F", "cmp"))}
        for k in ("R", "F"):
            for v in ("u", "P"):
                for h in (12, 24):
                    r = cs[k].loc[v]; dm(f"{sx}:{k}:{v}:{h}", num(r[f"r{h}"])); dm(f"{sx}:{k}:{v}:{h}:abs", f"{abs(r[f'r{h}']):.2f}"); dm(f"{sx}:{k}:{v}:{h}:lo", num(r[f"lo{h}"])); dm(f"{sx}:{k}:{v}:{h}:hi", num(r[f"hi{h}"]))
        dd = Dif[(Dif.start == st) & (Dif.contrast == "free-restricted")].set_index(["var", "h"])
        for v in ("u", "P"):
            for h in (12, 24):
                r = dd.loc[(v, h)]; dm(f"{sx}:D:{v}:{h}", num(r["diff"])); dm(f"{sx}:D:{v}:{h}:lo", num(r.lo)); dm(f"{sx}:D:{v}:{h}:hi", num(r.hi))
        for _, r in Wt[Wt.start == st].iterrows(): dm(f"{sx}:p:{r['eq']}", f"{r.p_boot:.3f}"); dm(f"{sx}:aic:{r['eq']}", f"{r.d_aic:.0f}"); dm(f"{sx}:bic:{r['eq']}", f"{r.d_bic:.0f}")
        # table rows for this start
        def trow(lab, k):
            if k == "D": pts = [num(dd.loc[(v, h)]["diff"]) + ("$^{**}$" if dd.loc[(v, h)].lo95 * dd.loc[(v, h)].hi95 > 0 else "$^{*}$" if dd.loc[(v, h)].lo * dd.loc[(v, h)].hi > 0 else "") for v in ("u", "P") for h in (12, 24)]; ivs = [f"[{num(dd.loc[(v, h)].lo)}, {num(dd.loc[(v, h)].hi)}]" for v in ("u", "P") for h in (12, 24)]
            else: pts = [num(cs[k].loc[v][f"r{h}"]) + stars(cs[k].loc[v], h) for v in ("u", "P") for h in (12, 24)]; ivs = [f"[{num(cs[k].loc[v][f'lo{h}'])}, {num(cs[k].loc[v][f'hi{h}'])}]" for v in ("u", "P") for h in (12, 24)]
            return [lab + " & " + " & ".join(pts) + r"\\", " & " + " & ".join(rf"{{\tiny {x}}}" for x in ivs) + r"\\"]
        rows += [rf"\multicolumn{{5}}{{l}}{{\textit{{Monthly equations from {st[:4]}}}}}\\"] + trow("FCI built from the components", "R") + trow("Components free", "F") + trow("Difference, free less restricted", "D")
        wt = Wt[Wt.start == st].set_index("eq")
        rows += [rf"Equal coefficients: bootstrap $p$ & \multicolumn{{2}}{{c}}{{{wt.loc['u'].p_boot:.3f}}} & \multicolumn{{2}}{{c}}{{{wt.loc['pi'].p_boot:.3f}}}\\", r"\addlinespace"]
    (REPORT / "tab_components.tex").write_text("\n".join([r"\begin{table}[tp]\centering\small", r"\caption{The Index Restriction: The FCI and Its Components (Real Version)}\label{tab:components}",
        r"\begin{tabular}{lrrrr}\toprule & \multicolumn{2}{c}{Unemployment gap (pp)} & \multicolumn{2}{c}{Price level (\%)}\\ \cmidrule(lr){2-3}\cmidrule(lr){4-5} & 12 m & 24 m & 12 m & 24 m\\ \midrule", *rows[:-1], r"\bottomrule\end{tabular}",
        r"\begin{flushleft}\footnotesize\textit{Notes:} Real two-year yield, funds rate and FCI, 12 lags, March--December 2020 dropped; per +1 pp on the two-year yield in the window. One daily block with the two rates and the three weighted components of the FCI (10-year yield, equity valuation, dollar); the window move of each component is its response to policy news, so the three add to the FCI's move. Restricted: the sum of the components (the FCI) as one regressor per lag in the monthly equations. Free: the three components as separate regressors. The two use the same bootstrap draws; the difference is paired. Equal coefficients: Wald test (HC1) that the three components have equal coefficients at every lag (24 restrictions), in the unemployment and the inflation equations, $p$-value from a block bootstrap under the restriction. $^{**}$, $^{*}$: 95\% and 90\% intervals exclude zero; 90\% intervals below.\end{flushleft}", r"\end{table}"]) + "\n")
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
components_test()

check_claims()                                                                       # after rob_summary (ROB)

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
fig, ax = plt.subplots(1, 1, figsize=(4.4, 2.8)); ax.axhline(0, color=GREY, lw=0.8)
c = next(c for c in base if c["form"] == HEAD_FORM and c["fci"] == HEAD_FORM); d = paths(c); d = d[d.kind == "fin"]
line(ax, d[d["var"] == "pol"], INK, "-", "2-year yield, real", alpha=0.10); line(ax, d[d["var"] == "idx"], GREY, "--", "FCI (2-year-yield units)", alpha=0.10)
line(ax, d[d["var"] == "ff"], BLUE, ":", "Federal funds rate, real", alpha=0.08)
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
    """Baseline figure: real rates with the FCI (bands), the nominal rates alone and with the FCI in the same model, and the Cholesky VAR of Section 3.1."""
    base = B96
    cs = dict(head=dict(form=HEAD_FORM, fci=HEAD_FORM, **base), nom0=dict(form="nom", fci=0, **base), nom1=dict(form="nom", fci="nom", **base))
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.9)); H_ = {}
    for ax, v, ylab in ((axs[0], "u", "Unemployment gap (pp)"), (axs[1], "P", "Core PCE price level (%)")):
        ax.axhline(0, color=GREY, lw=0.8)
        d = paths(cs["head"]); d = d[(d.kind == "macro") & (d["var"] == v)]
        ax.fill_between(d.h, d.lo, d.hi, color=BLUE, alpha=0.13, lw=0); ax.fill_between(d.h, d.lo68, d.hi68, color=BLUE, alpha=0.25, lw=0)
        H_["b"] = ax.plot(d.h, d.r, color=BLUE, lw=2.0)[0]
        for key, ls_ in (("nom0", "--"), ("nom1", ":")):
            e = paths(cs[key]); e = e[(e.kind == "macro") & (e["var"] == v)]; H_[key] = ax.plot(e.h, e.r, color=ORANGE, ls=ls_, lw=1.9)[0]
        c = ls_path("chol_2y_1996", v); H_["chol"] = ax.plot(c.h, c.point, color=INK, ls="-.", lw=1.5)[0]
        ax.set_xlabel("Months after the policy move"); ax.set_ylabel(ylab); ax.set_xlim(0, 36)
    labs = ["Real rates and FCI (baseline; bands: 68 and 90 percent)", "Nominal rates alone (same model)", "Nominal rates and FCI (same model)", "Recursive (Cholesky) VAR, 2-year yield (Section 3.1)"]
    fig.legend([H_["b"], H_["nom0"], H_["nom1"], H_["chol"]], labs, loc="lower center", ncol=2, frameon=False, fontsize=7.2)
    fig.tight_layout(rect=[0, 0.13, 1, 1]); fig.savefig(REPORT / "fig_size.pdf"); plt.close(fig)
fig_size()

def fig_steps():
    """fig_steps.pdf (1996) and fig_steps73.pdf (1973): columns = nominal and real, rows = unemployment gap and price level; rates alone (dashed) and with the FCI (solid); 68 and 90 percent bands."""
    for st, sx in STARTS:
        base = {**B96, "start": st}
        fig, axs = plt.subplots(2, 2, figsize=(7.0, 5.2), sharex=True)
        for j, f in enumerate(("nom", "real")):
            for i, (v, ylab) in enumerate((("u", "Unemployment gap (pp)"), ("P", "Core PCE price level (%)"))):
                ax = axs[i, j]; ax.axhline(0, color=GREY, lw=0.8)
                e = paths(dict(form=f, fci=0, **base)); e = e[(e.kind == "macro") & (e["var"] == v)]
                ax.fill_between(e.h, e.lo, e.hi, color=ORANGE, alpha=0.10, lw=0); ax.fill_between(e.h, e.lo68, e.hi68, color=ORANGE, alpha=0.20, lw=0); h2 = ax.plot(e.h, e.r, color=ORANGE, ls="--", lw=1.9)[0]
                d = paths(dict(form=f, fci=f, **base)); d = d[(d.kind == "macro") & (d["var"] == v)]
                ax.fill_between(d.h, d.lo, d.hi, color=BLUE, alpha=0.13, lw=0); ax.fill_between(d.h, d.lo68, d.hi68, color=BLUE, alpha=0.25, lw=0); h1 = ax.plot(d.h, d.r, color=BLUE, lw=2.0)[0]
                ax.set_xlim(0, 36)
                if i == 0: ax.set_title(f"{CS.FORMS[f]} rates and FCI", fontsize=8.5)
                if j == 0: ax.set_ylabel(ylab)
                if i == 1: ax.set_xlabel("Months after the policy move")
        for i in range(2):
            lo = min(axs[i, 0].get_ylim()[0], axs[i, 1].get_ylim()[0]); hi = max(axs[i, 0].get_ylim()[1], axs[i, 1].get_ylim()[1]); axs[i, 0].set_ylim(lo, hi); axs[i, 1].set_ylim(lo, hi)
        fig.legend([h1, h2], ["Two-year yield, funds rate and FCI", "Two-year yield and funds rate"], loc="lower center", ncol=2, frameon=False, fontsize=7.5)
        fig.tight_layout(rect=[0, 0.05, 1, 1]); fig.savefig(REPORT / f"fig_steps{sx}.pdf"); plt.close(fig)
fig_steps()

def fig_intro():
    """Figure 1: the headline (real) version, rates alone and with the FCI; columns = monthly equations from 1996 and from 1973, rows = unemployment gap and price level; 68 and 90 percent bands."""
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 5.2), sharex=True)
    for j, (st, title) in enumerate((("1996-01", "Monthly equations from 1996"), ("1973-01", "Monthly equations from 1973"))):
        base = {**B96, "start": st}
        for i, (v, ylab) in enumerate((("u", "Unemployment gap (pp)"), ("P", "Core PCE price level (%)"))):
            ax = axs[i, j]; ax.axhline(0, color=GREY, lw=0.8)
            e = paths(dict(form=HEAD_FORM, fci=0, **base)); e = e[(e.kind == "macro") & (e["var"] == v)]
            ax.fill_between(e.h, e.lo, e.hi, color=ORANGE, alpha=0.10, lw=0); ax.fill_between(e.h, e.lo68, e.hi68, color=ORANGE, alpha=0.20, lw=0); h2 = ax.plot(e.h, e.r, color=ORANGE, ls="--", lw=1.9)[0]
            d = paths(dict(form=HEAD_FORM, fci=HEAD_FORM, **base)); d = d[(d.kind == "macro") & (d["var"] == v)]
            ax.fill_between(d.h, d.lo, d.hi, color=BLUE, alpha=0.13, lw=0); ax.fill_between(d.h, d.lo68, d.hi68, color=BLUE, alpha=0.25, lw=0); h1 = ax.plot(d.h, d.r, color=BLUE, lw=2.0)[0]
            ax.set_xlim(0, 36)
            if i == 0: ax.set_title(title, fontsize=8.5)
            if j == 0: ax.set_ylabel(ylab)
            if i == 1: ax.set_xlabel("Months after the policy move")
    for i in range(2):
        lo = min(axs[i, 0].get_ylim()[0], axs[i, 1].get_ylim()[0]); hi = max(axs[i, 0].get_ylim()[1], axs[i, 1].get_ylim()[1]); axs[i, 0].set_ylim(lo, hi); axs[i, 1].set_ylim(lo, hi)
    fig.legend([h1, h2], ["Real two-year yield, funds rate and FCI", "Real two-year yield and funds rate"], loc="lower center", ncol=2, frameon=False, fontsize=7.5)
    fig.tight_layout(rect=[0, 0.05, 1, 1]); fig.savefig(REPORT / "fig_intro.pdf"); plt.close(fig)
fig_intro()
from lib import latex_style as LST
LST.restyle_dir(REPORT)                                                              # house LaTeX style: [tp] floats, Title Case captions, notes below the table
print("report inputs written to", REPORT)
