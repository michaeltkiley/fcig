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
    txt = ("\\begin{table}[tbp]\\centering" + ("\\small" if small else "") + "\n\\caption{" + title_case(caption) + "}\\label{" + label + "}\n" + body +
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

S15 = pd.read_csv(RES / "15_summary.csv"); S15r = S15[(S15.step == "rstar") & S15.set.isin(["FRBUS3", "PC1", "EQ", "ACT"])]
for fm_ in ("level", "change"):
    v_ = (S15r[S15r.form == fm_].geo_mse_ratio_to_mkt - 1) * 100
    mac(f"wt:{fm_}:min", float(v_.min()), 0); mac(f"wt:{fm_}:max", float(v_.max()), 0)
mac("lf:q50:b", float(Q9[(Q9.tau == 0.5) & (Q9.series == "Market|rstar")].iloc[0].b_flw))
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

# ------------------------------------------------------------------ exhibits of the agreement paper (steps 18-19)
W18 = pd.read_csv(RES / "18_weights.csv"); E18 = pd.read_csv(RES / "18_example.csv"); D18e = pd.read_csv(RES / "18_D_events.csv"); D18m = pd.read_csv(RES / "18_D_monthly.csv")
B18 = pd.read_csv(RES / "18_bridge_variance.csv"); MG = pd.read_csv(RES / "18_matched_grid.csv"); BE18 = pd.read_csv(RES / "18_bridge_episodes.csv")
P19 = pd.read_csv(RES / "19_prim.csv"); S19 = pd.read_csv(RES / "19_spec.csv"); PR19 = pd.read_csv(RES / "19_prop.csv"); SPF19 = pd.read_csv(RES / "19_spf.csv"); EP19 = pd.read_csv(RES / "19_episodes.csv"); OOS19 = pd.read_csv(RES / "19_oos.csv")
def w18(h, q):
    return W18[(W18.h == h) & (W18.quantity == q)].iloc[0]
def ex18(h, ix, q):
    return E18[(E18.h == h) & (E18["index"] == ix) & (E18.quantity == q)].iloc[0]
def ci(r, d=2):
    return f"[{f(r.lo, d)}, {f(r.hi, d)}]" if r.lo == r.lo else ""
rows = [["Equity valuation falls 5 log points", f(ex18(4, "market", "eq_effect").point, 3), ci(ex18(4, "market", "eq_effect"), 3), f(ex18(4, "frbus_b", "eq_effect").point, 3)],
        ["Dollar appreciates 3.9 log points", f(ex18(4, "market", "usd_effect").point, 3), ci(ex18(4, "market", "usd_effect"), 3), f(ex18(4, "frbus_b", "usd_effect").point, 3)],
        ["Dollar effect over equity effect", f(ex18(4, "market", "ratio_usd_eq").point), ci(ex18(4, "market", "ratio_usd_eq")), f(ex18(4, "frbus_b", "ratio_usd_eq").point)],
        ["Typical joint response to a unit of policy news", "1.00", "", f(ex18(4, "frbus_b", "joint_response").point, 3) + " " + ci(ex18(4, "frbus_b", "joint_response"), 2)]]
table("example", "Two Financial Movements That the Market Index Rates Alike", "tab:example", ["", "Market index", "90\\% interval", "FRB/US index"], rows,
      "Weights applied to the stated movements, with no change in the 10-year yield. Market index: two-year-yield points per movement, weights from announcement-window responses (Table~\\ref{tab:weights}); the interval takes the 5th and 95th percentiles over bootstrap samples of the announcements. FRB/US index: funds-rate points; the effect on GDP after four quarters of a persistent shift in the variable, divided by the effect of a persistent one percentage point rise in the funds rate. Typical joint response: the index applied to the responses of the three variables to a unit of policy news (one by construction for the market index).")
for h_ in (2, 4, 8):
    bp = w18(h_, "bpsi"); mac(f"ag:h{h_}:bpsi", bp.point, 3); mac(f"ag:h{h_}:bpsi:lo", bp.lo, 2); mac(f"ag:h{h_}:bpsi:hi", bp.hi, 2)
    rr = ex18(h_, "frbus_over_market", "ratio_of_ratios"); mac(f"ag:h{h_}:rr", rr.point); mac(f"ag:h{h_}:rr:lo", rr.lo); mac(f"ag:h{h_}:rr:hi", rr.hi)
    mac(f"ag:h{h_}:fr", ex18(h_, "frbus_b", "ratio_usd_eq").point)
    mac(f"ag:h{h_}:wbeq", w18(h_, "wB_eq").point, 3); mac(f"ag:h{h_}:wbusd", w18(h_, "wB_usd").point, 3)
mac("ag:mkt:ratio", ex18(4, "market", "ratio_usd_eq").point); mac("ag:mkt:ratio:lo", ex18(4, "market", "ratio_usd_eq").lo); mac("ag:mkt:ratio:hi", ex18(4, "market", "ratio_usd_eq").hi)
mac("ag:ex:eq:mkt", ex18(4, "market", "eq_effect").point, 3); mac("ag:ex:usd:mkt", ex18(4, "market", "usd_effect").point, 3); mac("ag:ex:eq:fr", ex18(4, "frbus_b", "eq_effect").point, 3); mac("ag:ex:usd:fr", ex18(4, "frbus_b", "usd_effect").point, 3)
rows = []
for h_ in (2, 4, 8):
    bp, rr = w18(h_, "bpsi"), ex18(h_, "frbus_over_market", "ratio_of_ratios")
    rows.append([f"{h_} quarters", f"{f(bp.point, 3)} [{f(bp.lo)}, {f(bp.hi)}]", f(w18(h_, "wB_eq").point, 3), f(w18(h_, "wB_usd").point, 3), f(ex18(h_, "frbus_b", "ratio_usd_eq").point), f"{f(rr.point)} [{f(rr.lo)}, {f(rr.hi)}]"])
table("agree", "Agreement on Announcements and the Contrast in Composition", "tab:agree", ["FRB/US horizon", "Joint response to policy news [90\\%]", "Normalized equity weight", "Normalized dollar weight", "Dollar over equity, FRB/US", "Ratio of ratios [90\\%]"], rows,
      "FRB/US weights for GDP at the horizon shown, persistent-shift experiment, in funds-rate points; the joint response is the FRB/US weights applied to the responses to a unit of policy news (market index: one). Normalized weights: FRB/US weights divided by that response, so that both indexes read one on a conventional surprise; market weights are 0.609 (10-year yield), $-0.051$ (equity valuation) and 0.065 (dollar). Ratio of ratios: the FRB/US dollar-over-equity ratio divided by the market's (\\bl{ag:mkt:ratio}); the interval comes from the bootstrap of the market weights, and the FRB/US weights are held fixed.")
mg = MG[MG.h == 4]
for hl_, nm_ in ((np.inf, "inf"), (8.0, "8"), (4.0, "4"), (2.0, "2")):
    r = mg[(mg.hl_eq == hl_) & (mg.hl_usd == hl_)]
    if len(r):
        mac(f"ag:mp:hl{nm_}", r.iloc[0].ratio_usd_eq)
MP18 = pd.read_csv(RES / "18_matched_paths.csv")
for hl_, nm_ in ((8.0, "8"), (4.0, "4"), (2.0, "2")):
    r = MP18[(MP18.h == 4) & (MP18.hl_eq == hl_) & (MP18.hl_usd == hl_) & (MP18.hl_y10 == hl_) & (MP18.quantity == "bpsi")]
    if len(r):
        r = r.iloc[0]; mac(f"ag:bp:hl{nm_}", r.point); mac(f"ag:bp:hl{nm_}:lo", r.lo); mac(f"ag:bp:hl{nm_}:hi", r.hi)
mac("ag:mp:min", float(mg.ratio_usd_eq.min())); mac("ag:mp:max", float(mg.ratio_usd_eq.max()))
def dm(change, per, stat, case="rstar", h=4):
    r = D18m[(D18m.h == h) & (D18m.case == case) & (D18m.change == change) & (D18m.period == per) & (D18m.stat == stat)].iloc[0]
    return r
def de(stat, h=4, spec="loo"):
    return D18e[(D18e.h == h) & (D18e.spec == spec) & (D18e.stat == stat)].iloc[0]
rows = [["Announcement windows, held out", f"{f(de('mean_abs').point, 3)}", f"{f(de('ratio_mean_abs').point)} [{f(de('ratio_mean_abs').lo)}, {f(de('ratio_mean_abs').hi)}]", "0", "--"]]
for ch_, labch in (("1m", "Monthly changes"), ("12m", "12-month changes")):
    for per_ in ("1996-2026", "1973-2026"):
        ma, ra, sh, rn = dm(ch_, per_, "mean_abs"), dm(ch_, per_, "ratio_mean_abs"), dm(ch_, per_, "share_gt_0p25"), dm(ch_, per_, "mean_run_0p25")
        rows.append([f"{labch}, {per_.replace('-', '--')}", f(ma.point, 3 if ch_ == "1m" else 2), f"{f(ra.point)} [{f(ra.lo)}, {f(ra.hi)}]", f"{sh.point * 100:.0f}", f(rn.point, 1) if rn.point == rn.point else "--"])
table("dsize", "How Large Is the Difference between the Two Readings?", "tab:dsize", ["Movements", "Mean $|D|$", "Ratio to market move [90\\%]", "Share above 0.25 (\\%)", "Mean run (months)"], rows,
      "$D$ is the FRB/US reading (four quarters, normalized so that a conventional policy surprise reads one) less the market reading, applied to the changes of the equity valuation, the 10-year yield and the dollar at the $r^*$ step. Announcement windows: held-out events (weights re-estimated without each event). Ratio: mean $|D|$ over mean absolute market move; interval from bootstrap samples of the announcements and, for the monthly history, of 12- or 24-month blocks of months. A run is consecutive months with $|D|$ above 0.25.")
mac("dz:ev:mean", de("mean_abs").point, 3); mac("dz:ev:ratio", de("ratio_mean_abs").point); mac("dz:ev:ratio:lo", de("ratio_mean_abs").lo); mac("dz:ev:ratio:hi", de("ratio_mean_abs").hi); mac("dz:ev:move", de("mean_abs_market_move").point, 3); mac("dz:ev:p90", de("p90_abs").point, 3)
for ch_ in ("1m", "12m"):
    mac(f"dz:{ch_}:ratio", dm(ch_, "1996-2026", "ratio_mean_abs").point); mac(f"dz:{ch_}:ratio:lo", dm(ch_, "1996-2026", "ratio_mean_abs").lo); mac(f"dz:{ch_}:ratio:hi", dm(ch_, "1996-2026", "ratio_mean_abs").hi)
    mac(f"dz:{ch_}:sh25", dm(ch_, "1996-2026", "share_gt_0p25").point * 100, 0); mac(f"dz:{ch_}:sh25:lo", dm(ch_, "1996-2026", "share_gt_0p25").lo * 100, 0); mac(f"dz:{ch_}:sh25:hi", dm(ch_, "1996-2026", "share_gt_0p25").hi * 100, 0)
    mac(f"dz:{ch_}:mean", dm(ch_, "1996-2026", "mean_abs").point, 2)
mac("dz:12m:nom", dm("12m", "1996-2026", "ratio_mean_abs", case="nominal").point); mac("dz:12m:nom:lo", dm("12m", "1996-2026", "ratio_mean_abs", case="nominal").lo); mac("dz:12m:nom:hi", dm("12m", "1996-2026", "ratio_mean_abs", case="nominal").hi)
mac("dz:12m:sh50", dm("12m", "1996-2026", "share_gt_0p5").point * 100, 0); mac("dz:12m:run", dm("12m", "1996-2026", "mean_run_0p25").point, 1); mac("dz:12m:maxrun", dm("12m", "1996-2026", "max_run_0p25").point, 0)
mac("dz:12m:corr", dm("12m", "1996-2026", "corr_D_m").point)
STG = [("w_eq", "Equity weights"), ("w_usd", "Dollar weights"), ("w_y10", "10-year weight"), ("scale", "Normalization of the weights"), ("policy", "Policy rate"), ("spread_bbb", "BBB spread"), ("spread_mortgage", "Mortgage spread"), ("house", "House prices")]
rows = []
for k_, lab in STG:
    a = B18[(B18.case == "rstar") & (B18.form == "level") & (B18.stage == k_)].iloc[0]; b = B18[(B18.case == "rstar") & (B18.form == "chg12") & (B18.stage == k_)].iloc[0]
    rows.append([lab, f"{a.share * 100:.0f} [{a.lo * 100:.0f}, {a.hi * 100:.0f}]", f"{b.share * 100:.0f} [{b.lo * 100:.0f}, {b.hi * 100:.0f}]"])
    mac(f"br:lvl:{k_}", a.share * 100, 0); mac(f"br:chg:{k_}", b.share * 100, 0)
table("bridge", "From the Market Index to the FRB/US Index: Shares of the Difference", "tab:bridge", ["Stage", "Level, share of variance (\\%)", "12-month change (\\%)"], rows,
      "Shares of the variance of the FRB/US index (with house prices) less the market index, relative to $r^*$, 1973--2026, attributed to each stage of a bridge between them: the weights on the three common assets, the normalization of the weights, then the contributions that only the FRB/US index has (policy rate, spreads, house prices); both indexes use the same inputs and centering. Intervals (5th to 95th percentile) from bootstrap samples of the announcements and of blocks of months.")
for epn in ("1998-2001", "2004-06", "2022-24"):
    t_ = BE18[(BE18.case == "rstar") & (BE18.form == "level") & (BE18.episode == epn) & (BE18.stage == "total_F_minus_M")]
    if len(t_):
        t_ = t_.iloc[0]; k_ = epn[:4]; mac(f"br:ep{k_}:gap", t_.point); mac(f"br:ep{k_}:lo", t_.lo); mac(f"br:ep{k_}:hi", t_.hi)
        e_ = BE18[(BE18.case == "rstar") & (BE18.form == "level") & (BE18.episode == epn) & (BE18.stage == "w_eq")].iloc[0]; mac(f"br:ep{k_}:eq", e_.point)
        h_ = BE18[(BE18.case == "rstar") & (BE18.form == "level") & (BE18.episode == epn) & (BE18.stage == "house")].iloc[0]; mac(f"br:ep{k_}:house", h_.point)
        u_ = BE18[(BE18.case == "rstar") & (BE18.form == "level") & (BE18.episode == epn) & (BE18.stage == "w_usd")].iloc[0]; mac(f"br:ep{k_}:usd", u_.point)
# composition tests
def pr(o, smp, ff="noff"):
    return P19[(P19.outcome == o) & (P19["sample"] == smp) & (P19.ff == ff)].iloc[0]
rows = []
for o_, lab in (("du", "Unemployment gap, 12 months"), ("gdp", "Real GDP growth, four quarters")):
    for smp, sl in (("main", "1976--2026"), ("1996+", "1996--2026"), ("ex2008-15", "Excluding 2008--15")):
        r = pr(o_, smp)
        rows.append([f"{lab}: {sl}", f"{int(r.n)}", f(r.a_dM), f"{f(r.c_D)} [{f(r.lo90_c)}, {f(r.hi90_c)}]", f"{f(r.effect_p5_p95)} [{f(r.effect_lo90)}, {f(r.effect_hi90)}]"])
        mac(f"cm:{o_}:{smp.replace('+', 'p').replace('-', '')}:c", r.c_D); mac(f"cm:{o_}:{smp.replace('+', 'p').replace('-', '')}:lo", r.lo90_c); mac(f"cm:{o_}:{smp.replace('+', 'p').replace('-', '')}:hi", r.hi90_c)
        mac(f"cm:{o_}:{smp.replace('+', 'p').replace('-', '')}:eff", r.effect_p5_p95); mac(f"cm:{o_}:{smp.replace('+', 'p').replace('-', '')}:efflo", r.effect_lo90); mac(f"cm:{o_}:{smp.replace('+', 'p').replace('-', '')}:effhi", r.effect_hi90)
        mac(f"cm:{o_}:{smp.replace('+', 'p').replace('-', '')}:a", r.a_dM); mac(f"cm:{o_}:{smp.replace('+', 'p').replace('-', '')}:n", r.n, 0)
table("comp", "Does the Composition of a Tightening Matter for the Outlook?", "tab:comp", ["", "$n$", "Index change", "Composition $D$ [90\\%]", "Outlook difference, 5th to 95th percentile [90\\%]"], rows,
      "Local projections of the 12-month-ahead change in the unemployment gap (four-quarter-ahead GDP growth) on own lags, the 12-month change of the market index relative to $r^*$ and the 12-month change of the normalized FRB/US-minus-market difference $D$ computed on the same changes (HAC standard errors, 18 lags; the intervals from block bootstrap are similar). Outlook difference: the coefficient on $D$ times the difference between the 5th and 95th percentiles of $D$ at a given index change, in percentage points of the unemployment gap (percent for GDP). If the FRB/US weights were right, the coefficient on $D$ would equal the coefficient on the index change.")
sp = S19[(S19["sample"] == "main") & (S19.ff == "noff") & (S19.outcome == "du")].set_index("spec")
mac("cm:eq:gain", sp.loc["eq", "gain_adj_r2"], 3); mac("cm:mkt:gain", sp.loc["mkt", "gain_adj_r2"], 3); mac("cm:free:gain", sp.loc["free", "gain_adj_r2"], 3); mac("cm:frbus:gain", sp.loc["frbus", "gain_adj_r2"], 3); mac("cm:y10:gain", sp.loc["y10", "gain_adj_r2"], 3); mac("cm:usd:gain", sp.loc["usd", "gain_adj_r2"], 3)
o_ = OOS19[(OOS19["sample"] == "main") & (OOS19.ff == "noff") & (OOS19.outcome == "du")].set_index("comparison")
mac("cm:eqmkt:dm", o_.loc["equities_vs_market_nonnested", "dm_t"], 1); mac("cm:eqmkt:rmse", o_.loc["equities_vs_market_nonnested", "rmse_ratio"]); mac("cm:frmkt:dm", o_.loc["frbus_weights_vs_market_nonnested", "dm_t"], 1); mac("cm:addD:cw", o_.loc["add_D_to_market", "cw_t"], 1)
pw = PR19[(PR19["sample"] == "main") & (PR19.ff == "noff") & (PR19.outcome == "du")].set_index("null")
mac("cm:prop:wm", pw.loc["w_M", "p_boot"]); mac("cm:prop:wb", pw.loc["w_B", "p_boot"])
rows = []
for tgt, sf_, lab in (("unemployment", "both", "Unemployment, both"), ("unemployment", "D_only", "Unemployment, $D$ alone"), ("unemployment", "market_only", "Unemployment, index change alone"), ("unemployment", "both_ex2008-15", "Unemployment, both, excluding 2008--15"), ("gdp", "both", "GDP, both")):
    for term in ("dM", "D"):
        r = SPF19[(SPF19.target == tgt) & (SPF19.spec == sf_) & (SPF19.term == term)]
        if len(r):
            r = r.iloc[0]; rows.append([f"{lab}: {'index change' if term == 'dM' else 'composition $D$'}", f"{int(r.n)}", f"{f(r.coef)} [{f(r.lo90)}, {f(r.hi90)}]", f(r.t, 1)])
r_ = SPF19[(SPF19.target == "unemployment") & (SPF19.spec == "both") & (SPF19.term == "D")].iloc[0]; mac("cm:spf:c", r_.coef); mac("cm:spf:lo", r_.lo90); mac("cm:spf:hi", r_.hi90); mac("cm:spf:t", r_.t, 1); mac("cm:spf:n", r_.n, 0)
r_ = SPF19[(SPF19.target == "unemployment") & (SPF19.spec == "both_ex2008-15") & (SPF19.term == "D")].iloc[0]; mac("cm:spfx:c", r_.coef); mac("cm:spfx:lo", r_.lo90); mac("cm:spfx:hi", r_.hi90)
r_ = SPF19[(SPF19.target == "unemployment") & (SPF19.spec == "market_only") & (SPF19.term == "dM")].iloc[0]; mac("cm:spf:dm", r_.coef); mac("cm:spf:dm:t", r_.t, 1)
table("spf", "Does the Financial Movement Predict the Forecasters' Error?", "tab:spf", ["", "$n$", "Coefficient [90\\%]", "$t$"], rows,
      "Regression of the realized change in the unemployment rate (real GDP growth) four quarters ahead less the median forecast of the Survey of Professional Forecasters on the 12-month changes of the market index and of $D$, with the financial data up to the month before each survey's deadline, 1990Q3--2025Q3; HAC standard errors, overlapping outcomes. A coefficient of zero means that the movement is already in the forecast. Incremental information only: the test says nothing about causation.")
# episodes
for _, r in EP19[~EP19.episode.str.contains("minus")].iterrows():  # the contrast row would overwrite the 1998 macros
    k_ = r.episode[:4]
    mac(f"ce:{k_}:dm", r.mean_dM); mac(f"ce:{k_}:D", r.mean_D); mac(f"ce:{k_}:contrib", r.contrib_D, 2); mac(f"ce:{k_}:contrib:lo", r.contrib_D_lo90, 2); mac(f"ce:{k_}:contrib:hi", r.contrib_D_hi90, 2)
EF19 = pd.read_csv(RES / "19_episode_fit.csv")
for _, r in EF19.iterrows():
    k_ = r.episode[:4]; mac(f"ce:{k_}:real", r.mean_y); mac(f"ce:{k_}:fcm", r.oos_fc_mkt); mac(f"ce:{k_}:fcf", r.oos_fc_frbus); mac(f"ce:{k_}:fco", r.oos_fc_own)
# figure D
Dm = {}
cs = __import__("lib.cases", fromlist=["inputs"]); X_ = cs.inputs(D, "rstar", rstar="rstar LW"); Xd_ = cs.demean(X_[["y10", "equities", "dollar"]]).loc["1973-01":"2026-09"]
w_M_ = W.weight.values; psi_ = W.response.values; b4_ = FW.frbus_weight.values; wB_ = b4_ / (b4_ @ psi_)
dX_ = Xd_.diff(12); mkt_ = dX_.values @ w_M_; Dd_ = dX_.values @ (wB_ - w_M_)
tt_ = Xd_.index.to_timestamp()
fig, ax = plt.subplots(2, 1, figsize=(7.5, 5.0), sharex=True)
ax[0].plot(tt_, mkt_, color=COLORS["market"], lw=1.2, label="Market-implied reading, 12-month change"); ax[0].plot(tt_, dX_.values @ wB_, color=COLORS["frbus"], lw=1.2, label="Spending-equivalent reading of the same changes, normalized")
ax[0].set_title("The two readings of the same financial movements", loc="left"); axes(ax[0], "points")
ax[1].plot(tt_, Dd_, color=COLORS["fcig"], lw=1.2, label="Difference $D$ (spending-equivalent less market-implied)"); ax[1].axhline(0.25, color="#999999", ls=":", lw=0.8); ax[1].axhline(-0.25, color="#999999", ls=":", lw=0.8)
for a_, b_ in (("1998-01-01", "2001-12-31"), ("2004-06-01", "2006-06-30"), ("2022-03-01", "2024-12-31")):
    for x_ in ax:
        x_.axvspan(pd.Timestamp(a_), pd.Timestamp(b_), color="#eeeeee", lw=0, zorder=0)
ax[1].set_title("The difference", loc="left"); axes(ax[1], "points")
figure("fig_D", fig)
mac("figD:corr", float(np.corrcoef(mkt_[12:], (dX_.values @ wB_)[12:])[0, 1]))

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
chk(float(SC["exp_post2010_n_out_ten"]) == 0 and float(SC["exp_post2010_n_out_usd"]) == 0 and 0 < float(SC["exp_post2010_n_out_eq"]) <= 40 and float(SC["roll_post2010_n_out_ten"]) > 0, "weights: expanding inside the band after 2010 (equity briefly out), rolling fails")
_wp = pd.read_csv(RES / "16_weight_path.csv"); _wb = pd.read_csv(RES / "weights_boot.csv")
_lo, _hi = _wb.w_eq.quantile(0.05), _wb.w_eq.quantile(0.95)
_e = _wp[(_wp.kind == "path") & (_wp.series == "eq") & (_wp.window == "expanding")].copy(); _e["date"] = pd.to_datetime(_e.date)
_out = _e[(_e.date >= "2011-01-01") & ((_e.value < _lo) | (_e.value > _hi))]
chk(len(_out) == int(round(float(SC["exp_post2010_n_out_eq"]))), "weights: the reported count of expanding-window equity weights outside the band equals the count computed from the stored path and draws")
chk(abs(float(SC["base_lo_eq"]) - _lo) < 1e-9 if "base_lo_eq" in SC else True, "weights: band edge equals the 5th percentile of the stored draws")
mac("exp:n", len(_out), 0)
M["exp:first"] = _out.date.min().strftime("%B %Y"); M["exp:last"] = _out.date.max().strftime("%B %Y"); M["abs:exp:first"] = M["exp:first"]; M["abs:exp:last"] = M["exp:last"]
M["abs:exp:n"] = M["exp:n"]
chk(len(_out) > 0 and _out.date.min() >= pd.Timestamp("2011-01-01"), "weights: outside-band dates are after 2010")
S15 = pd.read_csv(RES / "15_summary.csv"); sc_ = S15[(S15.step == "rstar") & (S15.form.str.contains("change|flow")) & (S15.set != "MKT")] if "set" in S15 else S15
chk(float(SC["w_rstar_n_holm_sig10"]) == 0 and float(SC["w_rstar_n_primary_tests"]) == 120 and float(SC["w_rstar_n_raw_sig10"]) == 25, "weights: 25 of 120 raw rejections, none after Holm")
chk(float(SC["lad_rstar_vs_nominal_all_n_ratio_below1"]) == 69 and float(SC["lad_rstar_vs_nominal_all_n_tests"]) == 91 and float(SC["lad_rstar_vs_nominal_all_n_holm_sig05"]) == 0, "ladder: 69 of 91, none after Holm at 5 percent")

num = lambda k: float(str(M[k]).replace("$-$", "-"))
# restrictions, SPF decomposition, daily ladder
RS19 = pd.read_csv(RES / "19_restrictions.csv"); SD19 = pd.read_csv(RES / "19_spf_decomp.csv"); AO20 = pd.read_csv(RES / "20_announce_vs_other.csv"); LD20 = pd.read_csv(RES / "20_ladder.csv")
def rs(o, smp, term, ff="noff"):
    return RS19[(RS19.outcome == o) & (RS19["sample"] == smp) & (RS19.ff == ff) & (RS19.term == term)].iloc[0]
rows = []
for o_, lab in (("gdp", "Real GDP growth over the next four quarters"), ("du", "Change in the unemployment gap over the next 12 months")):
    rows.append((r"\midrule" + "\n" if rows else "") + r"\multicolumn{5}{l}{\textit{" + lab + r"}} \\")
    for smp, sl in (("main", "1976--2026"), ("1996+", "1996--2026"), ("ex2008-15", "Excluding 2008--15")):
        b_, g_, d_ = rs(o_, smp, "beta"), rs(o_, smp, "gamma"), rs(o_, smp, "gamma_minus_beta")
        star = lambda r_: "*" if (r_.lo90 > 0 or r_.hi90 < 0) else ""
        rows.append([sl, f"{int(b_.n)}", f"{f(b_.coef)} [{f(b_.lo90)}, {f(b_.hi90)}]", f"{f(g_.coef)} [{f(g_.lo90)}, {f(g_.hi90)}]{star(g_)}", f"{f(d_.coef)} [{f(d_.lo90)}, {f(d_.hi90)}]{star(d_)}"])
        k_ = o_ + ":" + smp.replace("+", "p").replace("-", "")
        for nm_, r_ in (("beta", b_), ("gamma", g_), ("gmb", d_)):
            mac(f"rs:{k_}:{nm_}", r_.coef); mac(f"rs:{k_}:{nm_}:lo", r_.lo90); mac(f"rs:{k_}:{nm_}:hi", r_.hi90)
table("comp", "Does the Composition of a Tightening Help Predict Activity?", "tab:comp", ["", "$n$", "Market reading, $\\beta$", "Market reading sufficient: $\\gamma=0$", "FRB/US reading sufficient: $\\gamma-\\beta=0$"], rows,
      "Local projections of four-quarter-ahead real GDP growth (quarterly) and of the 12-month-ahead change in the unemployment gap (monthly) on own lags and $\\beta M+\\gamma D$, where $M$ is the 12-month change of the futures-factor market reading and $D$ the FRB/US reading of the same asset changes less $M$, both on the common scale. Brackets are 90 percent intervals (HAC, joint covariance of the coefficients); * marks a restriction rejected at the 10 percent level. If the market reading is a sufficient summary, $\\gamma=0$; if the FRB/US reading $M+D$ is, $\\gamma=\\beta$. The market weights are treated as known. A failure to reject is not evidence for either reading.", align="lrccc", small=False)
mac("rs:nrej:gamma", float(RS19[(RS19.term == "gamma")].reject_hac90.sum()), 0); mac("rs:nrej:gmb", float(RS19[(RS19.term == "gamma_minus_beta")].reject_hac90.sum()), 0); mac("rs:ntests", float(len(RS19[RS19.term == "gamma"])), 0)
def sdc(tgt, smp, comp, term="D"):
    return SD19[(SD19.target == tgt) & (SD19["sample"] == smp) & (SD19.component == comp) & (SD19.term == term)].iloc[0]
rows = []
for tgt, smp, lab in (("unemployment", "all", "Unemployment, 1990--2025"), ("unemployment", "ex2008-15", "Unemployment, excluding 2008--15"), ("gdp", "all", "Real GDP growth, 1990--2025")):
    for comp, cl in (("forecast", "Survey forecast"), ("realized", "Realized"), ("error", "Forecast error")):
        r = sdc(tgt, smp, comp)
        rows.append([f"{lab}: {cl}", f"{int(r.n)}", f"{f(r.coef)} [{f(r.lo90)}, {f(r.hi90)}]", f(r.effect_p5_p95)])
        k_ = {"unemployment": "u", "gdp": "g"}[tgt] + ":" + smp.replace("-", "") + ":" + comp
        mac(f"sd:{k_}", r.coef); mac(f"sd:{k_}:lo", r.lo90); mac(f"sd:{k_}:hi", r.hi90); mac(f"sd:{k_}:eff", r.effect_p5_p95)
for smp_, lab_ in (("ex2001", "Unemployment, excluding 2001"), ("ex2008-09", "Unemployment, excluding 2008--09"), ("ex2001-and-2008-09", "Unemployment, excluding 2001 and 2008--09")):
    for comp, cl in (("realized", "Realized"), ("error", "Forecast error")):
        r = sdc("unemployment", smp_, comp)
        rows.append([f"{lab_}: {cl}", f"{int(r.n)}", f"{f(r.coef)} [{f(r.lo90)}, {f(r.hi90)}]", f(r.effect_p5_p95)])
        k_ = "u:" + smp_.replace("-", "") + ":" + comp
        mac(f"sd:{k_}", r.coef); mac(f"sd:{k_}:lo", r.lo90); mac(f"sd:{k_}:hi", r.hi90); mac(f"sd:{k_}:blo", r.boot_lo90); mac(f"sd:{k_}:bhi", r.boot_hi90)
r = sdc("unemployment", "ex2008-15", "error"); mac("sd:u:ex200815:error:blo", r.boot_lo90); mac("sd:u:ex200815:error:bhi", r.boot_hi90)
r = sdc("unemployment", "all", "error"); mac("sd:u:all:error:blo", r.boot_lo90); mac("sd:u:all:error:bhi", r.boot_hi90)
table("spf", "What the Composition Predicts: Forecasts, Outcomes and Errors", "tab:spf", ["", "$n$", "Coefficient on $D$ [90\\%]", "Effect, 5th to 95th percentile"], rows,
      "Regressions of the Survey of Professional Forecasters' median forecast of the four-quarter-ahead change in the unemployment rate (real GDP growth), the realized change, and the forecast error (realized less forecast) on the 12-month changes of the market index and of $D$, financial data up to the month before each survey's deadline, 1990Q3--2025Q3; the coefficients on the forecast and the error add to the coefficient on the realization. HAC standard errors; effect in percentage points at the same index change. Incremental information only: the test says nothing about causation.")
# daily ladder
rows = []
for k_, lab in ((1, "One day"), (5, "One week"), (22, "22 trading days")):
    a = AO20[(AO20.k == k_) & (AO20.group == "ann") & (AO20.stat == "ratio")].iloc[0]; o = AO20[(AO20.k == k_) & (AO20.group == "other") & (AO20.stat == "ratio")].iloc[0]
    rows.append([lab, f"{f(a.point)} [{f(a.lo)}, {f(a.hi)}]", f"{int(a.n)}", f"{f(o.point)} [{f(o.lo)}, {f(o.hi)}]", f"{int(o.n)}"])
    mac(f"dl:k{k_}:ann", a.point); mac(f"dl:k{k_}:oth", o.point); mac(f"dl:k{k_}:ann:n", a.n, 0); mac(f"dl:k{k_}:oth:n", o.n, 0)
table("daily", "The Difference between the Readings on Announcement Days and Other Days", "tab:daily", ["Horizon", "Announcement windows [90\\%]", "$n$", "Other windows [90\\%]", "$n$"], rows,
      "Mean absolute difference $D$ between the normalized FRB/US reading and the market reading, as a ratio to the mean absolute market move, on the same three assets, 1996--2026 (daily 10-year yield, nominal broad dollar and CAPE; the nominal dollar and no adjustment for $r^*$ stand in for the real dollar and the $r^*$ transformation). Announcement windows end on a scheduled FOMC announcement date; other windows are non-overlapping and contain none. Intervals from joint bootstrap samples of the windows and of the announcements that set the weights.")
for k_ in (1, 5, 22, 66, 252):
    r = LD20[(LD20.series == "total") & (LD20.k == k_) & (LD20.stat == "ratio")].iloc[0]; mac(f"dl:lad{k_}", r.point)
# main exhibit: the three episodes (episodes in columns)
EPS = (("1998", "1998--2001"), ("2004", "2004--06"), ("2022", "2022--24"))
for k_, lab in EPS:
    mac(f"ce:{k_}:fr", num(f"ce:{k_}:dm") + num(f"ce:{k_}:D"))
def ep_row(label, fn):
    return [label] + [fn(k_) for k_, _ in EPS]
g_ = lambda t: r"\midrule" + "\n" + r"\multicolumn{4}{l}{\textit{" + t + r"}} \\"
rows = [g_("Full indexes, average level (points)"),
        ep_row("FRB/US index less market index [90\\% interval]", lambda k: f"{f(num(f'br:ep{k}:gap'))} [{f(num(f'br:ep{k}:lo'))}, {f(num(f'br:ep{k}:hi'))}]"),
        ep_row("\\quad of which: equity weights", lambda k: f(num(f"br:ep{k}:eq"))),
        g_("Same three assets, 12-month change (points)"),
        ep_row("Market-implied reading", lambda k: f(num(f"ce:{k}:dm"))),
        ep_row("Spending-equivalent reading", lambda k: f(num(f"ce:{k}:fr"))),
        ep_row("Difference $D$", lambda k: f(num(f"ce:{k}:D"))),
        g_("Change in the unemployment gap over the next 12 months (points)"),
        ep_row("Realized", lambda k: f(num(f"ce:{k}:real"))),
        ep_row("Forecast from the market-implied reading", lambda k: f(num(f"ce:{k}:fcm"))),
        ep_row("Forecast from the spending-equivalent reading", lambda k: f(num(f"ce:{k}:fcf")))]
table("epmain", "Two Readings of Three Episodes", "tab:epmain", ["", "1998--2001", "2004--06", "2022--24"], rows,
      "Top block: difference in the average levels of the full FRB/US index (with house prices) and the market index relative to $r^*$, in points, and the part that comes from the equity weights (Table~\\ref{tab:bridge}). Middle block: 12-month changes of the market index and of the normalized FRB/US reading, computed on the same three assets and averaged over the episode; $D$ is their difference. Bottom block: change in the unemployment gap over the following 12 months, averaged over the episode's origins, and recursive out-of-sample forecasts of it from the market reading and from the FRB/US reading (own lags included). A gap in levels can coexist with agreement in changes.", align="lccc", small=False)
# ladder on days with the announcement-day moves removed
for k_ in (1, 5, 22, 66, 252):
    r = LD20[(LD20.series == "exann") & (LD20.k == k_) & (LD20.stat == "ratio")].iloc[0]; mac(f"dl:ex{k_}", r.point)

# new figures: the two tightenings, persistence, the matched episode readings

fig, ax = plt.subplots(1, 2, figsize=(7.5, 3.3))
labs_ = ["Persistent", "Half-life\n8 qtrs", "Half-life\n4 qtrs", "Half-life\n2 qtrs"]
pts_ = []; los_ = []; his_ = []
for nm_, hl_ in (("persistent", np.inf), ("hl8", 8.0), ("hl4", 4.0), ("hl2", 2.0)):
    r = MP18[(MP18.h == 4) & (MP18.path == nm_) & (MP18.quantity == "bpsi")].iloc[0]; pts_.append(r.point); los_.append(r.point - r.lo); his_.append(r.hi - r.point)
ax[0].errorbar(range(4), pts_, yerr=[los_, his_], fmt="o", color=COLORS["frbus"], capsize=3)
ax[0].axhline(1.0, color=COLORS["market"], lw=1.2); ax[0].text(3.4, 1.01, "market = 1 by construction", ha="right", va="bottom", fontsize=7.5, color=COLORS["market"])
ax[0].set_xticks(range(4)); ax[0].set_xticklabels(labs_, fontsize=8); ax[0].set_ylim(0.5, 1.2)
ax[0].set_title("FRB/US reading of the typical\npolicy move (funds-rate points)", loc="left", fontsize=9)
rr_ = [num("ag:mp:hlinf"), num("ag:mp:hl8"), num("ag:mp:hl4"), num("ag:mp:hl2")]
ax[1].plot(range(4), rr_, "o", color=COLORS["frbus"]); ax[1].axhline(num("ag:mkt:ratio"), color=COLORS["market"], lw=1.2)
ax[1].text(3.4, num("ag:mkt:ratio") + 0.05, "market", ha="right", va="bottom", fontsize=7.5, color=COLORS["market"])
ax[1].set_xticks(range(4)); ax[1].set_xticklabels(labs_, fontsize=8); ax[1].set_ylim(0, 3.2)
ax[1].set_title("Dollar effect relative to equity effect,\nsame decay for both", loc="left", fontsize=9)
for a_ in ax:
    for sp_ in ("top", "right"): a_.spines[sp_].set_visible(False)
fig.tight_layout(); figure("fig_persist", fig)

# what the assets did in each episode (mean 12-month change) and each asset's part of D
dwt_ = wB_ - w_M_
for k_, a0, b0 in (("1998", "1998-01", "2001-12"), ("2004", "2004-06", "2006-06"), ("2022", "2022-03", "2024-12")):
    sel_ = (Xd_.index >= pd.Period(a0, "M")) & (Xd_.index <= pd.Period(b0, "M")); mdx_ = np.nanmean(dX_.values[sel_], axis=0)
    for j_, nm_ in enumerate(("y10", "eq", "usd")):
        mac(f"ce:{k_}:x{nm_}", mdx_[j_]); mac(f"ce:{k_}:c{nm_}", dwt_[j_] * mdx_[j_])
    chk(abs(float((dwt_ * mdx_).sum()) - num(f"ce:{k_}:D")) < 0.01, f"episode {k_}: asset parts add to D")
# within-episode paths, bootstrap bands for the episode averages, and how often the readings differ
WBd = pd.read_csv(RES / "weights_boot.csv")
def ep_boot(a0, b0):
    sel = (Xd_.index >= pd.Period(a0, "M")) & (Xd_.index <= pd.Period(b0, "M")); X_e = dX_.values[sel]; out = []
    for _, r in WBd.iterrows():
        wm = r[["w_ten", "w_eq", "w_usd"]].values.astype(float); ps = r[["psi_ten", "psi_eq", "psi_usd"]].values.astype(float); wb = b4_ / (b4_ @ ps)
        out.append([np.nanmean(X_e @ wm), np.nanmean(X_e @ wb), np.nanmean(X_e @ (wb - wm))] + list(np.nanmean(X_e * (wb - wm), axis=0)))
    return np.percentile(np.array(out), [5, 95], axis=0)
for k_, a0, b0 in (("1998", "1998-01", "2001-12"), ("2004", "2004-06", "2006-06"), ("2022", "2022-03", "2024-12")):
    q_ = ep_boot(a0, b0)
    for j_, nm_ in enumerate(("dm", "fr", "D", "cy10", "ceq", "cusd")):
        mac(f"ce:{k_}:{nm_}:lo", q_[0, j_]); mac(f"ce:{k_}:{nm_}:hi", q_[1, j_])
    sel_ = (Xd_.index >= pd.Period(a0, "M")) & (Xd_.index <= pd.Period(b0, "M")); mk_e = mkt_[sel_]; fr_e = (dX_.values @ wB_)[sel_]; D_e = Dd_[sel_]
    mac(f"ce:{k_}:opp", float(np.sum(np.sign(mk_e) != np.sign(fr_e))), 0); mac(f"ce:{k_}:nmo", float(sel_.sum()), 0); mac(f"ce:{k_}:big", float(np.sum(np.abs(D_e) > 0.25)), 0)
s96_ = np.asarray(Xd_.index >= pd.Period('1996-01', 'M')); DA_ = np.abs(Dd_[s96_]); MA_ = np.abs(mkt_[s96_])
mac("dz:12m:med", float(np.nanmedian(DA_)), 2); mac("dz:12m:p75", float(np.nanpercentile(DA_, 75)), 2); mac("dz:12m:p90", float(np.nanpercentile(DA_, 90)), 2); mac("dz:12m:bp", float(np.nanmean(DA_)) * 100, 0)
fig, ax = plt.subplots(2, 2, figsize=(7.6, 5.8), sharey="row")
for c_, (k_, a0, b0, lab) in enumerate((("1998", "1997-07", "2002-06", "1998--2001"), ("2022", "2021-09", "2025-06", "2022--24"))):
    sel_ = (Xd_.index >= pd.Period(a0, "M")) & (Xd_.index <= pd.Period(b0, "M")); t_ = tt_[sel_]
    ax[0, c_].plot(t_, mkt_[sel_], color=COLORS["market"], lw=1.3, label="Market-implied reading"); ax[0, c_].plot(t_, (dX_.values @ wB_)[sel_], color=COLORS["frbus"], lw=1.3, label="Spending-equivalent reading")
    ax[0, c_].axhline(0, color="#444444", lw=0.7); ax[0, c_].set_title(lab + ": 12-month change", loc="left", fontsize=9)
    for j_, (nm_, col_, lb_) in enumerate((("y10", "#888888", "10-year yield"), ("eq", "#2a9d4b", "Equity valuation"), ("usd", "#7b4fa0", "Dollar"))):
        ax[1, c_].plot(t_, (dX_.values * dwt_)[sel_][:, j_], color=col_, lw=1.2, label=lb_)
    ax[1, c_].plot(t_, Dd_[sel_], color="#222222", lw=1.4, ls="--", label="Difference $D$")
    ax[1, c_].axhline(0, color="#444444", lw=0.7); ax[1, c_].set_title("Contributions to the difference", loc="left", fontsize=9)
    for r_ in (0, 1):
        ax[r_, c_].axvspan(pd.Timestamp({"1998": "1998-01-01", "2022": "2022-03-01"}[k_]), pd.Timestamp({"1998": "2001-12-31", "2022": "2024-12-31"}[k_]), color="#eeeeee", lw=0, zorder=0)
        for sp_ in ("top", "right"): ax[r_, c_].spines[sp_].set_visible(False)
        ax[r_, c_].tick_params(labelsize=8)
ax[0, 0].legend(frameon=False, fontsize=7.5, loc="upper left")
import matplotlib.dates as mdates_
for a__ in ax.ravel():
    a__.xaxis.set_major_locator(mdates_.YearLocator()); a__.xaxis.set_major_formatter(mdates_.DateFormatter("%Y"))
ax[1, 0].set_ylim(-0.95, 0.85); ax[1, 0].legend(frameon=False, fontsize=6.8, loc="lower left", ncol=2)
ax[0, 0].set_ylabel("Points", fontsize=8); ax[1, 0].set_ylabel("Points", fontsize=8)
figure("fig_paths", fig)
fig, ax = plt.subplots(figsize=(6.2, 3.4))
ks_ = [("1998", "1998--2001"), ("2022", "2022--24")]
xx_ = np.arange(len(ks_)); wd_ = 0.34
m_ = [num(f"ce:{k}:dm") for k, _ in ks_]; r_ = [num(f"ce:{k}:fr") for k, _ in ks_]
b1 = ax.bar(xx_ - wd_ / 2, m_, wd_, color=COLORS["market"], label="Market-implied reading"); b2 = ax.bar(xx_ + wd_ / 2, r_, wd_, color=COLORS["frbus"], label="Spending-equivalent reading")
for bars_ in (b1, b2):
    for r0 in bars_:
        h0 = r0.get_height(); ax.text(r0.get_x() + r0.get_width() / 2, h0 + (0.03 if h0 >= 0 else -0.03), f"{h0:+.2f}", ha="center", va="bottom" if h0 >= 0 else "top", fontsize=8)
for j_, (nm_, off_) in enumerate((("dm", -wd_ / 2), ("fr", wd_ / 2))):
    v_ = [num(f"ce:{k}:{nm_}") for k, _ in ks_]; lo_ = [num(f"ce:{k}:{nm_}:lo") for k, _ in ks_]; hi_ = [num(f"ce:{k}:{nm_}:hi") for k, _ in ks_]
    ax.errorbar(xx_ + off_, v_, yerr=[np.array(v_) - np.array(lo_), np.array(hi_) - np.array(v_)], fmt="none", ecolor="#222222", capsize=3, lw=1)
ax.axhline(0, color="#444444", lw=0.8); ax.set_xticks(xx_); ax.set_xticklabels([l for _, l in ks_])
ax.set_ylabel("Average 12-month change, points"); ax.set_ylim(-0.6, 1.5); ax.legend(frameon=False, fontsize=8, loc="upper left")
for sp_ in ("top", "right"): ax.spines[sp_].set_visible(False)
figure("fig_episodes", fig)
# FRB/US expenditure channels (step 22; results stored, the step needs the Board's FRB/US package and is not in run_all)
SC22 = pd.read_csv(RES / "scalars_22_channels.csv", header=None, index_col=0)[1]
g22 = lambda k: float(SC22[k])
mac("ch:gdp:eq", g22("equity:persistent:gdp_q4"), 3); mac("ch:gdp:usd", g22("dollar:persistent:gdp_q4"), 3)
mac("ch:eq:cons", 100 * g22("equity:persistent:Consumption:share_q4"), 0); mac("ch:eq:bfi", 100 * g22("equity:persistent:Business fixed investment:share_q4"), 0)
mac("ch:eq:dom", 100 * g22("equity:persistent:domestic_share_q4"), 0); mac("ch:eq:nx", 100 * g22("equity:persistent:netexports_share_q4"), 0)
mac("ch:usd:exp", 100 * g22("dollar:persistent:Exports:share_q4"), 0); mac("ch:usd:imp", 100 * g22("dollar:persistent:Imports:share_q4"), 0)
mac("ch:usd:nx", 100 * g22("dollar:persistent:netexports_share_q4"), 0); mac("ch:usd:dom", 100 * g22("dollar:persistent:domestic_share_q4"), 1)
mac("ch:eq:cons4", 100 * g22("equity:halflife4:Consumption:share_q4"), 0); mac("ch:usd:nx4", 100 * g22("dollar:halflife4:netexports_share_q4"), 0)
mac("ch:eq:inv", 100 * g22("equity:persistent:Inventories:share_q4"), 0); mac("ch:eq:gov", 100 * g22("equity:persistent:Government:share_q4"), 0)
mac("ch:usd:inv", 100 * g22("dollar:persistent:Inventories:share_q4"), 0); mac("ch:usd:gov", 100 * g22("dollar:persistent:Government:share_q4"), 0)
mac("ch:replay:ffr", g22("replay:ffr_points_q4"), 3)
for k_, nm_ in (("10-year yield", "ten"), ("Equity valuation", "eq"), ("Dollar", "usd")):
    mac(f"ch:replay:{nm_}", 100 * g22(f"replay:{k_}:share"), 0); mac(f"ch:hike:{nm_}", 100 * g22(f"hike_spill:{k_}:share_of_hike_gdp"), 0)
FP22 = pd.read_csv(RES / "22_figure_persistent.csv")
fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.5), sharey=True)
grp_ = (("Consumption", ["Consumption"], "#2a9d4b"), ("Investment", ["Residential investment", "Business fixed investment"], "#1f4e9c"), ("Inventories", ["Inventories"], "#bbbbbb"),
        ("Government", ["Government"], "#d9a441"), ("Net exports", ["Exports", "Imports"], "#d95f02"))
