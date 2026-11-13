"""Step 7c (run after 07 and 07b). Exhibits added in the revision of 13 Nov 2026 on the external review (FS_QA FS-A71):
  tab_timing.tex  -- the two corrections side by side: announcement timing within the month (daily block against a monthly VAR with the window impact)
                     and financial conditions (yield alone against yield and FCI), for the nominal, real and r*-gap yield;
  tab_credit.tex  -- credit and the response: baseline, the excess bond premium in the monthly block, the daily Baa spread in the daily block;
                     the response of each credit measure; how much of the monthly variation in the excess bond premium the FCI's components account for;
  tab_jk.tex      -- information effects: the FCI weights re-estimated on the Jarocinski-Karadi subset and the responses with them;
  fig_ordinary.pdf -- the same 1 pp rise in the two-year yield on an ordinary day and in an announcement window: the accompanying FCI movement.
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
base = dict(macro="u,pi", start="1996-01", end=None, t2020="in", trend="none")

def res(c):
    d = pd.read_csv(RESULTS / f"{CS.case_id(c)}.csv"); return d[d.lags == L].set_index("var")
def star(r, h): return "$^{**}$" if r[f"lo95_{h}"] * r[f"hi95_{h}"] > 0 else ("$^{*}$" if r[f"lo{h}"] * r[f"hi{h}"] > 0 else "")
def mres(step, fci):
    d = pd.read_csv(RESULTS / f"monthly_{step}_{fci}_1996-01.csv"); return d[(d.lags == L) & (d.ident == "WE")]
def mval(d, v, h):
    r = d[(d["var"] == v) & (d.h == h)].iloc[0]; return r.r, ("$^{*}$" if r.lo * r.hi > 0 else "")

# ---------------------------------------------------------------- 1. timing and financial conditions (2 x 2 for each version)
rows, T = [], {}
for f in ("nom", "real", "rstar"):
    for v, h in (("u", 24), ("P", 24)):
        a = mval(mres(f, 0), v, h); b = res(dict(form=f, fci=0, **base)).loc[v]; c = mval(mres(f, f), v, h); dd = res(dict(form=f, fci=f, **base)).loc[v]
        T[(f, v)] = dict(m0=a[0], d0=b[f"r{h}"], m1=c[0], d1=dd[f"r{h}"])
        cells = [num(a[0]) + a[1], num(b[f"r{h}"]) + star(b, h), num(c[0]) + c[1], num(dd[f"r{h}"]) + star(dd, h)]
        rows.append((f, v, cells))
        t = T[(f, v)]
        for k, x in t.items(): mac(f"tm:{f}:{v}:{k}", num(x))
        mac(f"tm:{f}:{v}:fci", num(((t["m1"] - t["m0"]) + (t["d1"] - t["d0"])) / 2)); mac(f"tm:{f}:{v}:time", num(((t["d0"] - t["m0"]) + (t["d1"] - t["m1"])) / 2))
        mac(f"tm:{f}:{v}:timefci", num(t["d1"] - t["m1"])); mac(f"tm:{f}:{v}:timeno", num(t["d0"] - t["m0"]))
lines = []
for i, (f, v, cells) in enumerate(rows):
    lab = {"nom": "Nominal", "real": "Real", "rstar": "$r^*$-gap"}[f] if v == "u" else ""
    lines.append(f"{lab} & {'Unemployment gap (pp)' if v == 'u' else 'Price level (\\%)'} & " + " & ".join(cells) + r"\\" + (r"\addlinespace" if v == "P" and f != "rstar" else ""))
(REPORT / "tab_timing.tex").write_text("\n".join([r"\begin{table}[tp]\centering\small", r"\caption{Two Corrections: Announcement Timing and Financial Conditions (24 Months; 12 Lags)}\label{tab:timing2}", FIT,
    r"\begin{tabular}{llcccc}\toprule & & \multicolumn{2}{c}{Yield alone} & \multicolumn{2}{c}{Yield and FCI}\\ \cmidrule(lr){3-4}\cmidrule(lr){5-6}",
    r"Yield & Response & Monthly VAR & Daily block & Monthly VAR & Daily block\\ \midrule", *lines, r"\bottomrule\end{tabular}}",
    r"\begin{flushleft}\footnotesize\textit{Notes:} Per +1 pp on the two-year yield in the announcement window, 1996--2026. Monthly VAR: the window-impact monthly VAR of Section~\ref{sec:monthlyvar}, which takes the impact from the windows and treats every announcement as if it fell at the start of its month (end-of-month series). Daily block: the main model, which tracks when in the month each announcement falls. $^{**}$ and $^{*}$: the 95 and 90 percent intervals exclude zero.\end{flushleft}", r"\end{table}"]) + "\n")
for f in ("nom", "real", "rstar"):
    t = T[(f, "u")]
    chk(f"timing [{f}]: adding the FCI raises unemployment at 24 m with and without the daily block", t["m1"] > t["m0"] and t["d1"] > t["d0"])
    chk(f"timing [{f}]: the FCI's effect on unemployment exceeds the timing effect", (t["m1"] - t["m0"] + t["d1"] - t["d0"]) / 2 > abs((t["d0"] - t["m0"] + t["d1"] - t["m1"]) / 2))
    chk(f"timing [{f}]: the daily block raises unemployment by more with the FCI than without", t["d1"] - t["m1"] > t["d0"] - t["m0"])
    chk(f"timing [{f}]: with the yield alone neither model has unemployment rising at 24 m", t["m0"] < 0.05 and t["d0"] < 0.05)

# ---------------------------------------------------------------- 2. credit
cB = dict(form="rstar", fci="rstar", **base); cE = dict(form="rstar", fci="rstar", **{**base, "macro": "u,pi,ebp"}); cA = dict(form="rstar", fci="baa", **base)
cB0, cE0 = dict(form="rstar", fci=0, **base), dict(form="rstar", fci=0, **{**base, "macro": "u,pi,ebp"})
def paths(c): return pd.read_csv(RESULTS / f"{CS.case_id(c)}_paths.csv").query("lags == @L")
pE = paths(cE).query("kind == 'macro' and var == 'ebp'").set_index("h"); pA = paths(cA).query("kind == 'fin' and var == 'c2'").set_index("h")
rB, rE, rA, rB0, rE0 = res(cB), res(cE), res(cA), res(cB0), res(cE0)
idx0 = DD.event_index(); baa_imp = DD.baa_impact(idx0)
# share of the monthly variation in the excess bond premium accounted for by the three weighted components of the r*-gap FCI (1996-2026), levels and 3-month changes
D0 = pd.read_csv(OUT / "data_monthly.csv", index_col=0); D0.index = pd.PeriodIndex(D0.index, freq="M")
M0 = pd.read_csv(OUT / "macro_monthly.csv", index_col=0); M0.index = pd.PeriodIndex(M0.index, freq="M")
W = pd.read_csv(OUT / "market_weights.csv", index_col=0).weight
X = noteA.index_inputs(D0, "rstar", "rstar LW")[noteA.MARKET_VARS] * W.values
Z = X.join(M0.ebp).loc["1996-01":"2026-09"].dropna()
r2l = sm.OLS(Z.ebp, sm.add_constant(Z[noteA.MARKET_VARS])).fit().rsquared
dZ = Z.diff(3).dropna(); r2d = sm.OLS(dZ.ebp, sm.add_constant(dZ[noteA.MARKET_VARS])).fit().rsquared
r2eq = sm.OLS(dZ.ebp, sm.add_constant(dZ[["equities"]])).fit().rsquared
lines = []
for lab, r, r0, cred in (("Baseline", rB, rB0, "--"), ("Excess bond premium in the monthly block", rE, rE0, f"{num(pE.r[12])} [{num(pE.lo[12])}, {num(pE.hi[12])}]"),
                         ("Baa spread in the daily block", rA, rB0, f"{num(pA.r[12])} [{num(pA.lo[12])}, {num(pA.hi[12])}]")):
    lines.append(f"{lab} & {num(r0.loc['u'].r24)}{star(r0.loc['u'], 24)} & {num(r.loc['u'].r24)}{star(r.loc['u'], 24)} & {num(r.loc['P'].r24)}{star(r.loc['P'], 24)} & {cred}" + r"\\")
(REPORT / "tab_credit.tex").write_text("\n".join([r"\begin{table}[tp]\centering\small", r"\caption{Credit and the Response ($r^*$-Gap Yield; 12 Lags)}\label{tab:credit}", FIT,
    r"\begin{tabular}{lcccc}\toprule & Yield alone & \multicolumn{2}{c}{Yield and FCI} & Credit measure \\ \cmidrule(lr){2-2}\cmidrule(lr){3-4}\cmidrule(lr){5-5}",
    r" & Unemployment, 24 m & Unemployment, 24 m & Price level, 24 m & Response, 12 m (pp)\\ \midrule", *lines, r"\bottomrule\end{tabular}}",
    r"\begin{flushleft}\footnotesize\textit{Notes:} Per +1 pp on the two-year yield in the announcement window, 1996--2026. Excess bond premium: a third monthly variable, set like unemployment and inflation before markets within the month. Baa spread: Moody's Baa yield less the 10-year Treasury yield, in the daily block next to the yield and the FCI; its impact is its announcement-day change, because it has no intraday series. In the Baa row the yield-alone entry is the baseline's. Credit response: the excess bond premium, or the monthly average of the Baa spread, 12 months after the move, with its 90 percent interval. $^{**}$ and $^{*}$: the 95 and 90 percent intervals exclude zero.\end{flushleft}", r"\end{table}"]) + "\n")
for k, r in (("E", rE), ("A", rA), ("B", rB)):
    for v in ("u", "P"):
        mac(f"cr:{k}:{v}", num(r.loc[v].r24)); mac(f"cr:{k}:{v}:sig", "significant" if r.loc[v].lo24 * r.loc[v].hi24 > 0 else "not significant")
mac("cr:E0:u", num(rE0.loc["u"].r24)); mac("cr:B0:u", num(rB0.loc["u"].r24))
mac("cr:ebp12", num(pE.r[12])); mac("cr:baa12", num(pA.r[12])); mac("cr:baaimp", num(baa_imp))
mac("cr:r2lev", f"{100 * r2l:.0f}"); mac("cr:r2d", f"{100 * r2d:.0f}"); mac("cr:r2eq", f"{100 * r2eq:.0f}")
chk("credit: unemployment rises and the price level falls at 24 m with each credit measure added", all(r.loc["u"].r24 > 0 and r.loc["P"].r24 < 0 for r in (rE, rA)))
chk("credit: the price level at 24 m is significant at 10% with each credit measure", all(r.loc["P"].lo24 * r.loc["P"].hi24 > 0 for r in (rE, rA)))
chk("credit: each credit measure leaves the unemployment response at 24 m within 0.2 pp of the baseline", all(abs(r.loc["u"].r24 - rB.loc["u"].r24) < 0.2 for r in (rE, rA)))
chk("credit: the excess bond premium's response at 12 m has a 90% interval that includes zero", pE.lo[12] < 0 < pE.hi[12])

# ---------------------------------------------------------------- 3. information effects: weights from the Jarocinski-Karadi subset
WJ = pd.read_csv(OUT / "market_weights_jk.csv", index_col=0); WB = pd.read_csv(OUT / "market_weights.csv", index_col=0)
sh = lambda Wd: (Wd.weight * Wd.response) / (Wd.weight * Wd.response).sum()
cJ, cJJ, cS = dict(form="rstar", fci="jkw", **base), dict(form="rstar", fci="jkw", shock="jk", **base), dict(form="rstar", fci="rstar", shock="jk", **base)
rJ, rJJ, rS = res(cJ), res(cJJ), res(cS)
from lib import model as M
bJ = M.impact("jkw", idx0)[1]; bB = M.impact("rstar", idx0)[1]
IJ = pd.read_csv(OUT / "indexes_rstar_jkw.csv", index_col=0).market; IB = pd.read_csv(OUT / "indexes_rstar.csv", index_col=0).market
corr = float(np.corrcoef(IJ.loc["1996-01":], IB.loc["1996-01":])[0, 1])
lines = [f"{lab} & {Wd.weight['y10']:.3f} & {Wd.weight['equities']:.3f} & {Wd.weight['dollar']:.3f} & " + " & ".join(f"{x:.2f}" for x in sh(Wd)) + r"\\" for lab, Wd in (("All announcements (baseline)", WB), (f"Jarocinski--Karadi subset ({int(WJ.events.iloc[0])})", WJ))]
(REPORT / "tab_jk.tex").write_text("\n".join([r"\begin{table}[tp]\centering\small", r"\caption{FCI Weights Estimated without Information Shocks}\label{tab:jk}", FIT,
    r"\begin{tabular}{lcccccc}\toprule & \multicolumn{3}{c}{Weight} & \multicolumn{3}{c}{Share of a policy move}\\ \cmidrule(lr){2-4}\cmidrule(lr){5-7}",
    r"Announcements & 10-year yield & Equities & Dollar & 10-year yield & Equities & Dollar\\ \midrule", *lines, r"\bottomrule\end{tabular}}",
    r"\begin{flushleft}\footnotesize\textit{Notes:} Weights from the GLS regression of the window moves on policy news (companion paper), on all 253 announcements or only on those in which the two-year yield and the S\&P 500 move in opposite directions in the window \citep{jarocinski2020}. Share of a policy move: weight times the window response to policy news, as a share of the total. The weights apply to the 10-year yield (pp), 100 times the log of CAPE and 100 times the log of the real dollar.\end{flushleft}", r"\end{table}"]) + "\n")
mac("jk:n", int(WJ.events.iloc[0])); mac("jk:bF", f"{bJ:.2f}"); mac("jk:corr", f"{corr:.2f}")
for k, Wd in (("w", WJ), ("wb", WB)):
    for a in ("y10", "equities", "dollar"): mac(f"jk:{k}:{a}", f"{Wd.weight[a]:.2f}"); mac(f"jk:{k}:sh:{a}", f"{sh(Wd)[a]:.2f}")
for k, r in (("J", rJ), ("JJ", rJJ), ("S", rS)):
    for v in ("u", "P"): mac(f"jk:{k}:{v}", num(r.loc[v].r24)); mac(f"jk:{k}:{v}:sig", "significant" if r.loc[v].lo24 * r.loc[v].hi24 > 0 else "not significant")
chk("JK weights: unemployment rises and the price level falls at 24 m, with the full and the restricted surprise", all(r.loc["u"].r24 > 0 and r.loc["P"].r24 < 0 for r in (rJ, rJJ)))
chk("JK weights: price level at 24 m significant at 10% in both", all(r.loc["P"].lo24 * r.loc["P"].hi24 > 0 for r in (rJ, rJJ)))
chk("JK weights: the index is highly correlated with the baseline index (above 0.9 from 1996)", corr > 0.9)

# ---------------------------------------------------------------- 3b. the r*-gap index as a gap to a neutral level that moves with r* (Section 2.2), and the window responses in words
epbar = float((100 / D0.cape).loc[noteA.START:noteA.END].mean()); kap = WB.weight["y10"] - WB.weight["equities"] * 100 / epbar
mac("kap", f"{kap:.1f}"); mac("epbar", f"{epbar:.1f}")
for a in ("y10", "equities", "dollar"): mac(f"psi:{a}", f"{abs(WB.response[a]):.2f}" if a == "y10" else f"{abs(WB.response[a]):.1f}")
chk("the neutral level kappa r* rises with r* (kappa > 0)", kap > 0)

# ---------------------------------------------------------------- 4. figure: an ordinary day and an announcement window
z = np.load(OUT / "draws" / f"{CS.case_id(cB)}_L12.npz"); o0, od = float(z["ord0"]), z["ordd"]
rng = np.random.default_rng(7); wb = np.array([DD.window_impact(rng.choice(idx0, len(idx0)))[1] for _ in range(1000)])
fig, ax = plt.subplots(figsize=(6.2, 3.3)); x = np.arange(2); wdt = 0.36
ax.bar(x - wdt / 2, [1.0, 1.0], wdt, color=GREY, label="Two-year yield")
ax.bar(x + wdt / 2, [o0, bB], wdt, color=[ORANGE, BLUE], label="Financial conditions index")
ax.errorbar(x + wdt / 2, [o0, bB], yerr=[[o0 - np.percentile(od, 5), bB - np.percentile(wb, 5)], [np.percentile(od, 95) - o0, np.percentile(wb, 95) - bB]], fmt="none", ecolor=INK, capsize=4, lw=1)
for xi, val in zip(x + wdt / 2, [o0, bB]): ax.text(xi, val + 0.12, f"{val:.2f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(["An ordinary day", "An announcement window"]); ax.set_ylabel("Units (two-year-yield equivalents)"); ax.set_ylim(0, 1.45)
ax.axhline(0, color=GREY, lw=0.8); ax.legend(frameon=False, fontsize=8, loc="upper left"); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(REPORT / "fig_ordinary.pdf"); plt.close(fig)
mac("ord:lo", f"{np.percentile(od, 5):.2f}"); mac("ord:hi", f"{np.percentile(od, 95):.2f}"); mac("win:lo", f"{np.percentile(wb, 5):.2f}"); mac("win:hi", f"{np.percentile(wb, 95):.2f}")
mac("ord:ratio", f"{bB / o0:.1f}")
chk("ordinary day: the 90% intervals of the ordinary-day and window loadings do not overlap", np.percentile(od, 95) < np.percentile(wb, 5))

(REPORT / "numbers_rev.tex").write_text("\n".join(ML) + "\n")
from lib import latex_style as LST
LST.restyle_dir(REPORT)
if BAD: raise SystemExit("claims that no longer hold:\n  " + "\n  ".join(BAD))
print("07c: exhibits and numbers_rev.tex written; all claims hold")
