"""Step 22 (policy-rate experiment). What does a policy-rate surprise do in FRB/US, per unit of announcement news? (colleague report p.3.)

Experiment. The model's own monetary-policy shock, as in the Board's demos (pyfrbus demos example1): an add factor of size a on the inertial-Taylor-rule equation
(rffintay_aerr) in the first quarter of the simulation (2040Q1) ONLY, with the policy rule ACTIVE afterwards (nothing exogenized: the funds rate, the Treasury curve, the stock market, the
dollar, the BBB spread all respond; VAR expectations; steady-state baseline from 2040Q1, fiscal settings as in the Board's demos). The funds rate then follows the rule's own inertia.
Unit. FRB/US has no two-year yield. The two-year proxy is the average of the funds rate over the next eight quarters on the simulated path (quarters 1 to 8 after the shock), in
deviation from baseline [inference: under VAR expectations the market's expected path differs from the simulated path; the proxy is the path the model itself generates]. The shock size a is
set so that the proxy rises by 1 pp (linear scaling from a = 1, then re-run at the calibrated size to check linearity).
Reports, per unit (proxy +1 pp): the funds rate, bill, 5- and 10-year yields, stock wealth, real dollar on impact (quarter 1) and at quarter 4, GDP at quarter 4 and its funds-rate equivalent
(GDP / GDP of the persistent +1 pp hike with full transmission), against the announcement responses psi (market_weights.csv) and the three-asset replay b4'psi (the usual response priced
with the persistent per-unit multipliers, data/frbus_paths.csv). Pricing of the quarter-4 spillovers: move x persistent per-unit multiplier; the remainder is the policy-rate direct effect and
other channels (mortgage spread, BBB spread, house prices, paths within the year).
Writes results/22_policy_shock_paths.csv and scalars_22_policy_shock.csv."""
import os, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib.frbus_env import ensure_runtime
ensure_runtime()
import numpy as np, pandas as pd
from pyfrbus.frbus import Frbus
from lib.frbus_env import MODEL
from lib.frbus_common import Model
from lib.config import RES, DATA

t0 = time.time(); H = 16
M = Model(32); start, end, base = M.start, M.end, M.base
q = slice(start, start + H - 1)
h0, h1 = M.run(["rff"], ["rff"], 1.0); G = M.gdp(h1, h0, 32)                       # yardstick: persistent +1 pp hike, full transmission
fr = Frbus(str(MODEL))                                                           # fresh object: nothing exogenized
def shock(a):
    d1 = base.copy(); d1.loc[start, "rffintay_aerr"] = d1.loc[start, "rffintay_aerr"] + a
    return fr.solve(start, end, base.copy()), fr.solve(start, end, d1)
proxy = lambda s0, s1: float((s1.loc[start:start + 7, "rff"] - s0.loc[start:start + 7, "rff"]).mean())
s0, s1 = shock(1.0); p1 = proxy(s0, s1); a = 1.0 / p1
s0, s1 = shock(a); p2 = proxy(s0, s1)
out = {"d_rff": (s1.loc[q, "rff"] - s0.loc[q, "rff"]).values, "d_rtb": (s1.loc[q, "rtb"] - s0.loc[q, "rtb"]).values, "d_rg5": (s1.loc[q, "rg5"] - s0.loc[q, "rg5"]).values,
       "d_rg10": (s1.loc[q, "rg10"] - s0.loc[q, "rg10"]).values, "d_mortgage_spread": ((s1.loc[q, "rme"] - s1.loc[q, "rg10"]) - (s0.loc[q, "rme"] - s0.loc[q, "rg10"])).values,
       "d_rbbbp": (s1.loc[q, "rbbbp"] - s0.loc[q, "rbbbp"]).values, "stock_wealth_pct": 100 * np.log(s1.loc[q, "wpsn"] / s0.loc[q, "wpsn"]).values,
       "dollar_pct": 100 * np.log(s1.loc[q, "fpxr"] / s0.loc[q, "fpxr"]).values, "house_prices_pct": 100 * np.log(s1.loc[q, "phouse"] / s0.loc[q, "phouse"]).values,
       "gdp": M.gdp(s1, s0, H)}
