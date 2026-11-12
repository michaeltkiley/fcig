"""Step 22. What carries the FRB/US effect of the equity and dollar experiments? (colleague report p.3, 'build the economics around the two experiments'.)

Opens up the GDP response behind the FRB/US weights of Figure 1: the two stylized movements (equity valuation -5 log points, real dollar +3.9 log points) run in the Board's FRB/US
model (pyfrbus, VAR expectations) in the SAME set-up as experimental/ms_fci/frbus_paths.py: steady-state baseline from 2040Q1, fiscal settings as in the Board's demos,
persistent shift of the stated variable at impact, everything else that is an index variable held at baseline (the policy rate, 3-month bill, 5/10/30-year Treasuries, mortgage and
car-loan rates, BBB spread, dollar, oil are exogenized; stock wealth is free in the equity experiment and the required return on equity (req) is the shocked variable; the 28 VAR
expectation aggregates respond, design 'zfree'). The policy rate is therefore FIXED (the rule is inactive) in the two partial experiments; the funds-rate yardstick is the
+1 pp hike with full transmission (only rff exogenized), and the funds-rate equivalent is GDP(experiment) / GDP(hike) at the same quarter.

GDP object: xgdp, real GDP (chain-weighted 2012 dollars), reported as 100 x log(xgdp shocked / xgdp baseline) at quarter q after the shock (q = 1 is the quarter of impact; the
'four-quarter' effect is q = 4). Components: FRB/US approximates xgdp by a fixed-weight Divisia aggregation,
    dlog xgdp = y1 dlog xfs + y2 dlog ki + y3 dlog ki(-1),   dlog xfs = sum_i w_i dlog e_i
(y1 = 0.9985, y2 = 0.6264, y3 = -0.6249; w from the model's xfs equation: consumption ecnia 0.6849, residential eh 0.0386, business fixed investment ebfi 0.1324, federal
purchases egfe 0.0429 and egfl 0.0223, state and local egse 0.0395 and egsl 0.0691, exports ex 0.1203, non-oil imports emo -0.1399, petroleum imports emp -0.0101). Because the
log aggregator telescopes, the contribution of component i to the log-level difference of GDP at q is 100 y1 w_i [log e_i(shock) - log e_i(base)](q); inventories contribute
100 (y2 d(q) + y3 d(q-1)) with d = log ki(shock) - log ki(base). The residual (GDP difference less the sum of contributions) is the model's xgdp add-factor/approximation error and is reported.
Persistent shocks are run directly; a common decaying path (half-life 4 quarters, x_s = 0.5^((s-1)/4), x_1 = 1 at impact) is priced from the TEMPORARY-shock responses by linearity,
exactly as in step 18 (response(q) = sum_s x_s Tmp(q-s+1), per unit of the persistent experiment's impact unit).
Units: equity, per 1 percent fall in stock wealth at impact in the persistent experiment (scaled to 5, the stylized fall of 5 log points of equity valuation); dollar, per 1 percent
rise in the real exchange rate (scaled to 3.9).
Run with the Python environment that has pyfrbus's pinned libraries (pandas<3, sympy==1.3, symengine, scipy, networkx, multiprocess, lxml); the package is downloaded to raw/frbus
(gitignored) by experimental/ms_fci/frbus_sensitivities.get_package(). Usage: <venv>/bin/python 22_channels.py
Writes results/22_*.csv and scalars_22_channels.csv."""
import os, sys, re, time
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(ROOT, "raw", "frbus")
sys.path.insert(0, os.path.join(ROOT, "experimental", "ms_fci"))
RES = os.environ.get("FCI_RESULTS", os.path.join(HERE, "results"))
os.makedirs(RES, exist_ok=True)
import frbus_sensitivities as F
F.get_package()
from pyfrbus.frbus import Frbus
from pyfrbus.load_data import load_data

