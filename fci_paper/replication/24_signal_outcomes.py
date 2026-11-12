"""Step 24. Referee follow-ups: (A) a null benchmark for the size of D; (B) the composition tests under each definition of policy news; (C) the net-export result with D split by asset.
(A) benchmark: mean |w1'x - w0'x| / mean |w0'x| on the 12-month changes of the three assets, 1996-2026, for (i) bootstrap draws of the baseline market weights against the baseline point weights
    (within-market sampling noise), (ii) the other market definitions against the baseline, (iii) the normalised FRB/US weights against each market definition. The FRB/US-vs-market ratio should be read against (i) and (ii).
(B) for each definition d: D_d = (w_B,d - w_M,d)'x with w_B,d = b/(b'psi_d); regressions of step 19 (unemployment gap 12 months ahead; GDP growth four quarters ahead) and step 23 (net exports) on own lags, dM_d, D_d; gamma and gamma-beta with HAC 90% intervals.
(C) net exports on own lags, dM and D split into its three asset parts (weight gap x 12-month change of the asset), and on the three asset changes entered freely (baseline definition).
Writes results/24_*.csv and scalars_24_signal_outcomes.csv."""
import numpy as np, pandas as pd, statsmodels.api as sm
from lib import comp_core as C
from lib.config import RES, DATA
from lib.report import Scalars
from lib.stance_core import ffg, own

S = Scalars("24_signal_outcomes")
X, X12, dM0, D0, dB0, chk, W = C.changes()
b = W["b"]; FF = ffg("rstar").diff(12)
D21 = pd.read_csv(RES / "21_defs.csv")
def dq(d, q): return float(D21[(D21.definition == d) & (D21.quantity == q)].point.iloc[0])
DEFS = ("baseline", "two_year", "to_2019", "no_lower_bound")
wM = {d: np.array([dq(d, "wM_ten"), dq(d, "wM_eq"), dq(d, "wM_usd")]) for d in DEFS}; psi = {d: np.array([dq(d, "psi_ten"), dq(d, "psi_eq"), dq(d, "psi_usd")]) for d in DEFS}
wB = {d: b / (b @ psi[d]) for d in DEFS}
assert np.allclose(wM["baseline"], W["wM"], atol=1e-6) and np.allclose(wB["baseline"], W["wB"], atol=1e-6)
x = X12.loc["1996-01":"2026-09", C.VARS].values
# (A)
def ratio(w1, w0, xx=x): return float(np.mean(np.abs(xx @ (w1 - w0))) / np.mean(np.abs(xx @ w0)))
WBd = pd.read_csv(RES / "weights_boot.csv"); draws = [ratio(r[["w_ten", "w_eq", "w_usd"]].values.astype(float), wM["baseline"]) for _, r in WBd.iterrows()]
S.add("nb_within_market_median", float(np.median(draws))); S.add("nb_within_market_lo", float(np.percentile(draws, 5))); S.add("nb_within_market_hi", float(np.percentile(draws, 95)))
for d in DEFS[1:]: S.add(f"nb_market_{d}_vs_baseline", ratio(wM[d], wM["baseline"]))
for d in DEFS: S.add(f"nb_frbus_vs_market_{d}", ratio(wB[d], wM[d]))
# (B)
def regs_for(d):
    dM = X12 @ wM[d]; D = X12 @ (wB[d] - wM[d]); return {"dM": dM, "D": D}
def frame_net(c, regs, start):
    f4 = c.rolling(4).mean(); y = f4.shift(-4); ix = pd.PeriodIndex([k.asfreq("M", "e") for k in c.index], freq="M")
    cols = {"y": pd.Series(y.values, ix), "g4": pd.Series(f4.values, ix), "g1": pd.Series(c.values, ix)}
    for k, v in regs.items(): cols[k] = v.reindex(ix)
    return pd.DataFrame(cols).loc[start:"2026-09"].dropna()
def q(name):
    d = pd.read_csv(DATA / f"{name}.csv"); return pd.Series(d.iloc[:, 1].values, index=pd.PeriodIndex(pd.to_datetime(d.observation_date), freq="Q"))
NET = q("A019RY2Q224SBEA"); DOM = q("DPCERY2Q224SBEA") + q("A006RY2Q224SBEA")
rows = []
def fit(dname, outcome, Dd, cols, lags):
    r = C.hac(Dd, cols, lags); ci = r.conf_int(alpha=0.10)
    out = {}
    for term in cols:
        if term in ("dM", "D") or term.startswith("D_"):
            rows.append(dict(definition=dname, outcome=outcome, term=term, n=len(Dd), coef=r.params[term], se=r.bse[term], lo90=ci.loc[term, 0], hi90=ci.loc[term, 1]))
    if "dM" in cols and "D" in cols:
        t = r.t_test(f"D - dM = 0"); lo, hi = t.conf_int(alpha=0.10)[0]
        rows.append(dict(definition=dname, outcome=outcome, term="gamma_minus_beta", n=len(Dd), coef=float(np.squeeze(t.effect)), se=float(np.squeeze(t.sd)), lo90=lo, hi90=hi))
for d in DEFS:
    regs = regs_for(d)
    Du = C.frame("du", regs, FF, "1976-03", []); fit(d, "unemployment", Du, own("du") + ["dM", "D"], 18)
    Dg = C.gdp_frame(regs, FF, "1976-03", []); fit(d, "gdp", Dg, ["g4", "g1", "dM", "D"], 6)
    for nm, c in (("net_exports", NET), ("private_domestic", DOM)):
        fit(d, nm, frame_net(c, regs, "1976-03"), ["g4", "g1", "dM", "D"], 6)
# (C) split of D by asset, baseline
dwt = wB["baseline"] - wM["baseline"]
reg_c = {"dM": dM0, "D_ten": X12.y10 * dwt[0], "D_eq": X12.equities * dwt[1], "D_usd": X12.dollar * dwt[2], "dy10": X12.y10, "deq": X12.equities, "dusd": X12.dollar}
Fn = frame_net(NET, reg_c, "1976-03")
fit("baseline_split", "net_exports", Fn, ["g4", "g1", "dM", "D_ten", "D_eq", "D_usd"], 6)
r = C.hac(Fn, ["g4", "g1", "dy10", "deq", "dusd"], 6); ci = r.conf_int(alpha=0.10)
for t_ in ("dy10", "deq", "dusd"): rows.append(dict(definition="baseline_free", outcome="net_exports", term=t_, n=len(Fn), coef=r.params[t_], se=r.bse[t_], lo90=ci.loc[t_, 0], hi90=ci.loc[t_, 1]))
R = pd.DataFrame(rows); R.to_csv(RES / "24_signal_outcomes.csv", index=False)
for _, r in R.iterrows():
    for k in ("coef", "lo90", "hi90"): S.add(f"so_{r.definition}_{r.outcome}_{r.term}_{k}", r[k])
S.save(); print(R.round(3).to_string()); print({k: round(v, 3) for k, v in S.items.items() if k.startswith("nb_")})
