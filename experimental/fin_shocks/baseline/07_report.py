"""Step 7. Tables and figures of the results document from results/ (12-lag main tables by section, 3/6/12-lag appendix tables by panel, the response
figures, the weights table and the trade-off table). Compile report/baseline_robustness.tex with pdflatex (twice).   python3 05_report.py"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cases as CS
from lib.paths import RESULTS, REPORT, OUT, DATA

R = {CS.case_id(c): pd.read_csv(RESULTS / f"{CS.case_id(c)}.csv") for c in CS.unique_cases()}
MAIN_LAGS = 12

# ---------------------------------------------------------------- tables
def num(x):
    s = f"{abs(x):.2f}"; return ("$-$" if x < 0 and s != "0.00" else "") + s
def cell(r, h):
    star = "$^{*}$" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else ""
    return num(r[f"r{h}"]) + star, f"[{num(r[f'lo{h}'])}, {num(r[f'hi{h}'])}]"
def get(c, L):
    d = R[CS.case_id(c)]; g = d[d.lags == L]; return g[g["var"] == "u"].iloc[0], g[g["var"] == "P"].iloc[0]
def two_lines(c, L):
    u, p = get(c, L); cells = [cell(r, h) for r in (u, p) for h in (12, 24, 36)]
    return int(u.nobs), [x[0] for x in cells], [x[1] for x in cells]

HEAD = (r"\begin{tabular}{llcrrrrrrr}\toprule" "\n" r" & & & & \multicolumn{3}{c}{Unemployment gap (pp)} & \multicolumn{3}{c}{Price level (\%)}\\ \cmidrule(lr){5-7}\cmidrule(lr){8-10}" "\n"
        r"Case & FCI & Lags & Obs & 12 m & 24 m & 36 m & 12 m & 24 m & 36 m\\ \midrule")
NOTE = r"Per +1 pp on the 2-year yield. $^{*}$ = 90\% interval excludes zero; intervals in brackets. Obs = monthly observations in the equations."

def table(title, label, groups, lags, note, place="H"):
    """groups: list of (row label, [cases]); one block per label; lags: tuple of lag lengths shown for each case."""
    out = [rf"\begin{{table}}[{place}]\centering\footnotesize\setlength{{\tabcolsep}}{{2.2pt}}", rf"\caption{{{title}}}\label{{{label}}}", HEAD]
    for gi, (lab, cs) in enumerate(groups):
        if gi: out.append(r"\addlinespace")
        for ci, c in enumerate(cs):
            for li, L in enumerate(lags):
                n, pts, ivs = two_lines(c, L)
                a = (lab if ci == 0 and li == 0 else ""); f = CS.FCI_LABEL[c["fci"]] if li == 0 else ""
                out += [f"{a} & {f} & {L} & {n} & " + " & ".join(pts) + r"\\", r" & & & & " + " & ".join(rf"{{\scriptsize {x}}}" for x in ivs) + r"\\"]
    out += [r"\bottomrule\end{tabular}", rf"\par\smallskip\parbox{{0.96\linewidth}}{{\scriptsize {note} {NOTE}}}", r"\end{table}"]
    return "\n".join(out)

for g, pids in CS.GROUPS.items():                                                  # main text: 12 lags
    blocks = []
    for pid in pids:
        p = CS.panel_by_id(pid)
        if g == "B": blocks += [(CS.FORMS[f], [c for c in p["cases"] if c["form"] == f]) for f in ("nom", "real", "rstar")]
        else: blocks.append((CS.SHORT[pid], p["cases"]))
    notes = CS.GROUP_NOTE[g]
    (REPORT / f"tab_main_{g}.tex").write_text(table(CS.GROUP_TITLE[g] + " (12 lags)", f"tab:main{g}", blocks, (MAIN_LAGS,), notes) + "\n")
for p in CS.PANELS:                                                                  # appendix: 3, 6, 12 lags
    f = lambda c: CS.FORMS[c["form"]]
    blocks = [(f(c0), [c for c in p["cases"] if c["form"] == c0["form"]]) for c0 in p["cases"][::2]] if p["id"] == "B" else [(f(p["cases"][0]), p["cases"])]
    (REPORT / f"tab_app_{p['id']}.tex").write_text(table(p["title"], f"tab:app{p['id']}", blocks, (3, 6, 12), p["notes"], "p") + "\n")

# ---------------------------------------------------------------- monthly VAR benchmark tables
MON = {CS.monthly_id(m): pd.read_csv(RESULTS / f"{CS.monthly_id(m)}.csv") for m in CS.MONTHLY}
START_LABEL = {"1996-01": "1996 sample", "1973-01": "1973 sample"}
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
    out = [rf"\begin{{table}}[{place}]\centering\scriptsize\setlength{{\tabcolsep}}{{2pt}}", rf"\caption{{{title}}}\label{{{label}}}",
           r"\begin{tabular}{lllcrrrrrrr}\toprule" "\n" r" & & & & & \multicolumn{3}{c}{Unemployment gap (pp)} & \multicolumn{3}{c}{Price level (\%)}\\ \cmidrule(lr){6-8}\cmidrule(lr){9-11}" "\n"
           r"2-year & FCI & Identification & Lags & Obs & 12 m & 24 m & 36 m & 12 m & 24 m & 36 m\\ \midrule"]
    for si, step in enumerate(("nom", "real", "rstar")):
        if si: out.append(r"\addlinespace")
        for fci in (0, step):
            d = MON[CS.monthly_id(dict(step=step, fci=fci, start=start))]
            for ident in ("P1", "WE"):
                for L in lags:
                    n, pts, ivs = mcells(d, L, ident)
                    a = CS.FORMS[step] if (fci == 0 and ident == "P1" and L == lags[0]) else ""; f = CS.FCI_LABEL[fci] if (ident == "P1" and L == lags[0]) else ""
                    out += [f"{a} & {f} & {IDENT[ident] if L == lags[0] else ''} & {L} & {n} & " + " & ".join(pts) + r"\\", r" & & & & & " + " & ".join(rf"{{\tiny {x}}}" for x in ivs) + r"\\"]
    out += [r"\bottomrule\end{tabular}", rf"\par\smallskip\parbox{{0.96\linewidth}}{{\scriptsize {note}}}", r"\end{table}"]
    return "\n".join(out)
MNOTE = (r"Monthly VAR in the unemployment gap, core PCE inflation, the 2-year yield and, when included, the FCI (same step), sample as in the title, to September 2026, no trend, nothing dropped. "
         r"Proxy VAR: Nakamura--Steinsson surprise as instrument; sets are exact 90\% Anderson--Rubin sets, ``unbounded'' when the instrument cannot reject large effects; unit +1 pp on the monthly-average 2-year yield. "
         r"Window impact: impact vector measured in the announcement window and scaled by the share of the month after the announcement; 90\% bootstrap intervals; unit +1 pp 2-year in the window. The two units differ. $^{*}$ = 90\% interval excludes zero.")
for st, tag in (("1996-01", "1996"), ("1973-01", "1973")):
    (REPORT / f"tab_main_monthly{tag}.tex").write_text(monthly_table(f"Monthly VAR benchmark, {START_LABEL[st]} (12 lags)", f"tab:mainmonthly{tag}", (12,), MNOTE, st) + "\n")
    (REPORT / f"tab_app_monthly{tag}.tex").write_text(monthly_table(f"Monthly VAR benchmark, {START_LABEL[st]} (3, 6 and 12 lags)", f"tab:appmonthly{tag}", (3, 6, 12), MNOTE, st, "p") + "\n")
frows = []
for st in ("1996-01", "1973-01"):
    if st != "1996-01": frows.append(r"\addlinespace")
    for step in ("nom", "real", "rstar"):
        for fci in (0, step):
            d = MON[CS.monthly_id(dict(step=step, fci=fci, start=st))]; g = d[(d.ident == "P1") & (d["var"] == "u") & (d.h == 12)].set_index("lags")
            frows.append(f"{START_LABEL[st][:4] if (step == 'nom' and fci == 0) else ''} & {CS.FORMS[step] if fci == 0 else ''} & {CS.FCI_LABEL[fci]} & " + " & ".join(f"{g.F[L]:.1f}" for L in (3, 6, 12)) + " & "
                         + (f"{num(g.impact_fci[12])} & {num(g.win_bF[12])}" if fci else " & ") + r"\\")
(REPORT / "tab_monthly_F.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Monthly proxy VAR: first-stage strength and impact on the FCI}\label{tab:monthlyF}",
    r"\begin{tabular}{lllrrrrr}\toprule Start & 2-year & FCI & $F$ (3 lags) & $F$ (6) & $F$ (12) & Proxy impact on FCI & Window impact on FCI\\ \midrule", *frows, r"\bottomrule\end{tabular}",
    r"\par\smallskip\parbox{0.92\linewidth}{\scriptsize $F$: robust first-stage statistic of the policy-variable residual on the instrument (instrument months only). The instrument exists from 1996, so the first stage uses the 1996--2026 instrument months in both samples. Impact on FCI: response of the FCI per +1 pp on the 2-year yield, estimated from monthly residuals (proxy VAR, 12 lags) and measured in the announcement window.}", r"\end{table}"]) + "\n")

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
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize 1,000 samples of 369 months generated by the estimated r*-gap model with the FCI (12 lags), with the data's calendar and announcement days; policy reaches unemployment and prices only through the 2-year yield and the FCI. Data: the 1996 sample, 12 lags, r*-gap measures. True: the model's response per +1 pp on the monthly-average 2-year yield (panels A and B; ratio of the window response to its contemporaneous monthly-average response, an approximation) and per +1 pp in the window (panel C). Simulated: median and 5th--95th percentiles of the estimates.}", r"\end{table}"]
    return "\n".join(out)
(REPORT / "tab_proxy_sim.tex").write_text(sim_table() + "\n")

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
    LIT = pd.read_csv(DATA / "literature_irfs.csv"); tag = {"Bauer-Swanson benchmark": "bsb", "Bauer-Swanson unadjusted": "bsu"}; vm = {"unemployment rate (pp)": "u", "CPI (%)": "P"}
    for _, r in LIT.iterrows():
        k = f"lit:{tag[r.study]}:{vm[r.variable]}:{int(r.horizon_months)}"; d("bl:" + k, num(r.response_per_1pp)); d("blabs:" + k, f"{abs(r.response_per_1pp):.2f}")
    (REPORT / "numbers.tex").write_text("\n".join(L) + "\n")
write_numbers()

def check_claims():
    """The qualitative claims made in the note's Sections 3.1-3.2; raises an error if any stops being true of the results."""
    def g(f, fk, v, h):
        dd = R[CS.case_id(dict(form=f, fci=0 if fk == "no" else f, macro="u,pi", start="1996-01", end=None, t2020="in", trend="none"))]; r = dd[(dd.lags == MAIN_LAGS) & (dd["var"] == v)].iloc[0]
        return r[f"r{h}"], r[f"lo{h}"] * r[f"hi{h}"] > 0
    est = lambda *k: g(*k)[0]; sig = lambda *k: g(*k)[1]; S = ("nom", "real", "rstar"); bad = []
    chk = lambda name, ok: None if ok else bad.append(name)
    for f in ("nom", "real"):
        chk(f"{f}: yield alone, unemployment falls significantly at 12 m", est(f, "no", "u", 12) < 0 and sig(f, "no", "u", 12)); chk(f"{f}: yield alone, price level does not respond significantly at 24 m", not sig(f, "no", "P", 24))
    chk("rstar: yield alone, unemployment does not rise (12, 24 m)", est("rstar", "no", "u", 12) < 0.0 and not sig("rstar", "no", "u", 12) and not sig("rstar", "no", "u", 24)); chk("rstar: yield alone, price level falls significantly at 24 m", est("rstar", "no", "P", 24) < 0 and sig("rstar", "no", "P", 24))
    for f in S:
        chk(f"{f}: with FCI, no significant fall in unemployment", all(not (est(f, "yes", "u", h) < 0 and sig(f, "yes", "u", h)) for h in (12, 24, 36)))
        chk(f"{f}: with FCI, unemployment positive at 24 and 36 m", est(f, "yes", "u", 24) > 0 and est(f, "yes", "u", 36) > 0); chk(f"{f}: with FCI, unemployment significant at 36 m", sig(f, "yes", "u", 36))
        chk(f"{f}: with FCI, price level falls at 12, 24, 36 m, significantly at 24 and 36", all(est(f, "yes", "P", h) < 0 for h in (12, 24, 36)) and sig(f, "yes", "P", 24) and sig(f, "yes", "P", 36))
    chk("unemployment significant at 24 m with FCI only at the r*-gap step", sig("rstar", "yes", "u", 24) and not sig("nom", "yes", "u", 24) and not sig("real", "yes", "u", 24))
    chk("r*-gap with FCI has the largest price fall at 24 m", est("rstar", "yes", "P", 24) < min(est("nom", "yes", "P", 24), est("real", "yes", "P", 24)))
    chk("r*-gap with FCI: unemployment (12, 24 m) and price (24 m) responses larger than the Bauer-Swanson values quoted (+0.19, +0.17; -0.48)", est("rstar", "yes", "u", 12) > 0.19 and est("rstar", "yes", "u", 24) > 0.17 and est("rstar", "yes", "P", 24) < -0.48)
    LIT = pd.read_csv(DATA / "literature_irfs.csv"); lit = lambda st, v, h: float(LIT[(LIT.study == st) & (LIT.variable == {"u": "unemployment rate (pp)", "P": "CPI (%)"}[v]) & (LIT.horizon_months == h)].response_per_1pp.iloc[0])
    def band(f, fk, v, h):
        dd = R[CS.case_id(dict(form=f, fci=0 if fk == "no" else f, macro="u,pi", start="1996-01", end=None, t2020="in", trend="none"))]; r = dd[(dd.lags == MAIN_LAGS) & (dd["var"] == v)].iloc[0]; return r[f"lo{h}"], r[f"hi{h}"]
    for v in ("u", "P"):
        for h in (12, 24, 36):
            lo, hi = band("rstar", "yes", v, h); chk(f"Bauer-Swanson benchmark {v} {h} m inside our r*-gap 90% band", lo <= lit("Bauer-Swanson benchmark", v, h) <= hi)
            chk(f"r*-gap with FCI larger in absolute value than the Bauer-Swanson benchmark, {v} {h} m", abs(est("rstar", "yes", v, h)) > abs(lit("Bauer-Swanson benchmark", v, h)))
    for h in (12, 24, 36): chk(f"nominal yield alone: unemployment below the Bauer-Swanson unadjusted response, {h} m", est("nom", "no", "u", h) < lit("Bauer-Swanson unadjusted", "u", h) and est("nom", "no", "u", h) < 0)
    chk("nominal yield alone: price level within 0.15 of zero at 12, 24, 36 m", all(abs(est("nom", "no", "P", h)) <= 0.15 for h in (12, 24, 36)))
    chk("Bauer-Swanson unadjusted unemployment negative on impact and positive at 12-36 m", lit("Bauer-Swanson unadjusted", "u", 0) < 0 and all(lit("Bauer-Swanson unadjusted", "u", h) > 0 for h in (12, 24, 36)))
    assert not bad, "claims in the note no longer hold: " + "; ".join(bad)