t0 = time.time()
H = 16                      # quarters reported
HSOLVE = 32                 # simulation horizon of frbus_paths.py (end = start + HSOLVE + 7), so that results match the stored paths
HL = 4.0
data = load_data(os.path.join(RAW, "data_only_package", "LONGBASE.TXT"))
frbus = Frbus(os.path.join(RAW, "pyfrbus", "models", "model.xml"))
start = pd.Period("2040Q1"); end = start + HSOLVE + 7
data.loc[start:end, "dfpdbt"] = 0
data.loc[start:end, "dfpsrp"] = 1
base = frbus.init_trac(start, end, data)
CURVE = ["rtb", "rg5", "rg10", "rg30"]; PASS = ["rme", "rcar"]; OTHER = ["rbbbp", "req", "wpsn", "fpxr", "poil"]
FIXED = ["rff"] + CURVE + PASS + OTHER

# model coefficients of the GDP aggregation (read from model.xml, not typed)
xml = open(os.path.join(RAW, "pyfrbus", "models", "model.xml")).read()
def coefs(var, prefix):
    m = re.search(r"<variable>\s*<name>%s</name>(.*?)</variable>" % var, xml, re.S); s = re.sub(r"\s+", " ", m.group(1))
    return {int(i): float(v) for i, v in re.findall(r"<cf_name>%s\((\d+)\)</cf_name>\s*<cf_value>([-\d.eE]+)" % prefix, s)}
YG = coefs("xgdp", "y_xgdp"); YX = coefs("xfs", "y_xfs")
XFS = ["ecnia", "eh", "ebfi", "egfe", "egfl", "egse", "egsl", "ex", "emo", "emp"]
assert len(YX) == 10 and set(YG) == {1, 2, 3}
GROUPS = {"Consumption": ["ecnia"], "Residential investment": ["eh"], "Business fixed investment": ["ebfi"], "Government": ["egfe", "egfl", "egse", "egsl"],
          "Exports": ["ex"], "Imports": ["emo", "emp"], "Inventories": []}
FIN = ["rff", "rtb", "rg5", "rg10", "rg30", "rme", "rbbbp", "rcar"]
Q = slice(start, start + H - 1)
prev = start - 1

def run(exo, vars_, shift, mult=False, temporary=False):
    frbus.exogenize(list(exo))
    d0 = base.copy(); d1 = base.copy()
    last = start if temporary else end
    for v in vars_:
        d1.loc[start:last, v] = d1.loc[start:last, v] * (1 + shift) if mult else d1.loc[start:last, v] + shift
    return frbus.solve(start, end, d0), frbus.solve(start, end, d1)

def extract(s0, s1):
    """Paths of GDP, its contributions and the financial variables for quarters 1..H (arrays, element 0 = quarter 1)."""
    lg = lambda v: 100 * np.log(s1.loc[Q, v] / s0.loc[Q, v]).values
    out = {"gdp": lg("xgdp")}
    comp = {}
    for i, v in enumerate(XFS, 1):
        comp[v] = YG[1] * YX[i] * lg(v)
    d = np.log(s1.loc[start:start + H - 1, "ki"] / s0.loc[start:start + H - 1, "ki"]).values
    dl = np.concatenate([[0.0], d[:-1]])
    inv = 100 * (YG[2] * d + YG[3] * dl)
    for g, vs in GROUPS.items():
        out[g] = inv if g == "Inventories" else sum(comp[v] for v in vs)
    out["Sum of components"] = sum(out[g] for g in GROUPS)
    out["Residual"] = out["gdp"] - out["Sum of components"]
    for v in FIN:
        out["d_" + v] = (s1.loc[Q, v] - s0.loc[Q, v]).values
    out["d_mortgage_spread"] = ((s1.loc[Q, "rme"] - s1.loc[Q, "rg10"]) - (s0.loc[Q, "rme"] - s0.loc[Q, "rg10"])).values
    out["stock_wealth_pct"] = lg("wpsn"); out["dollar_pct"] = lg("fpxr")
    out["house_prices_pct"] = lg("phouse"); out["unemployment_gap_pp"] = (s1.loc[Q, "lur"] - s0.loc[Q, "lur"]).values if "lur" in s1.columns else np.full(H, np.nan)
    out["inflation_pp"] = (s1.loc[Q, "picxfe"] - s0.loc[Q, "picxfe"]).values if "picxfe" in s1.columns else np.full(H, np.nan)
    return out

