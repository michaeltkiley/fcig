"""Step 5. Like-for-like comparison at each step: our nominal indexes with the existing nominal ones, real with real, r* with r* (Table 4, Table 5, Figures 4-5)."""
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from fci import data, compare as K, report

N = report.Numbers("compare")
LEVEL = ["market", "gs", "frbus", "frbus_hp"]
pub = pd.read_csv(data.DATA / "fed_monthly_1yr.csv", parse_dates=["date"]).set_index("date").iloc[:, 0]; pub.index = pub.index.to_period("M")
S = {}
rows = {}
for case, lab in (("nominal", "Nominal"), ("real", "Real"), ("rstar", "r* (baseline)")):
    I = data.read(f"indexes_{case}.csv").loc["1974-01":]; F = data.read(f"flow_{case}.csv")
    I["fi"] = F.forward_impetus_p12
    S[case] = I
    z = I.loc["1990-01":] - I.loc["1990-01":].mean()                     # 1990-2026 zero point
    r = {"Market vs GS, levels": K.corr(I.market, I.gs), "Market vs FRB/US, levels": K.corr(I.market, I.frbus),
         "Market vs FRB/US with house prices, levels": K.corr(I.market, I.frbus_hp), "Market vs ANFCI, levels (1990-)": K.corr(z.market, z.anfci),
         "Market vs GS, 12-month changes": K.corr(I.market, I.gs, True), "Market vs FRB/US, 12-month changes": K.corr(I.market, I.frbus, True),
         "Forward impetus vs FCI-G (1-year)": K.corr(I.fi, I.fcig_1yr), "Forward impetus vs FRB/US growth impetus": K.corr(I.fi, I.frbus_gi_hp),
         "FCI-G vs FRB/US growth impetus": K.corr(I.fcig_1yr, I.frbus_gi_hp), "FCI-G vs market index level": K.corr(I.fcig_1yr, I.market),
         "Range of level indexes, 1974-2026": K.spread(I[LEVEL]).mean(), "Range of level indexes, 1990-2026": K.spread(z[LEVEL]).mean(),
         "Market index, latest": I.market.iloc[-1], "GS, latest": I.gs.iloc[-1], "FRB/US, latest": I.frbus.iloc[-1], "Forward impetus, latest": I.fi.iloc[-1],
         "FCI-G (1-year), latest": I.fcig_1yr.iloc[-1]}
    if case == "nominal":
        r["Forward impetus vs published FCI-G (1990-)"] = K.corr(I.fi, pub)
        r["FCI-G replication vs published (1990-)"] = K.corr(I.fcig_1yr, pub)
    rows[lab] = r
T = pd.DataFrame(rows)
print(T.round(2).to_string())
report.table("tab4_comparison", T.round(2), fmt="{:.2f}")
short = {"Nominal": "Nom", "Real": "Real", "r* (baseline)": "Rstar"}
KEYS = {"Market vs GS, levels": "MktGs", "Market vs FRB/US, levels": "MktFrbus", "Market vs FRB/US with house prices, levels": "MktFrbusHp",
        "Market vs ANFCI, levels (1990-)": "MktAnfci", "Market vs GS, 12-month changes": "MktGsChg", "Market vs FRB/US, 12-month changes": "MktFrbusChg",
        "Forward impetus vs FCI-G (1-year)": "FiFcig", "Forward impetus vs FRB/US growth impetus": "FiGi", "FCI-G vs FRB/US growth impetus": "FcigGi", "FCI-G vs market index level": "FcigLevel",
        "Range of level indexes, 1974-2026": "RangeLong", "Range of level indexes, 1990-2026": "RangeNinety", "Market index, latest": "MktLatest",
        "GS, latest": "GsLatest", "FRB/US, latest": "FrbusLatest", "Forward impetus, latest": "FiLatest", "FCI-G (1-year), latest": "FcigLatest",
        "Forward impetus vs published FCI-G (1990-)": "FiPub", "FCI-G replication vs published (1990-)": "FcigPub"}
for lab, r in rows.items():
    for k, v in r.items():
        N.add(short[lab] + KEYS[k], v)