for a_, (ex_, ttl_) in zip(ax, (("equity", "Equity valuation falls 5 log points"), ("dollar", "Dollar appreciates 3.9 log points"))):
    d_ = FP22[(FP22.experiment == ex_) & (FP22.quarter <= 16)]; q_ = d_.quarter.values; pos_ = np.zeros(len(q_)); neg_ = np.zeros(len(q_))
    for nm_, cols_, col_ in grp_:
        v_ = d_[cols_].sum(axis=1).values; b_ = np.where(v_ >= 0, pos_, neg_)
        a_.bar(q_, v_, bottom=b_, color=col_, width=0.8, label=nm_); pos_ = pos_ + np.where(v_ >= 0, v_, 0); neg_ = neg_ + np.where(v_ < 0, v_, 0)
    a_.plot(q_, d_.gdp.values, color="#111111", lw=1.6, label="GDP"); a_.axhline(0, color="#444444", lw=0.7); a_.set_title(ttl_, loc="left", fontsize=9); a_.set_xlabel("Quarters", fontsize=8)
    a_.tick_params(labelsize=8)
    for sp_ in ("top", "right"): a_.spines[sp_].set_visible(False)
ax[0].set_ylabel("Percent of GDP", fontsize=8); ax[0].legend(frameon=False, fontsize=7, loc="lower left", ncol=2)
figure("fig_channels", fig)
chk(num("ch:eq:cons") > 80 and num("ch:usd:nx") > 80 and abs(num("ch:usd:dom")) < 5, "channels: consumption carries the equity effect, net exports the dollar effect")
# policy-signal sensitivity (step 21)
SC21 = pd.read_csv(RES / "scalars_21_signal.csv", index_col=0)["value"]; D21 = pd.read_csv(RES / "21_defs.csv"); E21 = pd.read_csv(RES / "21_episodes.csv"); G21 = pd.read_csv(RES / "21_disagreement.csv"); S21 = pd.read_csv(RES / "21_signal_content.csv"); SB21 = pd.read_csv(RES / "21_signal_content_both.csv")
DEF21 = (("baseline", "base", "Futures factor"), ("two_year", "two", "Two-year yield"), ("to_2019", "t19", "Factor, through 2019"), ("no_lower_bound", "nlb", "Factor, no lower bound"))
c21 = lambda k: float(SC21[k])
def dq(d_, q_): return float(D21[(D21.definition == d_) & (D21.quantity == q_)].point.iloc[0])
def e21(d_, ep_, q_):
    r = E21[(E21.definition == d_) & (E21.episode == ep_) & (E21.quantity == q_)].iloc[0]; return r
