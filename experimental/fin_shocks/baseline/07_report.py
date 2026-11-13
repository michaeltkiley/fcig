"""Step 7. Tables and figures of the results document from results/ (12-lag main tables by section, 3/6/12-lag appendix tables by panel, the response
figures, the weights table and the trade-off table). Compile report/baseline_robustness.tex with pdflatex (twice).   python3 05_report.py"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cases as CS
from lib.paths import RESULTS, REPORT, OUT, DATA

R = {CS.case_id(c): pd.read_csv(RESULTS / f"{CS.case_id(c)}.csv") for c in CS.unique_cases()}
MAIN_LAGS = 12
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

for g, pids in CS.GROUPS.items():                                                  # main text: 12 lags
    blocks = []
    for pid in pids:
        p = CS.panel_by_id(pid)
        if g == "B": blocks += [(CS.FORMS[f], [c for c in p["cases"] if c["form"] == f]) for f in ("nom", "real", "rstar")]
        elif g == "R4": blocks += [(CS.FORMS[f] + (", start 1973" if pid == "R4b" else ""), [c for c in p["cases"] if c["form"] == f]) for f in ("nom", "real", "rstar")]
        else: blocks.append((CS.SHORT[pid], p["cases"]))
    notes = CS.GROUP_NOTE[g]
    (REPORT / f"tab_main_{g}.tex").write_text(table(CS.GROUP_TITLE[g] + " (12 lags)", f"tab:main{g}", blocks, (MAIN_LAGS,), notes) + "\n")
for p in CS.PANELS:                                                                  # appendix: 3, 6, 12 lags
    f = lambda c: CS.FORMS[c["form"]]
    blocks = [(CS.FORMS[fm], [c for c in p["cases"] if c["form"] == fm]) for fm in dict.fromkeys(c["form"] for c in p["cases"])] if p["id"] in ("B", "R4", "R4b", "R4c") else [(f(p["cases"][0]), p["cases"])]
    (REPORT / f"tab_app_{p['id']}.tex").write_text(table(p["title"], f"tab:app{p['id']}", blocks, (3, 6, 12), p["notes"], "p") + "\n")

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
MNOTE = (r"Monthly VAR in the unemployment gap, core PCE inflation, the end-of-month 2-year yield and, when included, the end-of-month FCI (same version), 1996 to September 2026, no trend, nothing dropped. "
         r"Proxy VAR: Nakamura--Steinsson surprise as instrument; sets are exact 90\% Anderson--Rubin sets, ``unbounded'' when the instrument cannot reject large effects. "
         r"Window impact: impact vector taken from the daily model (the end-of-month response to a window surprise); 90\% bootstrap intervals. Unit in both: +1 pp on the 2-year yield (the end-of-month response to a +1 pp window surprise is 0.92 to 1.01, so the two units are the same up to 8\%). $^{*}$ = 90\% interval excludes zero.")
(REPORT / "tab_main_monthly.tex").write_text(monthly_table("Monthly VAR benchmark (12 lags)", "tab:mainmonthly", (12,), MNOTE, "1996-01") + "\n")
(REPORT / "tab_app_monthly.tex").write_text(monthly_table("Monthly VAR benchmark (3, 6 and 12 lags)", "tab:appmonthly", (3, 6, 12), MNOTE, "1996-01", "p") + "\n")
frows = []
for step in ("nom", "real", "rstar"):
    for fci in (0, step):
        d = MON[CS.monthly_id(dict(step=step, fci=fci, start="1996-01"))]; g = d[(d.ident == "P1") & (d["var"] == "u") & (d.h == 12)].set_index("lags")
        frows.append(f"{CS.FORMS[step] if fci == 0 else ''} & {CS.FCI_LABEL[fci]} & " + " & ".join(f"{g.F[L]:.1f}" for L in (3, 6, 12)) + " & " + (f"{num(g.impact_fci[12])} & {num(g.eom_fci[12])}" if fci else " & ") + r"\\")
(REPORT / "tab_monthly_F.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Monthly proxy VAR: first-stage strength and impact on the FCI}\label{tab:monthlyF}",
    r"\begin{tabular}{llrrrrr}\toprule 2-year & FCI & $F$ (3 lags) & $F$ (6) & $F$ (12) & Proxy impact on FCI & Model impact on FCI\\ \midrule", *frows, r"\bottomrule\end{tabular}",
    r"\par\smallskip\parbox{0.92\linewidth}{\scriptsize $F$: robust first-stage statistic of the policy-variable residual on the instrument (instrument months only, 1996--2026). Impact on FCI: end-of-month response of the FCI per +1 pp on the end-of-month 2-year yield, estimated from monthly residuals (proxy VAR, 12 lags) and implied by the daily model.}", r"\end{table}"]) + "\n")

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
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize 1,000 samples of 369 months generated by the estimated r*-gap model with the FCI (12 lags), with the data's calendar and announcement days; policy reaches unemployment and prices only through the 2-year yield and the FCI. Data: the 1996 sample, 12 lags, r*-gap measures; end-of-month series in the monthly VAR. True: the model's response per +1 pp on the 2-year yield, in the window (panel C) and on the end-of-month yield (panels A and B; the window response divided by the model's end-of-month response of 0.92--1.01). Simulated: median and 5th--95th percentiles of the estimates.}", r"\end{table}"]
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
    dd = R[CS.case_id(dict(form="rstar", fci="rstar", macro="u,pi", start="1996-01", end=None, t2020="in", trend="none"))]; dd = dd[dd.lags == MAIN_LAGS]; cs_ = []
    for v in ("u", "P"):
        for h in (12, 24):
            r = dd[dd["var"] == v].iloc[0]; cs_.append((num(r[f"r{h}"]) + ("$^{*}$" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else ""), f"[{num(r[f'lo{h}'])}, {num(r[f'hi{h}'])}]"))
    main = [r"Main model (daily block) & " + " & ".join(c[0] for c in cs_) + r"\\", " & " + " & ".join(rf"{{\scriptsize {c[1]}}}" for c in cs_) + r"\\"]
    out = [r"\begin{table}[H]\centering\small", r"\caption{Monthly VARs with the FCI and the main model ($r^*$-gap two-year yield and FCI; 12 lags)}\label{tab:monthlycompact}",
           r"\begin{tabular}{lrrrr}\toprule & \multicolumn{2}{c}{Unemployment gap (pp)} & \multicolumn{2}{c}{Price level (\%)}\\ \cmidrule(lr){2-3}\cmidrule(lr){4-5} & 12 m & 24 m & 12 m & 24 m\\ \midrule",
           *mrow("P1", "Proxy VAR"), *mrow("WE", "Window-impact VAR"), *main, r"\bottomrule\end{tabular}",
           r"\par\smallskip\parbox{0.8\linewidth}{\scriptsize Per +1 pp on the two-year yield. $^{*}$: the 90\% interval excludes zero; intervals in brackets (Anderson--Rubin sets for the proxy VAR; bootstrap for the others). Monthly VARs use end-of-month values.}", r"\end{table}"]
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
    for f in ("nom", "real", "rstar"):
        for fci, fk in ((0, "no"), (f, "yes")):
            dd = R[CS.case_id(dict(form=f, fci=fci, macro="u,pi", start="1996-01", end=None, t2020="in", trend="none"))]; g = dd[dd.lags == MAIN_LAGS]
            for v in ("u", "P"):
                r = g[g["var"] == v].iloc[0]
                for h in (12, 24, 36):
                    k = f"{f}:{fk}:{v}:{h}"; d("bl:" + k, num(r[f"r{h}"])); d("blabs:" + k, f"{abs(r[f'r{h}']):.2f}"); d("blsig:" + k, "significant" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "not significant")
                    d("bllo:" + k, num(r[f"lo{h}"])); d("blhi:" + k, num(r[f"hi{h}"]))
    n = R[CS.case_id(dict(form="rstar", fci="rstar", macro="u,pi", start="1996-01", end=None, t2020="in", trend="none"))]; d("bl:nobs", str(int(n[n.lags == MAIN_LAGS].nobs.iloc[0])))
    BASE = dict(macro="u,pi", start="1996-01", end=None, t2020="in", trend="none")
    pth = lambda f, fci: (lambda d: d[d.lags == MAIN_LAGS])(pd.read_csv(RESULTS / f"{CS.case_id(dict(form=f, fci=fci, **BASE))}_paths.csv"))
    for f, fci, fk in (("nom", 0, "nom"), ("rstar", "rstar", "rstar")):                               # 2-year yield at the end of the announcement month, per +1 pp in the window
        e = pth(f, fci); d("bl:eom:" + fk, f"{e[(e.kind == 'fin_eom') & (e.h == 0)].r.iloc[0]:.2f}")
    u = pth("nom", 0); u = u[(u.kind == "macro") & (u["var"] == "u")]; i = u.r.idxmin(); d("bl:path:nom:no:u:min", num(u.r[i])); d("bl:path:nom:no:u:minh", str(int(u.h[i])))
    u = pth("rstar", "rstar"); u = u[(u.kind == "macro") & (u["var"] == "u")]; i = u.r.idxmax(); d("bl:path:rstar:yes:u:max", num(u.r[i])); d("bl:path:rstar:yes:u:maxh", str(int(u.h[i])))
    LS = pd.read_csv(RESULTS / "lit_style.csv").query("lags == 12"); LSI = pd.read_csv(RESULTS / "lit_style_info.csv").query("lags == 12").set_index("case")
    for key, case in (("c2y96", "chol_2y_1996"), ("c2y84", "chol_2y_1984"), ("cffr", "chol_ffr_1984_2007"), ("c2ycom", "chol_2y_1996_com"), ("cffrcom", "chol_ffr_1984_2007_com"), ("prox", "proxy_2y_1996")):
        for v in ("u", "P"):
            for h in (0, 12, 24, 36):
                r = LS[(LS.case == case) & (LS["var"] == v) & (LS.h == h)].iloc[0]; k = f"st:{key}:{v}:{h}"
                d("bl:" + k, num(r.point)); d("blabs:" + k, f"{abs(r.point):.2f}"); d("bllo:" + k, num(r.lo)); d("blhi:" + k, num(r.hi)); d("blsig:" + k, "significant" if r.lo * r.hi > 0 else "not significant")
        d("bl:st:" + key + ":nobs", str(int(LSI.nobs[case])))
    d("bl:st:prox:F", f"{LSI.F['proxy_2y_1996']:.1f}")
    # monthly VAR with the end-of-month 2-year yield and FCI (12 lags)
    for f in ("nom", "real", "rstar"):
        for fci, fk in ((0, "no"), (f, "yes")):
            m = MON[CS.monthly_id(dict(step=f, fci=fci, start="1996-01"))]; m = m[m.lags == MAIN_LAGS]; d(f"bl:mo:{f}:{fk}:F", f"{m.F.iloc[0]:.1f}")
            if fci: d(f"bl:mo:{f}:{fk}:impf", num(m.impact_fci.iloc[0])); d(f"bl:mo:{f}:{fk}:modf", num(m.eom_fci.iloc[0]))
            for ident in ("P1", "WE"):
                for v in ("u", "P"):
                    for h in (12, 24, 36):
                        r = m[(m.ident == ident) & (m["var"] == v) & (m.h == h)].iloc[0]; k = f"mo:{f}:{fk}:{ident}:{v}:{h}"
                        d("bl:" + k, num(r.r)); d("blabs:" + k, f"{abs(r.r):.2f}"); d("bllo:" + k, "$-\\infty$" if np.isinf(r.lo) else num(r.lo)); d("blhi:" + k, "$+\\infty$" if np.isinf(r.hi) else num(r.hi))
                        d("blsig:" + k, "unbounded" if r.unbounded else ("significant" if r.lo * r.hi > 0 else "not significant"))
    # simulation (r*-gap model as the true process)
    for _, r in SIM.iterrows():
        k = f"sim:{r.system}:{r.quantity}"; f = "{:.1f}" if r.quantity == "F" else "{:.2f}"; sg = lambda x: ("$-$" if x < 0 and f.format(abs(x)) != "0.00" else "") + f.format(abs(x))
        d("bl:" + k + ":data", sg(r.data)); d("bl:" + k + ":med", sg(r.sim_median)); d("bl:" + k + ":lo", sg(r.sim_p05)); d("bl:" + k + ":hi", sg(r.sim_p95)); d("bl:" + k + ":share", f"{100 * r.share_le_data:.0f}")
        if pd.notna(r.truth): d("bl:" + k + ":truth", sg(r.truth))
    # trade-off (Phillips multiplier)
    TT = pd.read_csv(RESULTS / "tradeoff.csv"); TT["fci"] = TT.fci.astype(str); TD = pd.read_csv(RESULTS / "tradeoff_diff.csv")
    for f in ("nom", "real", "rstar"):
        for fci, fk in ((0, "no"), (f, "yes")):
            t = TT[(TT.form == f) & (TT.fci == str(fci)) & (TT.macro == "u,pi") & (TT.start == "1996-01") & TT.end.isna() & (TT.t2020 == "in") & (TT.trend == "none") & (TT.lags == MAIN_LAGS)]
            for H in (24, 36):
                r = t[t.H == H].iloc[0]; k = f"tr:{f}:{fk}:{H}"
                d("bl:" + k, num(r.kappa)); d("blabs:" + k, f"{abs(r.kappa):.2f}"); d("bl:" + k + ":sac", f"{abs(1 / r.kappa):.1f}")
                d("bllo:" + k, "$-\\infty$" if np.isinf(r.k_lo) else num(r.k_lo)); d("blhi:" + k, "$+\\infty$" if np.isinf(r.k_hi) else num(r.k_hi))
                d("blsig:" + k, "bounded away from zero" if (not np.isinf(r.k_lo) and not np.isinf(r.k_hi) and r.k_lo * r.k_hi > 0) or (np.isinf(r.k_lo) != np.isinf(r.k_hi) and (r.k_hi < 0 if np.isinf(r.k_lo) else r.k_lo > 0)) else "includes zero")
    # robustness panels (12 lags): rb:<panel>:<no|yes>:<u|P>:<h> (no = same step without the FCI, yes = with it; panel R4: the FCI replaced by its components)
    for pid in ("R1a", "R1b", "R1c", "R1d", "R1e", "R2a", "R2b", "R2c", "R2d", "R3a", "R3b", "R4", "R4b", "R5a", "R5b"):
        for cs in CS.panel_by_id(pid)["cases"]:
            fk = "cmp" if cs["fci"] == "cmp" else ("no" if cs["fci"] == 0 else "yes"); form_tag = f":{cs['form']}" if pid.startswith("R4") else ""
            dd = R[CS.case_id(cs)]; g_ = dd[dd.lags == MAIN_LAGS]
            for v in ("u", "P"):
                r = g_[g_["var"] == v].iloc[0]
                for h in (12, 24, 36):
                    k = f"rb:{pid}{form_tag}:{fk}:{v}:{h}"; d("bl:" + k, num(r[f"r{h}"])); d("blabs:" + k, f"{abs(r[f'r{h}']):.2f}"); d("blsig:" + k, "significant" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "not significant")
                    d("bllo:" + k, num(r[f"lo{h}"])); d("blhi:" + k, num(r[f"hi{h}"]))
    WT = _wt()
    for _, r in WT[(WT.lags == MAIN_LAGS) & (WT.start == "1996-01")].iterrows(): e_ = r["eq"]; d(f"bl:wt:{r.step}:{e_}:p", f"{r.p_boot:.3f}"); d(f"bl:wt:{r.step}:{e_}:W", f"{r.wald:.1f}"); d(f"bl:wt:{r.step}:{e_}:q", str(int(r.restrictions)))
    for _, r in WT[(WT.lags == MAIN_LAGS) & (WT.start == "1973-01")].iterrows(): d(f"bl:wt73:{r.step}:{r['eq']}:p", f"{r.p_boot:.3f}")
    w73 = WT[(WT.lags == MAIN_LAGS) & (WT.start == "1973-01")].p_boot; d("bl:wt73:min", f"{w73.min():.2f}"); d("bl:wt73:max", f"{w73.max():.2f}")
    for nm_, st_, tz_ in (("R1b", "1996-01", "out"), ("R1c", "1973-01", "out")):                    # trade-off in the 2020-dropped samples
        t = TT[(TT.form == "rstar") & (TT.fci == "rstar") & (TT.macro == "u,pi") & (TT.start == st_) & TT.end.isna() & (TT.t2020 == tz_) & (TT.trend == "none") & (TT.lags == MAIN_LAGS) & (TT.H == 24)].iloc[0]
        d(f"bl:trs:{nm_}:24", num(t.kappa))
    from lib import daily as DD
    for nm in ("bs", "jk"): DD.use_surprise(nm); d(f"bl:ev:{nm}", str(len(DD.event_index())))
    DD.use_surprise("ns")
    from lib.daily import window_impact, event_index, EV
    from lib import monthly as MO
    from lib.model import MAC, fin_eom
    d("bl:bF", f"{window_impact(event_index())[1]:.2f}")
    for f in ("nom", "real", "rstar"):                                  # FCI innovation per unit of 2-year-yield innovation in ordinary months (monthly VAR residuals, 12 lags, 1996+, end-of-month)
        D = MAC[["u", "pi"]].join(fin_eom(f, f), how="inner").dropna(); X, Y, _ = MO.design(D, 12, "1996-01"); r = Y - X @ np.linalg.lstsq(X, Y, rcond=None)[0]
        d(f"bl:ord:{f}", f"{np.cov(r[:, 3], r[:, 2])[0, 1] / np.var(r[:, 2], ddof=1):.2f}")
    ie = event_index(); s_ = EV.ns.values[ie]                           # share of each window move explained by the policy-news surprise (R-squared)
    for col, k in (("UST2Y", "y2"), ("UST10Y", "y10"), ("SP500", "sp"), ("DXY", "usd"), ("idx_win", "fci")): d(f"bl:r2:{k}", f"{100 * np.corrcoef(s_, EV[col].values[ie])[0, 1] ** 2:.0f}")
    (REPORT / "numbers.tex").write_text("\n".join(L) + "\n")
write_numbers()

def check_claims():
    """The qualitative claims made in the note's Sections 3.1-3.2; raises an error if any stops being true of the results."""
    def g(f, fk, v, h):
        dd = R[CS.case_id(dict(form=f, fci=0 if fk == "no" else f, macro="u,pi", start="1996-01", end=None, t2020="in", trend="none"))]; r = dd[(dd.lags == MAIN_LAGS) & (dd["var"] == v)].iloc[0]
        return r[f"r{h}"], r[f"lo{h}"] * r[f"hi{h}"] > 0, r[f"lo95_{h}"] * r[f"hi95_{h}"] > 0
    est = lambda *k: g(*k)[0]; sig = lambda *k: g(*k)[1]; sig5 = lambda *k: g(*k)[2]; S = ("nom", "real", "rstar"); bad = []
    chk = lambda name, ok: None if ok else bad.append(name)
    for f in ("nom", "real"):
        chk(f"{f}: yield alone, unemployment falls significantly at 12 m", est(f, "no", "u", 12) < 0 and sig(f, "no", "u", 12)); chk(f"{f}: yield alone, price level does not respond significantly at 24 m", not sig(f, "no", "P", 24))
    chk("rstar: yield alone, unemployment does not rise (12, 24 m)", est("rstar", "no", "u", 12) < 0.0 and not sig("rstar", "no", "u", 12) and not sig("rstar", "no", "u", 24)); chk("rstar: yield alone, price level falls significantly at 24 m", est("rstar", "no", "P", 24) < 0 and sig("rstar", "no", "P", 24))
    for f in S:
        chk(f"{f}: with FCI, no significant fall in unemployment", all(not (est(f, "yes", "u", h) < 0 and sig(f, "yes", "u", h)) for h in (12, 24, 36)))
        chk(f"{f}: with FCI, unemployment positive at 24 and 36 m", est(f, "yes", "u", 24) > 0 and est(f, "yes", "u", 36) > 0)
        chk(f"{f}: with FCI, price level falls at 12, 24, 36 m", all(est(f, "yes", "P", h) < 0 for h in (12, 24, 36)))
    chk("with FCI, unemployment not significantly negative at any step and horizon", not any(est(f, "yes", "u", h) < 0 and sig(f, "yes", "u", h) for f in ("nom", "real", "rstar") for h in (12, 24, 36)))
    chk("with FCI, price level significant at 10% at 24 and 36 m at the real and r*-gap steps and not at the nominal step (upper bounds 0.02 and 0.01), and at 5% at 12, 24 and 36 m at the real and r*-gap steps", all(sig(f, "yes", "P", h) for f in ("real", "rstar") for h in (24, 36)) and not any(sig("nom", "yes", "P", h) for h in (24, 36)) and all(sig5(f, "yes", "P", h) for f in ("real", "rstar") for h in (12, 24, 36)))
    chk("r*-gap with FCI has the largest price fall at 24 m", est("rstar", "yes", "P", 24) < min(est("nom", "yes", "P", 24), est("real", "yes", "P", 24)))
    LS = pd.read_csv(RESULTS / "lit_style.csv").query("lags == 12"); ls = lambda c, v, h: LS[(LS.case == c) & (LS["var"] == v) & (LS.h == h)].iloc[0]; lsig = lambda c, v, h: ls(c, v, h).lo * ls(c, v, h).hi > 0
    for c in ("chol_2y_1996", "chol_2y_1984", "proxy_2y_1996"):
        chk(f"{c}: unemployment falls significantly at 12 m", ls(c, "u", 12).point < 0 and lsig(c, "u", 12)); chk(f"{c}: price level not significantly different from zero at 12, 24, 36 m", not any(lsig(c, "P", h) for h in (12, 24, 36)))
    for c in ("chol_2y_1996", "chol_2y_1984"): chk(f"{c}: unemployment significantly negative also at 24 m", ls(c, "u", 24).point < 0 and lsig(c, "u", 24))
    chk("proxy VAR: unemployment significantly negative at 24 m", ls("proxy_2y_1996", "u", 24).point < 0 and lsig("proxy_2y_1996", "u", 24))
    chk("chol_ffr_1984_2007: unemployment point estimate negative at 12 and 24 m, upper bound at most 0.02 (borderline, not clearly significant)", all(ls("chol_ffr_1984_2007", "u", h).point < 0 and ls("chol_ffr_1984_2007", "u", h).hi <= 0.02 for h in (12, 24)))
    chk("commodity-price control: 2-year Cholesky unemployment fall at 12 m still significant; funds-rate version negative at 12 m", ls("chol_2y_1996_com", "u", 12).point < 0 and lsig("chol_2y_1996_com", "u", 12) and ls("chol_ffr_1984_2007_com", "u", 12).point < 0)
    chk("baseline unemployment response at 12 m is above the Cholesky 2-year response and positive; nominal yield alone is of the same sign as the Cholesky", est("rstar", "yes", "u", 12) > 0 > ls("chol_2y_1996", "u", 12).point and est("nom", "no", "u", 12) < 0)
    mo = lambda f, fk, i, v, h: (lambda m: m[(m.lags == MAIN_LAGS) & (m.ident == i) & (m["var"] == v) & (m.h == h)].iloc[0])(MON[CS.monthly_id(dict(step=f, fci=0 if fk == "no" else f, start="1996-01"))])
    chk("monthly proxy VAR r*-gap with FCI: first-stage F below 10", mo("rstar", "yes", "P1", "u", 12).F < 10)
    chk("monthly window-impact VAR r*-gap with FCI: unemployment up and price level down, 12-36 m", all(mo("rstar", "yes", "WE", "u", h).r > 0 for h in (12, 24, 36)) and all(mo("rstar", "yes", "WE", "P", h).r < 0 for h in (12, 24, 36)))
    chk("monthly proxy VAR nominal without FCI: unemployment falls significantly at 12 m", mo("nom", "no", "P1", "u", 12).r < 0 and mo("nom", "no", "P1", "u", 12).lo * mo("nom", "no", "P1", "u", 12).hi > 0)
    sm = lambda s, q: SIM[(SIM.system == s) & (SIM.quantity == q)].iloc[0]
    chk("simulation: proxy VAR with FCI is noisy (90% range of u at 12 m wider than 1 pp and covering zero)", sm("proxy_fci", "u12").sim_p95 - sm("proxy_fci", "u12").sim_p05 > 1 and sm("proxy_fci", "u12").sim_p05 < 0 < sm("proxy_fci", "u12").sim_p95)
    chk("simulation: window-impact range narrower than the proxy-with-FCI range (u, 12 m)", sm("window", "u12").sim_p95 - sm("window", "u12").sim_p05 < sm("proxy_fci", "u12").sim_p95 - sm("proxy_fci", "u12").sim_p05)
    chk("simulation: data values lie inside the simulated 5-95 ranges (proxy with FCI: F and u12; proxy without FCI: u12)", all(sm(a, b).sim_p05 <= sm(a, b).data <= sm(a, b).sim_p95 for a, b in (("proxy_fci", "F"), ("proxy_fci", "u12"), ("proxy_nofci", "u12"))))
    chk("simulation: first-stage F below the data value in fewer than 25 percent of samples", sm("proxy_fci", "F").share_le_data < 0.25)
    chk("simulation: window-impact VAR centred on the truth (median within 0.05 of truth)", abs(sm("window", "u12").sim_median - sm("window", "u12").truth) < 0.05)
    chk("simulation: proxy VAR without FCI biased toward zero (median below half the truth)", sm("proxy_nofci", "u12").sim_median < 0.5 * sm("proxy_nofci", "u12").truth)
    # Section 4 (robustness) claims
    def rb(pid, fk, v, h):
        cs = next(x for x in CS.panel_by_id(pid)["cases"] if (x["fci"] == 0) == (fk == "no")); dd = R[CS.case_id(cs)]; r = dd[(dd.lags == MAIN_LAGS) & (dd["var"] == v)].iloc[0]; return r[f"r{h}"], r[f"lo{h}"] * r[f"hi{h}"] > 0, r[f"lo{h}"], r[f"hi{h}"]
    for pid in ("R1a", "R1b", "R1c", "R1d", "R1e"): chk(f"{pid}: with FCI unemployment positive at 12 m", rb(pid, "yes", "u", 12)[0] > 0); chk(f"{pid}: with FCI price level negative at 12, 24, 36 m", all(rb(pid, "yes", "P", h)[0] < 0 for h in (12, 24, 36)))
    chk("R2b and R2d (1973): price level negative with FCI at 12, 24, 36 m", all(rb(p_, "yes", "P", h)[0] < 0 for p_ in ("R2b", "R2d") for h in (12, 24, 36)))
    chk("R2c: unemployment without FCI negative, with FCI positive at 12 m; R3a: unemployment with FCI positive at 24 m and price level negative at 24 m", rb("R2c", "no", "u", 12)[0] < 0 < rb("R2c", "yes", "u", 12)[0] and rb("R3a", "yes", "u", 24)[0] > 0 and rb("R3a", "yes", "P", 24)[0] < 0)
    chk("R1: with FCI unemployment significant at 12 m in all but the 1973 start", all(rb(p_, "yes", "u", 12)[1] for p_ in ("R1b", "R1c", "R1d", "R1e")) and not rb("R1a", "yes", "u", 12)[1])
    chk("R1: price level significant at 12, 24, 36 m with and without the FCI in the three samples starting 1973", all(rb(p_, fk, "P", h)[1] and rb(p_, fk, "P", h)[0] < 0 for p_ in ("R1a", "R1c", "R1e") for fk in ("no", "yes") for h in (12, 24, 36)))
    chk("R1b: price level significant with the FCI at 24 m; R1d (ends 2019, from 1996): not significant at 12, 24, 36 m", rb("R1b", "yes", "P", 24)[1] and not any(rb("R1d", "yes", "P", h)[1] for h in (12, 24, 36)))
    chk("R1d: unemployment with FCI significant only at 12 m", rb("R1d", "yes", "u", 12)[1] and not rb("R1d", "yes", "u", 24)[1] and not rb("R1d", "yes", "u", 36)[1])
    chk("R2a (Kiley): unemployment without FCI falls significantly at 12 m; with FCI positive at 12 and 24 m, price level negative at 12 and 24 m", rb("R2a", "no", "u", 12)[0] < 0 and rb("R2a", "no", "u", 12)[1] and rb("R2a", "yes", "u", 12)[0] > 0 and rb("R2a", "yes", "u", 24)[0] > 0 and rb("R2a", "yes", "P", 12)[0] < 0 and rb("R2a", "yes", "P", 24)[0] < 0)
    chk("R2b (Kiley, 1973): price level with FCI significant at 12, 24, 36 m; unemployment not", all(rb("R2b", "yes", "P", h)[1] for h in (12, 24, 36)) and not any(rb("R2b", "yes", "u", h)[1] for h in (12, 24, 36)))
    chk("R2c (real + spline): unemployment without FCI falls significantly at 12 m, with FCI positive and not significant; price level with FCI not significant", rb("R2c", "no", "u", 12)[0] < 0 and rb("R2c", "no", "u", 12)[1] and rb("R2c", "yes", "u", 12)[0] > 0 and not any(rb("R2c", "yes", v, h)[1] for v in ("u", "P") for h in (12, 24, 36)))
    chk("R2d (real + spline, 1973): with FCI price level significant at 12, 24, 36 m; unemployment positive but not significant", all(rb("R2d", "yes", "P", h)[1] for h in (12, 24, 36)) and all(rb("R2d", "yes", "u", h)[0] > 0 and not rb("R2d", "yes", "u", h)[1] for h in (12, 24, 36)))
    chk("R3a (EBP): with FCI unemployment significant at 24 m (not 12); price significant at 12, 24, 36 m, also without the FCI", rb("R3a", "yes", "u", 24)[1] and not rb("R3a", "yes", "u", 12)[1] and all(rb("R3a", fk, "P", h)[1] for fk in ("no", "yes") for h in (12, 24, 36)))
    chk("R3a: unemployment without FCI nearer zero than the baseline without FCI at 12 m", abs(rb("R3a", "no", "u", 12)[0]) < abs(est("rstar", "no", "u", 12)))
    chk("R3b (EBP, 1973): unemployment close to zero (|r| < 0.1) with and without the FCI at 12, 24, 36 m; price significant in both", all(abs(rb("R3b", fk, "u", h)[0]) < 0.1 for fk in ("no", "yes") for h in (12, 24, 36)) and all(rb("R3b", fk, "P", h)[1] for fk in ("no", "yes") for h in (12, 24, 36)))
    cm = lambda f, v, h: (lambda dd: dd[(dd.lags == MAIN_LAGS) & (dd["var"] == v)].iloc[0])(R[CS.case_id(dict(form=f, fci="cmp", macro="u,pi", start="1996-01", end=None, t2020="in", trend="none"))])
    chk("R4 (components): unemployment point estimate positive at 12 and 24 m at every step", all(cm(f, "u", h)[f"r{h}"] > 0 for f in S for h in (12, 24)))
    chk("R4 (components): no significant response of unemployment or the price level at any step and horizon; price level point estimate not negative at 24 m", all(cm(f, v, h)[f"lo{h}"] * cm(f, v, h)[f"hi{h}"] < 0 for f in S for v in ("u", "P") for h in (12, 24, 36)) and all(cm(f, "P", 24)["r24"] > 0 for f in S))
    chk("R4 r*-gap: baseline unemployment at 12 m inside the components interval; baseline price level at 24 m below the components interval", cm("rstar", "u", 12)["lo12"] <= est("rstar", "yes", "u", 12) <= cm("rstar", "u", 12)["hi12"] and est("rstar", "yes", "P", 24) < cm("rstar", "P", 24)["lo24"])
    c73 = lambda f, v, h: (lambda dd: dd[(dd.lags == MAIN_LAGS) & (dd["var"] == v)].iloc[0])(R[CS.case_id(dict(form=f, fci="cmp", macro="u,pi", start="1973-01", end=None, t2020="in", trend="none"))])
    chk("R4b (components, start 1973), r*-gap: unemployment positive at 12, 24 m; price level negative at 12, 24, 36 m, significant at 12 m", all(c73("rstar", "u", h)["r%d" % h] > 0 for h in (12, 24)) and all(c73("rstar", "P", h)["r%d" % h] < 0 for h in (12, 24, 36)) and c73("rstar", "P", 12)["lo12"] * c73("rstar", "P", 12)["hi12"] > 0)
    chk("R4b: nominal step price level not negative at 24 and 36 m", c73("nom", "P", 24)["r24"] > 0 and c73("nom", "P", 36)["r36"] > 0)
    chk("R5 (alternative surprises): with FCI unemployment positive and price level negative at 12, 24, 36 m; responses at 24 m at least as large as the baseline's", all(rb(p_, "yes", "u", h)[0] > 0 and rb(p_, "yes", "P", h)[0] < 0 for p_ in ("R5a", "R5b") for h in (12, 24, 36)) and all(rb(p_, "yes", "u", 24)[0] >= est("rstar", "yes", "u", 24) and rb(p_, "yes", "P", 24)[0] <= est("rstar", "yes", "P", 24) for p_ in ("R5a", "R5b")))
    WT = _wt(); chk("weights test, monthly equations from 1973, 12 lags: no rejection at 5% in either equation at any step", bool((WT[(WT.start == "1973-01") & (WT.lags == MAIN_LAGS)].p_boot > 0.05).all())); wt = lambda s_, e_, L_: WT[(WT.step == s_) & (WT["eq"] == e_) & (WT.lags == L_) & (WT.start == "1996-01")].p_boot.iloc[0]
    chk("weights test, 12 lags: no rejection at 10% in the unemployment equation at any step; rejection at 10% in the inflation equation at every step, at 5% at the real and r*-gap steps", all(wt(s_, "u", 12) > 0.10 for s_ in S) and all(wt(s_, "pi", 12) < 0.10 for s_ in S) and wt("real", "pi", 12) < 0.05 and wt("rstar", "pi", 12) < 0.05)
    chk("r*-gap with FCI: unemployment at 24 m significant at 10% but not 5%; price level at 5% at every horizon", sig("rstar", "yes", "u", 24) and not sig5("rstar", "yes", "u", 24) and all(sig5("rstar", "yes", "P", h) for h in (12, 24, 36)))
    TT_ = pd.read_csv(RESULTS / "tradeoff.csv"); tr_ = lambda st, e_, t2, H_: TT_[(TT_.form == "rstar") & (TT_.fci == "rstar") & (TT_.macro == "u,pi") & (TT_.start == st) & (TT_.end.fillna(0).astype(float) == e_) & (TT_.t2020 == t2) & (TT_.trend == "none") & (TT_.lags == 12) & (TT_.H == H_) & (TT_["shock"] == "ns")].iloc[0]
    bnd = lambda r_: np.isfinite(r_.k_lo) and np.isfinite(r_.k_hi) and r_.k_hi < 0
    chk("multiplier set bounded and below zero at 24 m: baseline, 2020 dropped (1996, 1973), ends 2019 from 1973; unbounded: from 1973, ends 2019 from 1996", all(bnd(tr_(*a)) for a in (("1996-01", 0, "in", 24), ("1996-01", 0, "out", 24), ("1973-01", 0, "out", 24), ("1973-01", 2019, "in", 24))) and not any(np.isfinite(tr_(*a).k_lo) for a in (("1973-01", 0, "in", 24), ("1996-01", 2019, "in", 24))))
    assert not bad, "claims in the note no longer hold: " + "; ".join(bad)