# the yardstick: +1 pp hike with full transmission (only the policy rate exogenized)
h0, h1 = run(["rff"], ["rff"], 1.0)
HIKE = extract(h0, h1)
G = HIKE["gdp"]

EXP = {"equity": (["req"], 1.0, False, [v for v in FIXED if v != "wpsn"]),
       "dollar": (["fpxr"], 0.10, True, FIXED)}
RESP = {}; UNIT = {}
for name, (vars_, shift, mult, exo) in EXP.items():
    for shape in ("persistent", "temporary"):
        s0, s1 = run(exo, vars_, shift, mult, temporary=(shape == "temporary"))
        if shape == "persistent":
            UNIT[name] = (-100 * np.log(s1.loc[start, "wpsn"] / s0.loc[start, "wpsn"])) if name == "equity" else 100 * np.log(1 + shift)
        RESP[(name, shape)] = extract(s0, s1)
print(f"units (impact): equity {UNIT['equity']:.4f} % fall in stock wealth per +1 pp req; dollar {UNIT['dollar']:.4f} % per +10 %")

SCALE = {"equity": 5.0, "dollar": 3.9}      # the stylized movements of Figure 1
def path_for(name, hl):
    """Responses (dict of arrays) to the stylized movement; hl = inf: persistent run; else the decaying path priced from the temporary responses."""
    u = UNIT[name]; k = SCALE[name] / u
    if np.isinf(hl):
        R = RESP[(name, "persistent")]; return {v: k * R[v] for v in R}
    T = RESP[(name, "temporary")]; x = 0.5 ** (np.arange(H) / hl); out = {}
    for v in T:
        t = np.nan_to_num(T[v]); out[v] = k * np.array([sum(x[s] * t[q - s] for s in range(q + 1)) for q in range(H)])
    return out

rows = []; fig_rows = []
for name in ("equity", "dollar"):
    for tag, hl in (("persistent", np.inf), ("halflife4", HL)):
        P = path_for(name, hl)
        for q in range(H):
            rec = dict(experiment=name, path=tag, quarter=q + 1, gdp=P["gdp"][q], ffr_equivalent=P["gdp"][q] / G[q] * 1.0)
            for v in list(GROUPS) + ["Sum of components", "Residual"] + [c for c in P if c.startswith("d_") or c.endswith("_pct") or c in ("unemployment_gap_pp", "inflation_pp")]:
                rec[v] = P[v][q]
            rows.append(rec)
PATHS = pd.DataFrame(rows)
PATHS.to_csv(os.path.join(RES, "22_paths.csv"), index=False, float_format="%.6f")
# figure data: GDP path and stacked contributions, persistent paths, the two stylized movements
fd = PATHS[PATHS.path == "persistent"][["experiment", "quarter", "gdp"] + list(GROUPS) + ["Residual"]]
fd.to_csv(os.path.join(RES, "22_figure_persistent.csv"), index=False, float_format="%.6f")
PATHS[PATHS.path == "halflife4"][["experiment", "quarter", "gdp"] + list(GROUPS) + ["Residual"]].to_csv(os.path.join(RES, "22_figure_halflife4.csv"), index=False, float_format="%.6f")
pd.DataFrame({"quarter": np.arange(1, H + 1), **{k: v for k, v in HIKE.items()}}).to_csv(os.path.join(RES, "22_hike_paths.csv"), index=False, float_format="%.6f")