check_claims()

# ---------------------------------------------------------------- weights table (window responses)
w = pd.read_csv(OUT / "market_weights.csv", index_col=0)
names = {"y10": "10-year Treasury yield (pp)", "equities": "Equity valuation, 100 ln CAPE (\\%)", "dollar": "Real broad dollar, 100 ln (\\%)"}
sg = lambda x, f: (("$-$" if x < 0 else "$+$") + f.format(abs(x)))
rows = [f"{names[k]} & {sg(w.response[k], '{:.2f}')} ({w.se[k]:.2f}) & {sg(w.weight[k], '{:.3f}')} & {w.weight[k] * w.response[k]:.2f}\\\\" for k in w.index]
(REPORT / "tab_weights.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Market-index weights from policy news}\label{tab:weights}",
    r"\begin{tabular}{lrrr}\toprule Component & Response to policy news & Weight & Share of a policy move\\ \midrule", *rows, r"\bottomrule\end{tabular}",
    r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize Response of each 30-minute announcement-window change to the policy-news factor (scaled so the 2-year yield moves 1 pp), with robust standard errors; weights from the one-factor GLS of Note A; share = weight $\times$ response (the three shares sum to 1).}", r"\end{table}"]) + "\n")

# ---------------------------------------------------------------- trade-off table
try:
    T = pd.read_csv(RESULTS / "tradeoff.csv"); T["fci"] = T.fci.astype(str); D = pd.read_csv(RESULTS / "tradeoff_diff.csv")
    def kset(r):
        if np.isinf(r.k_lo) and np.isinf(r.k_hi): return "unbounded"
        lo = "$(-\\infty$" if np.isinf(r.k_lo) else f"[{num(r.k_lo)}"; hi = "$+\\infty)$" if np.isinf(r.k_hi) else f"{num(r.k_hi)}]"
        return f"{num(r.kappa)} {lo}, {hi}"
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
    d = D[D.lags == MAIN_LAGS].set_index("H")
    lines += [r"\addlinespace", "r*-gap minus nominal, with FCI & & " + " & ".join(f"[{num(d.lo[h])}, {num(d.hi[h])}]" for h in (24, 36)) + r"\\"]
    (REPORT / "tab_tradeoff.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Implied trade-off: Phillips multiplier $\kappa_H$ (12 lags)}\label{tab:tradeoff}",
        r"\begin{tabular}{llrr}\toprule Case & FCI & $H=24$ months & $H=36$ months\\ \midrule", *lines, r"\bottomrule\end{tabular}",
        r"\par\smallskip\parbox{0.9\linewidth}{\scriptsize $\kappa_H$ = core PCE price level at month $H$ (percent) per percentage-point year of cumulative unemployment-gap response (Barnichon and Mesters 2021); the sacrifice ratio is $-1/\kappa_H$. Point estimate and 90\% confidence set (Anderson--Rubin type) in brackets, computed exactly (a wide grid refined by bisection), so a finite end is never an artifact of the grid. An infinite end means that the 90\% interval of the cumulative unemployment response includes zero: the data then cannot rule out arbitrarily steep trade-offs on that side; ``unbounded'': both sides. Last row: paired difference over common announcement draws.}", r"\end{table}"]) + "\n")