check_claims()

# ---------------------------------------------------------------- test of the proportional-weights restriction
WTT = _wt(); wrows = []
for start, lab in (("1996-01", ""), ("1973-01", ", start 1973")):
    for step in ("nom", "real", "rstar"):
        cells = []
        for eq in ("u", "pi"):
            r = WTT[(WTT.step == step) & (WTT.lags == MAIN_LAGS) & (WTT["eq"] == eq) & (WTT.start == start)].iloc[0]; cells.append(f"{r.wald:.1f} & {r.p_boot:.3f}")
        wrows.append(f"{CS.FORMS[step]}{lab} & " + " & ".join(cells) + r"\\")
(REPORT / "tab_weights_test.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Test of the proportional-weights restriction (12 lags)}\label{tab:weightstest}",
    r"\begin{tabular}{lrrrr}\toprule & \multicolumn{2}{c}{Unemployment gap equation} & \multicolumn{2}{c}{Core PCE inflation equation}\\ \cmidrule(lr){2-3}\cmidrule(lr){4-5}", r"Version & Wald & Bootstrap $p$ & Wald & Bootstrap $p$\\ \midrule", *wrows, r"\bottomrule\end{tabular}",
    r"\par\smallskip\parbox{0.92\linewidth}{\scriptsize Wald statistic (heteroskedasticity-robust, HC1) for the restriction that the coefficients on the three weighted components (10-year yield, equity valuation, dollar) are equal at each lag (24 restrictions), in each monthly equation, and the bootstrap $p$-value (999 block-bootstrap draws under the restriction); monthly equations from 1996 (first three rows) and from 1973 (last three), no trend, 2020 in. The unrestricted equation is the one used in Section 4.4.}", r"\end{table}"]) + "\n")

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
              & (T.t2020 == c["t2020"]) & (T.trend == c["trend"]) & (T.lags == MAIN_LAGS)]
        return f"{lab} & {CS.FCI_LABEL[c['fci']]} & " + " & ".join(kset(t[t.H == h].iloc[0]) for h in (24, 36)) + r"\\"
    for f in ("nom", "real", "rstar"):
        lines += [trow(CS.FORMS[f] if c["fci"] == 0 else "", c) for c in CS.PANELS[0]["cases"] if c["form"] == f]
    lines.append(r"\addlinespace")
    for pid in ("R1a", "R1b", "R1c", "R1d", "R1e"):
        lines.append(trow(CS.SHORT[pid], CS.panel_by_id(pid)["cases"][1]))
    lines.append(r"\addlinespace")
    for pid in ("R2a", "R2b", "R2c", "R2d"):
        lines.append(trow(CS.SHORT[pid], CS.panel_by_id(pid)["cases"][1]))
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
    LG = (3, 6, 12); BASEC = dict(macro="u,pi", start="1996-01", end=None, t2020="in", trend="none"); ml = []; bad = []
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
        TL = pd.read_csv(RESULTS / "tradeoff.csv"); tt = lambda L, H: TL[(TL.form == "rstar") & (TL.fci == "rstar") & (TL.macro == "u,pi") & (TL.start == "1996-01") & TL.end.isna() & (TL.t2020 == "in") & (TL.trend == "none") & (TL.lags == L) & (TL.H == H)].iloc[0]
        kc = lambda t: f"{num(t.kappa)} " + ("[unbounded]" if not np.isfinite(t.k_lo) or not np.isfinite(t.k_hi) else f"[{num(t.k_lo)}, {num(t.k_hi)}]")
        line("Phillips multiplier, 24 m", [kc(tt(L, 24)) for L in LG]); mult_bounded = {L: bool(np.isfinite(tt(L, 24).k_lo) and np.isfinite(tt(L, 24).k_hi)) for L in LG}
    except FileNotFoundError: mult_bounded = {}
    rows.append(r"\addlinespace\multicolumn{4}{l}{\textit{All cases with the FCI in Sections 3 and 4 (16 cases, 3 horizons, 48 responses each)}}\\")
    cnt = {L: dict(Pneg=0, Psig=0, upos=0, usig=0, n=0, usigneg=0, Psigpos=0) for L in LG}
    for pn in CS.PANELS:
        for c in pn["cases"]:
            if c["fci"] in (0, "cmp", "cmpR", "cmpE"): continue
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
        dm(f"med:P:{L}", num(np.median([R[CS.case_id(c)].query("lags == @L and `var` == 'P'").iloc[0][f"r{h}"] for pn in CS.PANELS for c in pn["cases"] if c["fci"] not in (0, "cmp", "cmpR", "cmpE") for h in (12, 24, 36)])))
    dm("n", str(int(n_)))
    for L in LG:
        t = lit("chol_2y_1996", "u", 12, L); dm(f"chol:u12:{L}", num(t.point))
        b = bl("rstar", "yes", "P", 36, L); dm(f"rstar:P36:{L}", num(b.r36)); b = bl("rstar", "yes", "u", 24, L); dm(f"rstar:u24:{L}", num(b.r24))
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
    for L in LG:
        chk(f"lags {L}: with the FCI the price level falls in every case and horizon", cnt[L]["Pneg"] == n_ and cnt[L]["Psigpos"] == 0)
        chk(f"lags {L}: with the FCI no significant fall in unemployment (3 lags: one, Kiley from 1973 at 24 m)", cnt[L]["usigneg"] == (1 if L == 3 else 0))
        chk(f"lags {L}: unemployment rises in a large majority of responses with the FCI", cnt[L]["upos"] >= 0.7 * n_)
        t = lit("chol_2y_1996", "u", 12, L); chk(f"lags {L}: Cholesky unemployment falls significantly at 12 m", t.point < 0 and t.sig)
        pr = lit("proxy_2y_1996", "u", 24, L); chk(f"lags {L}: proxy VAR unemployment falls at 24 m", pr.point < 0)
        chk(f"lags {L}: without the FCI the r*-gap unemployment gap is not significantly positive", not any(sg(bl("rstar", "no", "u", h, L), h) and bl("rstar", "no", "u", h, L)[f"r{h}"] > 0 for h in (12, 24, 36)))
        chk(f"lags {L}: weights, 1996: inflation equation rejects proportional weights at 10% in every step, unemployment equation not at 5%", all(WTL[(WTL.start == "1996-01") & (WTL.lags == L) & (WTL["eq"] == "pi")].p_boot < 0.10) and all(WTL[(WTL.start == "1996-01") & (WTL.lags == L) & (WTL["eq"] == "u")].p_boot > 0.05))
    chk("weights, 1973: no rejection of proportional weights at 5% at any lag length, step or equation", all(WTL[(WTL.start == "1973-01") & (WTL.lags.isin(LG))].p_boot > 0.05))
    chk("price level significant in more cases with more lags", cnt[3]["Psig"] < cnt[6]["Psig"] < cnt[12]["Psig"])
    chk("point estimates of the baseline price response grow with the lag length", abs(bl("rstar", "yes", "P", 36, 3).r36) < abs(bl("rstar", "yes", "P", 36, 6).r36) < abs(bl("rstar", "yes", "P", 36, 12).r36))
    if mult_bounded: chk("the multiplier set at 24 m is bounded at 12 lags only", mult_bounded == {3: False, 6: False, 12: True})
    assert not bad, "claims on lag length no longer hold: " + "; ".join(bad)
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
    assert not bad, "claims on the bootstrap no longer hold: " + "; ".join(bad)