def g21(d_, st_):
    r = G21[(G21.definition == d_) & (G21["sample"] == "12m_changes_1996_2026") & (G21.stat == st_)].iloc[0]; return r
fx_ = lambda x, d=2: f(x, d)
iv_ = lambda a, lo, hi, d=2: f"{f(c21(a), d)} [{f(c21(lo), d)}, {f(c21(hi), d)}]"
cols_ = {}
for d_, k_, lab_ in DEF21:
    mac(f"sg:{k_}:n", dq(d_, "n_announcements"), 0)
    for nm_ in ("ten", "eq", "usd"): mac(f"sg:{k_}:w{nm_}", c21(f"{d_}_wM_{nm_}"), 3)
    for nm_ in ("bpsi", "ror", "ratio_mkt", "contrast_diff"):
        dd3_ = 3 if nm_ == "contrast_diff" else 2
        mac(f"sg:{k_}:{nm_}", c21(f"{d_}_{nm_}"), dd3_); mac(f"sg:{k_}:{nm_}:lo", c21(f"{d_}_{nm_}_lo"), dd3_); mac(f"sg:{k_}:{nm_}:hi", c21(f"{d_}_{nm_}_hi"), dd3_)
    mac(f"sg:{k_}:cm", c21(f"{d_}_contrast_mkt")); mac(f"sg:{k_}:cf", c21(f"{d_}_contrast_fr"))
    mac(f"sg:{k_}:d12", g21(d_, "ratio").point)
    for ep_, ek_ in (("1998-2001", "98"), ("2022-24", "22")):
        for q_, qn_ in (("market", "m"), ("frbus", "f"), ("D", "D")):
            r = e21(d_, ep_, q_); mac(f"sg:{k_}:{ek_}{qn_}", r.point); mac(f"sg:{k_}:{ek_}{qn_}:lo", r.lo); mac(f"sg:{k_}:{ek_}{qn_}:hi", r.hi)
    cols_[d_] = [f"{int(dq(d_, 'n_announcements'))}", f(c21(f"{d_}_wM_ten"), 3), f(c21(f"{d_}_wM_eq"), 3), f(c21(f"{d_}_wM_usd"), 3),
                 iv_(f"{d_}_bpsi", f"{d_}_bpsi_lo", f"{d_}_bpsi_hi", 3), iv_(f"{d_}_ratio_mkt", f"{d_}_ratio_mkt_lo", f"{d_}_ratio_mkt_hi"), iv_(f"{d_}_ror", f"{d_}_ror_lo", f"{d_}_ror_hi"),
                 f(c21(f"{d_}_contrast_mkt")), f(c21(f"{d_}_contrast_fr")), iv_(f"{d_}_contrast_diff", f"{d_}_contrast_diff_lo", f"{d_}_contrast_diff_hi", 3), f(g21(d_, "ratio").point),
                 f(e21(d_, "1998-2001", "market").point), f(e21(d_, "1998-2001", "frbus").point), f(e21(d_, "1998-2001", "D").point),
                 f(e21(d_, "2022-24", "market").point), f(e21(d_, "2022-24", "frbus").point), f(e21(d_, "2022-24", "D").point)]