# four-quarter shares
sc = []
def S(k, v): sc.append((k, float(v)))
for name in ("equity", "dollar"):
    for tag in ("persistent", "halflife4"):
        d = PATHS[(PATHS.experiment == name) & (PATHS.path == tag) & (PATHS.quarter == 4)].iloc[0]
        S(f"{name}:{tag}:gdp_q4", d.gdp); S(f"{name}:{tag}:ffr_eq_q4", d.ffr_equivalent); S(f"{name}:{tag}:residual_q4", d.Residual)
        for g in GROUPS:
            S(f"{name}:{tag}:{g}:q4", d[g]); S(f"{name}:{tag}:{g}:share_q4", d[g] / d.gdp)
        S(f"{name}:{tag}:domestic_q4", d["Consumption"] + d["Residential investment"] + d["Business fixed investment"])
        S(f"{name}:{tag}:domestic_share_q4", (d["Consumption"] + d["Residential investment"] + d["Business fixed investment"]) / d.gdp)
        S(f"{name}:{tag}:netexports_q4", d["Exports"] + d["Imports"]); S(f"{name}:{tag}:netexports_share_q4", (d["Exports"] + d["Imports"]) / d.gdp)
S("hike:gdp_q4", G[3])
for v in ("d_rff", "d_rg10", "d_mortgage_spread", "d_rbbbp", "stock_wealth_pct", "dollar_pct"):
    S(f"hike:{v}:q1", HIKE[v][0]); S(f"hike:{v}:q4", HIKE[v][3])
for g in GROUPS:
    S(f"hike:{g}:q4", HIKE[g][3])
S("unit:equity", UNIT["equity"]); S("unit:dollar", UNIT["dollar"])
S("yardstick:coef_y1", YG[1]); S("max_abs_residual", PATHS.Residual.abs().max()); S("max_abs_residual_over_gdp", (PATHS.Residual.abs() / PATHS.gdp.abs().clip(lower=1e-3)).max())

# verification against the stored package responses (data/frbus_paths.csv, zfree, persistent) and the stored weights
st = pd.read_csv(os.path.join(HERE, "data", "frbus_paths.csv")); st = st[(st["design"] == "zfree") & (st["shape"] == "persistent")]
fw = pd.read_csv(os.path.join(HERE, "results", "frbus_weights.csv"), index_col=0)
chk = []
for name, key, sign in (("equity", "req", -1.0), ("dollar", "fpxr", 1.0)):
    R = RESP[(name, "persistent")]
    for q in (4, 8):
        pass
    mine = sign * RESP[(name, "persistent")]["gdp"] / UNIT[name]           # per unit, sign as in the stored file
    ref = st[st.experiment == key].sort_values("quarter")
    for q in (1, 2, 4, 8, 12, 16):
        chk.append(dict(experiment=name, quarter=q, mine=mine[q - 1], stored=float(ref[ref.quarter == q].gdp_per_unit.iloc[0]), diff=mine[q - 1] - float(ref[ref.quarter == q].gdp_per_unit.iloc[0])))
    # the stored hike
hs = pd.read_csv(os.path.join(HERE, "data", "frbus_hike_paths.csv"))
for q in (4, 8, 12, 16):
    chk.append(dict(experiment="hike", quarter=q, mine=G[q - 1], stored=float(hs[hs.quarter == q].gdp.iloc[0]), diff=G[q - 1] - float(hs[hs.quarter == q].gdp.iloc[0])))
CH = pd.DataFrame(chk); CH.to_csv(os.path.join(RES, "22_verify.csv"), index=False, float_format="%.6f")
# funds-rate points of the stylized movements (Figure 1): GDP at q4 / hike GDP at q4
S("fig1:equity_ffr_points", PATHS[(PATHS.experiment == "equity") & (PATHS.path == "persistent") & (PATHS.quarter == 4)].ffr_equivalent.iloc[0])
S("fig1:dollar_ffr_points", PATHS[(PATHS.experiment == "dollar") & (PATHS.path == "persistent") & (PATHS.quarter == 4)].ffr_equivalent.iloc[0])
S("fig1:equity_ffr_points_stored", abs(fw.loc["equities", "frbus_weight"]) * 5.0); S("fig1:dollar_ffr_points_stored", fw.loc["dollar", "frbus_weight"] * 3.9)

