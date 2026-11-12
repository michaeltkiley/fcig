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
        d_ = 0 if (float(v).is_integer() and abs(v) >= 2) else (3 if abs(v) < 0.1 and v != 0 else 2)
        M[key] = f(v, d_); M["abs:" + key] = f(abs(v), d_)
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
        crow("Market and GS, levels since 1990", "mkt_gs_ninety"), crow("Market and FRB/US, levels since 1990", "mkt_frbus_ninety"),
        r"\multicolumn{4}{l}{\textit{Correlation of 12-month changes}} \\", crow("Market and GS", "mkt_gs_chg"), crow("Market and FRB/US", "mkt_frbus_chg"),
        r"\multicolumn{4}{l}{\textit{Correlation of flows}} \\", crow("Forward impetus and FCI-G", "fi_fcig"), crow("Forward impetus and FRB/US growth impetus", "fi_frbus_gi"), crow("FCI-G and FRB/US growth impetus", "fcig_frbus_gi"),
        r"\multicolumn{4}{l}{\textit{Average range of the four level indexes (pp)}} \\", crow("1974--2026", "range_long"), crow("1990--2026, zero at the 1990--2026 mean", "range_ninety"),
        r"\multicolumn{4}{l}{\textit{Latest reading, September 2026}} \\", crow("Market index", "latest_market", sign=True), crow("GS", "latest_gs", sign=True), crow("FRB/US index", "latest_frbus", sign=True),
        crow("Forward impetus", "latest_fi", sign=True), crow("FCI-G (1-year)", "latest_fcig", sign=True)]