labs_ = ["Announcements", "Market weight, 10-year yield", "Market weight, equity valuation", "Market weight, dollar", "Model reading of the usual response, $b_4'\\psi$ [90\\%]", "Market dollar-over-equity ratio [90\\%]", "Ratio of ratios [90\\%]",
         "Dollar-minus-equity effect, market (points)", "Dollar-minus-equity effect, FRB/US (points, normalized for each signal)", "Model less market [90\\%]", "Mean $|D|$ over mean $|$market move$|$, 12-month changes"]
# main text: the two signals on the same announcements (market weights; readings of the two movements of Figure 1)
for d_, k_, _ in DEF21[:2]:
    mac(f"sg:{k_}:eqf", c21(f"{d_}_eq_fr"), 3); mac(f"sg:{k_}:usdf", c21(f"{d_}_usd_fr"), 3)
rows = []
for i_ in (0, 1, 2, 3, 5):
    rows.append([labs_[i_]] + [cols_[d_][i_] for d_, _, _ in DEF21[:2]])
rows.append(r"\midrule" + "\n" + r"\multicolumn{3}{l}{\textit{Readings of the two movements of Figure~\ref{fig:four}}} \\")
rows.append(["Equity valuation falls 5 log points, market (points)"] + [f(c21(f"{d_}_eq_mkt"), 3) for d_, _, _ in DEF21[:2]])
rows.append(["Dollar appreciates 3.9 log points, market (points)"] + [f(c21(f"{d_}_usd_mkt"), 3) for d_, _, _ in DEF21[:2]])
rows.append(["Equity valuation falls, FRB/US (points, normalized for each signal)"] + [f(c21(f"{d_}_eq_fr"), 3) for d_, _, _ in DEF21[:2]])
rows.append(["Dollar appreciates, FRB/US (points, normalized for each signal)"] + [f(c21(f"{d_}_usd_fr"), 3) for d_, _, _ in DEF21[:2]])
for i_ in (7, 8, 9, 6, 4):
    rows.append([labs_[i_]] + [cols_[d_][i_] for d_, _, _ in DEF21[:2]])
table("signal", "Two Measures of Policy News on the Same Announcements", "tab:signal", [""] + [l for _, _, l in DEF21[:2]], rows,
      "The market weights are estimated on the same 253 announcement windows with two measures of policy news: the first principal component of the futures-based factor of \\citet{nakamura2018} (baseline) and the change in the two-year yield. The model weights are those of Table~\\ref{tab:frbus} in both columns, normalized by $b_4'\\psi$ for each measure. Effects are for the movements of Figure~\\ref{fig:four}, in points of the two-year yield; the FRB/US effects are divided by $b_4'\\psi$ computed with each signal's response vector, so this table's normalization changes with the signal, unlike the common futures-factor normalization of Tables~\\ref{tab:fourw} and~\\ref{tab:dist} (Table~\\ref{tab:example} gives the FRB/US effects in funds-rate points). Intervals are 5th and 95th percentiles over 5,000 bootstrap samples of the announcements, on common draws. Table~\\ref{tab:signalsens} adds the two sample checks.", align="lcc", small=False)
# appendix: all four definitions, no episodes
rows = [[l_] + [cols_[d_][i_] for d_, _, _ in DEF21] for i_, l_ in enumerate(labs_)]
table("signalsens", "Policy-News Definitions and Event Samples", "tab:signalsens", [""] + [l for _, _, l in DEF21], rows,
      "The market weights are re-estimated for each definition of policy news: the first principal component of the futures-based factor of \\citet{nakamura2018} (baseline), the change in the two-year yield in the same 253 announcement windows, the factor through 2019, and the factor outside the lower-bound years. The model weights are those of Table~\\ref{tab:frbus} in every column, normalized by $b_4'\\psi$ for each definition. Effects are for the movements of Figure~\\ref{fig:four} (equity valuation down 5 log points, dollar up 3.9 log points), in points of the two-year yield; the FRB/US effects are divided by $b_4'\\psi$ and so are on the common two-year-yield scale. Intervals are 5th and 95th percentiles over 5,000 bootstrap samples of the announcements, on common draws.", align="lcccc", small=False)