# the hike's own spillovers against the policy-news responses (psi): which assets carry the GDP effect of (i) a funds-rate hike with full transmission and (ii) the usual announcement response?
# persistent per-unit q4 effects of the 10-year (parallel long rates, as in frbus_sensitivities) and the BBB spread, run here with the same vintage as everything else
PER = {}
s0, s1 = run([v for v in FIXED if v not in PASS], ["rg5", "rg10", "rg30"], 1.0); PER["rg10"] = 100 * np.log(s1.loc[start + 3, "xgdp"] / s0.loc[start + 3, "xgdp"])
s0, s1 = run(FIXED, ["rbbbp"], 1.0); PER["rbbbp"] = 100 * np.log(s1.loc[start + 3, "xgdp"] / s0.loc[start + 3, "xgdp"])
PER["equity_pct_rise"] = -RESP[("equity", "persistent")]["gdp"][3] / UNIT["equity"] * -1.0   # GDP per 1% FALL in wealth is gdp/unit (negative); per 1% rise is its negative
PER["equity_pct_fall"] = RESP[("equity", "persistent")]["gdp"][3] / UNIT["equity"]
PER["dollar_pct_rise"] = RESP[("dollar", "persistent")]["gdp"][3] / UNIT["dollar"]
for k, v in PER.items(): S(f"perunit_q4:{k}", v)
mw = pd.read_csv(os.path.join(HERE, "results", "market_weights.csv"), index_col=0)
psi = fw["market_response"]
S("psi_ten", psi["y10"]); S("psi_eq", psi["equities"]); S("psi_usd", psi["dollar"])
# (ii) replay of the usual announcement response (persistent): GDP at q4 per unit of policy news = psi_j x per-unit effect; equity psi is in CAPE log points, mapped one-to-one to percent of stock wealth as in Figure 1
rep = {"10-year yield": PER["rg10"] * psi["y10"], "Equity valuation": PER["equity_pct_fall"] * (-psi["equities"]) , "Dollar": PER["dollar_pct_rise"] * psi["dollar"]}
tot = sum(rep.values()); S("replay:gdp_q4", tot); S("replay:ffr_points_q4", tot / G[3])
for k, v in rep.items(): S(f"replay:{k}:gdp_q4", v); S(f"replay:{k}:share", v / tot)
# (i) the hike's own asset spillovers at q4, priced with the same per-unit effects (approximate: the within-year paths vary; policy-rate direct effect and other channels are the remainder)
hk = {"10-year yield": PER["rg10"] * HIKE["d_rg10"][3], "BBB spread": PER["rbbbp"] * HIKE["d_rbbbp"][3], "Equity valuation": PER["equity_pct_fall"] * (-HIKE["stock_wealth_pct"][3]),
      "Dollar": PER["dollar_pct_rise"] * HIKE["dollar_pct"][3]}
tot2 = sum(hk.values())
for k, v in hk.items(): S(f"hike_spill:{k}:gdp_q4", v); S(f"hike_spill:{k}:share_of_hike_gdp", v / G[3])
S("hike_spill:sum_priced", tot2); S("hike_spill:remainder_share", (G[3] - tot2) / G[3])
S("hike_vs_psi:ten_ratio", HIKE["d_rg10"][3] / psi["y10"]); S("hike_vs_psi:equity_ratio", HIKE["stock_wealth_pct"][3] / psi["equities"]); S("hike_vs_psi:dollar_ratio", HIKE["dollar_pct"][3] / psi["dollar"])
pd.DataFrame(sc, columns=["key", "value"]).to_csv(os.path.join(RES, "scalars_22_channels.csv"), index=False, float_format="%.6f")
print("runtime %.0f s" % (time.time() - t0))
print(CH.to_string())
print(pd.DataFrame(sc, columns=["key", "value"]).to_string())