table("compare", "The Market Index and the Other Indexes at Each Step", "tab:compare", ["", "Nominal", "Real", "Relative to $r^*$"], rows,
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
mac("rb:spread:weights", RB.loc[5:7, "latest_market"].max() - RB.loc[1:1, "latest_market"].min() * 0 - RB.loc[5:7, "latest_market"].min())
mac("gap:frbus:lo", pct(BT["rstar_latest_gap_frbus"], 5)); mac("gap:frbus:hi", pct(BT["rstar_latest_gap_frbus"], 95))
mac("rstar:lw:mean", float(D["rstar LW"].loc["1973-01":"2026-09"].mean()))
mac("act:rstar:best:dm", float(ACT[(ACT.case == "rstar") & ACT["index"].isin(["Market index forward impetus", "FCI-G, 1-year lookback", "FRB/US growth impetus", "FCI-G, 3-year lookback"])].dm_t.min()))
for k_ in ("mkt", "gs", "frbus"):
    mac(f"shift:{k_}:gfc", SC[f"rstar_{k_}_gfc"] - SC[f"nominal_{k_}_gfc"])
sh_ = [SC[f"rstar_{k_}_gfc"] - SC[f"nominal_{k_}_gfc"] for k_ in ("mkt", "gs", "frbus")]
mac("shift:min", min(sh_)); mac("shift:max", max(sh_))
mac("rb:min:mkt:gs", RB.mkt_gs.min()); mac("rb:min:mkt:frbus", RB.mkt_frbus.min()); mac("rb:min:fi:fcig", RB.fi_fcig.min())

# ------------------------------------------------------------------ claims asserted in the text
c = lambda st, k: CMP.loc[k, st]
chk(c("rstar", "mkt_gs") >= 0.98 and c("real", "mkt_gs") >= 0.98 and c("nominal", "mkt_gs") <= 0.80, "market-GS: high in real and r* terms, low in nominal")
chk(all(c(s, "mkt_frbus") >= 0.90 for s in ("nominal", "real", "rstar")), "market-FRB/US at least 0.90 at every step")
chk(c("nominal", "range_long") > c("real", "range_long") > c("rstar", "range_long") and c("nominal", "range_ninety") > c("real", "range_ninety") > c("rstar", "range_ninety"), "range falls at each step")
chk(c("nominal", "range_long") - c("rstar", "range_long") > 3 * (c("nominal", "range_ninety") - c("rstar", "range_ninety")), "range reduction much larger over 1974-2026 than since 1990")
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
chk(CMP.loc["latest_frbus", "rstar"] > pct(BT["rstar_latest"], 95) and pct(BT["rstar_latest_gap_frbus"], 95) < 0, "FRB/US reading above the market interval; gap interval excludes zero")
chk(abs(SC["rstar_latest90_market"] - SC["rstar_latest_market"]) > 1, "1990 base moves the market reading by more than a point")
chk(SC["rstar_mkt_frbus_ninety"] < 0.85 and SC["rstar_mkt_gs_ninety"] > 0.9, "since 1990: market-FRB/US below 0.85, market-GS above 0.9")
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

# ------------------------------------------------------------------ exhibits of the stance restructuring (steps 08-17)
I8 = pd.read_csv(RES / "08_insample.csv"); O8 = pd.read_csv(RES / "08_oos.csv")
def pick(df, **kw):
    m = pd.Series(True, index=df.index)
    for k, v in kw.items():
        m &= df[k] == v
    return df[m].iloc[0]
OUT_LAB = {"du": "Unemployment gap", "pay": "Payroll growth", "pi": "Core inflation"}
rows = []
for outcome, index, form, per, lab in (("du", "market", "level", "full", "Market index, level"), ("du", "market", "flow", "full", "Market index, flow"), ("du", "market", "mixed", "full", "Market index, flow, with the gap in levels"),
                                        ("du", "gs", "flow", "full", "GS, flow"), ("du", "frbus", "flow", "full", "FRB/US index, flow"),
                                        ("du", "market", "flow", "zlb", "Market index, flow, 2009--15"), ("du", "market", "flow", "post", "Market index, flow, 2022--26"),
                                        ("pay", "market", "flow", "full", "Market index, flow"), ("pay", "market", "mixed", "full", "Market index, flow, with the gap in levels"),
                                        ("pi", "market", "flow", "full", "Market index, flow")):
    a = pick(I8, outcome=outcome, step="rstar", index=index, form=form, period=per); b = pick(O8, outcome=outcome, step="rstar", index=index, form=form, period=per)
    if not rows or rows[-1][0] != OUT_LAB[outcome] and (outcome != "du" or not any(r[0] == OUT_LAB["du"] for r in rows if isinstance(r, list))):
        pass
    rows.append([f"{OUT_LAB[outcome]}: {lab}", f(a.gain_idx_given_ff), f(a.t_idx_both, 1), f(a.gain_ff_given_idx), f(b.rmse_idx_given_ff), f(b.cw_idx_given_ff, 1) if per == "full" else "--"])
table("stance", "Does the Index Add to the Funds-Rate Gap?", "tab:stance", ["", "Gain of index", "$t$ of index", "Gain of gap", "RMSE ratio", "Clark--West"], rows,
      "Local projections of the 12-month change in the unemployment gap, 12-month payroll growth and 12-month core inflation on own lags, the funds-rate gap (effective funds rate less one-year expected inflation less $r^*$) and the index relative to $r^*$, 1976--2026 (2020 to March 2021 excluded; HAC standard errors, 18 lags). Gain of index (of gap): increase in adjusted $R^2$ from adding the index (the gap) to a model that has the other. Level: both in levels; flow: both as 12-month changes; mixed: gap in levels, index as 12-month change. RMSE ratio and Clark--West: recursive out-of-sample forecasts from 1995 of the model with both variables relative to the model with the gap alone (below 1: the index helps; Clark--West above 1.3 is significant at 10 percent); the 2009--15 and 2022--26 rows are in sample.")
E8 = pd.read_csv(RES / "08_episodes.csv"); T8 = pd.read_csv(RES / "08_today.csv")
rows = []
for ep, lab in (("conundrum 2004-06..2006-06", "June 2004 to June 2006"), ("tightening 2022-03..2024-12", "March 2022 to December 2024"), ("2022-03..2023-12", "March 2022 to December 2023")):
    def g(rs, ser):
        r = E8[(E8.rstar == rs) & (E8.episode == ep) & (E8.series == ser)]
        return r.iloc[0] if len(r) else None
    m, mk, gs_, fr = g("LW", "market"), g("Kiley", "market"), g("LW", "gs"), g("LW", "frbus")
    rows.append([lab, f(m.ffg), f(m.index_point), f"{f(m.diff_point)} [{f(m.diff_lo)}, {f(m.diff_hi)}]", f"{f(mk.diff_point)} [{f(mk.diff_lo)}, {f(mk.diff_hi)}]", f(gs_.diff_point), f(fr.diff_point)])
tl = {k: T8[(T8.rstar == k) & (T8.series == s)].iloc[0] for k, s in (("mk", "market"),) for k in ("LW", "Kiley")} if False else None
tm, tmk = T8[(T8.rstar == "LW") & (T8.series == "market")].iloc[0], T8[(T8.rstar == "Kiley") & (T8.series == "market")].iloc[0]
tg, tf = T8[(T8.rstar == "LW") & (T8.series == "gs")].iloc[0], T8[(T8.rstar == "LW") & (T8.series == "frbus")].iloc[0]
rows.append(["September 2026", f(tm.ffg), f(tm["index"]), f"{f(tm['diff'])} [{f(tm.diff_lo)}, {f(tm.diff_hi)}]", f"{f(tmk['diff'])} [{f(tmk.diff_lo)}, {f(tmk.diff_hi)}]", f(tg["diff"]), f(tf["diff"])])
table("episodes_stance", "The Index Relative to the Funds-Rate Gap in Three Episodes and Today", "tab:stancepisodes", ["", "Funds-rate gap", "Index", "Index less gap [90\\%]", "Kiley $r^*$ [90\\%]", "GS less gap", "FRB/US less gap"], rows,
      "Averages over the window of the funds-rate gap and the market index relative to $r^*$ (Laubach--Williams), each less its 1973--2026 mean; index less gap is in points (the index in two-year-yield points, the gap in funds-rate points). The 90 percent interval takes the 5th and 95th percentiles over " + f"{REPS}" + " bootstrap samples of the announcements (the weights); the Kiley column replaces $r^*$ in the index and in the gap. GS and FRB/US: point estimates only (their weights are held fixed).")
mac("st:today:wedge", tm["diff"]); mac("st:today:lo", tm.diff_lo); mac("st:today:hi", tm.diff_hi); mac("st:today:ffg", tm.ffg); mac("st:today:index", tm["index"]); mac("st:today:share", float(tm.share_draws_diff_neg) * 100, 0)
for i_, e_ in enumerate(("conundrum 2004-06..2006-06", "tightening 2022-03..2024-12", "2022-03..2023-12")):
    r = E8[(E8.rstar == "LW") & (E8.episode == e_) & (E8.series == "market")].iloc[0]; rk = E8[(E8.rstar == "Kiley") & (E8.episode == e_) & (E8.series == "market")].iloc[0]
    for c_ in ("diff_point", "diff_lo", "diff_hi", "ffg", "index_point"):
        mac(f"st:ep{i_}:{c_}", float(r[c_]))
    mac(f"st:ep{i_}:kiley", float(rk.diff_point)); mac(f"st:ep{i_}:share", float(r.share_draws_diff_neg) * 100, 0)
    mac(f"st:ep{i_}:months", float(r.n_months), 0)
for k_, v_ in (("level", "level"), ("flow", "flow"), ("mixed", "mixed")):
    a = pick(I8, outcome="du", step="rstar", index="market", form=k_, period="full"); b = pick(O8, outcome="du", step="rstar", index="market", form=k_, period="full")
    for c_, n_ in (("gain_idx_given_ff", "gain"), ("gain_ff_given_idx", "gainff"), ("t_idx_both", "t"), ("t_ff_alone", "tff"), ("t_idx_alone", "tidx"), ("r2a_ff", "r2ff"), ("r2a_idx", "r2idx")):
        mac(f"st:du:{k_}:{n_}", float(a[c_]))
    mac(f"st:du:{k_}:cw", float(b.cw_idx_given_ff)); mac(f"st:du:{k_}:rmse", float(b.rmse_idx_given_ff)); mac(f"st:du:{k_}:noos", float(b.n_oos), 0)
for per_ in ("zlb", "post"):
    a = pick(I8, outcome="du", step="rstar", index="market", form="flow", period=per_); mac(f"st:du:{per_}:t", float(a.t_idx_both)); mac(f"st:du:{per_}:n", float(a.n), 0)
    b = pick(O8, outcome="du", step="rstar", index="market", form="flow", period=per_); mac(f"st:du:{per_}:cw", float(b.cw_idx_given_ff)); mac(f"st:du:{per_}:rmseff", float(b.rmse_ff_vs_own))
    bm = pick(O8, outcome="du", step="rstar", index="market", form="mixed", period=per_); mac(f"st:du:{per_}:cwm", float(bm.cw_idx_given_ff))
for o_, k_ in (("pay", "flow"), ("pay", "mixed"), ("pi", "flow")):
    a = pick(I8, outcome=o_, step="rstar", index="market", form=k_, period="full"); b = pick(O8, outcome=o_, step="rstar", index="market", form=k_, period="full")
    mac(f"st:{o_}:{k_}:gain", float(a.gain_idx_given_ff)); mac(f"st:{o_}:{k_}:t", float(a.t_idx_both)); mac(f"st:{o_}:{k_}:cw", float(b.cw_idx_given_ff))
for ix_ in ("gs", "frbus"):
    a = pick(I8, outcome="du", step="rstar", index=ix_, form="flow", period="full"); b = pick(O8, outcome="du", step="rstar", index=ix_, form="flow", period="full")
    mac(f"st:du:{ix_}:gain", float(a.gain_idx_given_ff)); mac(f"st:du:{ix_}:cw", float(b.cw_idx_given_ff)); mac(f"st:du:{ix_}:t", float(a.t_idx_both))
P8 = pd.read_csv(RES / "08_primary.csv"); P8 = P8[P8.outcome == "du"].set_index("form")
for k_ in ("flow", "mixed"):
    mac(f"st:prim:{k_}:holm", float(P8.loc[k_, "p_holm"]), 2); mac(f"st:prim:{k_}:p", float(P8.loc[k_, "p"]), 3)
for step_ in ("nominal", "real"):
    a = pick(I8, outcome="du", step=step_, index="market", form="flow", period="full"); mac(f"st:du:{step_}:t", float(a.t_idx_both)); mac(f"st:du:{step_}:gain", float(a.gain_idx_given_ff))

# figure: the wedge
DS = pd.read_csv(RES / "08_diff_series.csv", index_col=0); DS.index = pd.PeriodIndex(DS.index, freq="M"); tt = DS.index.to_timestamp()
fig, ax = plt.subplots(2, 1, figsize=(7.5, 5.6), sharex=True)
ax[0].plot(tt, DS.ffg, color=COLORS["fcig"], lw=1.2, label="Funds-rate gap (real funds rate less $r^*$)"); ax[0].plot(tt, DS.market, color=COLORS["market"], lw=1.4, label="Market index relative to $r^*$")
ax[0].set_title("Both measures of the stance, each less its 1973--2026 mean", loc="left"); axes(ax[0], "percentage points")
ax[1].fill_between(tt, DS.diff_lo, DS.diff_hi, color=COLORS["market"], alpha=0.18, lw=0, label="90% interval (weights)"); ax[1].plot(tt, DS["diff"], color=COLORS["market"], lw=1.4, label="Index less funds-rate gap")
for a_, b_ in (("2004-06-01", "2006-06-30"), ("2022-03-01", "2024-12-31")):
    for x_ in ax:
        x_.axvspan(pd.Timestamp(a_), pd.Timestamp(b_), color="#eeeeee", lw=0, zorder=0)
ax[1].set_title("The wedge", loc="left"); axes(ax[1], "percentage points")
figure("fig_wedge", fig)

# level versus flow
M9 = pd.read_csv(RES / "09_mean.csv"); G9 = pd.read_csv(RES / "09_granger.csv").set_index("series")
G9i = G9
SER = [("Market|nominal", "Market index, nominal"), ("Market|real", "Market index, real"), ("Market|rstar", "Market index, relative to $r^*$"), ("GS|rstar", "GS, relative to $r^*$"),
       ("FRB/US|rstar", "FRB/US index, relative to $r^*$"), ("FCI-G|rstar", "FCI-G, relative to $r^*$"), ("NFCI|given", "NFCI"), ("ANFCI|given", "ANFCI")]
rows = []
for k_, lab in SER:
    a = M9[(M9.outcome == "du") & (M9.series == k_)].iloc[0]; b = M9[(M9.outcome == "pay") & (M9.series == k_)].iloc[0]
    rows.append([lab, f(a.t_lvl_both, 1), f(a.t_flw_both, 1), f(a.gain_lvl), f(a.gain_flw), f(b.t_lvl_both, 1), f(b.t_flw_both, 1)])
table("levelflow", "Level or Flow? Unemployment and Payrolls a Year Ahead", "tab:levelflow", ["", "$t$ level", "$t$ flow", "Gain level", "Gain flow", "$t$ level", "$t$ flow"], rows,
      "Local projections of the 12-month change in the unemployment gap (first four columns) and of 12-month payroll growth (last two) on own lags, the level of the index and its 12-month change entered together, 1976--2026 (HAC standard errors, 18 lags); gain: increase in adjusted $R^2$ of the index alone over own lags. FCI-G is a flow by construction: its reading is entered as the level and its change as the flow.")
rows = []
for k_, lab in [s for s in SER if s[0] in ("Market|nominal", "Market|rstar", "GS|rstar", "FRB/US|rstar", "FCI-G|rstar", "NFCI|given", "ANFCI|given")]:
    r = G9.loc[k_]
    rows.append([lab, f"{r.p_all12:.1e}".replace("e-0", "e$-$0").replace("e-", "e$-$") if r.p_all12 < 1e-3 else f"{r.p_all12:.3f}", f(r.p_sum, 2), f"{r.p_diff11:.1e}".replace("e-0", "e$-$0").replace("e-", "e$-$") if r.p_diff11 < 1e-3 else f"{r.p_diff11:.3f}"])
table("granger", "What the Granger Test on the Level Picks Up", "tab:granger", ["", "All 12 lags", "Current level (sum of lags)", "11 changes"], rows,
      "$p$-values of tests in the unemployment equation of the two-variable VAR (12 lags, 1973--2026): the 12 lags of the index jointly (the Granger test); their sum, which is the coefficient on the current level once the lags are rewritten as the level and 11 one-month changes; and the 11 changes jointly.")
def sci(x):
    e = int(np.floor(np.log10(x))); m_ = x / 10 ** e
    return f"${m_:.0f}\\times10^{{{e}}}$"
M["lf:mkt:p:all"] = sci(float(G9i.loc["Market|rstar", "p_all12"])); M["lf:mkt:p:diff"] = sci(float(G9i.loc["Market|rstar", "p_diff11"])); mac("lf:mkt:p_sum", float(G9i.loc["Market|rstar", "p_sum"]), 2)
M9s = M9.set_index(["outcome", "series"])
for k_, nm in (("Market|rstar", "mkt"), ("GS|rstar", "gs"), ("FRB/US|rstar", "frbus"), ("Market|nominal", "mktn"), ("Market|real", "mktr"), ("FCI-G|rstar", "fcig"), ("NFCI|given", "nfci"), ("ANFCI|given", "anfci")):
    for c_ in ("t_lvl_both", "t_flw_both", "gain_lvl", "gain_flw"):
        mac(f"lf:du:{nm}:{c_}", float(M9s.loc[("du", k_), c_]), 1 if c_.startswith("t_") else 2)
    mac(f"lf:pay:{nm}:t_flw", float(M9s.loc[("pay", k_), "t_flw_both"]), 1)
Q9 = pd.read_csv(RES / "09_quantile.csv"); q = Q9[(Q9.tau == 0.1) & (Q9.series == "Market|rstar")].iloc[0]
mac("lf:q10:b", q.b_flw); mac("lf:q10:lo", q.lo_flw); mac("lf:q10:hi", q.hi_flw)
q = Q9[(Q9.tau == 0.1) & (Q9.series == "NFCI|given")].iloc[0]; mac("lf:q10:nfci:b", q.b_lvl); mac("lf:q10:nfci:lo", q.lo_lvl); mac("lf:q10:nfci:hi", q.hi_lvl)

# NFCI complement
J = pd.read_csv(RES / "10_joint_lp.csv")
rows = []
for o_, h_, lab in (("du", 6, "Unemployment gap, 6 months"), ("du", 12, "Unemployment gap, 12 months"), ("du", 24, "Unemployment gap, 24 months"), ("pay", 12, "Payroll growth, 12 months"), ("rec12", 12, "Recession within 12 months (logit)")):
    a = J[(J.spec == "joint_nfci") & (J.outcome == o_) & (J.h == h_) & (J["var"] == "mkt_flw")]; b = J[(J.spec == "joint_nfci") & (J.outcome == o_) & (J.h == h_) & (J["var"] == "nfci")]
    if len(a) and len(b):
        a, b = a.iloc[0], b.iloc[0]
        rows.append([lab, f(a.b), f(a.t_hac, 1), f(b.b), f(b.t_hac, 1)])
        mac(f"nf:{o_}{h_}:mkt_t", a.t_hac, 1); mac(f"nf:{o_}{h_}:nfci_t", b.t_hac, 1); mac(f"nf:{o_}{h_}:mkt_b", a.b); mac(f"nf:{o_}{h_}:nfci_b", b.b)
table("nfci", "The Market Index and the NFCI Together", "tab:nfci", ["", "Market flow", "$t$", "NFCI level", "$t$"], rows,
      "Coefficients on the 12-month change of the market index relative to $r^*$ and on the level of the NFCI, entered together with own lags (unemployment gap in points per standard deviation of the regressor; HAC standard errors, 12 lags; logit coefficients in the last row).")

# purge
V11 = pd.read_csv(RES / "11_var.csv")
rows = []
for kind, lab in (("market", "Market index"), ("gs", "GS")):
    cells = []
    for ver in ("unpurged", "full", "recursive"):
        r = V11[(V11.kind == kind) & (V11.step == "rstar") & (V11.version == ver) & (V11.start == "1983-01")].iloc[0]
        cells.append(f"{f(r.phi12)} [{f(r.phi12_lo90)}, {f(r.phi12_hi90)}]"); mac(f"pg:{kind}:{ver}", r.phi12); mac(f"pg:{kind}:{ver}:lo", r.phi12_lo90); mac(f"pg:{kind}:{ver}:hi", r.phi12_hi90)
    rows.append([lab] + cells)
table("purge", "Does the Flow Survive Removing Activity?", "tab:purge", ["Relative to $r^*$", "Unpurged", "Purged, full sample", "Purged, recursive"], rows,
      "$\\Phi(12)$ with 90 percent block-bootstrap interval from the two-variable VAR (12 lags, January 1983 to September 2026). Purged: each input variable (10-year yield, equity valuation, dollar; GS inputs for GS) is regressed on current and 12 lags of the unemployment gap and 12-month core PCE inflation, on the full sample or recursively (expanding window), and the index is rebuilt from the residuals with unchanged weights.")
for kind in ("market",):
    for k_, c_ in (("full", "corr_fi_unpurged"), ("recursive", "corr_fi_unpurged")):
        r = V11[(V11.kind == kind) & (V11.step == "rstar") & (V11.version == k_) & (V11.start == "1983-01")].iloc[0]; mac(f"pg:{kind}:{k_}:corrfi", r[c_])
mac("pg:fall:full", (1 - float(V11[(V11.kind == "market") & (V11.step == "rstar") & (V11.version == "full") & (V11.start == "1983-01")].phi12.iloc[0]) / float(V11[(V11.kind == "market") & (V11.step == "rstar") & (V11.version == "unpurged") & (V11.start == "1983-01")].phi12.iloc[0])) * 100, 0)
mac("pg:fall:rec", (1 - float(V11[(V11.kind == "market") & (V11.step == "rstar") & (V11.version == "recursive") & (V11.start == "1983-01")].phi12.iloc[0]) / float(V11[(V11.kind == "market") & (V11.step == "rstar") & (V11.version == "unpurged") & (V11.start == "1983-01")].phi12.iloc[0])) * 100, 0)

# checks table: 1973+ against 1996+
C12 = pd.read_csv(RES / "12_checks.csv")
rows = []
for row_, lags, lab in (("a", 12, "(a) 1973--2026, 12 lags (main)"), ("b", 12, "(b) 1996--2026, 12 lags"), ("b", 4, "(b) 1996--2026, 4 lags"), ("c", 12, "(c) excluding 2008--15"), ("d", 12, "(d) weights through 2019"), ("e", 12, "(e) origins from 1974")):
    r = C12[(C12.row == row_) & (C12.lags == lags) & (C12.series == "Market") & (C12.step == "rstar")]
    if not len(r):
        continue
    r = r.iloc[0]
    rows.append([lab, f"{f(r.phi12)} [{f(r.phi12_lo90)}, {f(r.phi12_hi90)}]", f(r.du_t_flow, 1), f(r.du_t_level, 1), f(r.du_gain_flow), f(r.st_du_flow_gain), f(r.cw_du_flow, 1), f(r.pay_t_flow, 1)])
    mac(f"ck:{row_}{lags}:phi", r.phi12); mac(f"ck:{row_}{lags}:lo", r.phi12_lo90); mac(f"ck:{row_}{lags}:hi", r.phi12_hi90); mac(f"ck:{row_}{lags}:tflow", r.du_t_flow, 1); mac(f"ck:{row_}{lags}:tlevel", r.du_t_level, 1)
    mac(f"ck:{row_}{lags}:gain", r.du_gain_flow); mac(f"ck:{row_}{lags}:stgain", r.st_du_flow_gain); mac(f"ck:{row_}{lags}:cw", r.cw_du_flow, 1); mac(f"ck:{row_}{lags}:payt", r.pay_t_flow, 1)
    mac(f"ck:{row_}{lags}:oosn", r.oos_n, 0); mac(f"ck:{row_}{lags}:oosrec", r.oos_rec, 0)
table("checks96", "The Foundation on 1973--2026 and on 1996--2026", "tab:checks96", ["Relative to $r^*$", "$\\Phi(12)$ [90\\%]", "$t$ flow", "$t$ level", "Gain flow", "Gain of index given gap", "Clark--West", "$t$ payroll flow"], rows,
      "Market index relative to $r^*$. $\\Phi(12)$: VAR response of the unemployment gap after 12 months (2020 dummied; bootstrap interval). $t$ and gain: local projections of the 12-month change of the unemployment gap on the index level and 12-month change together (HAC, 18 lags); gain is the gain in adjusted $R^2$ of the flow over own lags. Gain of index given gap and Clark--West: as Table~\\ref{tab:stance}, flow form. Row (b) uses only origins from 1996 (out-of-sample evaluation from December 2004, one recession); (c) drops 2008--15 (dummies in the VAR, origins touching the window in the regressions); (d) weights from announcements through 2019; (e) regression origins from 1974. Payroll flow: unemployment is the claim, payrolls are not.")
L12 = pd.read_csv(RES / "12_ladder.csv")
for smp, nm in (("a", "full"), ("a_pre96", "pre96"), ("b", "p96")):
    r = L12[(L12["sample"] == smp) & (L12.series == "market") & (L12.later == "rstar") & (L12.earlier == "nominal")]
    if len(r):
        r = r.iloc[0]; mac(f"ld:{nm}:dr2", r.dr2, 3); mac(f"ld:{nm}:lo", r.dr2_lo90, 3); mac(f"ld:{nm}:hi", r.dr2_hi90, 3); mac(f"ld:{nm}:dm", r.dm_t, 1)
VS = pd.read_csv(RES / "12_var_subperiods.csv"); VS12 = VS[VS.lags == 12].set_index("period")
for per_ in VS12.index:
    k_ = per_.replace("-", "").replace(" ", "")
    mac(f"vs:{k_}", VS12.loc[per_, "phi12"]); mac(f"vs:{k_}:lo", VS12.loc[per_, "lo90"]); mac(f"vs:{k_}:hi", VS12.loc[per_, "hi90"])
print("subperiod keys:", list(VS12.index))

# neutrality
N13 = pd.read_csv(RES / "13_neutrality_diffs.csv")
rows = []
for ser, lab in (("Market|nominal", "Market index, nominal"), ("Market|real", "Market index, real"), ("Market|rstar", "Market index, $r^*$ (Laubach--Williams)"), ("Market|rstar_kiley", "Market index, $r^*$ (Kiley)"), ("GS|rstar", "GS, $r^*$"), ("FRBUS|rstar", "FRB/US index, $r^*$")):
    r = N13[(N13.series == ser) & (N13["from"] == "P2_1990-2007") & (N13.to == "P3_2009-19")].iloc[0]
    rows.append([lab, f"{f(r['diff'])} [{f(r.lo90)}, {f(r.hi90)}]", f(r.diff_in_sd)]); k_ = ser.split("|")[1] + ser.split("|")[0][:2].lower()
    mac(f"nu:{k_}", r["diff"]); mac(f"nu:{k_}:lo", r.lo90); mac(f"nu:{k_}:hi", r.hi90)
table("neutrality", "The Level of the Index at a Zero Unemployment Gap, 2009--19 against 1990--2007", "tab:neutrality", ["", "Change in level [90\\%]", "In standard deviations of the index"], rows,
      "Intercept of a regression of the index level on the unemployment gap, by period, 2009--19 minus 1990--2007, with a 90 percent block-bootstrap interval (24-month blocks). A level that means the same thing across regimes would show a change near zero.")

# real time
R17 = pd.read_csv(RES / "17_realtime_table.csv")
rows = []
for _, r in R17[R17.outcome == "du"].iterrows():
    rows.append([f"{r.panel}: {r.row}", f"{int(r.n)}", f(r.flow_t, 1), f(r.flow_gain), f(r.flow_cw, 1) if r.flow_cw == r.flow_cw else "--", f(r.mixed_t, 1), f(r.mixed_gain)])
table("realtime", "The Unemployment Results with Vintage Data and Real-Time $r^*$", "tab:realtime", ["Unemployment gap", "$n$", "$t$ flow", "Gain flow", "Clark--West", "$t$ mixed", "Gain mixed"], rows,
      "Market index relative to $r^*$, index given funds-rate gap (flow and mixed forms of Table~\\ref{tab:stance}), same designs on revised data and on data as known at the time: vintage unemployment rates (ALFRED) with the vintage CBO natural rate (from 2011) and the New York Fed's real-time Laubach--Williams $r^*$ (from 2005; published estimates have a gap from August 2020 to May 2023). The weights, the Kiley $r^*$, the earnings in CAPE and expected inflation are not real time. Clark--West only for the long sample.")
for _, r in R17[R17.outcome == "du"].iterrows():
    k_ = {"Revised data": "rev", "Vintage data": "vin", "Vintage data and NROU": "vinn", "Revised data, full-sample r*": "revf", "Revised data, real-time r*": "revr", "Vintage data, real-time r*": "vinr"}[r.row] + r.panel[:4]
    mac(f"rt:{k_}:t", r.flow_t, 1); mac(f"rt:{k_}:gain", r.flow_gain, 3); mac(f"rt:{k_}:mt", r.mixed_t, 1); mac(f"rt:{k_}:mg", r.mixed_gain, 3)
    if r.flow_cw == r.flow_cw:
        mac(f"rt:{k_}:cw", r.flow_cw, 2)

C8 = pd.read_csv(RES / "08_components.csv")
for _, r in C8.iterrows():
    nm = r.component.replace("+", "_")
    mac(f"cp:{r.outcome}:{nm}:gain", r.gain); mac(f"cp:{r.outcome}:{nm}:t", r.t, 1); mac(f"cp:{r.outcome}:{nm}:cw", r.cw, 1)
# weight path figure
W16 = pd.read_csv(RES / "16_weight_path.csv")
fig, ax = plt.subplots(1, 3, figsize=(8.5, 3.0))
for a_, (ser, nm) in zip(ax, (("ten", "10-year yield"), ("eq", "Equity valuation"), ("usd", "Real dollar"))):
    bl = W16[(W16.kind == "baseline") & (W16.series == ser)].iloc[0]
    a_.axhspan(bl.lo, bl.hi, color=COLORS["market"], alpha=0.12, lw=0); a_.axhline(bl.value, color=COLORS["grey"], lw=0.8)
    for win, col, lab in (("expanding", COLORS["market"], "Expanding window"), ("rolling20", COLORS["frbus"], "20-year rolling window")):
        p_ = W16[(W16.kind == "path") & (W16.series == ser) & (W16.window == win)]
        a_.plot(pd.to_datetime(p_.date), p_.value, color=col, lw=1.2, label=lab)
    a_.set_title(nm, loc="left"); a_.grid(alpha=0.25)
    for sp in ("top", "right"):
        a_.spines[sp].set_visible(False)
ax[0].legend(frameon=False, fontsize=7)
figure("fig_weight_path", fig)

# ------------------------------------------------------------------ claims of the stance paper
P8all = pd.read_csv(RES / "08_primary.csv")
chk(len(P8all) == 9 and int((P8all.p < 0.10).sum()) == 5 and int((P8all.p_holm < 0.10).sum()) == 1, "stance: nine primary tests, five raw p < 0.10, one Holm p < 0.10")
a_ = pick(I8, outcome="du", step="rstar", index="market", form="flow", period="full"); l_ = pick(I8, outcome="du", step="rstar", index="market", form="level", period="full")
chk(a_.gain_idx_given_ff > 0.08 and a_.gain_ff_given_idx < 0.02 and l_.gain_idx_given_ff < 0.02, "stance: index adds to the gap in flow form, gap adds nothing, level adds nothing")
chk(abs(float(pick(I8, outcome="pi", step="rstar", index="market", form="flow", period="full").gain_idx_given_ff)) < 0.01, "stance: nothing for core inflation")
e0 = E8[(E8.rstar == "LW") & (E8.series == "market")]
chk((e0[e0.episode.str.startswith(("conundrum", "tightening"))].diff_hi < 0).all() and (e0[e0.episode == "2022-03..2023-12"].diff_hi > 0).all(), "stance: 2004-06 and 2022-24 intervals exclude zero, 2022-23 includes it")
chk(tm.diff_hi < 0, "stance: September 2026 interval excludes zero")
chk(all(float(M9s.loc[("du", k_), "t_flw_both"]) > 4.5 and abs(float(M9s.loc[("du", k_), "t_lvl_both"])) < 1 for k_ in ("Market|rstar", "GS|rstar", "FRB/US|rstar")), "levelflow: market, GS, FRB/US flows t > 4.5, levels < 1")
chk(all(float(M9s.loc[("du", k_), "t_lvl_both"]) > 2.5 and float(M9s.loc[("du", k_), "t_flw_both"]) < 1.7 for k_ in ("NFCI|given", "ANFCI|given")), "levelflow: NFCI and ANFCI levels carry it")
gm = G9i.loc["Market|rstar"]; chk(gm.p_all12 < 1e-6 and gm.p_sum > 0.1 and gm.p_diff11 < 1e-4, "granger: all lags and changes significant, the sum is not")
jj = lambda o, h, v: J[(J.spec == "joint_nfci") & (J.outcome == o) & (J.h == h) & (J["var"] == v)].iloc[0]
chk(jj("du", 6, "mkt_flw").t_hac > 2.5 and jj("du", 12, "mkt_flw").t_hac > 2.5 and jj("du", 6, "nfci").t_hac > 2.5 and jj("du", 12, "nfci").t_hac > 2.5 and jj("du", 24, "nfci").t_hac > 4 and abs(jj("du", 24, "mkt_flw").t_hac) < 1 and jj("rec12", 12, "nfci").t_hac > 4 and jj("rec12", 12, "mkt_flw").t_hac < 2, "nfci: both keep 6 and 12 months, only NFCI at 24 months and for recessions")
chk(all(V11[(V11.step == "rstar") & (V11.start == "1983-01")].phi12_lo90 > 0), "purge: every r* interval above zero")
chk(30 <= float(M["pg:fall:full"]) <= 70 and 30 <= float(M["pg:fall:rec"]) <= 70, "purge: response falls 30 to 70 percent")
chk(float(N13[(N13.series == "Market|nominal") & (N13.to == "P3_2009-19") & (N13["from"] == "P2_1990-2007")]["diff"].iloc[0]) < -1 and float(N13[(N13.series == "Market|real") & (N13.to == "P3_2009-19") & (N13["from"] == "P2_1990-2007")]["diff"].iloc[0]) < -1 and float(N13[(N13.series == "Market|rstar") & (N13.to == "P3_2009-19") & (N13["from"] == "P2_1990-2007")]["diff"].iloc[0]) > 0 and abs(float(N13[(N13.series == "Market|rstar_kiley") & (N13.to == "P3_2009-19") & (N13["from"] == "P2_1990-2007")]["diff"].iloc[0])) < 0.5, "neutrality: nominal and real shift down, LW up, Kiley near zero")
c_a, c_b = C12[(C12.row == "a") & (C12.series == "Market") & (C12.step == "rstar")].iloc[0], C12[(C12.row == "b") & (C12.lags == 12) & (C12.series == "Market") & (C12.step == "rstar")].iloc[0]
chk(1.4 < (c_b.phi12_hi90 - c_b.phi12_lo90) / (c_a.phi12_hi90 - c_a.phi12_lo90) < 1.8 and c_b.phi12_lo90 > 0 and abs(c_b.pay_t_flow) < 2 and c_b.du_t_flow > 3.5, "1996+: interval about 1.6 times as wide, unemployment holds, payrolls do not")
chk(float(M["ld:p96:lo"].replace("$-$", "-")) > 0 and float(M["ld:pre96:lo"].replace("$-$", "-")) < 0 < float(M["ld:pre96:hi"]), "ladder: r* step helps on 1996+ and not before")
c_c = C12[(C12.row == "c") & (C12.series == "Market") & (C12.step == "rstar")].iloc[0]; chk(c_c.du_t_level > 3, "level t > 3 when 2008-15 is excluded")
R17a = R17[(R17.outcome == "du") & (R17.panel == "1976-2025")].set_index("row"); R17b = R17[(R17.outcome == "du") & (R17.panel == "2006-2025")].set_index("row")
chk(abs(R17a.loc["Vintage data", "flow_t"] - R17a.loc["Revised data", "flow_t"]) < 0.3 and R17b.loc["Revised data, real-time r*", "flow_gain"] < 0.5 * R17b.loc["Revised data, full-sample r*", "flow_gain"], "real time: vintage data leave the result, real-time r* cuts the gain by more than half")
chk(float(SC["exp_post2010_n_out_ten"]) == 0 and float(SC["exp_post2010_n_out_usd"]) == 0 and 0 < float(SC["exp_post2010_n_out_eq"]) <= 15 and float(SC["roll_post2010_n_out_ten"]) > 0, "weights: expanding inside the band after 2010 (equity briefly out), rolling fails")
S15 = pd.read_csv(RES / "15_summary.csv"); sc_ = S15[(S15.step == "rstar") & (S15.form.str.contains("change|flow")) & (S15.set != "MKT")] if "set" in S15 else S15
chk(float(SC["w_rstar_n_holm_sig10"]) == 0 and float(SC["w_rstar_n_primary_tests"]) == 120 and float(SC["w_rstar_n_raw_sig10"]) == 25, "weights: 25 of 120 raw rejections, none after Holm")
chk(float(SC["lad_rstar_vs_nominal_all_n_ratio_below1"]) == 69 and float(SC["lad_rstar_vs_nominal_all_n_tests"]) == 91 and float(SC["lad_rstar_vs_nominal_all_n_holm_sig05"]) == 0, "ladder: 69 of 91, none after Holm at 5 percent")

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
