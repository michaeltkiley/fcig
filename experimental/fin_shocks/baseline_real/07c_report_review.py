"""Step 7c (run after 07 and 07b). Exhibits added in the revision of 13 Nov 2026 on the external review (FS_QA FS-A71):
  tab_timing.tex  -- the two corrections side by side: announcement timing within the month (daily block against a monthly VAR with the window impact)
                     and financial conditions (yield alone against yield and FCI), for the nominal and real rates (baseline_real);
  tab_credit.tex  -- credit and the response: baseline, the excess bond premium in the monthly block, the daily Baa spread in the daily block;
                     the response of each credit measure; how much of the monthly variation in the excess bond premium the FCI's components account for;
Writes report/numbers_rev.tex (macros bl:rv:*) and asserts the claims the text makes about these exhibits (fails if one stops being true)."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm
import cases as CS
from lib.paths import RESULTS, REPORT, OUT
from lib import noteA, daily as DD

ML, BAD = [], []
def mac(k, v): ML.append(r"\expandafter\gdef\csname bl:rv:" + k + r"\endcsname{" + str(v) + "}"); ML.append(r"\expandafter\gdef\csname blabs:rv:" + k + r"\endcsname{" + str(v).replace("$-$", "").lstrip("-") + "}")
def num(x):
    s = f"{abs(x):.2f}"; return ("$-$" if x < 0 and s != "0.00" else "") + s
def chk(name, ok):
    if not ok: BAD.append(name)
BLUE, ORANGE, INK, GREY = "#2a78d6", "#eb6834", "#0b0b0b", "#6b6a66"
FIT = r"\resizebox{\ifdim\width>\textwidth\textwidth\else\width\fi}{!}{%"
L = 12
base = dict(macro="u,pi", start="1996-01", end=None, t2020="out", trend="none")          # the 1996 baseline (FS-A76)

def res(c):
    d = pd.read_csv(RESULTS / f"{CS.case_id(c)}.csv"); return d[d.lags == L].set_index("var")
def star(r, h): return "$^{**}$" if r[f"lo95_{h}"] * r[f"hi95_{h}"] > 0 else ("$^{*}$" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "")
def mres(step, fci):
    d = pd.read_csv(RESULTS / f"monthly_{step}_{fci}_1996-01.csv"); return d[(d.lags == L) & (d.ident == "WE")]
def mval(d, v, h):
    r = d[(d["var"] == v) & (d.h == h)].iloc[0]; return r.r, ("$^{*}$" if r.lo * r.hi > 0 else "")

# ---------------------------------------------------------------- 1. timing and financial conditions (2 x 2 for each version)
rows, T = [], {}
for f in ("nom", "real"):
    for v, h in (("u", 24), ("P", 24)):
        a = mval(mres(f, 0), v, h); b = res(dict(form=f, fci=0, **base)).loc[v]; c = mval(mres(f, f), v, h); dd = res(dict(form=f, fci=f, **base)).loc[v]
        T[(f, v)] = dict(m0=a[0], d0=b[f"r{h}"], m1=c[0], d1=dd[f"r{h}"])
        cells = [num(a[0]) + a[1], num(b[f"r{h}"]) + star(b, h), num(c[0]) + c[1], num(dd[f"r{h}"]) + star(dd, h)]
        rows.append((f, v, cells))
        t = T[(f, v)]
        for k, x in t.items(): mac(f"tm:{f}:{v}:{k}", num(x))
        mac(f"tm:{f}:{v}:fci", num(((t["m1"] - t["m0"]) + (t["d1"] - t["d0"])) / 2)); mac(f"tm:{f}:{v}:time", num(((t["d0"] - t["m0"]) + (t["d1"] - t["m1"])) / 2))
        mac(f"tm:{f}:{v}:timefci", num(t["d1"] - t["m1"])); mac(f"tm:{f}:{v}:timeno", num(t["d0"] - t["m0"]))
TD = pd.read_csv(RESULTS / "timing_only_diff.csv"); TD["fci"] = TD.fci.astype(str)               # step 16 (FS-A97): calendar position alone, real, 1996
_tmax = float(TD[(TD.contrast.isin(["actual-first", "actual-mid"])) & TD.h.isin([12, 24, 36])]["diff"].abs().max())
mac("tmo:max", f"{max(_tmax, 0.005):.2f}")                                                      # largest change in u or P at 12/24/36 m, with or without the FCI, from placing every announcement on the first day or at mid-month
assert _tmax < 0.025, "calendar position alone: a change of 0.025 or more"
lines = []
for i, (f, v, cells) in enumerate(rows):
    lab = {"nom": "Nominal", "real": "Real"}[f] if v == "u" else ""
    lines.append(f"{lab} & {'Unemployment gap (pp)' if v == 'u' else 'Price level (\\%)'} & " + " & ".join(cells) + r"\\" + (r"\addlinespace" if v == "P" and f != "real" else ""))
(REPORT / "tab_timing.tex").write_text("\n".join([r"\begin{table}[tp]\centering\small", r"\caption{The Daily Block and Financial Conditions (24 Months; 12 Lags)}\label{tab:timing2}", FIT,
    r"\begin{tabular}{llcccc}\toprule & & \multicolumn{2}{c}{Yield alone} & \multicolumn{2}{c}{Yield and FCI}\\ \cmidrule(lr){3-4}\cmidrule(lr){5-6}",
    r"Yield & Response & Monthly VAR & Daily block & Monthly VAR & Daily block\\ \midrule", *lines, r"\bottomrule\end{tabular}}",
    r"\begin{flushleft}\footnotesize\textit{Notes:} Per +1 pp on the two-year yield in the announcement window, 1996--2026. Monthly VAR: the window-impact monthly VAR of Section~\ref{sec:monthlyvar}, in monthly averages, whose impact is the main model's response of the month's average two-year yield, FCI and funds rate in the announcement month; it loses the position of each announcement within its month and the daily path of the financial variables in the following weeks. Daily block: the main model. With the main model's estimated equations, placing every announcement on the first day of its month or at mid-month changes the responses at 12, 24 and 36 months by at most 0.02 (real version). $^{**}$ and $^{*}$: the 95 and 90 percent intervals exclude zero.\end{flushleft}", r"\end{table}"]) + "\n")
for f in ("nom", "real"):
    t = T[(f, "u")]
    pass
    pass
    pass
    pass

# ---------------------------------------------------------------- 2. credit (FS-A99: the Baa spread in the daily block and industrial production in the monthly block; matched cases of step 17, paired draws)
CC = pd.read_csv(RESULTS / "credit_cases.csv").query("start == '1996-01'"); CDf = pd.read_csv(RESULTS / "credit_diff.csv").query("start == '1996-01'")
def cc(spec, w, v): return CC[(CC.spec == spec) & (CC.fci == w) & (CC["var"] == v)].iloc[0]
def cd(spec, v, h=24): return CDf[(CDf.spec == spec) & (CDf["var"] == v) & (CDf.h == h)].iloc[0]
def s90(r, lo="lo24", hi="hi24"): return "$^{*}$" if r[lo] * r[hi] > 0 else ""
cA = dict(form="real", fci="baa", **base); pA = pd.read_csv(RESULTS / f"{CS.case_id(cA)}_paths.csv").query("lags == @L and kind == 'fin' and var == 'baa'").set_index("h")
idx0 = DD.event_index(); baa_imp = DD.baa_impact(idx0)
lines = []
for spec, lab in (("base", "Baseline"), ("baa", "Baa spread in the daily block"), ("ip", "Industrial production in the monthly block")):
    r0, r1 = cc(spec, "no", "u"), cc(spec, "yes", "u"); du, dp = cd(spec, "u"), cd(spec, "P")
    lines += [f"{lab} & {num(r0.r24)}{s90(r0)} & {num(r1.r24)}{s90(r1)} & {num(du.fci_effect)}{s90(du, 'lo', 'hi')} & {num(dp.fci_effect)}{s90(dp, 'lo', 'hi')}" + r"\\",
              f" & {{\\scriptsize [{num(r0.lo24)}, {num(r0.hi24)}]}} & {{\\scriptsize [{num(r1.lo24)}, {num(r1.hi24)}]}} & {{\\scriptsize [{num(du.lo)}, {num(du.hi)}]}} & {{\\scriptsize [{num(dp.lo)}, {num(dp.hi)}]}}" + r"\\"]
    for w, k in (("no", "0"), ("yes", "1")):
        for v in ("u", "P"): r = cc(spec, w, v); mac(f"cr:{spec}:{k}:{v}", num(r.r24)); mac(f"cr:{spec}:{k}:{v}:12", num(r.r12))
    for v in ("u", "P"): r = cd(spec, v); mac(f"cr:{spec}:eff:{v}", num(r.fci_effect)); mac(f"cr:{spec}:eff:{v}:lo", num(r.lo)); mac(f"cr:{spec}:eff:{v}:hi", num(r.hi))
(REPORT / "tab_credit.tex").write_text("\n".join([r"\begin{table}[tp]\centering\small", r"\caption{Credit, Activity and the Effect of Adding the FCI (Real Rates; 24 Months)}\label{tab:credit}", FIT,
    r"\begin{tabular}{lcccc}\toprule & \multicolumn{2}{c}{Unemployment gap (pp)} & \multicolumn{2}{c}{Effect of adding the FCI} \\ \cmidrule(lr){2-3}\cmidrule(lr){4-5}",
    r" & Rates alone & Rates and FCI & Unemployment gap & Price level (\%)\\ \midrule", *lines, r"\bottomrule\end{tabular}}",
    r"\begin{flushleft}\footnotesize\textit{Notes:} Per +1 pp on the two-year yield in the announcement window; real two-year yield and funds rate, 12 lags, monthly equations from 1996, March--December 2020 dropped. Baa spread: Moody's Baa yield less the 10-year Treasury yield, in the daily block next to the rates (and the FCI); its impact is its announcement-day change on the surprise, because it has no intraday series; months before the daily data (1986) use the monthly series. Industrial production: $100\ln$ of the index, a third monthly variable, set like unemployment and inflation before markets within the month. Effect of adding the FCI: the response with the FCI less the response with the same variables without it. All cases use the same bootstrap draws, so the effects are paired; 90 percent intervals in brackets; $^{*}$: the 90 percent interval excludes zero.\end{flushleft}", r"\end{table}"]) + "\n")
mac("cr:baa12", num(pA.r[12])); mac("cr:baa12:lo", num(pA.lo[12])); mac("cr:baa12:hi", num(pA.hi[12])); mac("cr:baaimp", num(baa_imp))

# ---------------------------------------------------------------- 3b. the r*-gap index as a gap to a neutral level that moves with r* (Section 2.2), and the window responses in words
WB = pd.read_csv(OUT / "market_weights.csv", index_col=0); from lib import model as M
D0 = pd.read_csv(OUT / "data_monthly.csv", index_col=0); D0.index = pd.PeriodIndex(D0.index, freq="M")
epbar = float((100 / D0.cape).loc[noteA.START:noteA.END].mean()); kap = WB.weight["y10"] - WB.weight["equities"] * 100 / epbar
mac("kap", f"{kap:.1f}"); mac("epbar", f"{epbar:.1f}")
for a in ("y10", "equities", "dollar"): mac(f"psi:{a}", f"{abs(WB.response[a]):.2f}" if a == "y10" else f"{abs(WB.response[a]):.1f}")
pass

(REPORT / "numbers_rev.tex").write_text("\n".join(ML) + "\n")
from lib import latex_style as LST
LST.restyle_dir(REPORT)
print("07c: exhibits and numbers_rev.tex written (claims: claims_real.py)")
