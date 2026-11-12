"""Step 2. Weights of the market index from the response to policy news in announcement windows; conversion of GS, NFCI and ANFCI to the market index's units;
FRB/US weights on the same variables; weights under alternative news series and event samples; bootstrap draws of the weights (resampling announcements).
Writes results/market_weights.csv, conversions.csv, frbus_weights.csv, weights_variants.csv, weights_boot.csv."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from lib import data, indexes as I
from lib.config import RES, REPS_W, SEED
from lib.report import Scalars

S = Scalars("weights")
raw = I.events_raw()
ev = I.events()
Y = ev[["UST10Y", "SP500", "DXY"]].values
w, psi, se = I.gls_weights(Y, ev.ns.values)
pd.DataFrame({"weight": w, "response": psi, "se": se}, index=I.MARKET_VARS).to_csv(RES / "market_weights.csv")
S.add("n_events", len(ev)); S.add("event_first", ev.Date.min().strftime("%B %Y")); S.add("event_last", ev.Date.max().strftime("%B %Y"))
for k, lab in enumerate(["ten", "eq", "usd"]):
    S.add(f"psi_{lab}", psi[k]); S.add(f"se_{lab}", se[k]); S.add(f"w_{lab}", w[k]); S.add(f"share_{lab}", w[k] * psi[k])
S.add("ns_sd", ev.ns.std())
print("baseline weights", w.round(4), "responses", psi.round(3))

# GS: response of the daily GS replication to policy news, previous business day to the day after (its dollar input is a noon series)
g = pd.read_csv(data.DATA / "gs_daily.csv", parse_dates=["date"]).set_index("date").gs_fci
chg = []
for d in ev.Date:
    i = g.index.searchsorted(d)
    chg.append(g.iloc[i + 1] - g.iloc[i - 1] if 0 < i < len(g) - 1 and g.index[i] == d else np.nan)
ok = ~np.isnan(chg)
b_gs = sm.OLS(np.array(chg)[ok], sm.add_constant(ev.ns.values[ok])).fit(cov_type="HC1")
conv = {"GS": (b_gs.params[1], b_gs.bse[1])}
# NFCI, ANFCI: weekly change on the sum of policy news in the week (Friday-dated weeks), HAC 4 lags
for nm in ("NFCI", "ANFCI"):
    s = pd.read_csv(data.DATA / f"{nm}.csv"); s = pd.Series(s.iloc[:, 1].values, index=pd.to_datetime(s.iloc[:, 0]))
    wk = pd.Series(0.0, index=s.index)
    for d, v in zip(ev.Date, ev.ns):
        f = d + pd.Timedelta(days=(4 - d.weekday()) % 7)
        if f in wk.index:
            wk[f] += v
    j = pd.DataFrame({"dy": s.diff(), "ns": wk}).loc["1994-01-01":].dropna()
    r = sm.OLS(j.dy, sm.add_constant(j.ns)).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    conv[nm] = (r.params["ns"], r.bse["ns"])
C = pd.DataFrame(conv, index=["response", "se"]).T
C["to_2y"] = 1 / C.response
C.to_csv(RES / "conversions.csv")
for nm in conv:
    S.add(f"resp_{nm.lower()}", conv[nm][0]); S.add(f"se_resp_{nm.lower()}", conv[nm][1])
print(C.round(3))

# FRB/US: weights at four quarters and response of each variable to a persistent 1 pp funds-rate hike
P, G = I.frbus_paths()
s = I.phi_at(P, 4) / G[4]
H = pd.read_csv(data.DATA / "frbus_hike_paths.csv").set_index("quarter").loc[4]
psi_f = {"y10": H["rg10"], "equities": H["stocks %"], "dollar": H["dollar %"]}
T3 = pd.DataFrame({"frbus_weight": [s[v] for v in I.MARKET_VARS], "market_weight": w, "frbus_response": [psi_f[v] for v in I.MARKET_VARS], "market_response": psi},
                  index=I.MARKET_VARS)
T3.to_csv(RES / "frbus_weights.csv")
S.add("frbus_yardstick", -G[4])
for k, lab in enumerate(["ten", "eq", "usd"]):
    S.add(f"ratio_{lab}", s[I.MARKET_VARS[k]] / w[k])
S.add("spsi_frbus", sum(s[v] * psi_f[v] for v in I.MARKET_VARS)); S.add("spsi_market", sum(s[v] * psi[k] for k, v in enumerate(I.MARKET_VARS)))
print(T3.round(3))

# Alternative news series and event samples
def variant(df, kind):
    f = I.news(df, kind)
    return I.gls_weights(df[["UST10Y", "SP500", "DXY"]].values, f)
VARS = {"baseline": (raw, "ns"), "two_year": (raw, "ust2y"), "to_2019": (raw[raw.Date < "2020-01-01"], "ns"),
        "no_lower_bound": (raw[(raw.Date < "2008-12-01") | (raw.Date >= "2015-12-01")], "ns")}
rows = []
for k, (df, kind) in VARS.items():
    wv, pv, sv = variant(df, kind)
    rows.append({"variant": k, "n": len(df), **{f"w_{a}": wv[i] for i, a in enumerate(("ten", "eq", "usd"))}, **{f"psi_{a}": pv[i] for i, a in enumerate(("ten", "eq", "usd"))},
                 **{f"share_{a}": wv[i] * pv[i] for i, a in enumerate(("ten", "eq", "usd"))}})
pd.DataFrame(rows).to_csv(RES / "weights_variants.csv", index=False)
print(pd.DataFrame(rows).round(3).to_string())

# Bootstrap: resample announcements with replacement, recompute the policy-news factor and the weights
rng = np.random.default_rng(SEED)
B = []
for _ in range(REPS_W):
    df = raw.iloc[rng.integers(0, len(raw), len(raw))].reset_index(drop=True)
    wb, pb, _ = variant(df, "ns")
    B.append(np.r_[wb, pb])
B = pd.DataFrame(B, columns=["w_ten", "w_eq", "w_usd", "psi_ten", "psi_eq", "psi_usd"])
B.to_csv(RES / "weights_boot.csv", index=False)
print(B.describe().round(3).loc[["mean", "std"]])
S.save()
