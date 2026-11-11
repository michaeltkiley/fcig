"""Step 5. Like-for-like comparison at each step: correlations, cross-index range, latest readings (comparison table); widest and closest six-month windows with the group split;
the groups behind today's readings; and one row per variation of the construction (robustness summary).
Writes results/compare.csv, episodes.csv, latest_groups.csv, robust_rows.csv, scalars_compare.csv."""
import numpy as np, pandas as pd
from lib import data, compare as K
from lib.config import RES
from lib.report import Scalars

S = Scalars("compare")
LEVEL = ["market", "gs", "frbus", "frbus_hp"]
pub = pd.read_csv(data.DATA / "fed_monthly_1yr.csv", parse_dates=["date"]).set_index("date").iloc[:, 0]; pub.index = pub.index.to_period("M")
V = pd.read_csv(RES / "var_specs.csv").set_index("key")
FL = {c: data.read(f"flow_{c}_p12.csv") for c in ("nominal", "real", "rstar", "rstar_kiley")}
IX = {}
for c in ("nominal", "real", "rstar", "rstar_kiley"):
    I = data.read(f"indexes_{c}.csv").loc["1974-01":]
    I["fi"] = FL[c].forward_impetus
    IX[c] = I

def zero90(I):
    z = I.loc["1990-01":]
    return z - z.mean()

rows = {}
for case in ("nominal", "real", "rstar"):
    I = IX[case]; z = zero90(I)
    r = {"mkt_gs": K.corr(I.market, I.gs), "mkt_frbus": K.corr(I.market, I.frbus), "mkt_frbus_hp": K.corr(I.market, I.frbus_hp),
         "mkt_anfci": K.corr(z.market, z.anfci), "mkt_gs_ninety": K.corr(z.market, z.gs), "mkt_frbus_ninety": K.corr(z.market, z.frbus),
         "mkt_gs_sd": float(I.market.std() / I.gs.std()), "mkt_frbus_sd": float(I.market.std() / I.frbus.std()), "mkt_gs_chg": K.corr(I.market, I.gs, True), "mkt_frbus_chg": K.corr(I.market, I.frbus, True),
         "gs_frbus": K.corr(I.gs, I.frbus), "fi_fcig": K.corr(I.fi, I.fcig_1yr), "fi_frbus_gi": K.corr(I.fi, I.frbus_gi_hp), "fcig_frbus_gi": K.corr(I.fcig_1yr, I.frbus_gi_hp),
         "fcig_level": K.corr(I.fcig_1yr, I.market), "range_long": K.spread(I[LEVEL]).mean(), "range_ninety": K.spread(z[LEVEL]).mean(),
         "latest_market": I.market.iloc[-1], "latest_gs": I.gs.iloc[-1], "latest_frbus": I.frbus.iloc[-1], "latest_frbus_hp": I.frbus_hp.iloc[-1],
         "latest_fi": I.fi.iloc[-1], "latest_fcig": I.fcig_1yr.iloc[-1],
         "latest90_market": z.market.iloc[-1], "latest90_gs": z.gs.iloc[-1], "latest90_frbus": z.frbus.iloc[-1]}
    if case == "nominal":
        r["fi_pub"] = K.corr(I.fi, pub); r["fcig_pub"] = K.corr(I.fcig_1yr, pub)
    rows[case] = r
T = pd.DataFrame(rows)
T.to_csv(RES / "compare.csv")
for c in rows:
    for k, v in rows[c].items():
        S.add(f"{c}_{k}", v)

# What each step changes
z = {c: zero90(IX[c]) for c in ("nominal", "real", "rstar")}
S.add("step_nom_real_ninety", K.corr(z["nominal"].market, z["real"].market)); S.add("step_real_rstar_ninety", K.corr(z["real"].market, z["rstar"].market))
S.add("step_nom_real_long", K.corr(IX["nominal"].market, IX["real"].market)); S.add("step_real_rstar_long", K.corr(IX["real"].market, IX["rstar"].market))
for c in ("nominal", "real", "rstar"):
    S.add(f"{c}_mkt_gfc", z[c].market.loc["2009-01":"2016-12"].mean()); S.add(f"{c}_gs_gfc", z[c].gs.loc["2009-01":"2016-12"].mean()); S.add(f"{c}_frbus_gfc", z[c].frbus.loc["2009-01":"2016-12"].mean())
    for nm, d in (("seventyfour", "1974-06"), ("seventynine", "1979-12"), ("eightyone", "1981-06"), ("gfc", "2008-12")):
        S.add(f"{c}_fcig_{nm}", IX[c].fcig_1yr.loc[d])
# share of months with a cross-index range above 1 pp, r* baseline, 1990-
rg = K.spread(z["rstar"][LEVEL]); S.add("rstar_share_range_gt1_ninety", float((rg > 1).mean()))
rgl = K.spread(IX["rstar"][LEVEL]); S.add("rstar_max_range", float(rgl.max()))
# the three levels indexes only (without house prices): range
L3 = ["market", "gs", "frbus"]
S.add("rstar_range_three_long", K.spread(IX["rstar"][L3]).mean()); S.add("rstar_range_three_ninety", K.spread(z["rstar"][L3]).mean())