boot_summary()


# ---------------------------------------------------------------- Section 4: summary table of the robustness variations, macros and claims
def rob_summary():
    """tab_rob_summary.tex: baseline and every variation (r*-gap, 12 lags): the yield alone (unemployment at 12 m) and with the FCI (unemployment and price level at 24 m); macros bl:rob:*; claims."""
    ROWS = [("B", "Baseline", ""), ("R1a", "Start 1973", "Sample"), ("R1b", "2020 dropped", ""), ("R1c", "2020 dropped, start 1973", ""), ("R1d", "Ends 2019", ""), ("R1e", "Ends 2019, start 1973", ""),
            ("R2a", "Kiley $r^*$", "The $r^*$ adjustment and trends"), ("R2b", "Kiley $r^*$, start 1973", ""), ("R2c", "Real yield and FCI, spline trend", ""), ("R2d", "Real yield and FCI, spline trend, start 1973", ""),
            ("R3a", "Excess bond premium added", "Credit conditions"), ("R3b", "Excess bond premium added, start 1973", ""),
            ("R4", "Three components in place of the FCI", "Weights of the FCI"), ("R4b", "Three components, start 1973", ""),
            ("R5a", "Bauer--Swanson surprise", "The surprise"), ("R5b", "Jarocinski--Karadi surprise", "")]
    def row(pid, pick_fci):
        p_ = CS.panel_by_id(pid) if pid != "B" else dict(cases=[c for c in CS.PANELS[0]["cases"] if c["form"] == "rstar"])
        cs_ = [c for c in p_["cases"] if (c["fci"] == 0) == (not pick_fci) and (pid not in ("R4", "R4b") or c["form"] == "rstar")]
        if not cs_: return None
        d = R[CS.case_id(cs_[0])]; return d[d.lags == MAIN_LAGS]
    def cellv(d, v, h):
        r = d[d["var"] == v].iloc[0]; return r[f"r{h}"], stars(r, h), r
    lines = []; cnt = dict(Pneg=0, Psig5=0, Psig10=0, upos=0, usig10=0, usig5=0, n=0, no_uneg=0, no_n=0); res = {}
    for pid, lab, grp in ROWS:
        if grp: lines.append(r"\addlinespace" + rf"\multicolumn{{4}}{{l}}{{\textit{{{grp}}}}}\\")
        w, no = row(pid, True), row(pid, False)
        cells = []
        if no is not None: x, st, _ = cellv(no, "u", 12); cells.append(num(x) + st)
        else: cells.append("--")
        for v in ("u", "P"):
            x, st, r = cellv(w, v, 24); cells.append(num(x) + st)
        lines.append(f"{lab} & " + " & ".join(cells) + r"\\")
        res[pid] = dict(u24=cellv(w, "u", 24), P24=cellv(w, "P", 24), no_u12=(cellv(no, "u", 12) if no is not None else None))
        if pid not in ("B", "R4", "R4b"):
            cnt["n"] += 1; xP, sP, rP = res[pid]["P24"]; xu, su, ru = res[pid]["u24"]
            cnt["Pneg"] += xP < 0; cnt["Psig5"] += sP == "$^{**}$"; cnt["Psig10"] += sP != ""; cnt["upos"] += xu > 0; cnt["usig10"] += su != ""; cnt["usig5"] += su == "$^{**}$"
            xn = res[pid]["no_u12"][0]; cnt["no_n"] += 1; cnt["no_uneg"] += xn < 0
    out = [r"\begin{table}[H]\centering\small", r"\caption{The baseline and the robustness variations ($r^*$-gap two-year yield; 12 lags)}\label{tab:robsummary}",
           r"\begin{tabular}{lccc}\toprule & Yield alone & \multicolumn{2}{c}{Yield and FCI}\\ \cmidrule(lr){2-2}\cmidrule(lr){3-4} & Unemployment, 12 m & Unemployment, 24 m & Price level, 24 m\\ \midrule", *lines, r"\bottomrule\end{tabular}",
           r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize Per +1 pp on the two-year yield; unemployment gap in percentage points, price level in percent. $^{**}$ and $^{*}$: significant at the 5 and 10 percent levels (the 95\% and 90\% bootstrap intervals exclude zero). The variations are described in Sections 4.1 to 4.5; Appendix Tables give each at 12, 24 and 36 months and at 3, 6 and 12 lags. The three-component rows replace the FCI, so they have no yield-alone entry.}", r"\end{table}"]
    (REPORT / "tab_rob_summary.tex").write_text("\n".join(out) + "\n")
    ml = []; dm = lambda k, v: ml.append(r"\expandafter\gdef\csname bl:rob:" + k + r"\endcsname{" + str(v) + "}")
    for k, v in cnt.items(): dm(k, v)
    (REPORT / "numbers.tex").write_text((REPORT / "numbers.tex").read_text() + "\n".join(ml) + "\n")
    bad = []; chk = lambda name, ok: None if ok else bad.append(name); sig5 = lambda pid, k: res[pid][k][1] == "$^{**}$"; sig10 = lambda pid, k: res[pid][k][1] != ""
    chk("with the FCI the price level at 24 m falls in every variation with the r*-gap FCI (13)", cnt["Pneg"] == cnt["n"] == 13)
    chk("price level at 24 m: significant at 5% in 10 of 13 variations; not significant at 10% when the sample ends in 2019 (from 1996), with Kiley r* (from 1996) and with the spline trend (from 1996)", cnt["Psig5"] == 10 and cnt["Psig10"] == 10 and not any(sig10(k, "P24") for k in ("R1d", "R2a", "R2c")) and sig5("R1e", "P24"))
    chk("with the FCI unemployment at 24 m is positive in 12 of 13, significant at 10% in 4 (2020 dropped, EBP from 1996, both alternative surprises)", cnt["upos"] == 12 and cnt["usig10"] == 4 and all(sig10(k, "u24") for k in ("R1b", "R3a", "R5a", "R5b")))
    chk("with the FCI no variation has a significantly negative unemployment response at 24 m", not any(res[k]["u24"][0] < 0 and sig10(k, "u24") for k in res if k != "B"))
    chk("without the FCI unemployment at 12 m is negative in 11 of 13 (positive when 2020 is dropped from 1973 and when the sample from 1973 ends in 2019)", cnt["no_uneg"] == 11)
    chk("components from 1973: price level at 12 m negative and significant at 5%", (lambda r: r.r12 < 0 and r.lo95_12 * r.hi95_12 > 0)(R[CS.case_id([x for x in CS.panel_by_id("R4b")["cases"] if x["form"] == "rstar"][0])].query("lags == 12 and `var` == 'P'").iloc[0]))
    chk("alternative surprises: price level at 24 m significant at 5%, unemployment at 10% but not 5%", all(sig5(k, "P24") and sig10(k, "u24") and not sig5(k, "u24") for k in ("R5a", "R5b")))
    chk("Kiley and spline from 1973: price level significant at 5% at 24 m", all(sig5(k, "P24") for k in ("R2b", "R2d")))
    chk("components from 1996: price level at 24 m not significant, not negative (positive point estimate)", not sig10("R4", "P24") and res["R4"]["P24"][0] > 0 and res["R4"]["P24"][2]["lo24"] < 0 < res["R4"]["P24"][2]["hi24"])
    TT_ = pd.read_csv(RESULTS / "tradeoff.csv"); k_ = lambda form, fci, st, tr, H_: TT_[(TT_.form == form) & (TT_.fci == str(fci)) & (TT_.macro == "u,pi") & (TT_.start == st) & (TT_.end.isna()) & (TT_.t2020 == "in") & (TT_.trend == tr) & (TT_.lags == 12) & (TT_.H == H_) & (TT_["shock"] == "ns")].iloc[0]
    chk("multiplier set at 24 m: Kiley from 1996 bounded and includes zero; Kiley from 1973 and spline (both starts) unbounded", (lambda r_: np.isfinite(r_.k_lo) and np.isfinite(r_.k_hi) and r_.k_lo < 0 < r_.k_hi)(k_("kiley", "kiley", "1996-01", "none", 24)) and not any(np.isfinite(k_(f_, f_, st_, tr_, 24).k_lo) for f_, st_, tr_ in (("kiley", "1973-01", "none"), ("real", "1996-01", "spline"), ("real", "1973-01", "spline"))))
    DF_ = pd.read_csv(RESULTS / "tradeoff_diff.csv"); DF_ = DF_[DF_.lags == 12]
    chk("paired difference of the multipliers (r*-gap minus nominal) has an interval that includes zero at 24 and 36 m", all((DF_[DF_.H == h_].lo.iloc[0] < 0 < DF_[DF_.H == h_].hi.iloc[0]) for h_ in (24, 36)))
    assert not bad, "claims on the robustness section no longer hold: " + "; ".join(bad)
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
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.96\linewidth}{\scriptsize Monthly data, 12 lags, constant, no trend; unemployment gap, core PCE inflation and the end-of-month policy rate (the 2-year Treasury yield, or the effective federal funds rate where stated), policy rate ordered last in the Cholesky VARs; price level = cumulated inflation/12. " 
            + extra + r" Unit: +1 pp on the policy rate on impact. Brackets: 90\% intervals (residual bootstrap for the Cholesky VARs; exact Anderson--Rubin sets for the proxy VAR). $^{*}$ = excludes zero. Specification: baseline/lib/litstyle.py.}", r"\end{table}"]
    (REPORT / fname).write_text("\n".join(out) + "\n")