# What each step changes (section 4)
z = {c: S[c].loc["1990-01":] - S[c].loc["1990-01":].mean() for c in S}
N.add("StepNomRealNinety", K.corr(z["nominal"].market, z["real"].market)); N.add("StepRealRstarNinety", K.corr(z["real"].market, z["rstar"].market))
N.add("StepNomRealLong", K.corr(S["nominal"].market, S["real"].market)); N.add("StepRealRstarLong", K.corr(S["real"].market, S["rstar"].market))
for c, k in (("nominal", "Nom"), ("real", "Real"), ("rstar", "Rstar")):
    N.add(f"MktGFC{k}", z[c].market.loc["2009-01":"2016-12"].mean()); N.add(f"MktLatestNinety{k}", z[c].market.iloc[-1])
    N.add(f"FcigSeventyFour{k}", S[c].fcig_1yr.loc["1974-06"]); N.add(f"FcigSeventyNine{k}", S[c].fcig_1yr.loc["1979-12"])
    N.add(f"FcigEightyOne{k}", S[c].fcig_1yr.loc["1981-06"]); N.add(f"FcigGFC{k}", S[c].fcig_1yr.loc["2008-12"])
N.add("UsdNomSeventyThree", data.load().usd_nominal.loc["1973-01"], "{:.0f}"); N.add("UsdNomLatest", data.load().usd_nominal.iloc[-1], "{:.0f}")

# Table 5: widest and closest six-month windows, r* baseline, with the group split of the market index minus the FRB/US index (with house prices)
I = S["rstar"]
G = data.read("groups_rstar.csv")
lines = []
for kind, wide in (("Widest", True), ("Closest", False)):
    for e, v in K.windows(I[LEVEL], n=5, widest=wide):
        m = I.loc[e - 5:e, LEVEL].mean()
        d = {g: G.loc[e - 5:e, f"market|{g}"].mean() - (G.loc[e - 5:e, f"frbus_hp|{g}"].mean() if f"frbus_hp|{g}" in G else 0.0) for g in ("rates", "equities", "dollar")}
        d["other"] = -G.loc[e - 5:e, "frbus_hp|other"].mean()
        lines.append({"": kind, "Window": f"{(e - 5).strftime('%Y-%m')} to {e.strftime('%Y-%m')}", "Range": v, "Market": m.market, "GS": m.gs, "FRB/US": m.frbus,
                      "FRB/US+HP": m.frbus_hp, "Gap: rates": d["rates"], "equities": d["equities"], "dollar": d["dollar"], "house prices": d["other"]})
T5 = pd.DataFrame(lines).set_index("")
report.table("tab5_episodes", T5, fmt="{:+.2f}")
print(T5.round(2).to_string())

# Figure 4: the level indexes at each step; Figure 5: the market index across steps
fig, ax = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
for a, (case, title) in zip(ax, (("nominal", "Nominal"), ("real", "Real rates"), ("rstar", "Gaps to r* (baseline)"))):
    I = S[case]; t = I.index.to_timestamp()
    a.plot(t, I.market, color=report.COLORS["market"], lw=1.4, label="Market index")
    a.plot(t, I.gs, color=report.COLORS["gs"], lw=1.0, label="GS replication")
    a.plot(t, I.frbus, color=report.COLORS["frbus"], lw=1.0, label="FRB/US (macro-model) index")
    z = I.anfci.where(I.index >= pd.Period("1990-01", "M"))
    a.plot(t, z.clip(-8, 8), color=report.COLORS["anfci"], lw=0.8, alpha=0.7, label="ANFCI (from 1990, clipped at +/-8)")
    a.set_title(title, fontsize=9); report.axes(a)
ax[1].set_ylabel("pp (2-year yield or funds rate), tighter above zero")
report.figure("fig4_levels_by_step", fig)
fig, ax = plt.subplots(figsize=(10, 3.8))
for case, col, lab in (("nominal", report.COLORS["grey"], "Nominal"), ("real", report.COLORS["frbus"], "Real"), ("rstar", report.COLORS["market"], "Gaps to r* (baseline)")):
    ax.plot(S[case].index.to_timestamp(), S[case].market, color=col, lw=1.2 if case != "rstar" else 1.6, label=lab)
report.axes(ax, "pp of the 2-year yield")
report.figure("fig5_market_by_step", fig)
N.write()