# Episodes: widest and closest six-month windows (all months, and since 1990), r* baseline, group split of market minus FRB/US with house prices
I = IX["rstar"]; G = data.read("groups_rstar.csv")
lines = []
for label, sub, widest in (("Widest", None, True), ("Widest since 1990", "1990-01", True), ("Closest", None, False)):
    D0 = I[LEVEL] if sub is None else I.loc[sub:, LEVEL]
    for e, v in K.windows(D0, n=5, widest=widest):
        m = I.loc[e - 5:e, LEVEL].mean()
        d = {g: G.loc[e - 5:e, f"market|{g}"].mean() - (G.loc[e - 5:e, f"frbus_hp|{g}"].mean() if f"frbus_hp|{g}" in G else 0.0) for g in ("rates", "equities", "dollar")}
        d["house"] = -G.loc[e - 5:e, "frbus_hp|other"].mean()
        lines.append({"kind": label, "start": (e - 5).strftime("%Y-%m"), "end": e.strftime("%Y-%m"), "range": v, **{c: m[c] for c in LEVEL}, **{f"gap_{k}": x for k, x in d.items()}})
pd.DataFrame(lines).to_csv(RES / "episodes.csv", index=False)

# Groups behind today's readings (r* baseline; zero is the 1973-2026 average of each variable)
lg = G.iloc[-1]
rows2 = []
for lab in ("market", "gs", "frbus_hp"):
    rows2.append({"index": lab, **{g: lg.get(f"{lab}|{g}", 0.0) for g in ("rates", "equities", "dollar", "other")}, "total": I[{"market": "market", "gs": "gs", "frbus_hp": "frbus_hp"}[lab]].iloc[-1]})
pd.DataFrame(rows2).to_csv(RES / "latest_groups.csv", index=False)

# Robustness rows: one row per variation of the construction. Columns: market vs GS, market vs FRB/US (levels), average range of the level indexes since 1990 (zero 1990-2026),
# latest readings, yardstick Phi(12), forward impetus against FCI-G.
def row(label, m, gs, fr, fr2, phi, fcig, zero="full"):
    X = pd.concat([m.rename("market"), gs.rename("gs"), fr.rename("frbus"), fr2.rename("frbus_hp")], axis=1).loc["1974-01":]
    z90 = X.loc["1990-01":] - X.loc["1990-01":].mean()
    return {"variation": label, "mkt_gs": K.corr(X.market, X.gs), "mkt_frbus": K.corr(X.market, X.frbus), "range_ninety": K.spread(z90).mean(), "range_long": K.spread(X).mean(),
            "latest_market": X.market.iloc[-1], "latest_gs": X.gs.iloc[-1], "latest_frbus": X.frbus.iloc[-1],
            "phi12": phi.phi12, "phi12_lo": phi.phi12_lo90, "phi12_hi": phi.phi12_hi90, "fi_fcig": phi.corr_fi_fcig, "fi_fcig_lo": phi.corr_fi_fcig_lo90, "fi_fcig_hi": phi.corr_fi_fcig_hi90, "sig_from": phi.sig_from, "sig_to": phi.sig_to}
b = IX["rstar"]; MV = data.read("market_variants.csv")
R = [row("Baseline: Laubach-Williams r*, 12 lags, VAR 1973-2026", b.market, b.gs, b.frbus, b.frbus_hp, V.loc["rstar_p12"], b.fcig_1yr)]
k = IX["rstar_kiley"]
R.append(row("Kiley r*", k.market, k.gs, k.frbus, k.frbus_hp, V.loc["rstar_kiley_p12"], k.fcig_1yr))
R.append(row("4 VAR lags", b.market, b.gs, b.frbus, b.frbus_hp, V.loc["rstar_p4"], b.fcig_1yr))
R.append(row("VAR estimated from 1990", b.market, b.gs, b.frbus, b.frbus_hp, V.loc["rstar_p12_from1990"], b.fcig_1yr))
R.append(row("VAR estimated to 2019", b.market, b.gs, b.frbus, b.frbus_hp, V.loc["rstar_p12_to2019"], b.fcig_1yr))
for key, lab in (("two_year", "Weights: policy news is the 2-year yield"), ("to_2019", "Weights: announcements through 2019"), ("no_lower_bound", "Weights: no announcements at the lower bound")):
    mv = MV[key].copy(); mv.index = pd.PeriodIndex(mv.index, freq="M")
    R.append(row(lab, mv, b.gs, b.frbus, b.frbus_hp, V.loc[f"rstar_p12_w_{key}"], b.fcig_1yr))
Rb = pd.DataFrame(R)
Rb.to_csv(RES / "robust_rows.csv", index=False)
print(Rb.round(2).to_string())
S.save()