_F = pd.read_csv(RESULTS / "lit_style_info.csv").query("lags == 12").set_index("case").F["proxy_2y_1996"]
standard_table([("chol_2y_1996", "Cholesky, 2-year yield", "1996--2026"), ("proxy_2y_1996", "Proxy VAR, 2-year yield", "1996--2026")],
               "tab_standard.tex", "tab:standard", "Standard Methods: Responses to a 1 Percentage Point Rise in the Policy Rate", f"Proxy VAR: Nakamura--Steinsson policy news summed within the month as instrument; first-stage $F$ = {_F:.1f}.")
standard_table([("chol_2y_1996", "Cholesky, 2-year yield", "1996--2026"), ("chol_2y_1984", "Cholesky, 2-year yield", "1984--2026"), ("chol_ffr_1984_2007", "Cholesky, federal funds rate", "1984--2007"), ("proxy_2y_1996", "Proxy VAR, 2-year yield", "1996--2026")],
               "tab_standard_all.tex", "tab:standardall", "Standard methods with other samples and the federal funds rate", f"Proxy VAR: Nakamura--Steinsson policy news summed within the month as instrument; first-stage $F$ = {_F:.1f}.")
standard_table([("chol_2y_1996_com", "Cholesky + commodity prices, 2-year yield", "1996--2026"), ("chol_ffr_1984_2007_com", "Cholesky + commodity prices, federal funds rate", "1984--2007")],
               "tab_standard_com.tex", "tab:standardcom", "Standard methods with a commodity price index in the first block", "The log PPI for all commodities (monthly average) is added to the system and ordered before the policy rate.")