# history: episode readings under each definition (one home for the episode readings)
rows = [r"\multicolumn{5}{l}{\textit{1998--2001, average 12-month change}} \\"]
for i_, l_ in ((11, "Market-implied reading"), (12, "Spending-equivalent reading"), (13, "Difference $D$")): rows.append([l_] + [cols_[d_][i_] for d_, _, _ in DEF21])
rows.append(r"\midrule" + "\n" + r"\multicolumn{5}{l}{\textit{2022--24, average 12-month change}} \\")
for i_, l_ in ((14, "Market-implied reading"), (15, "Spending-equivalent reading"), (16, "Difference $D$")): rows.append([l_] + [cols_[d_][i_] for d_, _, _ in DEF21])
table("epdef", "Episode Readings under Each Definition of Policy News", "tab:epdef", [""] + [l for _, _, l in DEF21], rows,
      "Averages of the 12-month changes in the three assets relative to $r^*$ over the months of each episode, read with the market weights of each definition (points of the two-year yield) and with the FRB/US weights normalized for the same definition (points on the common two-year-yield scale); $D$ is the difference. Baseline intervals are in the text and in Table~\\ref{tab:epmain}.", align="lcccc", small=False)
mac("pr:two:contrast:bp", 100 * abs(float(pd.read_csv(RES / "25_proportionality.csv").pipe(lambda PR_: PR_[(PR_.definition == "two_year") & (PR_.quantity == "contrast_diff")]).diff_vs_baseline.iloc[0])), 0)
# what variation each signal captures
sc_ = lambda a_, r_: SB21[(SB21.asset == a_)]
for k_, v_ in (("sig:corr", c21("sig_corr_ns_2y")), ("sig:res", c21("sd_2y_residual_share") * 100)):
    mac(k_, v_, 2 if k_ == "sig:corr" else 0)
for a_ in ("eq", "usd", "ten"):
    for nm_, key_ in (("ns", f"both_{a_}_t_ns"), ("2y", f"both_{a_}_t_2y")):
        mac(f"sig:t:{a_}:{nm_}", c21(key_), 1)
mac("sig:cf:psi", c21("cfstep_w_eq_psi_shapley"), 3); mac("sig:cf:sig", c21("cfstep_w_eq_sigma_shapley"), 3)
mac("sg:pair:two:ror", c21("pair_two_year_ror")); mac("sg:pair:two:ror:lo", c21("pair_two_year_ror_lo")); mac("sg:pair:two:ror:hi", c21("pair_two_year_ror_hi"))
mac("fg:fcig", c21("fcig_ratio_usd_eq")); mac("fg:frbus", c21("frbus_ratio_usd_eq")); mac("fg:base", c21("fcig_baseline_ror")); mac("fg:two", c21("fcig_two_year_ror")); mac("fg:t19", c21("fcig_to_2019_ror")); mac("fg:nlb", c21("fcig_no_lower_bound_ror"))
for k_ in ("base", "two"): pass
# expenditure components (step 23)
X23 = pd.read_csv(RES / "23_expenditure.csv")
def x23(smp, o_, t_): return X23[(X23["sample"] == smp) & (X23.outcome == o_) & (X23.term == t_)].iloc[0]
rows = []
for smp, sl in (("main", "1976--2026"), ("1996+", "1996--2026")):
    for o_, ol in (("net_exports", "Net exports"), ("private_domestic", "Consumption and private investment")):
        for t_, tl in (("dM", "index change $\\beta$"), ("D", "composition $\\gamma$")):
            r = x23(smp, o_, t_)
            rows.append([f"{ol}, {sl}: {tl}", f"{int(r.n)}", f"{f(r.coef)} [{f(r.lo90)}, {f(r.hi90)}]", f"[{f(r.boot_lo90)}, {f(r.boot_hi90)}]", f(r.effect)])
            k_ = f"{o_[:3]}:{smp.replace('+', 'p')}:{t_}"; mac(f"ex:{k_}", r.coef); mac(f"ex:{k_}:lo", r.lo90); mac(f"ex:{k_}:hi", r.hi90); mac(f"ex:{k_}:blo", r.boot_lo90); mac(f"ex:{k_}:bhi", r.boot_hi90); mac(f"ex:{k_}:eff", r.effect)
    r = x23(smp, "dom_minus_net", "D"); rows.append([f"Consumption and investment less net exports, {sl}: $\\gamma$", f"{int(r.n)}", f(r.coef), f"[{f(r.boot_lo90)}, {f(r.boot_hi90)}]", f(r.effect)])
    k_ = f"dmn:{smp.replace('+', 'p')}"; mac(f"ex:{k_}", r.coef); mac(f"ex:{k_}:blo", r.boot_lo90); mac(f"ex:{k_}:bhi", r.boot_hi90)
table("expend", "Composition and the Expenditure Components of Growth", "tab:expend", ["", "$n$", "Coefficient [90\\% HAC]", "Bootstrap 90\\%", "Effect, 5th to 95th percentile"], rows,
      "Local projections of the mean contribution to real GDP growth (percentage points, annualized) of net exports and of consumption plus private investment over the next four quarters on own lags, the 12-month change of the market index and the 12-month change of $D$ (Section~\\ref{sec:onetest}); quarterly origins, HAC standard errors with 6 lags, 8-quarter block bootstrap with common draws for the two outcomes. Predictions stated from the channel logic before the components were estimated: the coefficient on $D$ is negative for net exports (P1) and larger for domestic demand than for net exports (P2). Effect: coefficient times the 5th-to-95th percentile range of $D$ at a given index change.")
chk(x23("main", "net_exports", "D").boot_hi90 < 0 and x23("main", "net_exports", "D").hi90 < 0, "expenditure: net-export coefficient on D negative with intervals below zero in the main sample")
chk(x23("1996+", "net_exports", "D").coef < 0 and x23("1996+", "net_exports", "D").hi90 > 0, "expenditure: 1996+ net-export coefficient negative, HAC interval includes zero")
for d_, k_, _ in DEF21:
    mac(f"sg:{k_}:eqm", c21(f"{d_}_eq_mkt"), 3); mac(f"sg:{k_}:usdm", c21(f"{d_}_usd_mkt"), 3)
fig, ax = plt.subplots(figsize=(6.6, 3.5))
xx_ = np.arange(2); wd_ = 0.26
series_ = (("Market-implied, futures factor", COLORS["market"], [num("ag:ex:eq:mkt"), num("ag:ex:usd:mkt")]), ("Market-implied, two-year yield", "#7fa6d9", [c21("two_year_eq_mkt"), c21("two_year_usd_mkt")]),
           ("Spending-equivalent (FRB/US)", COLORS["frbus"], [num("ag:ex:eq:fr"), num("ag:ex:usd:fr")]))
for j_, (lab_, col_, v_) in enumerate(series_):
    bars_ = ax.bar(xx_ + (j_ - 1) * wd_, v_, wd_, color=col_, label=lab_)
    for r_ in bars_: ax.text(r_.get_x() + r_.get_width() / 2, r_.get_height() + 0.005, f"{r_.get_height():.2f}", ha="center", va="bottom", fontsize=8)
ax.set_xticks(xx_); ax.set_xticklabels(["Equity valuation\nfalls 5 log points", "Dollar appreciates\n3.9 log points"])
ax.set_ylabel("Points (market: two-year yield; model: funds rate)", fontsize=8); ax.set_ylim(0, 0.5); ax.legend(frameon=False, fontsize=8, loc="upper left")
for sp_ in ("top", "right"): ax.spines[sp_].set_visible(False)
figure("fig_two", fig)
# step 25: what the two signals capture, monthly agreement, direct test of the market weights' relative proportion
SC25 = pd.read_csv(RES / "scalars_25_months.csv", index_col=0)["value"]; c25 = lambda k: float(SC25[k])
SP25 = pd.read_csv(RES / "25_signal_split.csv"); MC25 = pd.read_csv(RES / "25_monthly_classes.csv"); PR25 = pd.read_csv(RES / "25_proportionality.csv"); MP25 = pd.read_csv(RES / "25_market_proportion.csv")
mac("sp:resvar", 100 * c25("split_resid_var_share"), 0); mac("sp:resvar:lo", 100 * c25("split_resid_var_share_lo"), 0); mac("sp:resvar:hi", 100 * c25("split_resid_var_share_hi"), 0); mac("sp:ressd", 100 * c25("split_resid_sd_share"), 0)
for _, r in SP25.iterrows():
    kk_ = f"sp:{r.asset}:{'F' if r.component == 'futures_factor' else 'R'}"; mac(kk_, r.response, 2); mac(kk_ + ":lo", r.lo, 2); mac(kk_ + ":hi", r.hi, 2)
fig, axs = plt.subplots(2, 3, figsize=(7.2, 5.0))
tt_ = {"ten": "10-year yield\n(points per point)", "eq": "S&P 500\n(percent per point)", "usd": "Dollar (DXY)\n(percent per point)"}
for a_, ax_ in zip(("ten", "eq", "usd"), axs[0]):
    for j_, (cmp_, lab_, col_) in enumerate((("futures_factor", "Futures\nfactor", COLORS["market"]), ("two_year_residual", "Two-year change\noutside the factor", "#7fa6d9"))):
        r = SP25[(SP25.asset == a_) & (SP25.component == cmp_)].iloc[0]
        ax_.errorbar([j_], [r.response], yerr=[[r.response - r.lo], [r.hi - r.response]], fmt="o", color=col_, capsize=3)
    ax_.axhline(0, color="#444444", lw=0.7); ax_.set_xlim(-0.6, 1.6); ax_.set_xticks([0, 1]); ax_.set_xticklabels(["Futures\nfactor", "Residual"], fontsize=8); ax_.set_title(tt_[a_], loc="left", fontsize=8.5)
    for sp_ in ("top", "right"): ax_.spines[sp_].set_visible(False)
def d21row(d_, q_): return D21[(D21.definition == d_) & (D21.quantity == q_)].iloc[0]
for ax_, q_, ttl_ in ((axs[1][0], "wM_eq", "Market weight, equity valuation"), (axs[1][1], "wM_usd", "Market weight, dollar"), (axs[1][2], "ratio_mkt", "Dollar effect over equity effect,\nmarket weights")):
    for j_, (d_, col_) in enumerate((("baseline", COLORS["market"]), ("two_year", "#7fa6d9"))):
        r = d21row(d_, q_); ax_.errorbar([j_], [r.point], yerr=[[r.point - r.lo], [r.hi - r.point]], fmt="o", color=col_, capsize=3)
    ax_.axhline(0, color="#444444", lw=0.7); ax_.set_xlim(-0.6, 1.6); ax_.set_xticks([0, 1]); ax_.set_xticklabels(["Futures\nfactor", "Two-year\nyield"], fontsize=8); ax_.set_title(ttl_, loc="left", fontsize=8.5)
    for sp_ in ("top", "right"): ax_.spines[sp_].set_visible(False)
axs[1][2].set_ylim(-5, 12)
fig.tight_layout(); figure("fig_signal", fig)
for _, r in MP25.iterrows():
    k_ = {"two_year": "two", "to_2019": "t19", "no_lower_bound": "nlb"}[r.signal_b]
    mac(f"tp:{k_}", r["T"], 4); mac(f"tp:{k_}:lo", r.lo, 4); mac(f"tp:{k_}:hi", r.hi, 4); mac(f"tp:{k_}:pos", 100 * r.share_positive, 0)
    mac(f"tp:{k_}:rr", r.ratio_b_over_a, 2); mac(f"tp:{k_}:rr:lo", r.ratio_lo, 2); mac(f"tp:{k_}:rr:hi", r.ratio_hi, 2); mac(f"tp:{k_}:rr:pos", 100 * r.share_ratio_gt1, 0)
for d_, k_, _ in DEF21:
    for q_ in ("cross", "contrast_diff"):
        r = PR25[(PR25.definition == d_) & (PR25.quantity == q_)].iloc[0]; dd_ = 4 if q_ == "cross" else 2
        mac(f"pr:{k_}:{q_}", r.point, dd_); mac(f"pr:{k_}:{q_}:lo", r.lo, dd_); mac(f"pr:{k_}:{q_}:hi", r.hi, dd_)
        if d_ != "baseline": mac(f"pr:{k_}:{q_}:d", r.diff_vs_baseline, dd_); mac(f"pr:{k_}:{q_}:dlo", r.diff_lo, dd_); mac(f"pr:{k_}:{q_}:dhi", r.diff_hi, dd_); mac(f"pr:{k_}:{q_}:dpos", 100 * r.share_diff_positive, 0)
MCb = MC25[MC25.definition == "baseline"]
def mc_(per_, t_, cat_): return MCb[(MCb.period == per_) & (np.isclose(MCb.threshold, t_)) & (MCb.category == cat_)].iloc[0]
rows = []
CATL = {"agree": "Same sign", "near_zero": "Opposite signs, at least one reading within $t$ of zero", "opposing": "Opposite signs, both readings at least $t$", "big_gap": "Readings differ by at least $t$"}
for t_ in (0.10, 0.25):
    rows.append(r"\midrule" + "\n" + r"\multicolumn{4}{l}{\textit{Threshold $t$ = %s point}} \\" % f"{t_:.2f}")
    for cat_ in ("agree", "near_zero", "opposing", "big_gap"):
        row_ = [CATL[cat_]]
        for per_ in ("all", "1998-2001", "2022-24"):
            r = mc_(per_, t_, cat_); tk_ = int(round(t_ * 100)); pk_ = per_.replace("-", "")
            mac(f"mo:{pk_}:{tk_}:{cat_}", 100 * r.share, 1); mac(f"mo:{pk_}:{tk_}:{cat_}:lo", 100 * r.lo, 0); mac(f"mo:{pk_}:{tk_}:{cat_}:hi", 100 * r.hi, 0); mac(f"mo:{pk_}:{tk_}:{cat_}:n", r.n_count, 0)
            row_.append(f"{int(r.n_count)} ({f(100 * r.share, 1)}\\%) [{f(100 * r.lo, 0)}, {f(100 * r.hi, 0)}]")
        rows.append(row_)
rows.insert(0, ["Months", "369", "48", "34"])
for per_, pk_ in (("all", "all"), ("1998-2001", "19982001"), ("2022-24", "202224")):
    mac(f"mo:{pk_}:n", float(MCb[MCb.period == per_].n_months.iloc[0]), 0); mac(f"mo:{pk_}:maxgap", c25(f"mo_{per_}_max_abs_gap"), 2); mac(f"mo:{pk_}:meangap", c25(f"mo_{per_}_mean_abs_gap"), 2)