out["ffr_equivalent"] = out["gdp"] / G[:H]
P = pd.DataFrame({"quarter": np.arange(1, H + 1), **out}); P.to_csv(RES / "22_policy_shock_paths.csv", index=False, float_format="%.6f")
# announcement response and per-unit multipliers
mw = pd.read_csv(RES / "market_weights.csv", index_col=0); psi = dict(zip(("ten", "eq", "usd"), mw.response.values))
pp = pd.read_csv(DATA / "frbus_paths.csv"); pp = pp[(pp.design == "zfree") & (pp["shape"] == "persistent") & (pp.quarter == 4)].set_index("experiment").gdp_per_unit
ph = {"ten": float(pp["rg10"]), "eq": float(pp["req"]), "usd": float(pp["fpxr"])}      # GDP per pp of the 10-year; per 1% RISE of stock wealth (sign flipped in the file); per 1% rise of the dollar
S = []
def sc(k, v): S.append((k, float(v)))
sc("shock_size_rffintay_aerr", a); sc("proxy_at_a1", p1); sc("proxy_at_calibrated", p2)
s0b, s1b = shock(1.0); g1 = M.gdp(s1b, s0b, H)[3]; sc("linearity_gdp_q4_rel", abs(out["gdp"][3] - g1 * a) / abs(out["gdp"][3]))
for k in ("d_rff", "d_rtb", "d_rg5", "d_rg10", "stock_wealth_pct", "dollar_pct"):
    sc(f"{k}:q1", out[k][0]); sc(f"{k}:q4", out[k][3])
sc("rff_halflife_quarters", np.log(0.5) / np.log(out["d_rff"][4] / out["d_rff"][0]) * 4 if out["d_rff"][4] > 0 else np.nan)
sc("gdp_q4", out["gdp"][3]); sc("ffr_equivalent_q4", out["ffr_equivalent"][3])
for n, v in psi.items(): sc(f"psi_{n}", v)
# pricing of the spillovers along their paths: sum_s x_s Tmp(4 - s + 1), Tmp = per-unit response to a one-quarter shift (data/frbus_paths.csv, zfree, temporary); x = path of the move in quarter s
# (10-year: pp; equity: percent change of stock wealth, rise positive; dollar: percent). Also the cruder pricing at the quarter-4 level times the persistent multiplier.
pt = pd.read_csv(DATA / "frbus_paths.csv"); pt = pt[(pt.design == "zfree") & (pt["shape"] == "temporary")]
Tmp = {n: np.r_[0.0, pt[pt.experiment == e].sort_values("quarter").gdp_per_unit.values] for n, e in (("ten", "rg10"), ("eq", "req"), ("usd", "fpxr"))}
xpath = {"ten": out["d_rg10"], "eq": out["stock_wealth_pct"], "usd": out["dollar_pct"]}
priced = {n: sum(xpath[n][s - 1] * Tmp[n][4 - s + 1] for s in range(1, 5)) for n in Tmp}
priced_q4level = {"ten": ph["ten"] * out["d_rg10"][3], "eq": ph["eq"] * out["stock_wealth_pct"][3], "usd": ph["usd"] * out["dollar_pct"][3]}
for n in Tmp: sc(f"priced_q4level_gdp:{n}", priced_q4level[n])
for n, k in (("ten", "d_rg10"), ("eq", "stock_wealth_pct"), ("usd", "dollar_pct")): sc(f"move_over_psi_q1:{n}", out[k][0] / psi[n])
replay = {"ten": ph["ten"] * psi["ten"], "eq": ph["eq"] * psi["eq"], "usd": ph["usd"] * psi["usd"]}
sc("replay_gdp_q4", sum(replay.values())); sc("replay_ffr_points", sum(replay.values()) / G[3])
for n in ("ten", "eq", "usd"):
    sc(f"priced_gdp_q4:{n}", priced[n]); sc(f"priced_share:{n}", priced[n] / out["gdp"][3]); sc(f"replay_share:{n}", replay[n] / sum(replay.values())); sc(f"move_over_psi:{n}", (out[{"ten": "d_rg10", "eq": "stock_wealth_pct", "usd": "dollar_pct"}[n]][3]) / psi[n])
sc("priced_sum", sum(priced.values())); sc("remainder_gdp_q4", out["gdp"][3] - sum(priced.values())); sc("remainder_share", (out["gdp"][3] - sum(priced.values())) / out["gdp"][3])
sc("gdp_gap_vs_replay_q4", out["gdp"][3] - sum(replay.values())); sc("ffr_gap_vs_replay", out["ffr_equivalent"][3] - sum(replay.values()) / G[3])
Sdf = pd.DataFrame(S, columns=["key", "value"]); Sdf.to_csv(RES / "scalars_22_policy_shock.csv", index=False, float_format="%.6f")
print(P.round(4).head(8).to_string()); print(Sdf.round(4).to_string()); print("runtime %.0f s" % (time.time() - t0))
