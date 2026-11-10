"""Build report/tab_<panel>.tex from results/*.csv and cases.py. Compile report/baseline_robustness.tex (pdflatex, twice).
   python3 make_report.py"""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pandas as pd, cases as CS

R = {}
for f in glob.glob(os.path.join(HERE, "results", "*.csv")):
    R[os.path.basename(f)[:-4]] = pd.read_csv(f)

def num(x):
    s = f"{abs(x):.2f}"
    return ("$-$" if x < 0 and s != "0.00" else "") + s
def cell(r, v, h):
    p, lo, hi = r[f"r{h}"], r[f"lo{h}"], r[f"hi{h}"]
    star = "$^{*}$" if lo * hi > 0 else ""
    return num(p) + star, f"[{num(lo)}, {num(hi)}]"

def table(p):
    lines = [r"\begin{table}[p]\centering\footnotesize\setlength{\tabcolsep}{2.2pt}", rf"\caption{{{p['title']}}}\label{{tab:{p['id']}}}",
             r"\begin{tabular}{llcrrrrrrr}\toprule",
             r" & & & & \multicolumn{3}{c}{Unemployment gap (pp)} & \multicolumn{3}{c}{Price level (\%)}\\ \cmidrule(lr){5-7}\cmidrule(lr){8-10}",
             r"2-year & FCI & Lags & Obs & 12 m & 24 m & 36 m & 12 m & 24 m & 36 m\\ \midrule"]
    last = None
    for c in p["cases"]:
        d = R.get(CS.case_id(c))
        if d is None: continue
        if last is not None and c["form"] != last: lines.append(r"\addlinespace")
        last = c["form"]
        for L in (3, 6, 12):
            u = d[(d["var"] == "u") & (d.lags == L)].iloc[0]; pr = d[(d["var"] == "P") & (d.lags == L)].iloc[0]
            pts, ivs = zip(*[cell(r, v, h) for r, v in ((u, "u"), (pr, "P")) for h in (12, 24, 36)])
            lab = (CS.FORMS[c["form"]] if L == 3 else "")
            fl = (CS.FCI_LABEL[c["fci"]] if L == 3 else "")
            lines.append(f"{lab} & {fl} & {L} & {int(u.nobs)} & " + " & ".join(pts) + r"\\")
            lines.append(r" & & & & " + " & ".join(rf"{{\scriptsize {x}}}" for x in ivs) + r"\\")
    lines += [r"\bottomrule\end{tabular}", rf"\par\smallskip\parbox{{0.96\linewidth}}{{\scriptsize {p['notes']} Per +1 pp on the 2-year yield. $^{{*}}$ = 90\% interval excludes zero; intervals in brackets. Obs = monthly observations in the equations.}}", r"\end{table}"]
    return "\n".join(lines)

for p in CS.PANELS:
    open(os.path.join(HERE, "report", f"tab_{p['id']}.tex"), "w").write(table(p) + "\n")
print("tables for", sum(1 for p in CS.PANELS if all(CS.case_id(c) in R for c in p["cases"])), "complete panels of", len(CS.PANELS))