mac("mo:mat:n", c25("mo_all_material_n"), 0); mac("mo:mat:same", 100 * c25("mo_all_material_same_sign"), 1); mac("mo:mat:gaplt", 100 * c25("mo_all_material_gap_lt_025"), 0)
for d_, k_, _ in DEF21:
    for t_, tk_ in ((0.10, 10), (0.25, 25)):
        for cat_ in ("opposing", "big_gap", "agree"):
            r = MC25[(MC25.definition == d_) & (MC25.period == "all") & np.isclose(MC25.threshold, t_) & (MC25.category == cat_)].iloc[0]
            mac(f"mo:{k_}:{tk_}:{cat_}", 100 * r.share, 1); mac(f"mo:{k_}:{tk_}:{cat_}:n", r.n_count, 0); mac(f"mo:{k_}:{tk_}:{cat_}:lo", 100 * r.lo, 0); mac(f"mo:{k_}:{tk_}:{cat_}:hi", 100 * r.hi, 0)
table("months", "How Often the Two Readings Differ", "tab:months", ["", "1996--2026", "1998--2001", "2022--24"], rows,
      "Monthly 12-month changes in the three market variables (relative to $r^*$), read with the baseline market weights and with the FRB/US weights on the market's scale (points of the two-year yield). Each cell gives the number of months, the share of months, and the 5th to 95th percentile of the share over announcement-bootstrap draws of the market weights (the 12-month changes are held fixed; months overlap). 1996--2026 is 369 months, 1998--2001 is 48 and 2022--24 is 34.", align="lrrr")
chk(c25("mo_all_t25_opposing") < c25("mo_all_t25_big_gap") and c25("mo_all_t25_agree") > 0.8, "months: opposing readings rare, large gaps common (baseline weights)")
chk(c25("mo_2022-24_t25_opposing") == 0 and c25("mo_2022-24_t10_opposing") == 0, "months: no materially opposing readings in 2022-24")
_pr = lambda d_, q_: PR25[(PR25.definition == d_) & (PR25.quantity == q_)].iloc[0]
chk(_pr("baseline", "contrast_diff").lo > 0 and _pr("two_year", "contrast_diff").lo < 0 < _pr("two_year", "contrast_diff").hi, "signal: baseline contrast interval excludes zero (5,000 draws), two-year interval includes zero")
chk(_pr("baseline", "cross").hi < 0 and _pr("two_year", "cross").lo < 0 < _pr("two_year", "cross").hi, "signal: cross-product excludes zero for the futures factor and includes zero for the two-year yield")
chk(_pr("two_year", "contrast_diff").diff_lo < 0 < _pr("two_year", "contrast_diff").diff_hi, "signal: paired change in the contrast (two-year less factor) includes zero")
chk(MP25.iloc[0].lo < 0 < MP25.iloc[0].hi and MP25.iloc[0].share_positive > 0.9 and MP25.iloc[0].ratio_b_over_a > 1.5, "signal: direct test of the market weights: T positive in over 90 percent of draws, interval includes zero, ratio of market ratios above 1.5")
chk(0.15 < c25("split_resid_var_share") < 0.25 and SP25[(SP25.asset == "eq") & (SP25.component == "two_year_residual")].iloc[0].lo < 0 < SP25[(SP25.asset == "eq") & (SP25.component == "two_year_residual")].iloc[0].hi, "signal: remainder is about one-fifth of the variance of the two-year change and its equity response includes zero")
chk(0.8 < float(G21[(G21.definition == "baseline") & (G21["sample"] == "12m_changes_1996_2026") & (G21.stat == "ratio")].point.iloc[0]) / float(pd.read_csv(RES / "scalars_24_signal_outcomes.csv", index_col=0)["value"]["nb_market_two_year_vs_baseline"]) < 1.25, "the measure of policy news moves the reading about as much as the choice of weights (0.33 against 0.37)")
chk(c25("mo_1998-2001_t25_near_zero_n") + c25("mo_1998-2001_t25_opposing_n") == 7 and c25("mo_1998-2001_t25_big_gap_n") == 21 and 0.7 < c25("mo_1998-2001_max_abs_gap") < 0.8, "months: 1998-2001 signs differ in 7 of 48 months, gap of 0.25 in 21; largest gap 0.76 (Jan 1998)")
# step 26: four calibrations on common assets and units
SC26 = pd.read_csv(RES / "scalars_26_four_way.csv", index_col=0)["value"]
def c26(k):
    v = SC26[k]
    try: return float(v)
    except ValueError: return v
F26 = pd.read_csv(RES / "26_fig1.csv").set_index("portfolio"); H26 = pd.read_csv(RES / "26_history.csv").set_index("stat")
E26 = pd.read_csv(RES / "26_episodes.csv"); O26 = pd.read_csv(RES / "26_opposing_months.csv")
PN = {"F": "Market, futures factor", "G": "Published GS weights", "Y": "Market, two-year yield", "B": "FRB/US"}
PORD = ["F", "G", "Y", "B"]
for k in PORD:
    r = F26.loc[k]; mac(f"fw:fig:{k}", r.dollar_over_equity); mac(f"fw:eq:{k}", r.eq_reading, 2); mac(f"fw:usd:{k}", r.usd_reading, 2)
    for nm_, v_ in (("ten", r.w_ten), ("weq", r.w_eq), ("wusd", r.w_usd)): mac(f"fw:{nm_}:{k}", v_, 3)
    if k in ("F", "Y"): mac(f"fw:fig:{k}:lo", r.lo); mac(f"fw:fig:{k}:hi", r.hi)
mac("fw:gsraw", c26("gs_ratio_raw")); mac("fw:wYpsiF", c26("wY_on_psiF"), 3)
fig, ax = plt.subplots(figsize=(7.0, 3.4))
xx_ = np.arange(4); wd_ = 0.38
eqv = [F26.loc[k].eq_reading for k in PORD]; usv = [F26.loc[k].usd_reading for k in PORD]
b1 = ax.bar(xx_ - wd_ / 2, eqv, wd_, color="#9db7d5", label="Equity valuation falls 5 log points")
b2 = ax.bar(xx_ + wd_ / 2, usv, wd_, color="#1f4e9c", label="Dollar appreciates 3.9 log points")
for bb_ in list(b1) + list(b2): ax.text(bb_.get_x() + bb_.get_width() / 2, bb_.get_height() + 0.005, f"{bb_.get_height():.3f}", ha="center", va="bottom", fontsize=7)
for j_, k in enumerate(PORD): ax.text(j_, 0.47, f"ratio {F26.loc[k].dollar_over_equity:.2f}", ha="center", fontsize=8)
ax.set_xticks(xx_); ax.set_xticklabels(["Market,\nfutures factor", "Published GS\nweights", "Market,\ntwo-year yield", "FRB/US"], fontsize=8)
ax.set_ylabel("Points on the common two-year-yield scale", fontsize=8); ax.set_ylim(0, 0.52); ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=2)
for sp_ in ("top", "right"): ax.spines[sp_].set_visible(False)
figure("fig_four", fig)
chk(abs(c26("fig1_F") - 1) < 0.05 and abs(c26("fig1_G") - 1) < 0.1 and c26("fig1_Y") > 1.8 and c26("fig1_B") > 2.2, "four-way: futures factor and GS near one, two-year yield and FRB/US above two (Figure 1)")
# distance matrix
for a_ in PORD:
    for b_ in PORD:
        if a_ >= b_: continue
k_pair = lambda a_, b_: next(f"{x}{y}" for x, y in ((a_, b_), (b_, a_)) if f"mad_{x}{y}" in H26.index)
rows = []
for a_ in PORD:
    row_ = [PN[a_]]
    for b_ in PORD:
        if a_ == b_: row_.append("--"); continue
        kk_ = k_pair(a_, b_); d_ = H26.loc[f"mad_{kk_}"]; r_ = H26.loc[f"ratio_{kk_}"]
        row_.append(f"{f(100 * d_.point, 0)} ({f(r_.point)})")
        mac(f"fw:mad:{kk_}", 100 * d_.point, 0); mac(f"fw:ratio:{kk_}", r_.point); mac(f"fw:ratio:{kk_}:lo", r_.lo); mac(f"fw:ratio:{kk_}:hi", r_.hi)
        mac(f"fw:mad:{kk_}:lo", 100 * d_.lo, 0); mac(f"fw:mad:{kk_}:hi", 100 * d_.hi, 0)
    rows.append(row_)
table("dist", "How Far Apart Are the Four Readings?", "tab:dist", [""] + [PN[k] for k in PORD], rows,
      "Mean absolute difference between two readings of the same 12-month changes in the three assets relative to $r^*$, monthly, January 1996 to September 2026 (369 months), in basis points of the two-year yield; in parentheses, the same divided by the mean absolute reading of the market index with the futures factor (the common denominator). Every portfolio is normalized to read one on the futures-factor response to policy news, so that the distances reflect relative weights. Published GS weights: the U.S. weights on the 10-year yield, equities and the dollar, applied to the same series, with the GS policy-rate and spread terms held fixed. Intervals over 5,000 bootstrap draws of the announcements are in the text.", align="lcccc", small=False)
for nm_ in ("madFB_minus_madFY", "madBG_minus_madFB"):
    r_ = H26.loc[nm_]; mac(f"fw:{nm_.replace('_', '')}", 100 * r_.point, 0); mac(f"fw:{nm_.replace('_', '')}:lo", 100 * r_.lo, 0); mac(f"fw:{nm_.replace('_', '')}:hi", 100 * r_.hi, 0)
chk(H26.loc["mad_FG"].point < min(H26.loc[f"mad_{k}"].point for k in ("FY", "FB", "YB", "YG", "BG")), "four-way: the closest pair is F-G (cross-method)")
chk(H26.loc["madFB_minus_madFY"].lo < 0 < H26.loc["madFB_minus_madFY"].hi, "four-way: |B-F| vs |Y-F| ranking not distinguishable")
# judgments
J_ = [("all_same_sign", "All four readings have the same sign"), ("any_opposing_t10", "At least two materially opposing readings, $t$ = 10 bp"), ("any_opposing_t25", "At least two materially opposing readings, $t$ = 25 bp"),
      ("range_ge_t10", "Four-reading range at least 10 bp"), ("range_ge_t25", "Four-reading range at least 25 bp"), ("opp_FB_t25", "Market (futures factor) and FRB/US materially opposing, $t$ = 25 bp")]
rows = []
for k_, l_ in J_:
    r_ = H26.loc[k_]; rows.append([l_, f"{f(100 * r_.point, 1)}", f"[{f(100 * r_.lo, 1)}, {f(100 * r_.hi, 1)}]", f"{int(round(r_.point * c26('n_months')))}"])
    mac(f"fw:{k_.replace('_', ':')}", 100 * r_.point, 1); mac(f"fw:{k_.replace('_', ':')}:lo", 100 * r_.lo, 1); mac(f"fw:{k_.replace('_', ':')}:hi", 100 * r_.hi, 1); mac(f"fw:{k_.replace('_', ':')}:n", r_.point * c26("n_months"), 0)
table("four", "How Often the Four Readings Give Different Judgments", "tab:four", ["", "Percent of months", "90\\% interval", "Months"], rows,
      "Monthly 12-month changes in the three assets relative to $r^*$, January 1996 to September 2026 (369 months, overlapping), read with the four portfolios on the common two-year-yield scale. Materially opposing: at least one reading at least $t$ above zero and at least one at least $t$ below zero. Four-reading range: the largest less the smallest of the four readings. Intervals: 5th and 95th percentiles over 5,000 bootstrap draws of the announcements (market weights and the common response vector redrawn; FRB/US and GS weights fixed), conditional on the observed history.", align="lrrr", small=False)
mac("fw:nmonths", c26("n_months"), 0); mac("fw:opp25:n", c26("opp25_n"), 0); mac("fw:opp10:n", c26("opp10_n"), 0)
chk(int(c26("opp25_n")) == int(round(H26.loc["any_opposing_t25"].point * c26("n_months"))), "four-way: listed opposing months equal the computed share")
# the opposing months at 25 bp
o25 = O26[np.isclose(O26.threshold, 0.25)]
def mk_(v):
    t_ = f(v); return t_ + ("$^{+}$" if v >= 0.25 else "$^{-}$" if v <= -0.25 else "")
rows = [[pd.Period(r_.month, "M").strftime("%b %Y")] + [mk_(r_[k]) for k in PORD] for _, r_ in o25.iterrows()]
table("opp", "The Months of Materially Opposing Readings", "tab:opp", ["Month"] + [PN[k] for k in PORD], rows,
      "Twelve-month change in financial conditions under each portfolio, in points on the common two-year-yield scale (normalized to the futures-factor response), in the months in which at least one reading is at least 0.25 above zero ($^{+}$) and at least one at least 0.25 below zero ($^{-}$).", align="lrrrr", small=False)
nB_alone = int(sum((r_.tight == "B") for _, r_ in o25.iterrows())); nsplit = int(sum((set(r_.tight.split(",")) == {"F", "G"}) for _, r_ in o25.iterrows()))
mac("fw:opp25:Balone", nB_alone, 0); mac("fw:opp25:FGtight", nsplit, 0)
chk(nB_alone + nsplit == len(o25), "four-way: the opposing months are FRB/US alone tighter, or F and G tighter")
_ba = o25[o25.tight == "B"]; _fg = o25[o25.tight.apply(lambda x: set(x.split(",")) == {"F", "G"})]
chk((_ba.d_usd > 10).all() and (_ba.d_eq > 10).all() and (_ba.d_y10 < 0).all(), "four-way: FRB/US-alone months have the dollar up more than 10 percent, valuations up more than 10 percent and the 10-year yield down")
chk((_fg.d_eq < -20).all() and (_fg.d_usd < 0).all(), "four-way: F-and-G-tight months have valuations down more than 20 percent and the dollar down")
# episodes, four readings
for ep_ in ("1998-2001", "2022-24", "2004-06", "2008-09"):
    for k in PORD: mac(f"fw:ep:{ep_.replace('-', '')}:{k}", float(E26[(E26.episode == ep_) & (E26.portfolio == k)]["mean"].iloc[0]))
    mac(f"fw:ep:{ep_.replace('-', '')}:range", c26(f"ep_{ep_}_range_mean")); mac(f"fw:ep:{ep_.replace('-', '')}:opp", c26(f"ep_{ep_}_opp25"), 0)
for i_ in range(1, 4): mac(f"fw:topyear:{i_}", c26(f"top_year_{i_}"), 0); mac(f"fw:topyear:{i_}:range", c26(f"top_year_{i_}_range"))
chk(min(float(E26[(E26.episode == "2022-24") & (E26.portfolio == k)]["mean"].iloc[0]) for k in PORD) > 0.9, "four-way: every calibration shows about one point or more of tightening in 2022-24")
for k_, v_ in SC26.items():
    if str(k_).startswith("acc_"): mac("ac:" + str(k_)[4:].replace("_", ":"), float(v_), 2)
for k_ in ("corr_min", "corr_max", "corr_FB", "corr_FG", "sd_F", "sd_Y", "sd_B", "sd_G"): mac("fw:" + k_.replace("_", ":"), c26(k_))
for k_, v_ in SC26.items():
    if str(k_).startswith(("peak_", "dBF_", "dFB_", "range_ep")):
        if str(k_).endswith("_month"): M["fw:" + str(k_).replace("_", ":")] = str(v_)
        else: mac("fw:" + str(k_).replace("_", ":"), float(v_), 0 if str(k_).endswith("_n25") else 2)
