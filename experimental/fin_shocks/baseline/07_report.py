"""Step 7. Tables and figures of the results document from results/ (12-lag main tables by section, 3/6/12-lag appendix tables by panel, the response
figures, the weights table and the trade-off table). Compile report/baseline_robustness.tex with pdflatex (twice).   python3 05_report.py"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cases as CS
from lib.paths import RESULTS, REPORT, OUT

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

# ---------------------------------------------------------------- proxy-VAR simulation tables
SIM = pd.read_csv(RESULTS / "proxy_sim_summary.csv")
SIMLAB = {"F": "First-stage $F$", "u12 estimate": "Unemployment, 12 m", "P24 estimate": "Price level, 24 m", "u12 set unbounded": "Unemployment, 12 m: set unbounded",
          "P24 set unbounded": "Price level, 24 m: set unbounded", "u12 estimate negative": "Unemployment, 12 m: estimate negative",
          "u12 set bounded and below zero": "Unemployment, 12 m: set bounded and below zero", "impact on FCI per +1 pp 2-year": "Impact on the FCI per +1 pp 2-year",
          "u12 window impact (window units)": "Unemployment, 12 m (window units)", "P24 window impact (window units)": "Price level, 24 m (window units)"}
def sim_table(step, title, label, place="H"):
    d = SIM[SIM.step == step]; out = [rf"\begin{{table}}[{place}]\centering\footnotesize\setlength{{\tabcolsep}}{{3pt}}", rf"\caption{{{title}}}\label{{{label}}}",
        r"\begin{tabular}{lrrrrr}\toprule Quantity & Data & True & Simulated median & 5th--95th & Share $\le$ data\\ \midrule"]
    for sysname, head in (("nofci", "A. Proxy VAR without the FCI"), ("fci", "B. Proxy VAR with the FCI"), ("we", "C. Monthly VAR with the window impact")):
        out.append(rf"\multicolumn{{6}}{{l}}{{\textit{{{head}}}}}\\")
        for _, r in d[d.system == sysname].iterrows():
            if r.binary: cells = ("yes" if r.data else "no", "", f"{r.sim_median:.0f}" if False else "", "", f"{r.sim_freq:.2f}")
            else:
                f = "{:.1f}" if r.quantity == "F" else "{:.2f}"; sg = lambda x: ("$-$" if x < 0 and f.format(abs(x)) != "0.00" else "") + f.format(abs(x))
                cells = (sg(r.data), sg(r.truth) if pd.notna(r.truth) else "", sg(r.sim_median), f"[{sg(r.sim_p05)}, {sg(r.sim_p95)}]", f"{r.share_le_data:.2f}")
            out.append(f"\\quad {SIMLAB[r.quantity]} & " + " & ".join(cells) + r"\\")
    gen = (r"generated by the estimated r*-gap model with the FCI (12 lags) as the true process" + ("" if step == "rstar" else r", analysed with the 2-year yield and the FCI measured in " + {"nom": "nominal", "real": "real"}[step] + r" form (the r*-gap series plus the actual expected-inflation and r* terms, which do not depend on the policy shock)"))
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.95\linewidth}{\scriptsize 1,000 samples of 369 months " + gen + r", with the data's calendar and announcement days; proxy VAR with 12 lags. Data: the 1996 sample, 12 lags, in the same form. True: the r*-gap model's response per +1 pp on the monthly-average 2-year yield (ratio of the window response to its contemporaneous monthly-average response), or per +1 pp in the window in panel C. For yes/no rows the last column is the simulated frequency of the event. A data value near the middle of the simulated distribution (share close to 0.5) means the data look like a typical sample from the model.}", r"\end{table}"]
    return "\n".join(out)
for step in ("rstar", "nom", "real"):
    (REPORT / f"tab_proxy_sim_{step}.tex").write_text(sim_table(step, ("Would a monthly proxy VAR look like the data if the r*-gap model were true? " + {"rstar": "r*-gap measures", "nom": "Nominal measures", "real": "Real measures"}[step]), f"tab:proxysim{step}", "H" if step == "rstar" else "p") + "\n")

# ---------------------------------------------------------------- daily-block model on simulated samples
DSIM = pd.read_csv(RESULTS / "daily_sim_summary.csv"); DLAB = {"u12": "Unemployment, 12 m", "u24": "Unemployment, 24 m", "P12": "Price level, 12 m", "P24": "Price level, 24 m"}
def daily_sim_table():
    out = [r"\begin{table}[H]\centering\footnotesize\setlength{\tabcolsep}{3pt}", r"\caption{The daily-block model on samples simulated from the r*-gap model: data estimates and simulated distributions (12 lags)}\label{tab:dailysim}",
           r"\begin{tabular}{lrrrrrrr}\toprule & & \multicolumn{2}{c}{r*-gap measures} & \multicolumn{2}{c}{Nominal measures} & \multicolumn{2}{c}{Real measures}\\ \cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}",
           r"Response & True & Data & Simulated & Data & Simulated & Data & Simulated\\ \midrule"]
    for fci, head in ((1, "A. 2-year yield and FCI"), (0, "B. 2-year yield only")):
        out.append(rf"\multicolumn{{8}}{{l}}{{\textit{{{head}}}}}\\")
        for q in ("u12", "u24", "P12", "P24"):
            g = {f: DSIM[(DSIM.form == f) & (DSIM.fci == fci) & (DSIM.quantity == q)].iloc[0] for f in ("rstar", "nom", "real")}
            l1 = [num(g["rstar"].truth)] + sum([[num(g[f].data) + ("" if g[f].data_in_90 else r"$^{\dagger}$"), num(g[f].sim_median)] for f in ("rstar", "nom", "real")], [])
            l2 = [""] + sum([["", rf"{{\scriptsize [{num(g[f].sim_p05)}, {num(g[f].sim_p95)}]}}"] for f in ("rstar", "nom", "real")], [])
            out += [f"\\quad {DLAB[q]} & " + " & ".join(l1) + r"\\", " & " + " & ".join(l2) + r"\\"]
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.96\linewidth}{\scriptsize 1,000 samples of 369 months generated by the estimated r*-gap model with the FCI. On each sample the full model (daily HAR block and monthly equations, 12 lags, no trend) is re-estimated with the 2-year yield (and the FCI) measured in the stated form; nominal and real measures are the r*-gap series plus the actual expected-inflation and r* terms. Responses per +1 pp on the 2-year yield in the announcement window. True: the r*-gap model's responses, which equal the r*-gap data estimates by construction. Simulated: median and 5th--95th percentiles. $^{\dagger}$: the data estimate lies outside the simulated 90\% band.}", r"\end{table}"]
    return "\n".join(out)
(REPORT / "tab_daily_sim.tex").write_text(daily_sim_table() + "\n")

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
fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.4), sharex=True)
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
print("report inputs written to", REPORT)