except FileNotFoundError:
    print("tradeoff.csv missing: run 04_tradeoff.py first")

# ---------------------------------------------------------------- figures
BLUE, ORANGE, INK, GREY = "#2a78d6", "#eb6834", "#0b0b0b", "#6b6a66"      # validated pair (dataviz skill, light surface); ink for text and neutral series
plt.rcParams.update({"font.size": 8, "axes.edgecolor": GREY, "axes.labelcolor": INK, "text.color": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": 0.6, "axes.axisbelow": True})
def paths(c, L=MAIN_LAGS):
    d = pd.read_csv(RESULTS / f"{CS.case_id(c)}_paths.csv"); return d[d.lags == L]
def line(ax, d, color, ls, label, lo="lo", hi="hi", alpha=0.14):
    ax.fill_between(d.h, d[lo], d[hi], color=color, alpha=alpha, lw=0); ax.plot(d.h, d.r, color=color, ls=ls, lw=1.8, label=label)

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
fig.suptitle("Response to a policy move that raises the 2-year yield 1 percentage point (12 lags; bands: 90% intervals)", fontsize=8.5, y=0.995)
fig.tight_layout(); fig.savefig(REPORT / "fig_steps.pdf"); plt.close(fig)

fig, ax = plt.subplots(1, 1, figsize=(4.4, 2.8)); ax.axhline(0, color=GREY, lw=0.8)
c = next(c for c in base if c["form"] == "rstar" and c["fci"] == "rstar"); d = paths(c); d = d[d.kind == "fin"]
line(ax, d[d["var"] == "pol"], INK, "-", "2-year yield, r*-gap form", alpha=0.10); line(ax, d[d["var"] == "idx"], GREY, "--", "FCI (2-year-yield units)", alpha=0.10)
ax.set_xlabel("Months after the policy move"); ax.set_ylabel("Percentage points"); ax.legend(frameon=False, fontsize=7.5)
ax.set_title("Financial response (monthly averages; 12 lags; 90% bands)", fontsize=8)
fig.tight_layout(); fig.savefig(REPORT / "fig_financial.pdf"); plt.close(fig)

# size-of-effects figure: nominal yield alone vs the baseline, with literature values
def fig_size():
    base = dict(macro="u,pi", start="1996-01", end=None, t2020="in", trend="none")
    cs = dict(rstar=dict(form="rstar", fci="rstar", **base), nom0=dict(form="nom", fci=0, **base), nom1=dict(form="nom", fci="nom", **base))
    LIT = pd.read_csv(DATA / "literature_irfs.csv"); vm = {"u": "unemployment rate (pp)", "P": "CPI (%)"}
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.9)); H_ = {}
    for ax, v, ylab in ((axs[0], "u", "Unemployment gap (pp)"), (axs[1], "P", "Core PCE price level (%)")):
        ax.axhline(0, color=GREY, lw=0.8)
        d = paths(cs["rstar"]); d = d[(d.kind == "macro") & (d["var"] == v)]
        ax.fill_between(d.h, d.lo, d.hi, color=BLUE, alpha=0.13, lw=0); ax.fill_between(d.h, d.lo68, d.hi68, color=BLUE, alpha=0.25, lw=0)
        H_["b"] = ax.plot(d.h, d.r, color=BLUE, lw=2.0)[0]
        for key, ls in (("nom0", "--"), ("nom1", ":")):
            e = paths(cs[key]); e = e[(e.kind == "macro") & (e["var"] == v)]; H_[key] = ax.plot(e.h, e.r, color=ORANGE, ls=ls, lw=1.9)[0]
        for st, mk, fc, sz in (("Bauer-Swanson benchmark", "o", INK, 20), ("Bauer-Swanson unadjusted", "s", "none", 52)):
            sub = LIT[(LIT.study == st) & (LIT.variable == vm[v]) & LIT.horizon_months.isin([12, 24, 36])]
            H_[st] = ax.scatter(sub.horizon_months, sub.response_per_1pp, marker=mk, s=sz, facecolors=fc, edgecolors=INK, linewidths=1.2, zorder=5)
        ax.set_xlabel("Months after the policy move"); ax.set_ylabel(ylab); ax.set_xlim(0, 36)
    labs = ["r*-gap 2-year yield and FCI (baseline; bands: 68 and 90 percent)", "Nominal 2-year yield alone", "Nominal 2-year yield and FCI", "Bauer and Swanson (2023), orthogonalized surprise (Fig. 8)", "Bauer and Swanson (2023), unadjusted surprise (Fig. B.1)"]
    fig.legend([H_["b"], H_["nom0"], H_["nom1"], H_["Bauer-Swanson benchmark"], H_["Bauer-Swanson unadjusted"]], labs, loc="lower center", ncol=2, frameon=False, fontsize=7.2)
    fig.tight_layout(rect=[0, 0.17, 1, 1]); fig.savefig(REPORT / "fig_size.pdf"); plt.close(fig)
fig_size()
print("report inputs written to", REPORT)
