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
        elif g == "R4": blocks += [(CS.FORMS[f] + (", start 1973" if pid == "R4b" else ""), [c for c in p["cases"] if c["form"] == f]) for f in ("nom", "real", "rstar")]
        else: blocks.append((CS.SHORT[pid], p["cases"]))
    notes = CS.GROUP_NOTE[g]
    (REPORT / f"tab_main_{g}.tex").write_text(table(CS.GROUP_TITLE[g] + " (12 lags)", f"tab:main{g}", blocks, (MAIN_LAGS,), notes) + "\n")
for p in CS.PANELS:                                                                  # appendix: 3, 6, 12 lags
    f = lambda c: CS.FORMS[c["form"]]
    blocks = [(CS.FORMS[fm], [c for c in p["cases"] if c["form"] == fm]) for fm in dict.fromkeys(c["form"] for c in p["cases"])] if p["id"] in ("B", "R4", "R4b") else [(f(p["cases"][0]), p["cases"])]
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
MNOTE = (r"Monthly VAR in the unemployment gap, core PCE inflation, the end-of-month 2-year yield and, when included, the end-of-month FCI (same step), 1996 to September 2026, no trend, nothing dropped. "
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
    LS = pd.read_csv(RESULTS / "lit_style.csv"); LSI = pd.read_csv(RESULTS / "lit_style_info.csv").set_index("case")
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
    WT = pd.read_csv(RESULTS / "weights_test.csv")
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
        return r[f"r{h}"], r[f"lo{h}"] * r[f"hi{h}"] > 0
    est = lambda *k: g(*k)[0]; sig = lambda *k: g(*k)[1]; S = ("nom", "real", "rstar"); bad = []
    chk = lambda name, ok: None if ok else bad.append(name)
    for f in ("nom", "real"):
        chk(f"{f}: yield alone, unemployment falls significantly at 12 m", est(f, "no", "u", 12) < 0 and sig(f, "no", "u", 12)); chk(f"{f}: yield alone, price level does not respond significantly at 24 m", not sig(f, "no", "P", 24))
    chk("rstar: yield alone, unemployment does not rise (12, 24 m)", est("rstar", "no", "u", 12) < 0.0 and not sig("rstar", "no", "u", 12) and not sig("rstar", "no", "u", 24)); chk("rstar: yield alone, price level falls significantly at 24 m", est("rstar", "no", "P", 24) < 0 and sig("rstar", "no", "P", 24))
    for f in S:
        chk(f"{f}: with FCI, no significant fall in unemployment", all(not (est(f, "yes", "u", h) < 0 and sig(f, "yes", "u", h)) for h in (12, 24, 36)))
        chk(f"{f}: with FCI, unemployment positive at 24 and 36 m", est(f, "yes", "u", 24) > 0 and est(f, "yes", "u", 36) > 0)
        chk(f"{f}: with FCI, price level falls at 12, 24, 36 m", all(est(f, "yes", "P", h) < 0 for h in (12, 24, 36)))
    chk("with FCI, unemployment not significantly negative at any step and horizon", not any(est(f, "yes", "u", h) < 0 and sig(f, "yes", "u", h) for f in ("nom", "real", "rstar") for h in (12, 24, 36)))
    chk("with FCI, price level significant at 24 and 36 m at the real and r*-gap steps, at 36 m only at the nominal step", all(sig(f, "yes", "P", h) for f in ("real", "rstar") for h in (24, 36)) and sig("nom", "yes", "P", 36) and not sig("nom", "yes", "P", 24))
    chk("r*-gap with FCI has the largest price fall at 24 m", est("rstar", "yes", "P", 24) < min(est("nom", "yes", "P", 24), est("real", "yes", "P", 24)))
    LS = pd.read_csv(RESULTS / "lit_style.csv"); ls = lambda c, v, h: LS[(LS.case == c) & (LS["var"] == v) & (LS.h == h)].iloc[0]; lsig = lambda c, v, h: ls(c, v, h).lo * ls(c, v, h).hi > 0
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
    WT = pd.read_csv(RESULTS / "weights_test.csv"); chk("weights test, monthly equations from 1973, 12 lags: no rejection at 5% in either equation at any step", bool((WT[(WT.start == "1973-01") & (WT.lags == MAIN_LAGS)].p_boot > 0.05).all())); wt = lambda s_, e_, L_: WT[(WT.step == s_) & (WT["eq"] == e_) & (WT.lags == L_) & (WT.start == "1996-01")].p_boot.iloc[0]
    chk("weights test, 12 lags: no rejection at 5% in the unemployment equation at any step; rejection in the inflation equation at every step", all(wt(s_, "u", 12) > 0.05 for s_ in S) and all(wt(s_, "pi", 12) < 0.05 for s_ in S))
    assert not bad, "claims in the note no longer hold: " + "; ".join(bad)
check_claims()

# ---------------------------------------------------------------- test of the proportional-weights restriction
WTT = pd.read_csv(RESULTS / "weights_test.csv"); wrows = []
for start, lab in (("1996-01", ""), ("1973-01", ", start 1973")):
    for step in ("nom", "real", "rstar"):
        cells = []
        for eq in ("u", "pi"):
            r = WTT[(WTT.step == step) & (WTT.lags == MAIN_LAGS) & (WTT["eq"] == eq) & (WTT.start == start)].iloc[0]; cells.append(f"{r.wald:.1f} & {r.p_boot:.3f}")
        wrows.append(f"{CS.FORMS[step]}{lab} & " + " & ".join(cells) + r"\\")
(REPORT / "tab_weights_test.tex").write_text("\n".join([r"\begin{table}[H]\centering\small", r"\caption{Test of the proportional-weights restriction (12 lags)}\label{tab:weightstest}",
    r"\begin{tabular}{lrrrr}\toprule & \multicolumn{2}{c}{Unemployment gap equation} & \multicolumn{2}{c}{Core PCE inflation equation}\\ \cmidrule(lr){2-3}\cmidrule(lr){4-5}", r"Step & Wald & Bootstrap $p$ & Wald & Bootstrap $p$\\ \midrule", *wrows, r"\bottomrule\end{tabular}",
    r"\par\smallskip\parbox{0.92\linewidth}{\scriptsize Wald statistic (heteroskedasticity-robust, HC1) for the restriction that the coefficients on the three weighted components (10-year yield, equity valuation, dollar) are equal at each lag (24 restrictions), in each monthly equation, and the bootstrap $p$-value (999 residual draws under the restriction); monthly equations from 1996 (first three rows) and from 1973 (last three), no trend, 2020 in. The unrestricted equation is the one used in Robustness 4.}", r"\end{table}"]) + "\n")

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

# ---------------------------------------------------------------- standard methods (Section 3.1) and the baseline figure (Section 3.2)
LSR = pd.read_csv(RESULTS / "lit_style.csv")
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
    info = pd.read_csv(RESULTS / "lit_style_info.csv").set_index("case")
    for case, lab, smp in rows:
        cells = []
        for v in ("u", "P"):
            for h in (12, 24, 36):
                r = LSR[(LSR.case == case) & (LSR["var"] == v) & (LSR.h == h)].iloc[0]; cells.append((num(r.point) + ("$^{*}$" if r.lo * r.hi > 0 else ""), f"[{num(r.lo)}, {num(r.hi)}]"))
        out += [f"{lab} & {smp} & {int(info.nobs[case])} & " + " & ".join(c[0] for c in cells) + r"\\", r" & & & " + " & ".join(rf"{{\scriptsize {c[1]}}}" for c in cells) + r"\\"]
    out += [r"\bottomrule\end{tabular}", r"\par\smallskip\parbox{0.96\linewidth}{\scriptsize Monthly data, 12 lags, constant, no trend; unemployment gap, core PCE inflation and the end-of-month policy rate (the 2-year Treasury yield, or the effective federal funds rate where stated), policy rate ordered last in the Cholesky VARs; price level = cumulated inflation/12. " 
            + extra + r" Unit: +1 pp on the policy rate on impact. Brackets: 90\% intervals (residual bootstrap for the Cholesky VARs; exact Anderson--Rubin sets for the proxy VAR). $^{*}$ = excludes zero. Specification: baseline/lib/litstyle.py.}", r"\end{table}"]
    (REPORT / fname).write_text("\n".join(out) + "\n")
_F = pd.read_csv(RESULTS / "lit_style_info.csv").set_index("case").F["proxy_2y_1996"]
standard_table([("chol_2y_1996", "Cholesky, 2-year yield", "1996--2026"), ("chol_2y_1984", "Cholesky, 2-year yield", "1984--2026"), ("chol_ffr_1984_2007", "Cholesky, federal funds rate", "1984--2007"), ("proxy_2y_1996", "Proxy VAR, 2-year yield", "1996--2026")],
               "tab_standard.tex", "tab:standard", "Standard methods after the early 1980s: responses to a 1 percentage point rise in the policy rate", f"Proxy VAR: Nakamura--Steinsson policy news summed within the month as instrument; first-stage $F$ = {_F:.1f}.")
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
print("report inputs written to", REPORT)
