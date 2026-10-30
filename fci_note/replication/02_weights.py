"""Step 2. Market-index weights from policy news (Table 1), conversions of GS and NFCI/ANFCI to 2-year-yield units, and the FRB/US comparison (Table 3)."""
import numpy as np, pandas as pd
import statsmodels.api as sm
from fci import data, indexes as I, report

N = report.Numbers("weights")
ev = I.events()
w, psi, se = I.gls_weights(ev[["UST10Y", "SP500", "DXY"]].values, ev.ns.values)
N.add("NEvents", len(ev), "{:d}"); N.add("EventFirst", ev.Date.min().strftime("%B %Y"), "{}"); N.add("EventLast", ev.Date.max().strftime("%B %Y"), "{}")
names = ["10-year Treasury yield (pp)", "Equity valuation, 100 ln CAPE (percent)", "Real broad dollar, 100 ln (percent)"]
T = pd.DataFrame({"Response to policy news": [f"{p:+.2f} ({s:.2f})" for p, s in zip(psi, se)], "Weight": [f"{x:+.3f}" for x in w],
                  "Share of a policy move": [f"{x:.2f}" for x in w * psi]}, index=names)
report.table("tab1_market_weights", T)
for k, lab in enumerate(["Ten", "Eq", "Usd"]):
    N.add(f"Psi{lab}", abs(psi[k])); N.add(f"W{lab}", w[k], "{:.3f}"); N.add(f"Share{lab}", w[k] * psi[k])
pd.DataFrame({"weight": w, "response": psi, "se": se}, index=I.MARKET_VARS).to_csv(data.OUT / "market_weights.csv")

# GS: response of the daily GS replication to policy news, previous business day to the day after (its dollar input is a noon series)
g = pd.read_csv(data.DATA / "gs_daily.csv", parse_dates=["date"]).set_index("date").gs_fci
chg = []
for d in ev.Date:
    i = g.index.searchsorted(d)
    chg.append(g.iloc[i + 1] - g.iloc[i - 1] if 0 < i < len(g) - 1 and g.index[i] == d else np.nan)
ok = ~np.isnan(chg)
b_gs = sm.OLS(np.array(chg)[ok], sm.add_constant(ev.ns.values[ok])).fit(cov_type="HC1")
# NFCI, ANFCI: weekly change on the sum of policy news in the week (Friday-dated weeks), HAC 4
conv = {"GS": (b_gs.params[1], b_gs.bse[1])}
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
C.to_csv(data.OUT / "conversions.csv")
print(C.round(3))
N.add("GSResp", conv["GS"][0]); N.add("NFCIResp", conv["NFCI"][0], "{:.3f}"); N.add("ANFCIResp", conv["ANFCI"][0], "{:.3f}")

# FRB/US: impulse-response weights at 4 quarters and the response of each variable to a persistent 1 pp hike (weighting note)
P, G = I.frbus_paths()
s = I.phi_at(P, 4) / G[4]
H = pd.read_csv(data.DATA / "frbus_hike_paths.csv").set_index("quarter").loc[4]
psi_f = {"y10": H["rg10"], "equities": H["stocks %"], "dollar": H["dollar %"]}
T3 = pd.DataFrame({"FRB/US weight": [s[v] for v in I.MARKET_VARS], "Market weight": w,
                   "FRB/US response": [psi_f[v] for v in I.MARKET_VARS], "Market response": psi}, index=["10-year yield", "Equities (CAPE)", "Real dollar"])
report.table("tab3_frbus_vs_market", T3, fmt="{:+.3f}")
N.add("FrbusYardstick", -G[4], "{:.4f}")
for k, v in enumerate(I.MARKET_VARS):
    N.add(f"Ratio{['Ten','Eq','Usd'][k]}", s[v] / w[k])
N.add("SPsiFrbus", sum(s[v] * psi_f[v] for v in I.MARKET_VARS)); N.add("SPsiMarket", sum(s[v] * psi[k] for k, v in enumerate(I.MARKET_VARS)))
print(T3.round(3))
N.write()
