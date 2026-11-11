"""Step 7. Everything the paper reads from report/: tables (tab_*.tex, complete floats), figures (fig_*.pdf) and numbers.tex (one macro \\bl{key} for every number quoted in the text).
The qualitative statements of the text are asserted here (check_claims): the script stops with an error when one stops being true."""
import re
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from lib import data, compare as K
from lib.config import RES, REP, REPS
from lib.latex_style import title_case
from lib.report import COLORS, axes, figure, load_scalars

SC = load_scalars()
M = {}                                  # macro name -> LaTeX text
BAD = []                                # failed claims

# ------------------------------------------------------------------ formatting helpers
def f(x, d=2, sign=False):
    """Number as LaTeX text with a proper minus sign."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    s = f"{abs(x):.{d}f}"
    if round(x, d) < 0:
        return "$-$" + s
    return ("+" + s) if sign and round(x, d) > 0 else s

def mac(name, x, d=2, sign=False):
    M[name] = f(x, d, sign) if not isinstance(x, str) else x
    M["abs:" + name] = f(abs(x), d) if not isinstance(x, str) else x

def chk(cond, text):
    if not cond:
        BAD.append(text)

def table(name, caption, label, header, rows, notes, align=None, small=True, size=None):
    """Complete float: caption in Title Case, tabular shrunk to the text width if wider, notes under the table."""
    ncol = len(header)
    align = align or "l" + "r" * (ncol - 1)
    L = [r"\begin{tabular}{" + align + "}", r"\toprule", " & ".join(header) + r" \\", r"\midrule"]
    for r in rows:
        L.append(r if isinstance(r, str) else " & ".join(r) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    body = "\n".join(L)
    body = "\\resizebox{\\ifdim\\width>\\textwidth\\textwidth\\else\\width\\fi}{!}{%\n" + body + "}"
    txt = ("\\begin{table}[tp]\\centering" + ("\\small" if small else "") + "\n\\caption{" + title_case(caption) + "}\\label{" + label + "}\n" + body +
           "\n\\begin{flushleft}\\footnotesize\\textit{Notes:} " + notes + "\\end{flushleft}\n\\end{table}\n")
    (REP / f"tab_{name}.tex").write_text(txt)

def midrule(label=None):
    return r"\midrule" if label is None else r"\midrule" + "\n" + r"\multicolumn{%d}{l}{\textit{" + label + "}} \\\\"

STEP = {"nominal": "Nominal", "real": "Real", "rstar": "Relative to $r^*$"}
IDX = {c: data.read(f"indexes_{c}.csv") for c in ("nominal", "real", "rstar", "rstar_kiley")}
FL = {c: data.read(f"flow_{c}_p12.csv") for c in IDX}
V = pd.read_csv(RES / "var_specs.csv").set_index("key")
CMP = pd.read_csv(RES / "compare.csv", index_col=0)
BT = pd.read_csv(RES / "index_boot.csv")
WB = pd.read_csv(RES / "weights_boot.csv")
W = pd.read_csv(RES / "market_weights.csv", index_col=0)
FW = pd.read_csv(RES / "frbus_weights.csv", index_col=0)
WV = pd.read_csv(RES / "weights_variants.csv").set_index("variant")
ACT = pd.read_csv(RES / "activity.csv")
EP = pd.read_csv(RES / "episodes.csv")
RB = pd.read_csv(RES / "robust_rows.csv")
LG = pd.read_csv(RES / "latest_groups.csv").set_index("index")
D = data.load()
pct = lambda s, q: float(np.percentile(s, q))

# ------------------------------------------------------------------ macros from scalars and results
for k, v in SC.items():
    key = k.replace("_", ":")
    if isinstance(v, str):
        M[key] = v
    else:
        M[key] = f(v, 3 if abs(v) < 0.1 and v != 0 else 2); M["abs:" + key] = f(abs(v), 3 if abs(v) < 0.1 and v != 0 else 2)
M["n:events"] = f"{int(SC['n_events'])}"
for key, r in V.iterrows():
    k = key.replace("_", ":")
    for c in ("granger_F", "phi6", "phi12", "phi24", "phi12_lo90", "phi12_hi90", "phi24_lo90", "phi24_hi90", "own12", "own24", "corr_fi_fcig", "corr_fi_fcig_lo90", "corr_fi_fcig_hi90"):
        mac(f"var:{k}:{c}", r[c])
    for c in ("sig_from", "sig_to", "n_sig", "lags"):
        M[f"var:{k}:{c}"] = f"{int(r[c])}" if r[c] == r[c] else "none"
    M[f"var:{k}:granger_p"] = "$<$0.0001" if r.granger_p < 1e-4 else f(r.granger_p, 4)
for lab, sub in (("ten", "w_ten"), ("eq", "w_eq"), ("usd", "w_usd")):
    mac(f"wb:{lab}:lo", pct(WB[sub], 5)); mac(f"wb:{lab}:hi", pct(WB[sub], 95)); mac(f"wb:{lab}:sd", WB[sub].std())
for st in ("nominal", "real", "rstar"):
    for c in ("corr_gs", "corr_frbus", "corr_gs_chg", "corr_frbus_chg", "range_long", "range_ninety", "latest", "latest_gap_gs", "latest_gap_frbus", "corr_base"):
        s = BT[f"{st}_{c}"]
        mac(f"bt:{st}:{c}:lo", pct(s, 5)); mac(f"bt:{st}:{c}:hi", pct(s, 95)); mac(f"bt:{st}:{c}:sd", s.std())
mac("frw:eq:pct", float((WB.w_eq.abs() < abs(FW.loc["equities", "frbus_weight"])).mean() * 100), 0)
mac("frw:usd:pct", float((WB.w_usd > FW.loc["dollar", "frbus_weight"]).mean() * 100), 0)
mac("frw:ten:pct", float((WB.w_ten < FW.loc["y10", "frbus_weight"]).mean() * 100), 0)
for k, r in WV.iterrows():
    for c in WV.columns:
        mac(f"wv:{k}:{c}", float(r[c]), 3 if c.startswith("w_") else 2)
for i, r in RB.iterrows():
    for c in RB.columns[1:]:
        mac(f"rb:{i}:{c}", float(r[c]))
for _, r in ACT.iterrows():
    tag = f"act:{r.case}:" + {"Market index forward impetus": "fi", "FCI-G, 1-year lookback": "fcig1", "FCI-G, 3-year lookback": "fcig3", "FRB/US growth impetus": "gi", "Market index (level)": "level",
                              "Market index current pressure": "cp", "GS (level)": "gs", "FRB/US index (level)": "frbus"}[r["index"]]
    for c in ("coef", "se", "gain", "oos_ratio", "r_1995_2007", "r_2008_2019", "r_2021_2025", "dm_t"):
        mac(f"{tag}:{c}", float(r[c]))
for _, r in LG.reset_index().iterrows():
    for c in ("rates", "equities", "dollar", "other", "total"):
        mac(f"lg:{r['index']}:{c}", float(r[c]))
mac("lg:gap:eq", LG.loc["market", "equities"] - LG.loc["frbus_hp", "equities"]); mac("lg:gap:usd", LG.loc["market", "dollar"] - LG.loc["frbus_hp", "dollar"])
mac("lg:gap:total", LG.loc["market", "total"] - LG.loc["frbus_hp", "total"]); mac("lg:gap:rates", LG.loc["market", "rates"] - LG.loc["frbus_hp", "rates"])
mac("okun:phi12", 2 * V.loc["rstar_p12", "phi12"], 1)

# ------------------------------------------------------------------ tables
# Table: weights
rows = []
names = {"y10": "10-year Treasury yield (pp)", "equities": "Equity valuation, 100 ln CAPE (percent)", "dollar": "Real broad dollar, 100 ln (percent)"}
for k, lab in (("y10", "ten"), ("equities", "eq"), ("dollar", "usd")):
    r = W.loc[k]
    rows.append([names[k], f"{f(r.response)} ({r.se:.2f})", f(r.weight, 3), f"[{f(pct(WB['w_' + lab], 5), 3)}, {f(pct(WB['w_' + lab], 95), 3)}]", f"{r.weight * r.response:.2f}"])
table("weights", "Market Index: Responses to Policy News and Weights", "tab:weights", ["", "Response", "Weight", "90\\% interval", "Share of policy move"], rows,
      f"Announcement windows, {int(SC['n_events'])} announcements, {SC['event_first']} to {SC['event_last']}. Response: change in the window per unit of policy news, which moves the two-year yield by 1 percentage point (heteroskedasticity-robust standard errors in parentheses). Weight: one-factor generalized least squares, normalized so that the weights applied to the responses sum to 1. Interval: 5th and 95th percentiles of weights re-estimated on {len(WB)} bootstrap samples of the announcements. Share: weight times response.")

# Table: FRB/US and market weights
rows = []
for k, lab, nm in (("y10", "ten", "10-year yield (pp)"), ("equities", "eq", "Equity valuation (percent)"), ("dollar", "usd", "Real dollar (percent)")):
    r = FW.loc[k]
    rows.append([nm, f(r.frbus_weight, 3), f(r.market_weight, 3), f"[{f(pct(WB['w_' + lab], 5), 3)}, {f(pct(WB['w_' + lab], 95), 3)}]", f(r.frbus_response, 2), f(r.market_response, 2)])
table("frbus", "FRB/US and Market Weights on the Three Common Variables", "tab:frbus", ["", "FRB/US weight", "Market weight", "90\\% interval", "FRB/US response", "Market response"], rows,
      "FRB/US weight: effect on GDP after four quarters of a persistent unit shift in the variable, divided by the effect of a persistent 1 percentage point rise in the federal funds rate (" + f(SC["frbus_yardstick"], 4) + " percent of GDP); funds-rate points per unit. Market weight: two-year-yield points per unit (Table~\\ref{tab:weights}); the interval is its bootstrap interval. FRB/US response: change in the variable four quarters after a persistent 1 percentage point funds-rate rise (VAR expectations). Market response: change in the announcement window per unit of policy news.")

# Table: VAR by step
rows = []
for key, lab in (("nominal_p12", "Nominal"), ("real_p12", "Real"), ("rstar_p12", "Relative to $r^*$ (baseline)"), ("rstar_kiley_p12", "Relative to $r^*$ (Kiley)"), ("rstar_p4", "Relative to $r^*$, 4 lags")):
    r = V.loc[key]
    p = "$<$0.0001" if r.granger_p < 1e-4 else f"{r.granger_p:.4f}"
    rows.append([lab, f"{int(r.lags)}", f"{r.granger_F:.2f}", p, f(r.phi6), f"{f(r.phi12)} [{f(r.phi12_lo90)}, {f(r.phi12_hi90)}]", f(r.phi24), f"{int(r.sig_from)}--{int(r.sig_to)}"])
table("var", "Unemployment Response to a Tightening of the Market Index", "tab:var", ["", "Lags", "Granger $F$", "$p$", "$\\Phi(6)$", "$\\Phi(12)$ [90\\%]", "$\\Phi(24)$", "Months significant"], rows,
      "Monthly VAR in the unemployment gap and the market index, January 1973 to September 2026, 2020 months with dummies; unemployment first. $\\Phi(h)$: response of the unemployment gap (percentage points) $h$ months after an innovation that raises the index by one unit. Granger: test that the lags of the index do not enter the unemployment equation. Interval: 5th and 95th percentiles of " + f"{REPS}" + " block-bootstrap draws (12-month blocks of residuals). Months significant: first and last month with the 90 percent band above zero.")

# Table: matched comparison by step
def crow(lab, key, d=2, sign=False):
    return [lab] + [f(CMP.loc[key, c], d, sign) for c in ("nominal", "real", "rstar")]
rows = [r"\multicolumn{4}{l}{\textit{Correlation of levels}} \\",
        crow("Market and GS", "mkt_gs"), crow("Market and FRB/US", "mkt_frbus"), crow("Market and FRB/US with house prices", "mkt_frbus_hp"), crow("Market and ANFCI (from 1990)", "mkt_anfci"),
        r"\multicolumn{4}{l}{\textit{Correlation of 12-month changes}} \\", crow("Market and GS", "mkt_gs_chg"), crow("Market and FRB/US", "mkt_frbus_chg"),
        r"\multicolumn{4}{l}{\textit{Correlation of flows}} \\", crow("Forward impetus and FCI-G", "fi_fcig"), crow("Forward impetus and FRB/US growth impetus", "fi_frbus_gi"), crow("FCI-G and FRB/US growth impetus", "fcig_frbus_gi"),
        r"\multicolumn{4}{l}{\textit{Average range of the four level indexes (pp)}} \\", crow("1974--2026", "range_long"), crow("1990--2026, zero at the 1990--2026 mean", "range_ninety"),
        r"\multicolumn{4}{l}{\textit{Latest reading, September 2026}} \\", crow("Market index", "latest_market", sign=True), crow("GS", "latest_gs", sign=True), crow("FRB/US index", "latest_frbus", sign=True),
        crow("Forward impetus", "latest_fi", sign=True), crow("FCI-G (1-year)", "latest_fcig", sign=True)]
table("compare", "The Market Index and the Other Indexes at Each Step, 1974--2026", "tab:compare", ["", "Nominal", "Real", "Relative to $r^*$"], rows,
      "Monthly. Level indexes (market, GS, FRB/US, FRB/US with house prices) in two-year-yield points (market, GS) or funds-rate points (FRB/US), tighter above zero, relative to the 1973--2026 mean of each variable. FCI-G and the growth impetus of FRB/US in percentage points of GDP growth; forward impetus in index units. Range: highest minus lowest of the four level indexes in a month, averaged. ANFCI converted to two-year-yield points by its response to policy news. Real and $r^*$ versions of GS and FCI-G are my replications with real rates or gaps to $r^*$.")

# Table: episodes
rows = []
for kind in ("Widest", "Widest since 1990", "Closest"):
    sub = EP[EP.kind == kind].head(3 if kind != "Widest" else 3)
    rows.append(r"\multicolumn{10}{l}{\textit{" + kind + r"}} \\")
    for _, r in sub.iterrows():
        rows.append([f"{r.start} to {r.end}", f(r["range"]), f(r.market), f(r.gs), f(r.frbus), f(r.frbus_hp), f(r.gap_equities, 2, True), f(r.gap_dollar, 2, True), f(r.gap_rates, 2, True), f(r.gap_house, 2, True)])
table("episodes", "Widest and Closest Six-Month Windows, Relative to $r^*$", "tab:episodes", ["Window", "Range", "Market", "GS", "FRB/US", "FRB/US+HP", "Equities", "Dollar", "Rates", "House"], rows,
      "Non-overlapping six-month windows ranked by the average range of the four level indexes (averages over the window; relative to the 1973--2026 mean). Gap: market index minus FRB/US index with house prices, by group of variables. The first group ranks all months, the second months from 1990.")

# Table: sampling uncertainty
rows = []
for st in ("nominal", "real", "rstar"):
    cell = lambda key, bkey, d=2: f"{f(CMP.loc[key, st], d)} [{f(pct(BT[f'{st}_{bkey}'], 5), d)}, {f(pct(BT[f'{st}_{bkey}'], 95), d)}]"
    rows.append([STEP[st], cell("mkt_gs", "corr_gs"), cell("mkt_frbus", "corr_frbus"), cell("range_ninety", "range_ninety"), cell("latest_market", "latest"), f(CMP.loc["latest_gs", st], 2, True), f(CMP.loc["latest_frbus", st], 2, True)])
table("boot", "How the Sampling Error of the Weights Affects the Market Index", "tab:boot", ["", "Corr. with GS", "Corr. with FRB/US", "Range, 1990--2026", "Latest, market", "Latest, GS", "Latest, FRB/US"], rows,
      f"Point estimate and 5th to 95th percentile over {len(BT)} bootstrap samples of the announcements, each re-estimating the policy-news factor and the weights. Correlations of monthly levels, 1974--2026. Range: average range of the four level indexes since 1990, relative to the 1990--2026 mean. GS and FRB/US are held fixed (their weights are not estimated here).")

# Table: activity (r*)
def arow(lab, tag, case="rstar"):
    g = lambda c: float(ACT[(ACT.case == case) & (ACT["index"] == tag)][c].iloc[0])
    return [lab, f"{g('coef'):.2f} ({g('se'):.2f})", f(g("gain")), f(g("oos_ratio")), f(g("r_1995_2007")), f(g("r_2008_2019")), f(g("r_2021_2025")), f(g("dm_t"))]
rows = [arow("Market index forward impetus", "Market index forward impetus"), arow("FCI-G, 1-year lookback", "FCI-G, 1-year lookback"), arow("FRB/US growth impetus", "FRB/US growth impetus"),
        arow("Market index (level)", "Market index (level)"), arow("GS (level)", "GS (level)"), arow("FRB/US index (level)", "FRB/US index (level)")]
table("activity", "Unemployment Gap 12 Months Ahead on the Current Index Reading, Relative to $r^*$", "tab:activity", ["", "Coefficient", "Gain in adj.\\ $R^2$", "RMSE ratio", "1995--2007", "2008--19", "2021--25", "DM $t$"], rows,
      "Local projection $u_{t+12}=a+b\\,u_t+c\\,x_t$, 1976--2026; coefficient $c$ (HAC standard error); gain in adjusted $R^2$ over $u_t$ alone. Out of sample: recursive estimates, forecast origins 1995--2025; ratio of root mean squared errors to the projection on $u_t$ alone (below 1: the index helps), also for three subperiods; DM: Diebold--Mariano $t$ (negative: index better). Months touching 2020 to March 2021 excluded.")

# Table: robustness summary
rows = []
for i, r in RB.iterrows():
    lab = r.variation
    rows.append([lab, f(r.mkt_gs), f(r.mkt_frbus), f(r.range_ninety), f(r.latest_market, 2, True), f"{f(r.phi12)} [{f(r.phi12_lo)}, {f(r.phi12_hi)}]", f"{f(r.fi_fcig)} [{f(r.fi_fcig_lo)}, {f(r.fi_fcig_hi)}]"])
table("robust", "Variations of the Construction", "tab:robust", ["", "Market--GS", "Market--FRB/US", "Range", "Latest", "$\\Phi(12)$ [90\\%]", "Flow--FCI-G [5--95\\%]"], rows,
      "Baseline: relative to $r^*$ (Laubach--Williams), 12 lags, VAR from 1973, announcement-window weights from the Nakamura--Steinsson factor. Market--GS and Market--FRB/US: correlations of monthly levels, 1974--2026. Range: average range of the four level indexes, 1990--2026. Latest: market index, September 2026. $\\Phi(12)$: unemployment response after 12 months with 90 percent block-bootstrap interval. Flow--FCI-G: correlation of the forward impetus with FCI-G (1-year), with the 5th to 95th percentile over bootstrap draws of the response. In the three weights variations GS and FRB/US are the baseline ones.")
print("tables written:", sorted(p.name for p in REP.glob("tab_*.tex")))

# ------------------------------------------------------------------ figures
LEVEL = ["market", "gs", "frbus"]
LAB = {"market": "Market index", "gs": "GS replication", "frbus": "FRB/US index"}
# Figure 1: the level indexes at each step
fig, ax = plt.subplots(3, 1, figsize=(7.5, 8.2), sharex=True)
for a, c, title in zip(ax, ("nominal", "real", "rstar"), ("Nominal", "Real rates", "Relative to $r^*$")):
    I = IDX[c]; t = I.index.to_timestamp()
    for k, lw in (("gs", 1.0), ("frbus", 1.0), ("market", 1.6)):
        a.plot(t, I[k], color=COLORS[k], lw=lw, label=LAB[k])
    a.set_title(title, loc="left"); axes(a, "pp, tighter above zero", legend=(c == "nominal"))
figure("fig_levels", fig)

# Figure: expected inflation and r*
fig, ax = plt.subplots(1, 2, figsize=(7.5, 3.2))
t = D.loc["1973-01":].index.to_timestamp(); X = D.loc["1973-01":]
ax[0].plot(t, X.einf_1y, color=COLORS["market"], lw=1.2, label="1-year"); ax[0].plot(t, X.einf_10y, color=COLORS["frbus"], lw=1.2, label="10-year")
ax[0].axvspan(t[(X.index >= "1982-01").argmax()], t[(X.index >= "1982-12").argmax()], color="#dddddd", lw=0)
ax[0].set_title("Expected inflation (percent)", loc="left"); axes(ax[0])
ax[1].plot(t, X["rstar LW"], color="black", lw=1.2, label="Laubach--Williams (baseline)"); ax[1].plot(t, X["rstar Kiley"], color=COLORS["grey"], lw=1.2, label="Kiley (check)")
ax[1].set_title("$r^*$, one-sided estimates (percent)", loc="left"); axes(ax[1])
figure("fig_inflation_rstar", fig)

# Figure: the market index at each step
fig, ax = plt.subplots(figsize=(7.5, 3.2))
for c, col, lab, lw in (("nominal", COLORS["grey"], "Nominal", 1.1), ("real", COLORS["frbus"], "Real", 1.1), ("rstar", COLORS["market"], "Relative to $r^*$", 1.6)):
    ax.plot(IDX[c].index.to_timestamp(), IDX[c].market, color=col, lw=lw, label=lab)
ax.axvspan(pd.Timestamp("2009-01-01"), pd.Timestamp("2016-12-31"), color="#eeeeee", lw=0)
axes(ax, "two-year-yield points, tighter above zero")
figure("fig_market_steps", fig)

# Figure: unemployment response
fig, ax = plt.subplots(figsize=(7.0, 3.4))
P = {k: pd.read_csv(RES / f"var_paths_{k}.csv") for k in ("rstar_p12", "rstar_p4", "nominal_p12")}
b = P["rstar_p12"]
ax.fill_between(b.h, b.lo90, b.hi90, color=COLORS["market"], alpha=0.14, lw=0, label="90% band"); ax.fill_between(b.h, b.lo68, b.hi68, color=COLORS["market"], alpha=0.28, lw=0, label="68% band")
ax.plot(b.h, b.phi, color=COLORS["market"], lw=1.8, label="Relative to $r^*$, 12 lags (baseline)")
ax.plot(P["rstar_p4"].h, P["rstar_p4"].phi, color=COLORS["market"], lw=1.1, ls="--", label="Relative to $r^*$, 4 lags")
ax.plot(P["nominal_p12"].h, P["nominal_p12"].phi, color=COLORS["grey"], lw=1.1, label="Nominal, 12 lags")
ax.set_xlabel("months after a one-unit tightening of the market index")
axes(ax, "unemployment gap, percentage points")
figure("fig_var", fig)

# Figure: level and flow
I = IDX["rstar"]; F = FL["rstar"]; t = I.index.to_timestamp()
fig, ax = plt.subplots(2, 1, figsize=(7.5, 5.6), sharex=True)
ax[0].plot(t, I.market, color=COLORS["market"], lw=1.4, label="Market index (level), two-year-yield points")
ax[0].set_title("Level: where financial conditions stand, relative to $r^*$", loc="left"); axes(ax[0])
ax[1].plot(t, F.forward_impetus, color=COLORS["market"], lw=1.4, label="Market index forward impetus (index units)")
ax[1].plot(t, I.fcig_1yr, color=COLORS["fcig"], lw=1.0, alpha=0.8, label="FCI-G, 1-year lookback, relative to $r^*$ (pp of GDP growth)")
ax[1].set_title("Flow: what the past year's changes imply for the next year", loc="left"); axes(ax[1])
figure("fig_level_flow", fig)

# Figure: today's reading with the sampling interval of the weights
fig, ax = plt.subplots(figsize=(7.0, 3.2))
xs = {"nominal": 0, "real": 1, "rstar": 2}
for st, x in xs.items():
    lo, hi = pct(BT[f"{st}_latest"], 5), pct(BT[f"{st}_latest"], 95)
    ax.plot([x - 0.2, x - 0.2], [lo, hi], color=COLORS["market"], lw=2.2, alpha=0.5)
    ax.plot(x - 0.2, CMP.loc["latest_market", st], "o", color=COLORS["market"], label="Market index (90% interval, sampling error of weights)" if x == 0 else None)
    ax.plot(x, CMP.loc["latest_gs", st], "s", color=COLORS["gs"], label="GS replication" if x == 0 else None)
    ax.plot(x + 0.2, CMP.loc["latest_frbus", st], "^", color=COLORS["frbus"], label="FRB/US index" if x == 0 else None)
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["Nominal", "Real", "Relative to $r^*$"]); ax.set_xlim(-0.6, 2.6)
axes(ax, "September 2026, points, tighter above zero")
figure("fig_today", fig)

# Figure: FCI-G scale
S = pd.read_csv(RES / "fcig_scale.csv", header=[0, 1], index_col=0)
fig, ax = plt.subplots(figsize=(7.0, 3.4))
for nm, col, lab in (("rstar", COLORS["market"], "FCI-G relative to $r^*$, 1974--2026"), ("nominal", COLORS["grey"], "FCI-G nominal replication, 1974--2026"), ("published", COLORS["fcig"], "Published FCI-G, 1990--2026")):
    b_, s_ = S[(nm, "b")], S[(nm, "se")]
    ax.plot(b_.index, b_, color=col, lw=1.5, label=lab); ax.fill_between(b_.index, b_ - 1.645 * s_, b_ + 1.645 * s_, color=col, alpha=0.12, lw=0)
ax.plot([0, 12], [0, 0.5], color="#999999", ls="--", lw=1, label="FCI-G's own claim (0.5 by month 12)")
ax.set_xlabel("months ahead"); axes(ax, "unemployment gap, pp, per +1 reading")
figure("fig_fcig_scale", fig)

# Figure (appendix): current pressure
fig, ax = plt.subplots(figsize=(7.5, 3.2))
ax.plot(t, I.market, color=COLORS["market"], lw=1.3, label="Market index (eventual pressure)")
ax.plot(t, F.current_pressure, color=COLORS["frbus"], lw=1.1, label="Current pressure")
ax.plot(t, F.forward_impetus, color=COLORS["fcig"], lw=1.0, label="Forward impetus")
axes(ax, "two-year-yield points")
figure("fig_current_pressure", fig)

# ------------------------------------------------------------------ appendix tables
# weights variants
rows = []
lab = {"baseline": "Baseline: Nakamura--Steinsson factor", "two_year": "Policy news is the 2-year yield change", "to_2019": "Announcements through 2019", "no_lower_bound": "No announcements December 2008--November 2015"}
for k, r in WV.iterrows():
    rows.append([lab[k], f"{int(r.n)}", f(r.w_ten, 3), f(r.w_eq, 3), f(r.w_usd, 3), f(r.psi_ten, 2), f(r.psi_eq, 2), f(r.psi_usd, 2)])
table("wvar", "Weights under Other Policy-News Series and Event Samples", "tab:wvar", ["", "Events", "$w$ 10-year", "$w$ equities", "$w$ dollar", "$\\psi$ 10-year", "$\\psi$ equities", "$\\psi$ dollar"], rows,
      "Weights $w$ and responses $\\psi$ as in Table~\\ref{tab:weights}, re-estimated on each sample or with the window change of the two-year yield as the policy-news measure. In each case the weights applied to the responses sum to 1.")
# all VAR cases
rows = []
for key, r in V.iterrows():
    nm = {"nominal": "Nominal", "real": "Real", "rstar": "$r^*$", "rstar_kiley": "$r^*$ (Kiley)"}[r.step]
    suf = re.sub(r"^.*_p\d+_?", "", key)
    extra = {"": "", "from1990": ", from 1990", "to2019": ", to 2019", "w_two_year": ", weights: 2-year news", "w_to_2019": ", weights: to 2019", "w_no_lower_bound": ", weights: no lower bound"}[suf]
    p = "$<$0.0001" if r.granger_p < 1e-4 else f"{r.granger_p:.4f}"
    rows.append([nm + extra, f"{int(r.lags)}", f"{r.start[:4]}--{r.end[:4]}", f"{r.granger_F:.2f}", p, f(r.phi6), f"{f(r.phi12)} [{f(r.phi12_lo90)}, {f(r.phi12_hi90)}]", f"{f(r.phi24)} [{f(r.phi24_lo90)}, {f(r.phi24_hi90)}]", f"{int(r.sig_from)}--{int(r.sig_to)}", f(r.corr_fi_fcig)])
table("var_all", "The VAR in All Cases", "tab:varall", ["Case", "Lags", "Sample", "Granger $F$", "$p$", "$\\Phi(6)$", "$\\Phi(12)$ [90\\%]", "$\\Phi(24)$ [90\\%]", "Months", "Flow--FCI-G"], rows,
      "As Table~\\ref{tab:var}. Months: first and last month with the 90 percent band above zero. Flow--FCI-G: correlation of the forward impetus with the FCI-G of the same step, 1974--2026.", small=True)
# activity: real and nominal
for case, nm in (("real", "Real"), ("nominal", "Nominal")):
    rows = [arow(lab_, tag, case) for lab_, tag in (("Market index forward impetus", "Market index forward impetus"), ("FCI-G, 1-year lookback", "FCI-G, 1-year lookback"), ("FCI-G, 3-year lookback", "FCI-G, 3-year lookback"),
                                               ("FRB/US growth impetus", "FRB/US growth impetus"), ("Market index (level)", "Market index (level)"), ("Market index current pressure", "Market index current pressure"),
                                               ("GS (level)", "GS (level)"), ("FRB/US index (level)", "FRB/US index (level)"))]
    table(f"activity_{case}", f"Unemployment Gap 12 Months Ahead, {nm} Versions", f"tab:activity{case}", ["", "Coefficient", "Gain in adj.\\ $R^2$", "RMSE ratio", "1995--2007", "2008--19", "2021--25", "DM $t$"], rows,
          "As Table~\\ref{tab:activity}.")
# Kiley check
Ik, Ib = IDX["rstar_kiley"], IDX["rstar"]
rows = []
for c, lab_ in (("market", "Market index"), ("gs", "GS"), ("frbus", "FRB/US index"), ("fcig_1yr", "FCI-G, 1-year")):
    rows.append([lab_, f(K.corr(Ib[c], Ik[c])), f(K.corr(Ib[c], Ik[c], True))])
rows.append(["Market forward impetus", f(K.corr(FL["rstar"].forward_impetus, FL["rstar_kiley"].forward_impetus)), ""])
rows.append(["Forward impetus, 4 against 12 lags", f(K.corr(FL["rstar"].forward_impetus, data.read("flow_rstar_p4.csv").forward_impetus)), ""])
table("checks", "Checks: Kiley $r^*$ and 4 Lags, Correlations with the Baseline", "tab:checks", ["", "Levels", "12-month changes"], rows, "Correlations of monthly series, 1973--2026.")
mac("chk:kiley:mkt", K.corr(Ib.market, Ik.market)); mac("chk:p4:fi", K.corr(FL["rstar"].forward_impetus, data.read("flow_rstar_p4.csv").forward_impetus))
mac("chk:cp", K.corr(Ib.market, FL["rstar"].current_pressure))

# latest groups table (appendix)
rows = [[{"market": "Market index", "gs": "GS", "frbus_hp": "FRB/US with house prices"}[i], f(r.rates, 2, True), f(r.equities, 2, True), f(r.dollar, 2, True), f(r.other, 2, True), f(r.total, 2, True)] for i, r in LG.iterrows()]
table("latestgroups", "Contributions to the Readings for September 2026, Relative to $r^*$", "tab:latestgroups", ["", "Rates", "Equities", "Dollar", "Other", "Total"], rows,
      "Contribution of each group of variables to the index in September 2026 (weight times the variable relative to its 1973--2026 mean), in points; rates include policy rate, 10-year yield and spreads, other is house prices. Equity valuation is the earnings-yield gap to $r^*$.")

# ------------------------------------------------------------------ remaining macros
mac("boot:reps", float(len(BT)), 0); M["abs:boot:reps"] = M["boot:reps"]
M["frbus:yardstick"] = f(SC["frbus_yardstick"], 4)
M["usd:nom:1973"] = f(SC["usd_nom_1973"], 0); M["usd:nom:latest"] = f(SC["usd_nom_latest"], 0)
M["rstar:share:range:gt1:ninety"] = f(SC["rstar_share_range_gt1_ninety"] * 100, 0)
mac("rstar:lw:mean", float(D["rstar LW"].loc["1973-01":"2026-09"].mean()))
mac("act:rstar:best:dm", float(ACT[(ACT.case == "rstar") & ACT["index"].isin(["Market index forward impetus", "FCI-G, 1-year lookback", "FRB/US growth impetus", "FCI-G, 3-year lookback"])].dm_t.min()))
for k_ in ("mkt", "gs", "frbus"):
    mac(f"shift:{k_}:gfc", SC[f"rstar_{k_}_gfc"] - SC[f"nominal_{k_}_gfc"])
mac("rb:min:mkt:gs", RB.mkt_gs.min()); mac("rb:min:mkt:frbus", RB.mkt_frbus.min()); mac("rb:min:fi:fcig", RB.fi_fcig.min())

# ------------------------------------------------------------------ claims asserted in the text
c = lambda st, k: CMP.loc[k, st]
chk(c("rstar", "mkt_gs") >= 0.98 and c("real", "mkt_gs") >= 0.98 and c("nominal", "mkt_gs") <= 0.80, "market-GS: high in real and r* terms, low in nominal")
chk(all(c(s, "mkt_frbus") >= 0.90 for s in ("nominal", "real", "rstar")), "market-FRB/US at least 0.90 at every step")
chk(c("nominal", "range_long") > c("real", "range_long") > c("rstar", "range_long") and c("nominal", "range_ninety") > c("real", "range_ninety") > c("rstar", "range_ninety"), "range falls at each step")
chk(c("rstar", "range_long") > 0.9 and c("rstar", "range_ninety") > 0.8, "range stays near a point")
chk(all(c(s, "fi_fcig") >= 0.79 for s in ("nominal", "real", "rstar")), "flow-FCI-G at least 0.79 at every step")
chk(all(c(s, "fcig_level") < 0.4 for s in ("nominal", "real", "rstar")), "FCI-G level correlation with market index below 0.4")
chk(c("rstar", "fcig_frbus_gi") > c("rstar", "fi_fcig"), "FCI-G is closer to the FRB/US growth impetus than to the forward impetus")
chk(c("rstar", "mkt_anfci") < 0.3, "ANFCI correlation below 0.3")
chk(V.loc["rstar_p12", "granger_p"] < 1e-4 and V.loc["rstar_p12", "phi12_lo90"] > 0, "baseline VAR: Granger p < 1e-4 and yardstick interval above zero")
chk((V.phi12_lo90 > 0).all(), "yardstick interval above zero in every VAR case")
chk(V.loc["rstar_p12", "phi12"] > V.loc["rstar_p4", "phi12"], "12-lag yardstick above 4-lag")
chk(V.loc["rstar_p12_from1990", "sig_to"] < V.loc["rstar_p12", "sig_to"], "response from a 1990 sample fades earlier")
chk(V.loc["rstar_p4", "corr_fi_fcig"] < V.loc["rstar_p12", "corr_fi_fcig"], "4-lag flow correlates less with FCI-G")
chk(SC["rstar_mkt_gfc"] > 0 > SC["real_mkt_gfc"] and SC["rstar_mkt_gfc"] > 0 > SC["nominal_mkt_gfc"], "2009-16: tight relative to r*, easy in real and nominal terms")
chk(all(SC[f"rstar_{k_}_gfc"] > SC[f"nominal_{k_}_gfc"] for k_ in ("mkt", "gs", "frbus")) and all(SC[f"rstar_{k_}_gfc"] > 0 for k_ in ("mkt", "gs", "frbus")), "2009-16: all three indexes tighter at the r* step and above the 1990-2026 mean")
chk(SC["cape_7780"] < 0.5 * SC["cape_mean"], "CAPE in 1977-80 below half its mean")
chk(SC["step_nom_real_ninety"] > 0.95 and SC["step_real_rstar_ninety"] < 0.7, "nominal-real step changes little after 1990, r* step a lot")
chk(abs(SC["real_fcig_seventyfour"]) < 0.1 and SC["nominal_fcig_seventyfour"] > 0.4, "FCI-G mid-1974: tightening in nominal, not real")
chk(CMP.loc["latest_gs", "rstar"] < CMP.loc["latest_market", "rstar"] < CMP.loc["latest_frbus", "rstar"], "readings ordered GS < market < FRB/US at the r* step")
lo, hi = pct(BT["rstar_latest"], 5), pct(BT["rstar_latest"], 95)
chk(hi - lo > CMP.loc["latest_frbus", "rstar"] - CMP.loc["latest_gs", "rstar"], "90% interval of the market reading wider than the GS-FRB/US gap")
chk(lo < CMP.loc["latest_gs", "rstar"] < hi, "market interval contains the GS reading")
for lab, k in (("eq", "equities"), ("usd", "dollar"), ("ten", "y10")):
    wf = FW.loc[k, "frbus_weight"]
    chk(pct(WB["w_" + lab], 5) <= wf <= pct(WB["w_" + lab], 95), f"FRB/US {k} weight inside the bootstrap interval")
chk(FW.loc["equities", "frbus_weight"] / FW.loc["equities", "market_weight"] < 1 < FW.loc["dollar", "frbus_weight"] / FW.loc["dollar", "market_weight"], "FRB/US: less on equities, more on the dollar")
chk(pct(BT["rstar_corr_gs"], 5) > 0.85 and pct(BT["rstar_corr_frbus"], 5) > 0.85, "weights sampling: correlations stay above 0.85 (5th percentile)")
A = ACT[ACT.case == "rstar"].set_index("index")
flows = ["Market index forward impetus", "FCI-G, 1-year lookback", "FRB/US growth impetus"]
levels = ["Market index (level)", "GS (level)", "FRB/US index (level)"]
chk(all(A.loc[x, "gain"] > 0.08 for x in flows) and all(A.loc[x, "gain"] < 0.03 for x in levels), "flows add more than 0.08 to adjusted R2, levels less than 0.03")
chk(all(A.loc[x, "oos_ratio"] < 1 for x in flows) and all(A.loc[x, "dm_t"] > -1.645 for x in flows), "flows reduce RMSE out of sample, not significantly")
chk(all(A.loc[x, "r_2021_2025"] > 1 for x in flows) and all(A.loc[x, "r_1995_2007"] < 1 and A.loc[x, "r_2008_2019"] < 1 for x in flows), "gains before 2020, reversal 2021-25")
chk(V.loc["rstar_p12", "phi12_lo90"] < A.loc["Market index forward impetus", "coef"] < V.loc["rstar_p12", "phi12_hi90"], "forward impetus coefficient inside the yardstick interval")
chk(0.35 < SC["fcig_scale_rstar"] < 0.6 and SC["fcig_scale_published"] < 0.25, "FCI-G scale: near 0.5 for r* version 1974-2026, below 0.25 for the published series")
RA = ACT[ACT.case == "real"].set_index("index")
chk(all(A.loc[x, "gain"] >= RA.loc[x, "gain"] for x in flows), "r* flows have at least the adjusted R2 gain of real flows")
wide = EP[EP.kind == "Widest"].head(4); since = EP[EP.kind == "Widest since 1990"]; close = EP[EP.kind == "Closest"]
chk((wide.gap_equities > 1.4).all() and all(s.startswith(("1977", "1978", "1979", "1980")) for s in wide.start), "widest windows 1977-80, equity gap above 1.4")
chk(since.head(3).start.str[:4].astype(int).between(1998, 2000).all() and (since.head(3).gap_equities < -1.3).all() and (since.head(3).market < since.head(3).frbus).all(), "widest since 1990: 1998-2000, market looser, equity gap below -1.3")
chk((close.gap_equities.abs() < 0.5).all() and (close.gap_dollar.abs() < 0.5).all(), "closest windows: equity and dollar gaps below 0.5")
chk(LG.loc["market", "equities"] < LG.loc["frbus_hp", "equities"] < 0 and LG.loc["market", "dollar"] < LG.loc["frbus_hp", "dollar"], "today: equities lower the market index more, the dollar raises it less")
chk(RB.mkt_gs.min() >= 0.9 and RB.mkt_frbus.min() >= 0.9 and RB.fi_fcig.min() >= 0.7 and (RB.phi12_lo > 0).all(), "robustness rows: correlations and yardstick")
chk((RB.loc[1, ["latest_market", "latest_gs", "latest_frbus"]].values < RB.loc[0, ["latest_market", "latest_gs", "latest_frbus"]].values).all() and (RB.loc[0, ["latest_market", "latest_gs", "latest_frbus"]].values - RB.loc[1, ["latest_market", "latest_gs", "latest_frbus"]].values).max() < 0.5, "Kiley r*: all readings looser, by less than 0.5")
chk(SC["rstar_ki_post"] > SC["rstar_lw_post"], "Kiley r* higher than LW after 2008")
wvl = {"baseline": RB.loc[0, "latest_market"], "two_year": RB.loc[5, "latest_market"], "to_2019": RB.loc[6, "latest_market"], "no_lower_bound": RB.loc[7, "latest_market"]}
order = sorted(WV.index, key=lambda k: abs(WV.loc[k, "w_eq"]))
chk(all(wvl[order[i]] > wvl[order[i + 1]] for i in range(3)), "readings fall as the equity weight rises (four weight sets)")
chk(SC["rstar_lw_latest"] < D["rstar LW"].loc["1973-01":"2026-09"].mean(), "r* now below its 1973-2026 mean")
chk(SC["einf_1981"] > 8 and SC["einf_latest"] < 3 and SC["rstar_lw_pre"] > 2.5 > 1 > SC["rstar_lw_post"] - 0.2, "inflation expectations and r* movements quoted in Section 3.1")

# ------------------------------------------------------------------ write numbers.tex and check the paper's macros
def norm(k):
    return k.replace("_", ":")
L = ["% generated by replication/07_report.py: do not edit", r"\newcommand{\bl}[1]{\csname bl:#1\endcsname}"]
for k, v in sorted(M.items()):
    L.append(r"\expandafter\gdef\csname bl:" + norm(k) + r"\endcsname{" + str(v) + "}")
(REP / "numbers.tex").write_text("\n".join(L) + "\n")
defined = {norm(k) for k in M}
used = set()
for tex in (REP.parent.parent / "paper").glob("*.tex"):
    used |= set(re.findall(r"\\bl\{([^}]*)\}", tex.read_text()))
for tex in REP.glob("tab_*.tex"):
    used |= set(re.findall(r"\\bl\{([^}]*)\}", tex.read_text()))
missing = sorted(used - defined)
print(f"{len(M)} macros written; {len(used)} used in the paper; undefined: {missing}")
if BAD:
    print("CLAIMS THAT NO LONGER HOLD:\n  " + "\n  ".join(BAD))
assert not BAD, "claims in the paper no longer hold"
assert not missing, "undefined macros: " + ", ".join(missing)
print("all claims hold; all macros resolve")