def fig_size():
    """Baseline figure: r*-gap 2-year yield with the FCI (bands), the nominal yield alone and with the FCI in the same model, and the Cholesky VAR of Section 3.1."""
    base = dict(macro="u,pi", start="1996-01", end=None, t2020="in", trend="none")
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
    """Figure 1 (introduction): the r*-gap two-year yield alone and with the FCI (same surprise, normalization, sample and bootstrap; 68 and 90 percent bands)."""
    base = dict(macro="u,pi", start="1996-01", end=None, t2020="in", trend="none")
    cs = dict(with_=dict(form="rstar", fci="rstar", **base), alone=dict(form="rstar", fci=0, **base))
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.3))
    for ax, v, ylab in ((axs[0], "u", "Unemployment gap (pp)"), (axs[1], "P", "Core PCE price level (%)")):
        ax.axhline(0, color=GREY, lw=0.8)
        e = paths(cs["alone"]); e = e[(e.kind == "macro") & (e["var"] == v)]
        ax.fill_between(e.h, e.lo, e.hi, color=ORANGE, alpha=0.10, lw=0); ax.fill_between(e.h, e.lo68, e.hi68, color=ORANGE, alpha=0.20, lw=0); h2 = ax.plot(e.h, e.r, color=ORANGE, ls="--", lw=1.9)[0]
        d = paths(cs["with_"]); d = d[(d.kind == "macro") & (d["var"] == v)]
        ax.fill_between(d.h, d.lo, d.hi, color=BLUE, alpha=0.13, lw=0); ax.fill_between(d.h, d.lo68, d.hi68, color=BLUE, alpha=0.25, lw=0); h1 = ax.plot(d.h, d.r, color=BLUE, lw=2.0)[0]
        ax.set_xlabel("Months after the policy move"); ax.set_ylabel(ylab); ax.set_xlim(0, 36)
    fig.legend([h1, h2], ["Yield and FCI, both relative to the neutral rate", "Yield alone, relative to the neutral rate"], loc="lower center", ncol=2, frameon=False, fontsize=7.5)
    fig.tight_layout(rect=[0, 0.08, 1, 1]); fig.savefig(REPORT / "fig_intro.pdf"); plt.close(fig)
fig_intro()
from lib import latex_style as LST
LST.restyle_dir(REPORT)                                                              # house LaTeX style: [tp] floats, Title Case captions, notes below the table
print("report inputs written to", REPORT)