DI19 = pd.read_csv(RES / "19_dist.csv")
for o_ in ("du", "gdp"):
    r_ = DI19[(DI19.outcome == o_) & (DI19["sample"] == "main")].iloc[0]
    mac(f"pw:{o_}:sdM", r_.sd_dM); mac(f"pw:{o_}:sdD", r_.sd_D); mac(f"pw:{o_}:sdDperp", r_.sd_Dperp); mac(f"pw:{o_}:corr", r_.corr_dM_D)
chk(c26("corr_min") > 0.9, "four-way: the four readings are highly correlated (above 0.9) although their sizes differ")
chk(all(abs(sum(c26(f"acc_jan1998_{k}_{a}") for a in ("y10", "eq", "usd")) - c26(f"acc_jan1998_{k}_total")) < 1e-9 for k in PORD) and c26("acc_jan1998_B_total") > 0.25 and max(c26(f"acc_jan1998_{k}_total") for k in ("F", "Y", "G")) < -0.25, "January 1998: contributions add to the readings; FRB/US tightening, the other three easing, each beyond 25 bp")
chk(c26("acc_jan1998_x_usd") > 10 and c26("acc_jan1998_x_eq") > 10 and c26("acc_jan1998_x_y10") < 0, "January 1998: dollar and valuations up more than 10, yield relative to r* down")
chk(c26("acc_ep200809_x_eq") < -30 and abs(c26("acc_ep200809_x_usd")) < 1 and c26("acc_ep200809_x_y10") > 0 and c26("acc_ep200809_F_eq") - c26("acc_ep200809_B_eq") > 0.5, "2008-09: equities dominate; the equity term alone separates the futures-factor and FRB/US readings by more than half a point")
chk(abs(c26("acc_ep202224_B_total") - c26("acc_ep202224_F_total")) < 0.02 and c26("acc_ep202224_B_eq") < c26("acc_ep202224_F_eq") and c26("acc_ep202224_B_usd") > c26("acc_ep202224_F_usd") and min(c26(f"acc_ep202224_{k}_{a}") for k in PORD for a in ("y10", "eq", "usd")) > 0, "2022-24: all three assets tighten under every calibration; equity and dollar differences offset between the futures-factor and FRB/US readings")
chk(c26("peak_ep202224_month") == "October 2022" and c26("peak_ep200809_month") == "March 2009", "peak months of the 12-month change")
chk(abs(float(DI19[(DI19.outcome == "gdp") & (DI19["sample"] == "main")].sd_Dperp.iloc[0]) / float(DI19[(DI19.outcome == "gdp") & (DI19["sample"] == "main")].sd_dM.iloc[0]) - 0.2) < 0.03, "outcome test: composition orthogonal to the market reading has about a fifth of the reading's standard deviation")
# F-B pair opposing months versus any pair
MO26 = pd.read_csv(RES / "26_monthly.csv")
def _opp(a_, b_, t_): return ((np.sign(MO26[a_]) != np.sign(MO26[b_])) & (np.minimum(MO26[a_].abs(), MO26[b_].abs()) >= t_))
fb25, fb10 = int(_opp("F", "B", 0.25).sum()), int(_opp("F", "B", 0.10).sum())
mac("fw:fb25:n", fb25, 0); mac("fw:fb10:n", fb10, 0)
chk(fb25 == int(c26("opp25_n")) and set(MO26.month[_opp("F", "B", 0.25)]) == set(o25.month), "four-way: at 25 bp the four calibrations add no opposing month to the futures-factor/FRB/US pair")
chk(2 * fb10 == int(c26("opp10_n")), "four-way: at 10 bp the four calibrations double the opposing months of the pair")
# four normalized weight vectors (Table 1): three rows, with intervals for the estimated market weights
D21b = pd.read_csv(RES / "21_defs.csv")
def wint_(d_, q_):
    r_ = D21b[(D21b.definition == d_) & (D21b.quantity == q_)].iloc[0]; return f" [{f(r_.lo, 3)}, {f(r_.hi, 3)}]"
rows = []
for lab_, col_, q_ in (("10-year yield (per percentage point)", "w_ten", "wM_ten"), ("Equity valuation (per log point)", "w_eq", "wM_eq"), ("Dollar (per log point)", "w_usd", "wM_usd")):
    rows.append([lab_, f(F26.loc["F"][col_], 3) + wint_("baseline", q_), f(F26.loc["G"][col_], 3), f(F26.loc["Y"][col_], 3) + wint_("two_year", q_), f(F26.loc["B"][col_], 3)])
table("fourw", "Four Sets of Weights on One Scale", "tab:fourw", [""] + [PN[k] for k in PORD], rows,
      "Weights on the three assets relative to $r^*$, each set normalized to read one on the response of the three assets to one unit of futures-factor policy news (the common two-year-yield scale). Market weights: generalized least squares on 253 announcement windows, with policy news measured by the futures factor or by the change in the two-year yield; brackets are 90 percent intervals over 5,000 bootstrap draws of the announcements (for the two-year-yield weights, of the weights on their own signal, which differ from the entries by a factor of \\bl{fw:wYpsiF}). FRB/US: effects on GDP after four quarters of persistent shifts. Published GS weights: the U.S.\\ weights on the 10-year yield, equities and the dollar, with the GS policy-rate and spread terms held fixed. The FRB/US and GS weights are not estimated here.", align="lcccc", small=False)
# four-column episode table
EPW = (("2008-09", "January 2008 to December 2009"), ("1998-2001", "January 1998 to December 2001"), ("2022-24", "March 2022 to December 2024"))
rows = []
for ep_, win_ in EPW:
    vals_ = [float(E26[(E26.episode == ep_) & (E26.portfolio == k)]["mean"].iloc[0]) for k in PORD]
    rows.append([f"{ep_.replace('-', '--')} ({win_})"] + [f(v) for v in vals_] + [f(c26(f"ep_{ep_}_range_mean")), f"{int(c26(f'ep_{ep_}_opp25'))}"])
table("ep4", "Four Readings of Three Episodes", "tab:ep4", ["Episode (months)"] + [PN[k] for k in PORD] + ["Mean range", "Opposing months"], rows,
      "Average over the months of each episode of the 12-month change in financial conditions under each portfolio, in points on the common two-year-yield scale (normalized to the futures-factor response). Mean range: average over the months of the largest less the smallest reading. Opposing months: months with at least one reading at least 0.25 above zero and one at least 0.25 below. The readings use the 10-year yield, equity valuation and the dollar only; corporate spreads, which the published GS index and the full FRB/US index contain, are held fixed.", align="lrrrrrr", small=False)
# figure: four readings month by month in three windows
fig, ax = plt.subplots(1, 3, figsize=(7.6, 3.3), sharey=False)
CL = {"F": COLORS["market"], "Y": "#7fa6d9", "B": COLORS["frbus"], "G": COLORS["gs"]}
MO26["date"] = pd.PeriodIndex(MO26.month, freq="M").to_timestamp()
for a_, (w0, w1, s0, s1, ttl) in zip(ax, (("2006-07", "2011-06", "2008-01", "2009-12", "2008--09"), ("1996-07", "2002-12", "1998-01", "2001-12", "1998--2001"), ("2020-07", "2026-09", "2022-03", "2024-12", "2022--24"))):
    m_ = MO26[(MO26.month >= w0) & (MO26.month <= w1)]
    for k in PORD: a_.plot(m_.date, m_[k], color=CL[k], lw=1.3, label=PN[k])
    a_.axvspan(pd.Timestamp(s0 + "-01"), pd.Timestamp(s1 + "-28"), color="#eeeeee", lw=0, zorder=0); a_.axhline(0, color="#444444", lw=0.6)
    a_.set_title(ttl, loc="left", fontsize=9); a_.tick_params(labelsize=7)
    for sp_ in ("top", "right"): a_.spines[sp_].set_visible(False)
import matplotlib.dates as mdates_
for a_ in ax: a_.xaxis.set_major_locator(mdates_.YearLocator(2)); a_.xaxis.set_major_formatter(mdates_.DateFormatter("%Y"))
ax[0].set_ylabel("Points, common scale", fontsize=8)
h_, l_ = ax[0].get_legend_handles_labels(); fig.legend(h_, l_, loc="upper center", ncol=4, frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, 1.0))
fig.tight_layout(rect=[0, 0, 1, 0.88]); fig.savefig(REP / "fig_ep4.pdf"); plt.close(fig)
# GS-input check (step 27)
SC27 = pd.read_csv(RES / "scalars_27_gs_inputs.csv", index_col=0)["value"].astype(float); c27 = lambda k: float(SC27[k])
SETL = (("rstar", "Relative to $r^*$ (paper)"), ("real_cape", "Real, 100 ln CAPE"), ("gs_inputs", "Nominal, 100 ln CAPE, nominal dollar"))
rows = [r"\multicolumn{4}{l}{\textit{Mean absolute distance between two readings (basis points)}} \\"]
for a_, b_ in (("F", "G"), ("F", "B"), ("Y", "B"), ("F", "Y"), ("B", "G"), ("Y", "G")):
    rows.append([f"{PN[a_]} vs {PN[b_]}"] + [f(100 * c27(f"{sn}_mad_{a_}{b_}"), 0) for sn, _ in SETL])
    for sn, _ in SETL: mac(f"gi:{sn}:{a_}{b_}", 100 * c27(f"{sn}_mad_{a_}{b_}"), 0)
rows.append(r"\midrule" + "\n" + r"\multicolumn{4}{l}{\textit{Judgments across the four readings, 369 months}} \\")
for k_, l_, sc_ in (("all_same_sign", "All four the same sign (percent of months)", 100), ("any_opp_t25", "Months with materially opposing readings, 25 basis points", 369), ("any_opp_t10", "Months with materially opposing readings, 10 basis points", 369),
                    ("range_ge_t25", "Four-reading range at least 25 basis points (percent of months)", 100)):
    rows.append([l_] + [f(sc_ * c27(f"{sn}_{k_}"), 1 if sc_ == 100 else 0) for sn, _ in SETL])
    for sn, _ in SETL: mac(f"gi:{sn}:{k_.replace('_', ':')}", sc_ * c27(f"{sn}_{k_}"), 1 if sc_ == 100 else 0)
rows.append(r"\midrule" + "\n" + r"\multicolumn{4}{l}{\textit{Average reading, January 2008 to December 2009 (points)}} \\")
for k in PORD:
    rows.append([PN[k]] + [f(c27(f"{sn}_ep_2008-09_{k}")) for sn, _ in SETL])
    for sn, _ in SETL: mac(f"gi:{sn}:ep0809:{k}", c27(f"{sn}_ep_2008-09_{k}"))
table("gsin", "Four Readings of History", "tab:gsin", [""] + [l for _, l in SETL], rows,
      "Twelve-month changes in the 10-year yield, equity valuation and the dollar, monthly, January 1996 to September 2026 (369 overlapping months), read with the four sets of weights of Table~\\ref{tab:fourw}. Each column applies all four sets, unchanged, to the same series: the paper's series relative to $r^*$; the real 10-year yield, 100 times the log of the cyclically adjusted price-earnings ratio (prices over a 10-year average of earnings, the documented GS equity concept) and the real dollar; and the nominal 10-year yield, the same equity measure and the nominal broad dollar, the nearest publicly reproducible GS inputs. Distances are mean absolute differences between two readings in basis points of the two-year yield; the mean absolute futures-factor reading is \\bl{gi:rstar:meanF} basis points in the first column. Materially opposing: at least one reading at least the threshold above zero and one at least the threshold below. Range: the largest less the smallest reading. Corporate spreads are held fixed. Intervals for the first column are in the text.", align="lccc", small=False)
mac("gi:rstar:meanF", 100 * c27("rstar_mean_abs_F"), 0)
for sn, _ in SETL:
    mac(f"gi:{sn}:fgnear", 100 * c27(f"{sn}_FG_minus_nearest"), 0); mac(f"gi:{sn}:fgnear:lo", 100 * c27(f"{sn}_FG_minus_nearest_lo"), 0); mac(f"gi:{sn}:fgnear:hi", 100 * c27(f"{sn}_FG_minus_nearest_hi"), 0)
chk(all(c27(f"{sn}_mad_FG") < min(c27(f"{sn}_mad_{p_}") for p_ in ("FY", "FB", "YB", "YG", "BG")) for sn, _ in SETL), "GS inputs: F-G is the closest pair under all three input sets")
chk(all(max(c27(f"{sn}_mad_FY"), c27(f"{sn}_mad_BG")) >= c27(f"{sn}_mad_FB") for sn, _ in SETL), "GS inputs: a within-method distance is at least the F-B distance under all three input sets")
chk(all(c27(f"{sn}_FG_minus_nearest_lo") < 0 < c27(f"{sn}_FG_minus_nearest_hi") for sn, _ in SETL), "GS inputs: paired interval for F-G less the nearest other pair includes zero")
# policy-rate experiment in FRB/US (step 22_policy_shock)
SC22p = pd.read_csv(RES / "scalars_22_policy_shock.csv", index_col=0)["value"]; p22 = lambda k: float(SC22p[k])
for k_ in ("ten", "eq", "usd"):
    mac(f"ps:q1:{k_}", p22(f"move_over_psi_q1:{k_}")); mac(f"ps:pr:{k_}", 100 * p22(f"priced_share:{k_}"), 0)
mac("ps:rem", 100 * p22("remainder_share"), 0); mac("ps:gdp", p22("gdp_q4")); mac("ps:ffr", p22("ffr_equivalent_q4")); mac("ps:replay", p22("replay_ffr_points")); mac("ps:hl", p22("rff_halflife_quarters"), 1)
mac("ps:size", p22("shock_size_rffintay_aerr"), 2); mac("ps:lin", 100 * p22("linearity_gdp_q4_rel"), 1)
PT = pd.read_csv(RES / "scalars_22_policy_shock.csv", index_col=0)["value"]
# the sensitivity band: episode readings over four definitions of policy news and four persistence assumptions
WP = pd.read_csv(RES / "22_weights_by_persistence.csv"); WP = WP[WP.h == 4].set_index("path")
PATHS_ = (("persistent", "Persistent"), ("hl8", "Half-life 8"), ("hl4", "Half-life 4"), ("hl2", "Half-life 2"))
psi21 = lambda d_: np.array([dq(d_, "psi_ten"), dq(d_, "psi_eq"), dq(d_, "psi_usd")]); wm21 = lambda d_: np.array([dq(d_, "wM_ten"), dq(d_, "wM_eq"), dq(d_, "wM_usd")])
BAND = {}
for k_, a0, b0 in (("1998", "1998-01", "2001-12"), ("2004", "2004-06", "2006-06"), ("2022", "2022-03", "2024-12")):
    sel_ = (Xd_.index >= pd.Period(a0, "M")) & (Xd_.index <= pd.Period(b0, "M")); mdx_ = np.nanmean(dX_.values[sel_], axis=0)
    mk_ = {d_: float(wm21(d_) @ mdx_) for d_, _, _ in DEF21}
    sp_ = {(d_, pa_): float((WP.loc[pa_, ["b_ten", "b_eq", "b_usd"]].values.astype(float) @ mdx_) / (WP.loc[pa_, ["b_ten", "b_eq", "b_usd"]].values.astype(float) @ psi21(d_))) for d_, _, _ in DEF21 for pa_, _ in PATHS_}
    BAND[k_] = (mk_, sp_)
    mac(f"bd:{k_}:mlo", min(mk_.values())); mac(f"bd:{k_}:mhi", max(mk_.values())); mac(f"bd:{k_}:flo", min(sp_.values())); mac(f"bd:{k_}:fhi", max(sp_.values()))
    mac(f"bd:{k_}:fsig:lo", min(sp_[(d_, "persistent")] for d_, _, _ in DEF21)); mac(f"bd:{k_}:fsig:hi", max(sp_[(d_, "persistent")] for d_, _, _ in DEF21))
    mac(f"bd:{k_}:fper:lo", min(sp_[("baseline", pa_)] for pa_, _ in PATHS_)); mac(f"bd:{k_}:fper:hi", max(sp_[("baseline", pa_)] for pa_, _ in PATHS_))
chk(abs(BAND["1998"][1][("baseline", "persistent")] - num("ce:1998:fr")) < 0.005 and abs(BAND["2022"][0]["baseline"] - num("ce:2022:dm")) < 0.005, "band: baseline cell reproduces the episode readings")
fig, ax = plt.subplots(figsize=(7.0, 3.6))
for e_, (k_, lab_) in enumerate((("1998", "1998--2001"), ("2022", "2022--24"))):
    mk_, sp_ = BAND[k_]
    ax.scatter([e_ * 1.0 - 0.18 + 0.02 * i for i in range(len(mk_))], list(mk_.values()), color=COLORS["market"], s=26, alpha=0.55, zorder=3, label="Market-implied (four definitions of policy news)" if e_ == 0 else None)
    ax.scatter([e_ * 1.0 - 0.18 + 0.02 * 0], [mk_["baseline"]], color=COLORS["market"], s=60, zorder=4, edgecolor="black", label="Baseline" if e_ == 0 else None)
    xs_ = [e_ * 1.0 + 0.14 + 0.02 * i for i in range(len(sp_))]
    ax.scatter(xs_, list(sp_.values()), color=COLORS["frbus"], s=26, alpha=0.55, zorder=3, label="Spending-equivalent (four definitions $\\times$ four persistence assumptions)" if e_ == 0 else None)
    ax.scatter([xs_[0]], [sp_[("baseline", "persistent")]], color=COLORS["frbus"], s=60, zorder=4, edgecolor="black")
for e_, k_ in enumerate(("1998", "2022")):
    for nm_, xo_ in (("dm", e_ - 0.18), ("fr", e_ + 0.14)):
        v_ = num(f"ce:{k_}:{nm_}"); ax.plot([xo_, xo_], [num(f"ce:{k_}:{nm_}:lo"), num(f"ce:{k_}:{nm_}:hi")], color="#222222", lw=1.1, zorder=2)
ax.axhline(0, color="#444444", lw=0.8); ax.set_xticks([-0.02, 0.98]); ax.set_xticklabels(["1998--2001", "2022--24"]); ax.set_xlim(-0.5, 1.5)
ax.set_ylabel("Average 12-month change, points"); ax.legend(frameon=False, fontsize=7.5, loc="upper left")
for sp__ in ("top", "right"): ax.spines[sp__].set_visible(False)
figure("fig_band", fig)
# step 24: null benchmark, outcomes under each definition, split of D
SC24 = pd.read_csv(RES / "scalars_24_signal_outcomes.csv", index_col=0)["value"]; c24 = lambda k: float(SC24[k]); O24 = pd.read_csv(RES / "24_signal_outcomes.csv")
mac("nb:med", c24("nb_within_market_median")); mac("nb:lo", c24("nb_within_market_lo")); mac("nb:hi", c24("nb_within_market_hi"))
mac("nb:two", c24("nb_market_two_year_vs_baseline")); mac("nb:t19", c24("nb_market_to_2019_vs_baseline")); mac("nb:nlb", c24("nb_market_no_lower_bound_vs_baseline")); mac("nb:fr", c24("nb_frbus_vs_market_baseline"))
def o24(d_, o_, t_): return O24[(O24.definition == d_) & (O24.outcome == o_) & (O24.term == t_)].iloc[0]
rows = []
for d_, k_, lab_ in DEF21:
    row = [lab_]
    for o_ in ("unemployment", "gdp", "net_exports"):
        r = o24(d_, o_, "D"); g_ = o24(d_, o_, "gamma_minus_beta"); row.append(f"{f(r.coef)} [{f(r.lo90)}, {f(r.hi90)}]"); row.append(f"{f(g_.coef)} [{f(g_.lo90)}, {f(g_.hi90)}]" if o_ != "net_exports" else "")
        mac(f"so:{k_}:{o_[:3]}:g", r.coef); mac(f"so:{k_}:{o_[:3]}:glo", r.lo90); mac(f"so:{k_}:{o_[:3]}:ghi", r.hi90); mac(f"so:{k_}:{o_[:3]}:gb", g_.coef); mac(f"so:{k_}:{o_[:3]}:gblo", g_.lo90); mac(f"so:{k_}:{o_[:3]}:gbhi", g_.hi90)
    rows.append(row[:1] + [row[1], row[2], row[3], row[4], row[5]])
table("sigout", "Composition and Outcomes under Each Definition of Policy News", "tab:sigout", ["", "Unemployment, $\\gamma$", "$\\gamma-\\beta$", "GDP growth, $\\gamma$", "$\\gamma-\\beta$", "Net exports, $\\gamma$"], rows,
      "Coefficient on the composition term $D$ (and its difference from the coefficient on the market index change) in the regressions of Sections~\\ref{sec:onetest} and~\\ref{sec:expend}, 1976--2026, with $D$ and the market index change computed with the market weights of each definition of policy news and the model weights normalized by that definition's $b_4'\\psi$; HAC 90 percent intervals.", align="lccccc", small=True)
for t_, nm_ in (("D_ten", "ten"), ("D_eq", "eq"), ("D_usd", "usd")):
    r = o24("baseline_split", "net_exports", t_); mac(f"so:split:{nm_}", r.coef); mac(f"so:split:{nm_}:lo", r.lo90); mac(f"so:split:{nm_}:hi", r.hi90)
for t_ in ("deq", "dusd", "dy10"):
    r = o24("baseline_free", "net_exports", t_); mac(f"so:free:{t_}", r.coef, 3); mac(f"so:free:{t_}:lo", r.lo90, 3); mac(f"so:free:{t_}:hi", r.hi90, 3)
s76_ = np.asarray(Xd_.index >= pd.Period("1976-03", "M")) & np.isfinite(dX_.values).all(axis=1)
mac("so:corr:eq", float(np.corrcoef(Dd_[s76_], dX_.values[s76_, 1])[0, 1])); mac("so:corr:usd", float(np.corrcoef(Dd_[s76_], dX_.values[s76_, 2])[0, 1]))
WPall = pd.read_csv(RES / "22_weights_by_persistence.csv"); mac("bp:min", float(WPall.bpsi.min())); mac("bp:max", float(WPall.bpsi.max()))
mac("bd:2022:fper:spread", BAND["2022"][1][("baseline", "persistent")] - min(BAND["2022"][1][("baseline", pa_)] for pa_, _ in PATHS_), 3); mac("bd:1998:fper:spread", max(BAND["1998"][1][("baseline", pa_)] for pa_, _ in PATHS_) - min(BAND["1998"][1][("baseline", pa_)] for pa_, _ in PATHS_), 3)
chk(c24("nb_within_market_median") > 0.2 and c24("nb_frbus_vs_market_baseline") < 0.4, "null benchmark: within-market weight noise (median 0.2+) comparable to the FRB/US-vs-market ratio")
chk(all(c21(f"{d_}_ror") > 1 for d_, _, _ in DEF21) and c21("two_year_ror") < c21("baseline_ror") < c21("to_2019_ror"), "signal: direction of the contrast the same in all four definitions; size varies (1.2 to 3.6)")
chk(all(abs(c21(f"{d_}_contrast_fr") - 0.25) < 0.03 for d_, _, _ in DEF21), "signal: model contrast 0.24 to 0.26 points under every definition")
chk(all(e21(d_, "1998-2001", "market").point < 0 < e21(d_, "1998-2001", "frbus").point for d_, _, _ in DEF21), "signal: 1998-2001 opposite signs under every definition")
chk(num("ce:1998:dm") < 0 < num("ce:1998:fr") and abs(num("ce:2022:dm") - num("ce:2022:fr")) < 0.05, "episodes: 1998-2001 readings have opposite signs; 2022-24 readings within 0.05")
chk(all(0.2 < num(f"dl:lad{k_}") < 0.4 and 0.2 < num(f"dl:ex{k_}") < 0.4 for k_ in (1, 5, 22, 66, 252)), "ladder: all-days and ex-announcement ratios between 0.2 and 0.4")

# ------------------------------------------------------------------ claims of the agreement paper
bp4 = w18(4, "bpsi"); chk(num("ag:bp:hl4:hi") < 1 and num("ag:bp:hl4") < 0.9, "decaying paths (half-life 4 quarters): typical response below one, interval excludes one")
chk(bp4.lo < 1 < bp4.hi and 0.9 < bp4.point < 1.05, "agreement: FRB/US typical response near one, interval includes one at four quarters")
chk(all(w18(h_, "bpsi").lo < 1 < w18(h_, "bpsi").hi for h_ in (2, 4, 8)), "agreement on announcements not rejected at 2, 4, 8 quarters")
chk(de("share_gt_0p25").point == 0 and de("ratio_mean_abs").point < 0.25, "held-out announcements: difference never above 0.25, ratio below 0.25")
chk(0.25 < dm("12m", "1996-2026", "ratio_mean_abs").point < 0.4 and dm("12m", "1996-2026", "share_gt_0p25").point > 0.3, "12-month changes: ratio about a third, above 0.25 in more than 30 percent of months")
chk(ex18(4, "frbus_over_market", "ratio_of_ratios").lo > 1 and ex18(2, "frbus_over_market", "ratio_of_ratios").lo < 1, "ratio of ratios: interval above one at 4 quarters, includes one at 2")
chk(all(num(f"ag:mp:hl{k_}") > 2.3 for k_ in ("inf", "8", "4", "2")), "matched persistence: contrast above 2.3 for every half-life")
chk(num("br:lvl:w_eq") > num("br:lvl:w_usd") > num("br:lvl:house"), "bridge: equity weights first, then dollar, then houses")
chk(num("br:ep1998:gap") > 1 and num("br:ep1998:lo") > 0 and num("br:ep2004:eq") > 0 > num("br:ep2004:house"), "episodes: 1998-2001 gap above one with interval above zero; 2004-06 equities offset by houses")
c_main, c_96, c_x = pr("du", "main"), pr("du", "1996+"), pr("du", "ex2008-15")
chk(c_main.lo90_c < 0 < c_main.hi90_c and c_96.lo90_c < 0 < c_96.hi90_c and c_main.c_D < 0 < c_x.c_D, "composition: intervals include zero, sign changes across samples")
chk(abs(c_main.effect_p5_p95) < 0.5 and c_main.effect_hi90 - c_main.effect_lo90 > 1, "composition: outlook difference small with an interval wider than one point")
chk(sp.loc["eq", "gain_adj_r2"] > 0.10 and sp.loc["eq", "gain_adj_r2"] < sp.loc["mkt", "gain_adj_r2"] and sp.loc["usd", "gain_adj_r2"] < 0.01, "equities alone: gain above 0.10, below the market index; dollar nothing")
chk(float(pw.loc["w_M", "p_boot"]) > 0.1 and float(pw.loc["w_B", "p_boot"]) > 0.1, "proportionality not rejected")
chk(all(OOS19[(OOS19.comparison == "add_D_to_market") & (OOS19.outcome == "du")].cw_t < 1.3), "adding D never significantly improves out-of-sample unemployment forecasts")
rs_ = SPF19[(SPF19.target == "unemployment") & (SPF19.spec == "both") & (SPF19.term == "D")].iloc[0]
chk(rs_.hi90 < 0 and SPF19[(SPF19.target == "unemployment") & (SPF19.spec == "market_only") & (SPF19.term == "dM")].iloc[0].coef > 0, "SPF: D coefficient negative with interval below zero, index change positive")
chk(abs(num("ce:2022:D")) < 0.05 and num("ce:2022:real") < num("ce:2022:fcm"), "2022-24: D near zero and unemployment rose less than forecast")

# claims of the revised agreement paper
for k_ in (1, 5, 22):
    a_, o_ = AO20[(AO20.k == k_) & (AO20.group == "ann") & (AO20.stat == "ratio")].iloc[0], AO20[(AO20.k == k_) & (AO20.group == "other") & (AO20.stat == "ratio")].iloc[0]
    chk(abs(a_.point - o_.point) < 0.05, f"daily: announcement and other ratios within 0.05 at k={k_}")
CT20 = pd.read_csv(RES / "20_contrasts.csv")
chk(all(0.2 < num(f"dl:lad{k_}") < 0.4 for k_ in (1, 5, 22, 66, 252)), "ladder: ratio between 0.2 and 0.4 at every horizon")
chk(rs("du", "main", "gamma").lo90 < 0 < rs("du", "main", "gamma").hi90 and rs("du", "main", "gamma_minus_beta").lo90 < 0 < rs("du", "main", "gamma_minus_beta").hi90, "main sample: neither restriction rejected")
chk(rs("du", "1996+", "gamma_minus_beta").hi90 < 0 and num("rs:nrej:gamma") == 0 and num("rs:nrej:gmb") == 2, "1996+: model restriction rejected; market restriction never; model rejected in 2 of 12")
chk(sdc("unemployment", "all", "forecast").lo90 < 0 < sdc("unemployment", "all", "forecast").hi90 and sdc("unemployment", "all", "realized").hi90 < 0 and sdc("unemployment", "all", "error").hi90 < 0 and sdc("gdp", "all", "error").coef > 0, "SPF: D predicts realized and error, not the forecast; GDP error positive")
chk(abs(num("ce:2022:D")) < 0.05 and num("br:ep2022:gap") > 0.5 and num("br:ep1998:gap") > 1, "episodes: 2022-24 D near zero with a gap in levels; 1998-2001 gap above one")

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
